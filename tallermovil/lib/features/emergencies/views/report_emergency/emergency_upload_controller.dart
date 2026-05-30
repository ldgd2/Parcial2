import 'dart:async';
import 'package:flutter/material.dart';
import 'package:tallermovil/core/notification/notification_controller.dart';
import 'package:tallermovil/core/network/api_client.dart';
import 'package:tallermovil/core/storage/local_storage.dart';
import 'package:tallermovil/features/emergencies/data/emergency_service.dart';
import 'package:tallermovil/features/emergencies/models/emergency_report.dart';
import 'package:tallermovil/core/network/offline_sync_service.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:dio/dio.dart';

class EmergencyUploadController extends ChangeNotifier {
  // Singleton
  static final EmergencyUploadController _instance = EmergencyUploadController._internal();
  factory EmergencyUploadController() => _instance;
  EmergencyUploadController._internal();

  bool isUploading = false;
  double progress = 0.0;
  String? currentError;

  final EmergencyService _emergencyService = EmergencyService(
    apiClient: ApiClient(localStorage: LocalStorage()),
  );

  Future<void> queueEmergency({
    required String? audioPath,
    required List<String> imagePaths,
    required String placa,
    required String descripcion,
    required double latitude,
    required double longitude,
    required String address,
    int? existingEmergencyId, // Si viene ID, es un UPDATE
    bool isSync = false,
  }) async {
    if (isUploading) return;

    isUploading = true;
    progress = 0.1;
    currentError = null;
    notifyListeners();

    try {
      // VERIFICACIÓN PWA OFFLINE: Si no hay internet, no intentamos enviar, guardamos localmente directo.
      if (!isSync) {
        final connectivityResult = await Connectivity().checkConnectivity();
        if (connectivityResult.every((r) => r == ConnectivityResult.none)) {
           isUploading = false;
           await OfflineSyncService().saveOfflineEmergency(
             audioPath: audioPath,
             imagePaths: imagePaths,
             placa: placa,
             descripcion: descripcion,
             latitude: latitude,
             longitude: longitude,
             address: address,
           );
           return;
        }
      }

      // 1. Subir multimedia (solo los archivos locales que no son URLs)
      final List<String> newFiles = [];
      final List<String> existingUrls = [];

      if (audioPath != null) {
        if (audioPath.startsWith('http') || audioPath.startsWith('/uploads')) {
          existingUrls.add(audioPath); // Es una URL, se mantiene
        } else {
          newFiles.add(audioPath);
        }
      }

      for (var path in imagePaths) {
        if (path.startsWith('http') || path.startsWith('/uploads')) {
          existingUrls.add(path);
        } else {
          newFiles.add(path);
        }
      }

      progress = 0.3;
      notifyListeners();

      String? audioUrl = audioPath?.startsWith('http') == true || audioPath?.startsWith('/uploads') == true ? audioPath : null;
      final List<String> imageUrls = List.from(existingUrls.where((u) => !u.endsWith('.m4a') && !u.endsWith('.aac')));
      String? rawTranscription;

      if (newFiles.isNotEmpty) {
        final uploadResult = await _emergencyService.uploadMultimedia(newFiles);
        final List<dynamic> archivos = uploadResult['archivos'];
        rawTranscription = uploadResult['transcripcion_cruda'];

        for (var f in archivos) {
          final url = f['url'] as String;
          if (url.endsWith('.m4a') || url.endsWith('.aac')) {
            audioUrl = url;
          } else {
            imageUrls.add(url);
          }
        }
      }
      
      progress = 0.7;
      notifyListeners();

      // 2. Enviar reporte (POST o PUT)
      final report = EmergencyReport(
        descripcion: descripcion.isNotEmpty ? descripcion : 'Emergencia reportada por audio/fotos',
        direccion: address,
        latitud: latitude,
        longitud: longitude,
        placaVehiculo: placa,
        audioUrl: audioUrl,
        evidenciasUrls: imageUrls,
        textoAdicional: rawTranscription,
      );

      if (existingEmergencyId != null) {
        await _emergencyService.updateEmergency(existingEmergencyId, report);
      } else {
        await _emergencyService.submitEmergency(report);
      }
      
      progress = 1.0;
      isUploading = false;
      notifyListeners();

      await NotificationController.showLocalNotification(
        title: existingEmergencyId != null ? "S.O.S. Actualizado" : "S.O.S. Enviado",
        body: "Tu reporte ha sido procesado correctamente.",
        payload: {"tipo": "emergencia_confirmada"}
      );

    } catch (e) {
      isUploading = false;
      currentError = e.toString();
      notifyListeners();
      
      // Fallback para CU16: Si hay un error de conexión, guardar en BD local
      if (e is DioException && 
          (e.type == DioExceptionType.connectionError || 
           e.type == DioExceptionType.receiveTimeout || 
           e.type == DioExceptionType.connectionTimeout)) {
        
        if (!isSync) { // No re-guardar si estamos intentando sincronizar
           await OfflineSyncService().saveOfflineEmergency(
             audioPath: audioPath,
             imagePaths: imagePaths,
             placa: placa,
             descripcion: descripcion,
             latitude: latitude,
             longitude: longitude,
             address: address,
           );
        }
        return; // Evita mostrar error de fallo completo, pues se guardó offline
      }

      if (!isSync) {
        await NotificationController.showLocalNotification(
          title: "Error en S.O.S.",
          body: "No pudimos procesar tu reporte. Reintenta.",
          payload: {"tipo": "emergencia_error"}
        );
      }
    }
  }

  Future<void> cancelEmergency(int id) async {
    try {
      await _emergencyService.cancelEmergency(id);
      // Opcional: refrescar UI o notificar
    } catch (e) {
      debugPrint("Error cancelando emergencia: $e");
    }
  }

  void clearError() {
    currentError = null;
    notifyListeners();
  }
}
