import 'package:flutter/material.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/storage/local_storage.dart';
import '../../../../shared/components/feedback/t_snackbar.dart';
import '../../../home/ui/main_navigation_screen.dart';
import '../../data/auth_api_service.dart';
import '../../data/auth_repository.dart';

import '../../../../core/notification/notification_controller.dart';

class LoginController extends ChangeNotifier {
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  final formKey = GlobalKey<FormState>();

  bool isLoading = false;
  late final AuthRepository _repository;

  LoginController() {
    final storage = LocalStorage();
    final apiClient = ApiClient(localStorage: storage);
    final apiService = AuthApiService(apiClient: apiClient);
    _repository = AuthRepository(apiService: apiService, localStorage: storage);
  }

  @override
  void dispose() {
    emailController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  bool isTecnico = false;

  void toggleRole() {
    isTecnico = !isTecnico;
    notifyListeners();
  }

  Future<void> login(BuildContext context) async {
    if (formKey.currentState?.validate() ?? false) {
      isLoading = true;
      notifyListeners();
      
      try {
        await _repository.loginAndSaveSession(
          emailController.text.trim(),
          passwordController.text,
          rol: isTecnico ? 'tecnico' : 'cliente',
        );

        // Registrar token de notificaciones al iniciar sesión
        await NotificationController.initNotifications();
        
        if (!context.mounted) return;

        TSnackbar.success(context, '¡Inicio de sesión exitoso!');
        
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const MainNavigationScreen()),
        );
      } catch (e) {
        if (!context.mounted) return;
        TSnackbar.error(context, e.toString());
      } finally {
        isLoading = false;
        notifyListeners();
      }
    }
  }

  void resetPassword() {
    // Lógica para resetear contraseña
  }
}
