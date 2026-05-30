import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:tallermovil/features/emergencies/views/report_emergency/emergency_upload_controller.dart';
import 'package:tallermovil/core/notification/notification_controller.dart';

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
          CREATE TABLE offline_emergencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audio_path TEXT,
            image_paths TEXT,
            placa TEXT,
            descripcion TEXT,
            latitude REAL,
            longitude REAL,
            address TEXT,
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
        syncPendingEmergencies();
      }
    });
  }

  /// Guarda una solicitud en la base de datos local
  Future<void> saveOfflineEmergency({
    String? audioPath,
    required List<String> imagePaths,
    required String placa,
    required String descripcion,
    required double latitude,
    required double longitude,
    required String address,
  }) async {
    final db = await database;
    await db.insert('offline_emergencies', {
      'audio_path': audioPath,
      'image_paths': jsonEncode(imagePaths),
      'placa': placa,
      'descripcion': descripcion,
      'latitude': latitude,
      'longitude': longitude,
      'address': address,
    });
    
    // Notificar al usuario que se guardó offline
    await NotificationController.showLocalNotification(
      title: "Modo Offline Activo",
      body: "Tu emergencia fue guardada. Se enviará automáticamente cuando recuperes la conexión.",
      payload: {"tipo": "emergencia_offline"}
    );
  }

  /// Intenta enviar todas las emergencias pendientes
  Future<void> syncPendingEmergencies() async {
    if (_isSyncing) return;
    
    // Verifica si realmente hay internet
    final connectivityResult = await Connectivity().checkConnectivity();
    if (connectivityResult.every((r) => r == ConnectivityResult.none)) return;

    _isSyncing = true;
    try {
      final db = await database;
      final pending = await db.query('offline_emergencies', orderBy: 'created_at ASC');

      if (pending.isEmpty) {
        _isSyncing = false;
        return;
      }

      debugPrint("Sincronizando \${pending.length} emergencias offline...");

      for (var row in pending) {
        final id = row['id'] as int;
        
        try {
          // Llama al controller (que ya tiene la lógica de upload multimedia y POST)
          await EmergencyUploadController().queueEmergency(
            audioPath: row['audio_path'] as String?,
            imagePaths: List<String>.from(jsonDecode(row['image_paths'] as String)),
            placa: row['placa'] as String,
            descripcion: row['descripcion'] as String,
            latitude: row['latitude'] as double,
            longitude: row['longitude'] as double,
            address: row['address'] as String,
            isSync: true, // Flag para evitar notificación duplicada de éxito
          );

          // Si el envío fue exitoso, elimina de la base de datos local
          await db.delete('offline_emergencies', where: 'id = ?', whereArgs: [id]);
          
        } catch (e) {
          debugPrint("Error sincronizando emergencia offline ID \$id: \$e");
          // Si falla, se queda en la BD para el próximo intento.
        }
      }
      
      // Notificar éxito si se subieron registros
      if (pending.isNotEmpty) {
        await NotificationController.showLocalNotification(
          title: "Sincronización Exitosa",
          body: "Tus emergencias pendientes fueron enviadas al servidor.",
          payload: {"tipo": "emergencia_sync_ok"}
        );
      }

    } finally {
      _isSyncing = false;
    }
  }
}
