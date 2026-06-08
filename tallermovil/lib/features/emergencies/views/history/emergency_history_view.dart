import 'package:flutter/material.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/components/cards/t_card.dart';
import '../../../../shared/components/feedback/t_badge.dart';
import '../../../../shared/components/layout/t_spacing.dart';
import '../../../../shared/components/typography/t_text.dart';
import '../../../../shared/components/loaders/t_loader.dart';
import 'emergency_history_controller.dart';
import '../detail/emergency_detail_view.dart';

class EmergencyHistoryView extends StatefulWidget {
  const EmergencyHistoryView({super.key});

  @override
  State<EmergencyHistoryView> createState() => _EmergencyHistoryViewState();
}

class _EmergencyHistoryViewState extends State<EmergencyHistoryView> {
  late final EmergencyHistoryController controller;

  @override
  void initState() {
    super.initState();
    controller = EmergencyHistoryController();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, child) {
        if (controller.isLoading) {
          return const Center(child: TLoader());
        }

        if (controller.emergencies.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.history_outlined, size: 64, color: AppColors.textMuted),
                TSpacing.verticalMedium(),
                TText.h3('No tienes reportes aún'),
                TText.body('Tus solicitudes aparecerán aquí.'),
              ],
            ),
          );
        }

        return RefreshIndicator(
          onRefresh: controller.loadHistory,
          child: ListView.builder(
            padding: const EdgeInsets.all(24.0),
            itemCount: controller.emergencies.length,
            itemBuilder: (context, index) {
              final emergency = controller.emergencies[index];
              final status = emergency['estado_actual'] ?? 'PENDIENTE';
              final color = _getStatusColor(status, context);
              
              return Padding(
                padding: const EdgeInsets.only(bottom: 16.0),
                child: TCard(
                  onTap: () async {
                    await Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => EmergencyDetailView(emergency: emergency),
                      ),
                    );
                    controller.loadHistory();
                  },
                  child: Row(
                    children: [
                      // Indicador de color lateral
                      Container(
                        width: 4,
                        height: 60,
                        decoration: BoxDecoration(
                          color: color,
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                      TSpacing.horizontalMedium(),
                      
                      // Contenido
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: TText.h3(
                                    emergency['descripcion'] ?? 'Emergencia sin título',
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                _buildStatusBadge(status),
                              ],
                            ),
                            TSpacing.verticalSmall(),
                            Row(
                              children: [
                                const Icon(Icons.directions_car_outlined, size: 14, color: AppColors.textMuted),
                                TSpacing.horizontalXSmall(),
                                TText.label(emergency['placaVehiculo'] ?? 'N/A'),
                                TSpacing.horizontalMedium(),
                                const Icon(Icons.access_time, size: 14, color: AppColors.textMuted),
                                TSpacing.horizontalXSmall(),
                                TText.label('${emergency['fecha']} ${emergency['hora']}'),
                              ],
                            ),
                            if (emergency['direccion'] != null) ...[
                              TSpacing.verticalXSmall(),
                              TText.label(
                                emergency['direccion'],
                                color: AppColors.textMuted,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                            // Mostrar Monto si está finalizado
                            if (status.toUpperCase() == 'ATENDIDO' || status.toUpperCase() == 'COMPLETADO' || emergency['idPago'] != null) ...[
                              TSpacing.verticalSmall(),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                decoration: BoxDecoration(
                                  color: AppColors.success.withValues(alpha: 0.1),
                                  borderRadius: BorderRadius.circular(4),
                                  border: Border.all(color: AppColors.success.withValues(alpha: 0.2)),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    const Icon(Icons.payments_outlined, size: 12, color: AppColors.success),
                                    TSpacing.horizontalSmall(),
                                    TText.label(
                                      'Monto: \$${emergency['monto_pago'] ?? emergency['pago']?['monto'] ?? '--.--'}',
                                      color: AppColors.success,
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                      TSpacing.horizontalSmall(),
                      const Icon(Icons.chevron_right, color: AppColors.textMuted),
                    ],
                  ),
                ),
              );
            },
          ),
        );
      },
    );
  }

  Color _getStatusColor(String status, BuildContext context) {
    switch (status.toUpperCase()) {
      case 'PENDIENTE': return AppColors.warning;
      case 'ASIGNADO':
      case 'EN PROCESO': return Theme.of(context).colorScheme.primary;
      case 'COMPLETADO':
      case 'ATENDIDO': return AppColors.success;
      case 'CANCELADO': return AppColors.danger;
      default: return AppColors.textMuted;
    }
  }

  Widget _buildStatusBadge(String status) {
    switch (status.toUpperCase()) {
      case 'PENDIENTE':
        return TBadge.warning('Pendiente');
      case 'ASIGNADO':
        return TBadge.info('Asignado');
      case 'EN PROCESO':
        return TBadge.info('En Proceso');
      case 'COMPLETADO':
      case 'ATENDIDO':
        return TBadge.success('Finalizado');
      case 'CANCELADO':
        return TBadge.error('Cancelado');
      default:
        return TBadge.info(status);
    }
  }
}
