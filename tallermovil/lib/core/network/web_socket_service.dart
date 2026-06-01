import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../storage/local_storage.dart';

class WebSocketService {
  WebSocketChannel? _channel;
  final StreamController<Map<String, dynamic>> _messageController = StreamController.broadcast();
  
  Stream<Map<String, dynamic>> get messages => _messageController.stream;

  Future<void> connect(int emergenciaId) async {
    try {
      final userId = await LocalStorage().getUserId();
      final rol = await LocalStorage().getRol();
      
      // En entorno de desarrollo (ej. emulador Android)
      final baseUrl = 'ws://192.168.100.244:8000';
      final wsUrl = Uri.parse('$baseUrl/api/v1/ws/auxilio/$emergenciaId?user_id=$userId&role=$rol');
      
      _channel = WebSocketChannel.connect(wsUrl);
      
      _channel?.stream.listen(
        (data) {
          try {
            final decoded = json.decode(data as String);
            _messageController.add(decoded);
          } catch (e) {
            debugPrint('Error decodificando WS: $e');
          }
        },
        onError: (error) {
          debugPrint('Error en WebSocket: $error');
        },
        onDone: () {
          debugPrint('WebSocket cerrado.');
        },
      );
    } catch (e) {
      debugPrint('Error al conectar WebSocket: $e');
    }
  }

  void sendGpsUpdate(double lat, double lng, double destLat, double destLng) {
    if (_channel != null) {
      _channel!.sink.add(json.encode({
        'type': 'gps',
        'lat': lat,
        'lng': lng,
        'dest_lat': destLat,
        'dest_lng': destLng,
      }));
    }
  }

  void sendChatMessage(String text, String senderName) {
    if (_channel != null) {
      _channel!.sink.add(json.encode({
        'type': 'chat',
        'text': text,
        'sender_name': senderName,
      }));
    }
  }

  void disconnect() {
    _channel?.sink.close();
    _channel = null;
  }

  void dispose() {
    disconnect();
    _messageController.close();
  }
}
