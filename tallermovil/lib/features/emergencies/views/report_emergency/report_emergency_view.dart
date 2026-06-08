import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:tallermovil/core/theme/app_colors.dart';
import 'package:tallermovil/shared/components/buttons/t_button.dart';
import 'package:tallermovil/shared/components/cards/t_card.dart';
import 'package:tallermovil/shared/components/inputs/t_text_input.dart';
import 'package:tallermovil/shared/components/inputs/t_dropdown.dart';
import 'package:tallermovil/shared/components/layout/t_spacing.dart';
import 'package:tallermovil/shared/components/typography/t_text.dart';

import 'report_emergency_controller.dart';

class ReportEmergencyView extends StatefulWidget {
  final Map<String, dynamic>? existingEmergency;
  const ReportEmergencyView({super.key, this.existingEmergency});

  @override
  State<ReportEmergencyView> createState() => _ReportEmergencyViewState();
}

class _ReportEmergencyViewState extends State<ReportEmergencyView> {
  late final ReportEmergencyController controller;

  @override
  void initState() {
    super.initState();
    controller = ReportEmergencyController(existingEmergency: widget.existingEmergency);
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: TText.h3('Reportar Emergencia'),
      ),
      body: AnimatedBuilder(
        animation: controller,
        builder: (context, child) {
          String minutes = controller.formatTime(controller.recordDuration ~/ 60);
          String seconds = controller.formatTime(controller.recordDuration % 60);

          return SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                TText.body(
                  'Por favor, describe oralmente el problema del vehículo o sube evidencias. Tienes un máximo de 2 MINUTOS.',
                ),
                TSpacing.verticalLarge(),

                // Contenedor Grabadora
                TCard(
                  child: Column(
                    children: [
                      TText.h1(
                        '$minutes:$seconds',
                        color: controller.isRecording ? AppColors.danger : AppColors.textPrimary,
                      ),
                      TSpacing.verticalMedium(),
                      
                      GestureDetector(
                        onTap: controller.isRecording 
                            ? controller.stopRecording 
                            : () => controller.startRecording(context),
                        child: Container(
                          width: 80,
                          height: 80,
                          decoration: BoxDecoration(
                            color: controller.isRecording ? AppColors.danger : AppColors.primary,
                            shape: BoxShape.rectangle,
                            boxShadow: controller.isRecording ? [
                              BoxShadow(color: AppColors.danger.withAlpha(128), blurRadius: 20, spreadRadius: 5)
                            ] : [],
                          ),
                          child: Icon(
                            controller.isRecording ? Icons.stop : Icons.mic,
                            color: Colors.white,
                            size: 40,
                          ),
                        ).animate(target: controller.isRecording ? 1 : 0).scale(begin: const Offset(1,1), end: const Offset(1.1,1.1)),
                      ),
                      TSpacing.verticalMedium(),
                      TText.label(
                        controller.isRecording ? 'Grabando...' : (controller.audioPath != null ? 'Audio listo para enviar' : 'Toque para grabar'),
                      ),
                      if (controller.audioPath != null && !controller.isRecording) ...[
                        TSpacing.verticalMedium(),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            TButton(
                              label: controller.isPlaying ? "Detener" : "Reproducir",
                              onPressed: controller.playRecording,
                              variant: TButtonVariant.outline,
                              isFullWidth: false,
                              icon: controller.isPlaying ? Icons.stop : Icons.play_arrow,
                            ),
                            TSpacing.horizontalSmall(),
                            IconButton(
                              icon: const Icon(Icons.delete_outline, color: Colors.red),
                              onPressed: controller.clearAudio,
                            )
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
                
                TSpacing.verticalLarge(),

                // Selector Multi-media
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    TText.h3('Evidencias Visuales'),
                    IconButton(
                      icon: const Icon(Icons.add_a_photo, color: AppColors.primary),
                      onPressed: controller.pickImage,
                    ),
                  ],
                ),
                TSpacing.verticalSmall(),
                
                // Carrusel horizontal de imágenes
                if (controller.imagePaths.isNotEmpty)
                  SizedBox(
                    height: 80,
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      itemCount: controller.imagePaths.length,
                      itemBuilder: (context, index) {
                        return Container(
                          margin: const EdgeInsets.only(right: 8),
                          width: 80,
                          decoration: BoxDecoration(
                            color: AppColors.neutral100_map,
                            borderRadius: BorderRadius.zero,
                          ),
                          child: const Center(child: Icon(Icons.image, color: AppColors.textMuted)),
                          // Nota ideal: Usar Image.file(File(controller.imagePaths[index]))
                        );
                      },
                    ),
                  ),

                TSpacing.verticalLarge(),

                TDropdown<String>(
                  label: 'Vehículo Afectado',
                  hint: 'Selecciona tu vehículo',
                  items: controller.vehicles.map((v) => TDropdownItem<String>(
                    value: v['placa']?.toString() ?? '', 
                    label: '${v['marca']} ${v['modelo']} (${v['placa']})'
                  )).toList(),
                  onChanged: (val) {
                    if (val != null) controller.setPlaca(val);
                  },
                ),

                TSpacing.verticalMedium(),
                TTextInput(
                  label: 'Descripción (Si no puede hablar)',
                  hint: 'Ej: Choque frontal',
                  onChanged: controller.setDescripcion,
                ),

                TSpacing.verticalXLarge(),

                TButton(
                  label: 'Obtener GPS y Generar Reporte',
                  icon: Icons.satellite_alt_outlined,
                  isLoading: controller.isUploading,
                  onPressed: (controller.audioPath != null || controller.imagePaths.isNotEmpty) 
                      ? () => controller.submitReport(context) 
                      : null,
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
