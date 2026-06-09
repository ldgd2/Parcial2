import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../../../shared/components/cards/t_card.dart';
import '../../../../shared/components/feedback/t_badge.dart';
import '../../../../shared/components/layout/t_spacing.dart';
import '../../../../shared/components/typography/t_text.dart';
import '../../../../shared/components/loaders/t_loader.dart';
// import '../../../../shared/components/buttons/t_button.dart';
import '../../../../core/theme/app_colors.dart';
import 'home_controller.dart';
import '../../../emergencies/views/report_emergency/report_emergency_view.dart';
import '../../../emergencies/views/report_emergency/emergency_upload_controller.dart';
import '../../../../core/network/socket_service.dart';
import '../../../../core/services/update_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late final HomeController controller;
  late final EmergencyUploadController uploadController;

  @override
  void initState() {
    super.initState();
    controller = HomeController();
    uploadController = EmergencyUploadController();
    
    // Conectar WebSocket desde el inicio para notificaciones y chat en tiempo real
    SocketService().connect();

    // Comprobar actualizaciones
    WidgetsBinding.instance.addPostFrameCallback((_) {
      UpdateService.checkForUpdates(context);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: ListenableBuilder(
        listenable: Listenable.merge([controller, uploadController]),
        builder: (context, child) {
          if (controller.isLoading) {
            return const Center(child: TLoader());
          }

          return Stack(
            children: [
              RefreshIndicator(
                onRefresh: controller.loadData,
                child: SingleChildScrollView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (uploadController.isUploading) const SizedBox(height: 80),
                      
                      TText.h1('¡Hola de nuevo!'),
                      TSpacing.verticalSmall(),
                      TText.body('Este es el resumen de tu cuenta y vehículos.'),
                      TSpacing.verticalLarge(),
                      
                      TText.h2('Mis Vehículos'),
                      TSpacing.verticalMedium(),
                      
                      if (controller.vehicles.isEmpty)
                        TCard(
                          child: Center(
                            child: TText.body('No tienes vehículos registrados.'),
                          ),
                        )
                      else
                        ...controller.vehicles.map((v) => Padding(
                          padding: const EdgeInsets.only(bottom: 12.0),
                          child: TCard(
                            onTap: () {},
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    TText.h3('${v['marca']} ${v['modelo']}'),
                                    TBadge.success(v['placa']),
                                  ],
                                ),
                                TSpacing.verticalSmall(),
                                TText.body('Año: ${v['anio']}'),
                              ],
                            ),
                          ),
                        )),
                      
                      TSpacing.verticalLarge(),
                      TText.h2('Emergencias Recientes'),
                      TSpacing.verticalMedium(),
                      
                      if (controller.emergencies.isEmpty)
                        TCard(
                          child: TText.body('No hay emergencias recientes.'),
                        )
                      else
                        ...controller.emergencies.map((e) {
                          bool isInvalida = e['es_valida'] == false;
                          String estado = e['estado_actual'] ?? 'PENDIENTE';
                          bool canCancel = estado == 'PENDIENTE' || estado == 'INICIADA';
                          String motivo = e['resumen_ia']?['motivo_rechazo'] ?? 'La IA no pudo validar este reporte.';

                          return Padding(
                            padding: const EdgeInsets.only(bottom: 12.0),
                            child: TCard(
                              color: isInvalida ? AppColors.danger.withOpacity(0.1) : null,
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Expanded(
                                        child: TText.h3(
                                          e['resumen_ia']?['titulo_emergencia'] ?? 'Reporte S.O.S',
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ),
                                      TBadge(
                                        text: estado == 'PENDIENTE' || estado == 'INICIADA' ? 'ENVIADO' : estado,
                                        variant: isInvalida 
                                          ? TBadgeVariant.error 
                                          : (canCancel ? TBadgeVariant.warning : TBadgeVariant.success),
                                      ),
                                      if (canCancel || isInvalida)
                                        PopupMenuButton<String>(
                                          icon: const Icon(Icons.more_vert, color: AppColors.textSecondary),
                                          color: AppColors.surface,
                                          onSelected: (value) async {
                                            if (value == 'corregir') {
                                              await Navigator.push(
                                                context,
                                                MaterialPageRoute(
                                                  builder: (_) => ReportEmergencyView(existingEmergency: e),
                                                ),
                                              );
                                              controller.loadData();
                                            } else if (value == 'cancelar') {
                                              bool? confirm = await showDialog<bool>(
                                                context: context,
                                                builder: (ctx) => AlertDialog(
                                                  backgroundColor: AppColors.surface,
                                                  title: TText.h3('Cancelar Reporte'),
                                                  content: TText.body('¿Estás seguro de que deseas cancelar este reporte?'),
                                                  actions: [
                                                    TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('VOLVER')),
                                                    TextButton(
                                                      onPressed: () => Navigator.pop(ctx, true), 
                                                      child: const Text('SÍ, CANCELAR', style: TextStyle(color: AppColors.danger))
                                                    ),
                                                  ],
                                                ),
                                              );
                                              if (confirm == true) {
                                                await uploadController.cancelEmergency(e['id']);
                                                controller.loadData();
                                              }
                                            }
                                          },
                                          itemBuilder: (context) => [
                                            if (isInvalida)
                                              const PopupMenuItem(
                                                value: 'corregir',
                                                child: Row(
                                                  children: [
                                                    Icon(Icons.edit, size: 18, color: AppColors.primary),
                                                    SizedBox(width: 8),
                                                    Text('Corregir Reporte', style: TextStyle(color: Colors.white)),
                                                  ],
                                                ),
                                              ),
                                            const PopupMenuItem(
                                              value: 'cancelar',
                                              child: Row(
                                                children: [
                                                  Icon(Icons.cancel_outlined, size: 18, color: AppColors.danger),
                                                  SizedBox(width: 8),
                                                  Text('Cancelar Reporte', style: TextStyle(color: AppColors.danger)),
                                                ],
                                              ),
                                            ),
                                          ],
                                        ),
                                    ],
                                  ),
                                  TSpacing.verticalSmall(),
                                  if (isInvalida) ...[
                                    TText.body('⚠️ RECHAZADO POR IA:', color: AppColors.danger),
                                    TText.body(motivo, color: AppColors.danger),
                                  ] else ...[
                                    TText.body(e['descripcion'] ?? ''),
                                  ],
                                ],
                              ),
                            ),
                          );
                        }),
                      
                      TSpacing(height: 100),
                    ],
                  ),
                ),
              ),
              
              if (uploadController.isUploading)
                Positioned(
                  top: 0, left: 0, right: 0,
                  child: Container(
                    padding: EdgeInsets.only(top: MediaQuery.of(context).padding.top + 10, bottom: 15, left: 20, right: 20),
                    decoration: BoxDecoration(
                      color: AppColors.primary.withOpacity(0.9),
                      borderRadius: BorderRadius.zero,
                      boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.3), blurRadius: 10, spreadRadius: 2)],
                    ),
                    child: Row(
                      children: [
                        const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)),
                        TSpacing.horizontalMedium(),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              TText.label('Enviando S.O.S...', color: Colors.white),
                              TSpacing.verticalSmall(),
                              LinearProgressIndicator(
                                value: uploadController.progress,
                                backgroundColor: Colors.white24,
                                valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ).animate().slideY(begin: -1, end: 0),
                ),

              if (uploadController.currentError != null)
                Positioned(
                  top: MediaQuery.of(context).padding.top + 10, left: 20, right: 20,
                  child: TCard(
                    color: AppColors.danger.withOpacity(0.9),
                    child: Row(
                      children: [
                        const Icon(Icons.error_outline, color: Colors.white),
                        TSpacing.horizontalMedium(),
                        Expanded(child: TText.body('Error al enviar: ${uploadController.currentError}', color: Colors.white)),
                        IconButton(icon: const Icon(Icons.close, color: Colors.white), onPressed: () => uploadController.clearError())
                      ],
                    ),
                  ).animate().shake(),
                ),
            ],
          );
        },
      ),
    );
  }
}
