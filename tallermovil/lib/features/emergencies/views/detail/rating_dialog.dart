import 'package:flutter/material.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/storage/local_storage.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/components/typography/t_text.dart';
import '../../../../shared/components/buttons/t_button.dart';
import '../../../../shared/components/layout/t_spacing.dart';

class RatingDialog extends StatefulWidget {
  final int idEmergencia;
  final Map<String, dynamic>? calificacionExistente;

  const RatingDialog({
    super.key,
    required this.idEmergencia,
    this.calificacionExistente,
  });

  @override
  State<RatingDialog> createState() => _RatingDialogState();
}

class _RatingDialogState extends State<RatingDialog> {
  int _puntuacionTaller = 5;
  int _puntuacionTecnico = 5;
  final TextEditingController _comentarioController = TextEditingController();
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    if (widget.calificacionExistente != null) {
      _puntuacionTaller = (widget.calificacionExistente!['puntuacion_taller'] ?? 5).toInt();
      _puntuacionTecnico = (widget.calificacionExistente!['puntuacion_tecnico'] ?? 5).toInt();
      _comentarioController.text = widget.calificacionExistente!['comentario'] ?? '';
    }
  }

  Future<void> _submit() async {
    setState(() => _isSubmitting = true);
    try {
      final payload = {
        'puntuacion_taller': _puntuacionTaller,
        'puntuacion_tecnico': _puntuacionTecnico,
        'comentario': _comentarioController.text.trim(),
      };

      final apiClient = ApiClient(localStorage: LocalStorage());
      
      if (widget.calificacionExistente != null) {
        final idCalif = widget.calificacionExistente!['id'];
        await apiClient.dio.put('/calificaciones/cliente/$idCalif', data: payload);
      } else {
        await apiClient.dio.post('/calificaciones/${widget.idEmergencia}', data: payload);
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('¡Valoración guardada exitosamente!'), backgroundColor: AppColors.success),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al guardar: $e'), backgroundColor: AppColors.danger),
        );
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  Widget _buildStars(int currentVal, ValueChanged<int> onChanged) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(5, (index) {
        final starVal = index + 1;
        return IconButton(
          onPressed: () => onChanged(starVal),
          icon: Icon(
            starVal <= currentVal ? Icons.star : Icons.star_border,
            color: Colors.amber,
            size: 36,
          ),
        );
      }),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isEdit = widget.calificacionExistente != null;
    return Dialog(
      backgroundColor: AppColors.surface,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TText.h2(isEdit ? 'Editar Valoración' : 'Calificar Servicio'),
            TSpacing.verticalLarge(),
            
            TText.body('Califica al Taller', color: AppColors.textSecondary),
            _buildStars(_puntuacionTaller, (v) => setState(() => _puntuacionTaller = v)),
            
            TSpacing.verticalMedium(),
            TText.body('Califica al Técnico en terreno', color: AppColors.textSecondary),
            _buildStars(_puntuacionTecnico, (v) => setState(() => _puntuacionTecnico = v)),
            
            TSpacing.verticalMedium(),
            TextField(
              controller: _comentarioController,
              maxLines: 3,
              style: const TextStyle(color: Colors.white),
              decoration: const InputDecoration(
                hintText: '¿Qué tal fue la atención y reparación?',
                hintStyle: TextStyle(color: AppColors.textMuted),
                border: OutlineInputBorder(),
                filled: true,
                fillColor: AppColors.background,
              ),
            ),
            
            TSpacing.verticalLarge(),
            Row(
              children: [
                Expanded(
                  child: TButton(
                    label: 'Cancelar',
                    variant: TButtonVariant.outline,
                    onPressed: () => Navigator.pop(context),
                  ),
                ),
                TSpacing.horizontalMedium(),
                Expanded(
                  child: TButton(
                    label: isEdit ? 'Actualizar' : 'Enviar',
                    variant: TButtonVariant.primary,
                    isLoading: _isSubmitting,
                    onPressed: _submit,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
