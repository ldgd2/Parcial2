import 'package:dio/dio.dart';
import '../storage/local_storage.dart';

class ApiClient {
  final Dio dio;
  final LocalStorage localStorage;

  // URL del servidor local donde corre el backend de FastAPI
  static const String serverUrl = 'http://192.168.100.244:8000';
  static const String baseUrl = '$serverUrl/api/v1';

  ApiClient({required this.localStorage}) : dio = Dio(BaseOptions(baseUrl: baseUrl)) {
    // Interceptor para inyectar automáticamente el token JWT en cada llamada
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Buscamos el token en SharedPreferences
          final token = await localStorage.getToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          options.headers['Content-Type'] = 'application/json';
          return handler.next(options);
        },
        onError: (DioException e, handler) async {
          // Si el token expiró (401), podríamos disparar una alerta global o redirect al login
          if (e.response?.statusCode == 401) {
            await localStorage.clearSession();
            // TODO: Emitir evento para desloguear al usuario a nivel UI
          }
          return handler.next(e);
        },
      ),
    );
  }
}
