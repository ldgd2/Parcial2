import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/storage/local_storage.dart';
import '../../../shared/components/layout/t_list_tile.dart';
import '../../../shared/components/typography/t_text.dart';
import '../../../shared/components/layout/t_spacing.dart';
import '../../auth/views/login/login_view.dart';
import '../../payments/views/manage_cards_view.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: TText.h3('Ajustes'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(24.0),
        children: [
          TText.h2('Cuenta'),
          TSpacing.verticalMedium(),
          TListTile(
            title: 'Cerrar Sesión',
            subtitle: 'Finalizar sesión actual de forma segura',
            leading: const Icon(Icons.logout_outlined, color: AppColors.danger),
            onTap: () async {
              await LocalStorage().clearSession();
              if (!context.mounted) return;
              Navigator.pushAndRemoveUntil(
                context, 
                MaterialPageRoute(builder: (_) => const LoginView()),
                (route) => false
              );
            },
          ),
          TSpacing.verticalLarge(),
          TText.h2('Pagos'),
          TSpacing.verticalMedium(),
          TListTile(
            title: 'Mis Tarjetas',
            subtitle: 'Gestionar métodos de pago y tarjetas guardadas',
            leading: Icon(Icons.credit_card_outlined, color: Theme.of(context).colorScheme.primary),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const ManageCardsView()),
              );
            },
          ),
          TSpacing.verticalLarge(),
          TText.h2('Preferencias'),
          TSpacing.verticalMedium(),
          TListTile(
            title: 'Notificaciones',
            subtitle: 'Gestionar alertas y avisos',
            leading: Icon(Icons.notifications_outlined, color: Theme.of(context).colorScheme.primary),
            onTap: () {},
          ),
          TSpacing.verticalMedium(),
          TListTile(
            title: 'Privacidad y Seguridad',
            subtitle: 'Configurar accesos y datos',
            leading: Icon(Icons.security_outlined, color: Theme.of(context).colorScheme.primary),
            onTap: () {},
          ),
        ],
      ),
    );
  }
}
