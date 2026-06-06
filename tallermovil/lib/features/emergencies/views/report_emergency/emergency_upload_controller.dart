import 'dart:async';
import 'package:flutter/material.dart';
import 'package:tallermovil/core/notification/notification_controller.dart';
import 'package:tallermovil/core/network/api_client.dart';
import 'package:tallermovil/core/storage/local_storage.dart';
import 'package:tallermovil/features/emergencies/data/emergency_service.dart';
import 'package:tallermovil/features/emergencies/models/emergency_report.dart';
import 'package:uuid/uuid.dart';

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
    String? uuidLocal,
  }) async {
    if (isUploading) return;

    isUploading = true;
    progress = 0.1;
    currentError = null;
    notifyListeners();

    final localId = uuidLocal ?? const Uuid().v4();

    try {
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
        uuidLocal: localId,
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
      
      // Si el interceptor de Dio resolvió con un 200 OK falso para offline, podemos detectarlo
      // Pero dado que la UI puede procesar el 'success' igual, está bien.
      
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
