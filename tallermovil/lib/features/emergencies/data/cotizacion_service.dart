import 'package:dio/dio.dart';
import '../../../../core/network/api_client.dart';

class CotizacionService {
  final ApiClient apiClient;

  CotizacionService({required this.apiClient});

  /// Obtiene las cotizaciones de una emergencia
  Future<List<Map<String, dynamic>>> getCotizaciones(int idEmergencia) async {
    try {
      final response = await apiClient.dio.get('/cotizaciones/emergencia/$idEmergencia');
      return List<Map<String, dynamic>>.from(response.data);
    } on DioException catch (e) {
      throw Exception(e.response?.data?['detail'] ?? 'Error al cargar cotizaciones');
    }
  }

  /// Actualiza el estado de una cotización (Aceptar o Rechazar)
  Future<void> updateEstado(int idCotizacion, String nuevoEstado, {String? condiciones}) async {
    try {
      await apiClient.dio.put(
        '/cotizaciones/$idCotizacion/estado',
        data: {
          'estado': nuevoEstado,
          if (condiciones != null) 'condiciones': condiciones,
        },
      );
    } on DioException catch (e) {
      throw Exception(e.response?.data?['detail'] ?? 'Error al actualizar cotización');
    }
  }
}
