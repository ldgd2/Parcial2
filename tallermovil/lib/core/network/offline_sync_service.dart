import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:tallermovil/core/notification/notification_controller.dart';
import 'package:dio/dio.dart';

class OfflineSyncService {
  static final OfflineSyncService _instance = OfflineSyncService._internal();
  factory OfflineSyncService() => _instance;
  OfflineSyncService._internal();

  Database? _db;
  bool _isSyncing = false;

  Future<Database> get database async {
    if (_db != null) return _db!;
    _db = await _initDB();
    return _db!;
  }

  Future<Database> _initDB() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'offline_sync.db');

    return await openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE offline_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            method TEXT NOT NULL,
            headers TEXT,
            payload TEXT,
            files_paths TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
          )
        ''');
      },
    );
  }

  /// Inicia el listener de conexión para sincronizar automáticamente
  void initialize() {
    Connectivity().onConnectivityChanged.listen((List<ConnectivityResult> results) {
      if (results.any((r) => r == ConnectivityResult.mobile || r == ConnectivityResult.wifi)) {
        syncPendingRequests();
      }
    });
  }

  Future<void> saveOfflineRequest({
    required String url,
    required String method,
    Map<String, dynamic>? headers,
    Map<String, dynamic>? payload,
    List<String>? filesPaths,
  }) async {
    final db = await database;
    await db.insert('offline_requests', {
      'url': url,
      'method': method,
      'headers': headers != null ? jsonEncode(headers) : null,
      'payload': payload != null ? jsonEncode(payload) : null,
      'files_paths': filesPaths != null ? jsonEncode(filesPaths) : null,
    });
    
    // Notificar al usuario que se guardó offline (opcional, el interceptor mostrará un Toast o notificación también)
    await NotificationController.showLocalNotification(
      title: "Modo Offline Activo",
      body: "Tu petición se enviará cuando haya conexión.",
      payload: {"tipo": "offline_queued"}
    );
  }

  /// Intenta enviar todas las peticiones pendientes
  Future<void> syncPendingRequests() async {
    if (_isSyncing) return;
    
    final connectivityResult = await Connectivity().checkConnectivity();
    if (connectivityResult.every((r) => r == ConnectivityResult.none)) return;

    _isSyncing = true;
    try {
      final db = await database;
      final pending = await db.query('offline_requests', orderBy: 'created_at ASC');

      if (pending.isEmpty) {
        _isSyncing = false;
        return;
      }

      debugPrint("Sincronizando \${pending.length} peticiones offline...");
      
      // Necesitamos un cliente dio básico para no volver a pasar por el interceptor offline
      // Se podría inyectar ApiClient, pero para evitar dependencias circulares, instanciamos uno
      // o usamos ApiClient sin el interceptor offline. Usaremos un Dio limpio por ahora.
      // IMPORTANTE: si las peticiones requieren Token, deberíamos inyectarlo, pero ya vienen
      // con el token original dentro de la columna 'headers'.
      
      final dioClient = Dio();

      for (var row in pending) {
        final id = row['id'] as int;
        
        try {
          final url = row['url'] as String;
          final method = row['method'] as String;
          final headersStr = row['headers'] as String?;
          final payloadStr = row['payload'] as String?;
          final filesPathsStr = row['files_paths'] as String?;

          final headers = headersStr != null ? jsonDecode(headersStr) as Map<String, dynamic> : null;
          final payload = payloadStr != null ? jsonDecode(payloadStr) as Map<String, dynamic> : null;
          final filesPaths = filesPathsStr != null ? List<String>.from(jsonDecode(filesPathsStr)) : <String>[];

          dynamic requestData = payload;

          // Si hay archivos, convertimos a FormData
          // (Asumiremos que el backend los recibe con una key específica como 'files', 
          // dependiendo de tu API, tal vez tengas que serializarlos distinto, 
          // pero el estándar es multipart/form-data)
          if (filesPaths.isNotEmpty) {
            final formData = FormData();
            
            // Añadir campos del payload
            if (payload != null) {
              payload.forEach((key, value) {
                formData.fields.add(MapEntry(key, value.toString()));
              });
            }

            // Añadir archivos
            for (var path in filesPaths) {
               final fileName = path.split('/').last;
               formData.files.add(MapEntry(
                 'files', // <-- esto asume que en el backend se recibe en el form param 'files'
                 await MultipartFile.fromFile(path, filename: fileName)
               ));
            }
            requestData = formData;
          }

          // Ejecutar petición original
          final options = Options(
            method: method,
            headers: headers?.map((key, value) => MapEntry(key, value.toString())),
          );

          await dioClient.request(
            url,
            data: requestData,
            options: options,
          );

          // Si el envío fue exitoso (retorna código 2xx/3xx), elimina de la base de datos local
          await db.delete('offline_requests', where: 'id = ?', whereArgs: [id]);
          
        } catch (e) {
          debugPrint("Error sincronizando petición offline ID \$id: \$e");
          // Si es un DioException y el backend respondió (por ejemplo un 400 Bad Request o un 500)
          // podríamos decidir si borrarlo para no atorar la cola, 
          // o dejarlo para reintentar. Por ahora lo dejamos.
        }
      }
      
      if (pending.isNotEmpty) {
        await NotificationController.showLocalNotification(
          title: "Sincronización Exitosa",
          body: "Tus peticiones pendientes fueron enviadas al servidor.",
          payload: {"tipo": "sync_ok"}
        );
      }

    } finally {
      _isSyncing = false;
    }
  }
}
