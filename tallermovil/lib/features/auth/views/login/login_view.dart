import 'package:flutter/material.dart';
import '../../../../shared/components/buttons/t_button.dart';
import '../../../../shared/components/cards/t_card.dart';
import '../../../../shared/components/inputs/t_text_input.dart';
import '../../../../shared/components/layout/t_spacing.dart';
import '../../../../shared/layouts/form_page_layout.dart';
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
        
        // Tema dinámico choquito
        final currentTheme = Theme.of(context);
        final dynamicTheme = currentTheme.copyWith(
          colorScheme: currentTheme.colorScheme.copyWith(
            primary: isTecnico ? Colors.redAccent.shade700 : currentTheme.colorScheme.primary,
          ),
        );

        return AnimatedTheme(
          data: dynamicTheme,
          duration: const Duration(milliseconds: 500),
          curve: Curves.easeInOutCubic,
          child: FormPageLayout(
            title: isTecnico ? "Portal Técnico" : "Bienvenido",
            formKey: controller.formKey,
            body: Column(
              children: [
                TSpacing.verticalXLarge(),
                
                // Animated Switcher for the Logo
                AnimatedSwitcher(
                  duration: const Duration(milliseconds: 500),
                  transitionBuilder: (child, animation) => ScaleTransition(scale: animation, child: child),
                  child: Icon(
                    isTecnico ? Icons.build_circle : Icons.directions_car, 
                    key: ValueKey(isTecnico),
                    size: 80, 
                    color: isTecnico ? Colors.redAccent.shade700 : currentTheme.colorScheme.primary
                  ),
                ),
                TSpacing.verticalLarge(),
                
                AnimatedContainer(
                  duration: const Duration(milliseconds: 500),
                  curve: Curves.easeInOutCubic,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: isTecnico ? Colors.red.withOpacity(0.1) : Colors.transparent,
                        blurRadius: 20,
                        spreadRadius: 5,
                      )
                    ]
                  ),
                  child: TCard(
                    title: isTecnico ? "Acceso Operativo" : "Inicia Sesión",
                    child: Column(
                      children: [
                        TTextInput(
                          label: "Correo Electrónico",
                          hint: isTecnico ? "tecnico@taller.com" : "ejemplo@taller.com",
                          prefixIcon: Icons.email_outlined,
                          keyboardType: TextInputType.emailAddress,
                          controller: controller.emailController,
                          validator: (val) => val != null && val.contains('@') ? null : 'Correo inválido',
                        ),
                        TTextInput(
                          label: "Contraseña",
                          prefixIcon: Icons.lock_outline,
                          isPassword: true,
                          controller: controller.passwordController,
                          validator: (val) => val != null && val.length >= 6 ? null : 'Mínimo 6 caracteres',
                        ),
                        TSpacing.verticalMedium(),
                        TButton(
                          label: "Ingresar al Sistema",
                          onPressed: () => controller.login(context),
                          isLoading: controller.isLoading,
                          icon: Icons.login,
                        ),
                        TSpacing.verticalMedium(),
                        TButton(
                          label: "Olvidé mi contraseña",
                          onPressed: controller.resetPassword,
                          variant: TButtonVariant.text,
                        ),
                        const Divider(height: 30),
                        
                        // Botón de cambio de rol
                        AnimatedSwitcher(
                          duration: const Duration(milliseconds: 400),
                          child: TButton(
                            key: ValueKey(isTecnico),
                            label: isTecnico ? "¿No eres técnico? Ingresa como Cliente" : "Soy Técnico",
                            onPressed: controller.toggleRole,
                            variant: TButtonVariant.outline,
                            icon: isTecnico ? Icons.person : Icons.build,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                
                TSpacing.verticalXLarge(),
                AnimatedOpacity(
                  opacity: isTecnico ? 0.0 : 1.0,
                  duration: const Duration(milliseconds: 300),
                  child: isTecnico ? const SizedBox.shrink() : TButton(
                    label: "Crear Nueva Cuenta",
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => const RegisterView()),
                      );
                    },
                    variant: TButtonVariant.outline,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
