import 'package:dio/dio.dart';
import '../../../../core/network/api_client.dart';
import '../models/emergency_report.dart';


class EmergencyService {
  final ApiClient apiClient;

  EmergencyService({required this.apiClient});

  /// Sube los archivos multimedia (audio y fotos) al servidor
  Future<Map<String, dynamic>> uploadMultimedia(List<String> filePaths) async {
    try {
      final List<MultipartFile> multipartFiles = [];
      for (final path in filePaths) {
        multipartFiles.add(await MultipartFile.fromFile(
          path,
          filename: path.split('/').last,
        ));
      }

      final formData = FormData.fromMap({
        'files': multipartFiles,
      });

      final response = await apiClient.dio.post(
        '/emergencias/upload-multimedia',
        data: formData,
      );

      return response.data;
    } on DioException catch (e) {
      throw Exception(e.response?.data?['detail'] ?? 'Error al subir archivos');
    }
  }

  /// Registra la emergencia oficial en el backend
  Future<void> submitEmergency(EmergencyReport report, {List<String>? localFiles}) async {
    try {
      await apiClient.dio.post(
        '/emergencias/reportar',
        data: report.toJson(),
      );
    } on DioException catch (e) {
      throw Exception(e.response?.data?['detail'] ?? 'Error al enviar reporte');
    }
  }

  /// Obtiene el historial de emergencias del cliente
  Future<List<Map<String, dynamic>>> getHistory() async {
    try {
      final response = await apiClient.dio.get('/emergencias/mis-solicitudes');
      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw Exception(e.response?.data?['detail'] ?? 'Error al cargar historial');
    }
  }

  /// Obtiene el historial de emergencias del taller (para el técnico)
  Future<List<Map<String, dynamic>>> getTallerHistory(String codTaller) async {
    try {
      final response = await apiClient.dio.get('/talleres/$codTaller/solicitudes');
      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw Exception(e.response?.data?['detail'] ?? 'Error al cargar historial del taller');
    }
  }

  /// Actualiza una emergencia (ej: corregir una rechazada por IA)
  Future<void> updateEmergency(int id, EmergencyReport report) async {
    try {
      await apiClient.dio.put(
        '/emergencias/$id',
        data: report.toJson(),
      );
    } on DioException catch (e) {
      throw Exception(e.response?.data?['detail'] ?? 'Error al actualizar reporte');
    }
  }

  /// Cancela una emergencia
  Future<void> cancelEmergency(int id) async {
    try {
      await apiClient.dio.delete('/emergencias/$id');
    } on DioException catch (e) {
      throw Exception(e.response?.data?['detail'] ?? 'Error al cancelar emergencia');
    }
  }
}
