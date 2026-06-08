import 'package:flutter/material.dart';
import '../../../../shared/components/buttons/t_button.dart';
import '../../../../shared/components/cards/t_card.dart';
import '../../../../shared/components/inputs/t_text_input.dart';

import '../register/register_view.dart';
import 'login_controller.dart';

class LoginView extends StatefulWidget {
  const LoginView({super.key});

  @override
  State<LoginView> createState() => _LoginViewState();
}

class _LoginViewState extends State<LoginView> {
  late final LoginController controller;

  @override
  void initState() {
    super.initState();
    controller = LoginController();
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, child) {
        final isTecnico = controller.isTecnico;
        
        final currentTheme = Theme.of(context);
        final dynamicColor = isTecnico ? const Color(0xFFFF5733) : const Color(0xFF3B82F6);
        
        final dynamicTheme = currentTheme.copyWith(
          colorScheme: currentTheme.colorScheme.copyWith(
            primary: dynamicColor,
            outlineVariant: const Color(0xFF222222),
          ),
        );

        return AnimatedTheme(
          data: dynamicTheme,
          duration: const Duration(milliseconds: 500),
          curve: Curves.easeInOutCubic,
          child: Scaffold(
            backgroundColor: const Color(0xFF050505),
            body: SafeArea(
              child: Center(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(24.0),
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 400),
                    child: TCard(
                      padding: 32.0,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          // Custom Header
                          Column(
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Text("■", style: TextStyle(color: dynamicColor, fontSize: 16)),
                                  const SizedBox(width: 8),
                                  const Text("FIELDWORK", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, letterSpacing: 3.0)),
                                  const Text("_OS", style: TextStyle(color: Color(0xFF71717A), fontWeight: FontWeight.bold, fontSize: 14, letterSpacing: 3.0)),
                                ],
                              ),
                              const SizedBox(height: 24),
                              Text("Acceso al Sistema".toUpperCase(), 
                                textAlign: TextAlign.center,
                                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, letterSpacing: 1.0)
                              ),
                              const SizedBox(height: 8),
                              Text(isTecnico ? "CREDENCIALES DE OPERADOR" : "CREDENCIALES DE CLIENTE",
                                textAlign: TextAlign.center,
                                style: const TextStyle(fontSize: 10, color: Color(0xFF71717A), letterSpacing: 2.0)
                              ),
                            ],
                          ),
                          const SizedBox(height: 24),
                          const Divider(color: Color(0xFF222222), height: 1),
                          const SizedBox(height: 24),

                          Form(
                            key: controller.formKey,
                            child: Column(
                              children: [
                                TTextInput(
                                  label: isTecnico ? "IDENTIFICADOR OPERATIVO" : "IDENTIFICADOR DE CLIENTE",
                                  hint: isTecnico ? "operador@taller.com" : "cliente@ejemplo.com",
                                  prefixIcon: Icons.terminal,
                                  keyboardType: TextInputType.emailAddress,
                                  controller: controller.emailController,
                                  validator: (val) => val != null && val.contains('@') ? null : 'CÓDIGO INVÁLIDO',
                                ),
                                TTextInput(
                                  label: "CLAVE DE ACCESO",
                                  prefixIcon: Icons.password,
                                  isPassword: true,
                                  controller: controller.passwordController,
                                  validator: (val) => val != null && val.length >= 6 ? null : 'MÍNIMO 6 CARACTERES',
                                ),
                                const SizedBox(height: 16),
                                TButton(
                                  label: controller.isLoading ? "SINCRONIZANDO..." : "INICIAR SESIÓN",
                                  onPressed: () => controller.login(context),
                                  isLoading: controller.isLoading,
                                  icon: Icons.login,
                                ),
                                const SizedBox(height: 16),
                                
                                AnimatedSwitcher(
                                  duration: const Duration(milliseconds: 400),
                                  child: TButton(
                                    key: ValueKey(isTecnico),
                                    label: isTecnico ? "INTERFAZ DE CLIENTE" : "INTERFAZ DE TALLER",
                                    onPressed: controller.toggleRole,
                                    variant: TButtonVariant.outline,
                                    icon: isTecnico ? Icons.person : Icons.build,
                                  ),
                                ),
                                const SizedBox(height: 16),
                                AnimatedOpacity(
                                  opacity: isTecnico ? 0.0 : 1.0,
                                  duration: const Duration(milliseconds: 300),
                                  child: isTecnico ? const SizedBox.shrink() : TButton(
                                    label: "REGISTRAR UNIDAD",
                                    onPressed: () {
                                      Navigator.push(
                                        context,
                                        MaterialPageRoute(builder: (context) => const RegisterView()),
                                      );
                                    },
                                    variant: TButtonVariant.text,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}
