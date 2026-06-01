import 'package:flutter/material.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/storage/local_storage.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/components/typography/t_text.dart';
import '../../../../shared/components/buttons/t_button.dart';
import '../../../../shared/components/cards/t_card.dart';
import '../../../../shared/components/layout/t_spacing.dart';
import '../../data/cotizacion_service.dart';

class QuoteReviewView extends StatefulWidget {
  final Map<String, dynamic> quote;
  final int emergencyId;

  const QuoteReviewView({super.key, required this.quote, required this.emergencyId});

  @override
  State<QuoteReviewView> createState() => _QuoteReviewViewState();
}

class _QuoteReviewViewState extends State<QuoteReviewView> {
  late CotizacionService _service;
  bool _isProcessing = false;

  @override
  void initState() {
    super.initState();
    _service = CotizacionService(apiClient: ApiClient(localStorage: LocalStorage()));
  }

  Future<void> _updateStatus(String status) async {
    if (status == 'ACEPTADA') {
      final double total = (widget.quote['costo_mano_obra'] ?? 0).toDouble() + (widget.quote['costo_repuestos'] ?? 0).toDouble();
      final tallerNombre = widget.quote['taller']?['nombre'] ?? 'este taller';
      
      bool? confirm = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          backgroundColor: AppColors.surface,
          title: TText.h3('Confirmar Selección'),
          content: TText.body('Estás a punto de confirmar el servicio con $tallerNombre por un total de \$${total.toStringAsFixed(2)}. ¿Deseas proceder?'),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('CANCELAR')),
            TextButton(
              onPressed: () => Navigator.pop(ctx, true), 
              child: const Text('SÍ, ACEPTAR', style: TextStyle(color: AppColors.primary))
            ),
          ],
        ),
      );
      if (confirm != true) return;
    }

    setState(() => _isProcessing = true);
    try {
      await _service.updateEstado(widget.quote['id'], status);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Cotización $status exitosamente'), backgroundColor: status == 'ACEPTADA' ? AppColors.success : null),
        );
        Navigator.pop(context, true); // Devuelve true para recargar
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString().replaceAll('Exception: ', '')), backgroundColor: AppColors.danger),
        );
      }
    } finally {
      if (mounted) setState(() => _isProcessing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final q = widget.quote;
    final double manoObra = (q['costo_mano_obra'] ?? 0).toDouble();
    final double repuestos = (q['costo_repuestos'] ?? 0).toDouble();
    final double total = manoObra + repuestos;

    return Scaffold(
      appBar: AppBar(
        title: TText.h3('Revisión de Cotización'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      TText.h3('Propuesta #${q['id']}'),
                      _buildStatusBadge(q['estado']),
                    ],
                  ),
                  TSpacing.verticalSmall(),
                  TText.body(q['descripcion_servicio'] ?? 'Sin descripción'),
                ],
              ),
            ),
            TSpacing.verticalLarge(),
            
            TText.h3('Desglose de Costos'),
            TSpacing.verticalSmall(),
            TCard(
              color: AppColors.surface.withValues(alpha: 0.5),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      TText.body('Mano de Obra:'),
                      TText.body('\$${manoObra.toStringAsFixed(2)}'),
                    ],
                  ),
                  TSpacing.verticalSmall(),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      TText.body('Repuestos:'),
                      TText.body('\$${repuestos.toStringAsFixed(2)}'),
                    ],
                  ),
                  const Divider(color: AppColors.border, height: 32),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      TText.h2('Total Estimado:'),
                      TText.h2('\$${total.toStringAsFixed(2)}', color: AppColors.primary),
                    ],
                  ),
                ],
              ),
            ),
            
            TSpacing.verticalLarge(),
            TCard(
              child: Row(
                children: [
                  const Icon(Icons.timer, color: AppColors.primary),
                  TSpacing.horizontalMedium(),
                  Expanded(
                    child: TText.body('Tiempo estimado de entrega: ${q['tiempo_estimado_horas']} horas'),
                  )
                ],
              ),
            ),

            if (q['condiciones'] != null && q['condiciones'].toString().isNotEmpty) ...[
              TSpacing.verticalLarge(),
              TText.h3('Condiciones'),
              TSpacing.verticalSmall(),
              TCard(
                child: TText.body(q['condiciones']),
              ),
            ],

            if (q['estado'] == 'PENDIENTE') ...[
              TSpacing.verticalXLarge(),
              TButton(
                label: 'Aceptar Cotización',
                icon: Icons.check_circle,
                isLoading: _isProcessing,
                onPressed: () => _updateStatus('ACEPTADA'),
              ),
              TSpacing.verticalMedium(),
              TButton(
                label: 'Rechazar',
                icon: Icons.cancel,
                variant: TButtonVariant.outline,
                isLoading: _isProcessing,
                onPressed: () => _updateStatus('RECHAZADA'),
              ),
            ]
          ],
        ),
      ),
    );
  }

  Widget _buildStatusBadge(String status) {
    Color bg;
    switch (status) {
      case 'PENDIENTE': bg = AppColors.warning; break;
      case 'ACEPTADA': bg = AppColors.success; break;
      case 'RECHAZADA': bg = AppColors.danger; break;
      default: bg = AppColors.info;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: bg.withValues(alpha: 0.2), border: Border.all(color: bg)),
      child: Text(status, style: TextStyle(color: bg, fontSize: 10, fontWeight: FontWeight.bold)),
    );
  }
}
