import '../../../core/storage/local_storage.dart';
import '../models/login_request.dart';
import '../models/register_request.dart';
import 'auth_api_service.dart';

class AuthRepository {
  final AuthApiService apiService;
  final LocalStorage localStorage;

  AuthRepository({
    required this.apiService,
    required this.localStorage,
  });

  /// Orquesta el flujo de negocio: llama a la API y persiste si fue exitoso
  Future<void> loginAndSaveSession(String username, String password, {String rol = 'cliente'}) async {
    // 1. Crear el objeto DTO
    final request = LoginRequest(correo: username, contrasena: password, rol: rol);
    
    // 2. Hacer la llamada de Red
    final authResponse = await apiService.login(request);

    // 3. Guardar en el dispositivo de forma segura el Token
    await localStorage.saveToken(authResponse.accessToken);

    // 4. Guardar datos de contexto de negocio
    await localStorage.saveSessionData(
      codTaller: authResponse.taller ?? '',
      rol: authResponse.rol,
      userId: authResponse.userId,
    );
  }

  /// Registra un nuevo cliente y su vehículo
  Future<void> register(RegisterRequest request) async {
    await apiService.register(request);
  }

  /// Limpia la sesión localmente y notifica al backend
  Future<void> logout() async {
    await apiService.logout();
    await localStorage.clearSession();
  }
}
