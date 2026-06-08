import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter/material.dart';
import '../network/api_client.dart';
import '../storage/local_storage.dart';
import '../../main.dart';
import '../../features/emergencies/views/detail/client/emergency_detail_view.dart';
import '../../features/chat/ui/chat_view.dart';

class NotificationController {
  static final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  static final FlutterLocalNotificationsPlugin _localNotifications = FlutterLocalNotificationsPlugin();

  static Future<void> initNotifications() async {
    // 1. Solicitar permisos
    NotificationSettings settings = await _messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      print('✅ Permisos de notificaciones concedidos.');
      
      // 2. Obtener Token
      String? token = await _messaging.getToken();
      if (token != null) {
        print('FCM Token: $token');
        await _saveTokenToBackend(token);
      }

      // 3. Suscribirse a tópico general
      await _messaging.subscribeToTopic('todos');
    }

    // 4. Configurar notificaciones locales para Android en primer plano
    const AndroidInitializationSettings initializationSettingsAndroid = AndroidInitializationSettings('@mipmap/ic_launcher');
    const InitializationSettings initializationSettings = InitializationSettings(android: initializationSettingsAndroid);
    
    await _localNotifications.initialize(settings: initializationSettings);

    // 5. Escuchar mensajes en primer plano
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      RemoteNotification? notification = message.notification;
      AndroidNotification? android = message.notification?.android;

      if (notification != null && android != null) {
        _localNotifications.show(
          id: notification.hashCode,
          title: notification.title,
          body: notification.body,
          notificationDetails: const NotificationDetails(
            android: AndroidNotificationDetails(
              'high_importance_channel',
              'High Importance Notifications',
              importance: Importance.max,
              priority: Priority.high,
              icon: '@mipmap/ic_launcher',
            ),
          ),
        );
      }
    });

    // 6. Escuchar cuando se abre la app desde una notificación (en segundo plano)
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      _handleNotificationClick(message);
    });

    // 7. Verificar si se abrió la app desde una notificación terminada
    RemoteMessage? initialMessage = await _messaging.getInitialMessage();
    if (initialMessage != null) {
      _handleNotificationClick(initialMessage);
    }
  }

  static void _handleNotificationClick(RemoteMessage message) async {
    final data = message.data;
    final emergencyId = data['emergencia_id'];

    if (emergencyId != null) {
      print('DEBUG NOTI: Click en emergencia $emergencyId - Tipo: ${data['tipo']}');
      
      final tipo = data['tipo'];
      if (tipo == 'chat') {
        TallerMovilApp.navigatorKey.currentState?.push(
          MaterialPageRoute(
            builder: (_) => ChatView(emergenciaId: int.parse(emergencyId.toString())),
          ),
        );
        return;
      }

      try {
        final storage = LocalStorage();
        final apiClient = ApiClient(localStorage: storage);
        
        final response = await apiClient.dio.get('/gestion-emergencia/$emergencyId');
        final emergency = response.data;

        TallerMovilApp.navigatorKey.currentState?.push(
          MaterialPageRoute(
            builder: (_) => EmergencyDetailView(emergency: emergency),
          ),
        );
      } catch (e) {
        print('Error navegando desde noti: $e');
      }
    }
  }

  static Future<void> _saveTokenToBackend(String token) async {
    try {
      final storage = LocalStorage();
      final tokenJwt = await storage.getToken();
      if (tokenJwt != null) {
        final apiClient = ApiClient(localStorage: storage);
        await apiClient.dio.post('/notificaciones/registrar-token', data: {
          'token': token,
          'dispositivo': 'android'
        });
        print('Token de notificación registrado en el backend.');
      }
    } catch (e) {
      print(' Error al registrar token en backend: $e');
    }
  }

  @pragma('vm:entry-point')
  static Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
    print("Handling a background message: ${message.messageId}");
  }

  static Future<void> showLocalNotification({
    required String title,
    required String body,
    Map<String, dynamic>? payload,
  }) async {
    await _localNotifications.show(
      id: DateTime.now().millisecondsSinceEpoch ~/ 1000,
      title: title,
      body: body,
      notificationDetails: const NotificationDetails(
        android: AndroidNotificationDetails(
          'local_channel',
          'Local Notifications',
          importance: Importance.max,
          priority: Priority.high,
          icon: '@mipmap/ic_launcher',
        ),
      ),
    );
  }
}
