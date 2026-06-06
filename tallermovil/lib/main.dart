import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import 'core/theme/app_theme.dart';
import 'core/theme/app_colors.dart';
import 'shared/widgets/primary_button.dart';
import 'shared/widgets/custom_text_field.dart';
import 'shared/widgets/glass_card.dart';
import 'shared/widgets/status_badge.dart';

import 'features/auth/views/login/login_view.dart';


import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_stripe/flutter_stripe.dart';
import 'core/notification/notification_controller.dart';
import 'core/config/stripe_config.dart';
import 'core/network/offline_sync_service.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Inicializar Firebase
  try {
    await Firebase.initializeApp();
    // Configurar handler en segundo plano
    FirebaseMessaging.onBackgroundMessage(NotificationController.firebaseMessagingBackgroundHandler);
    // Inicializar controlador de notificaciones
    await NotificationController.initNotifications();
  } catch (e) {
    debugPrint('⚠️ Firebase no pudo inicializarse (Verificar google-services.json): $e');
  }

  // Inicializar Stripe
  try {
    Stripe.publishableKey = StripeConfig.publishableKey;
    Stripe.merchantIdentifier = StripeConfig.merchantIdentifier;
    await Stripe.instance.applySettings();
  } catch (e) {
    debugPrint('⚠️ Stripe no pudo inicializarse: $e');
  }

  // Inicializar servicio de sincronización offline (CU16)
  OfflineSyncService().initialize();

  runApp(const TallerMovilApp());
}

class TallerMovilApp extends StatefulWidget {
  static final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();
  
  const TallerMovilApp({super.key});

  @override
  State<TallerMovilApp> createState() => _TallerMovilAppState();
}

class _TallerMovilAppState extends State<TallerMovilApp> {
  bool _isOffline = false;

  @override
  void initState() {
    super.initState();
    Connectivity().onConnectivityChanged.listen((results) {
      setState(() {
        _isOffline = results.contains(ConnectivityResult.none);
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Taller Móvil OS',
      navigatorKey: TallerMovilApp.navigatorKey,
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme, // Inyectando nuestro Design System
      home: const LoginView(),
      builder: (context, child) {
        return Column(
          children: [
            if (_isOffline)
              Container(
                width: double.infinity,
                color: Colors.red,
                padding: const EdgeInsets.only(top: 40, bottom: 4), // Para el SafeArea
                child: const Text(
                  'fuera de conexion',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold, decoration: TextDecoration.none),
                ),
              ),
            Expanded(child: child ?? const SizedBox()),
          ],
        );
      },
    );
  }
}

class ThemeShowcaseScreen extends StatefulWidget {
  const ThemeShowcaseScreen({super.key});

  @override
  State<ThemeShowcaseScreen> createState() => _ThemeShowcaseScreenState();
}

class _ThemeShowcaseScreenState extends State<ThemeShowcaseScreen> {
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('FieldWork OS Components'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Typografía
            Text('Typography', style: Theme.of(context).textTheme.labelSmall),
            const SizedBox(height: 16),
            Text('Header 1', style: Theme.of(context).textTheme.displayLarge),
            Text('Header 2', style: Theme.of(context).textTheme.displayMedium),
            Text('Header 3', style: Theme.of(context).textTheme.displaySmall),
            const SizedBox(height: 8),
            Text('This is a body text displaying the Inter font mapping exactly like the web. Dynamic, legible, and crisp.', style: Theme.of(context).textTheme.bodyMedium),
            
            const SizedBox(height: 32),
            
            // Badges
            Text('Status Badges', style: Theme.of(context).textTheme.labelSmall),
            const SizedBox(height: 16),
            const Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                StatusBadge(text: 'En Curso', status: BadgeStatus.info),
                StatusBadge(text: 'Completado', status: BadgeStatus.success),
                StatusBadge(text: 'Critico', status: BadgeStatus.error),
                StatusBadge(text: 'Pendiente', status: BadgeStatus.warning),
              ],
            ).animate().fadeIn().slideX(),

            const SizedBox(height: 32),

            // Inputs
            Text('Form Controls', style: Theme.of(context).textTheme.labelSmall),
            const SizedBox(height: 16),
            const CustomTextField(
              label: 'Patente / Placa',
              hint: 'Ej: AB 123 CD',
              prefixIcon: Icon(Icons.directions_car_outlined, color: AppColors.textMuted),
            ).animate().fadeIn(delay: 200.ms).slideY(begin: 0.1),

            const SizedBox(height: 32),

            // Tarjetas (GlassCards)
            Text('Surface Cards (Glass)', style: Theme.of(context).textTheme.labelSmall),
            const SizedBox(height: 16),
            GlassCard(
              onTap: () {},
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Audi Q5 - Fallo Motor', style: Theme.of(context).textTheme.displaySmall),
                      const StatusBadge(text: 'Urgente', status: BadgeStatus.error),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text('Operador reportó humo saliendo por la parte frontal después de impacto leve.', style: Theme.of(context).textTheme.bodyMedium),
                ],
              ),
            ).animate().fadeIn(delay: 400.ms).scale(begin: const Offset(0.95, 0.95)),

            const SizedBox(height: 32),

            // Botones
            Text('Buttons & Actions', style: Theme.of(context).textTheme.labelSmall),
            const SizedBox(height: 16),
            PrimaryButton(
              text: 'Asignar Técnico',
              icon: Icons.person_add_outlined,
              isLoading: _isLoading,
              onPressed: () async {
                setState(() => _isLoading = true);
                await Future.delayed(2.seconds);
                setState(() => _isLoading = false);
              },
            ).animate().fadeIn(delay: 600.ms).slideY(begin: 0.1),
            
            const SizedBox(height: 16),
            
            PrimaryButton(
              text: 'Rechazar Solicitud',
              icon: Icons.close,
              isDestructive: true,
              onPressed: () {},
            ).animate().fadeIn(delay: 700.ms).slideY(begin: 0.1),
          ],
        ),
      ),
    );
  }
}
