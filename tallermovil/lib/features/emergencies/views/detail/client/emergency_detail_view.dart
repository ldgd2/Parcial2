import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:path_provider/path_provider.dart';
import '../../../../../core/network/api_client.dart';
import '../../../../../core/storage/local_storage.dart';
import '../../../../../core/theme/app_colors.dart';
import '../../../../../shared/components/cards/t_card.dart';
import '../../../../../shared/components/feedback/t_badge.dart';
import '../../../../../shared/components/layout/t_spacing.dart';
import '../../../../../shared/components/typography/t_text.dart';
import '../../../../../shared/components/buttons/t_button.dart';
import '../../../../../shared/components/loaders/t_loader.dart';
import '../../../../chat/ui/chat_view.dart';
import '../../../../payments/views/payment_selection_view.dart';
import '../../../data/cotizacion_service.dart';
import 'quote_review_view.dart';
import 'package:url_launcher/url_launcher.dart';
import '../tech/live_tracking_screen.dart';
import 'rating_dialog.dart';

class EmergencyDetailView extends StatefulWidget {
  final Map<String, dynamic> emergency;

  const EmergencyDetailView({super.key, required this.emergency});

  @override
  State<EmergencyDetailView> createState() => _EmergencyDetailViewState();
}

class _EmergencyDetailViewState extends State<EmergencyDetailView> {
  final AudioPlayer _audioPlayer = AudioPlayer();
  bool isPlaying = false;

  Map<String, dynamic> _emergencyData = {};
  List<Map<String, dynamic>> _cotizaciones = [];
  bool _isLoading = true;
  String _sortOption = 'Menor Precio';

  StreamSubscription? _socketSubscription;

  @override
  void initState() {
    super.initState();
    _emergencyData = widget.emergency;
    _audioPlayer.onPlayerStateChanged.listen((state) {
      if (mounted) {
        setState(() {
          isPlaying = state == PlayerState.playing;
        });
      }
    });

    _refreshData();
  }


  Future<void> _refreshData() async {
    try {
      final storage = LocalStorage();
      final apiClient = ApiClient(localStorage: storage);
      final response = await apiClient.dio.get('/emergencias/${widget.emergency['id']}');
      
      final cotService = CotizacionService(apiClient: apiClient);
      final cotList = await cotService.getCotizaciones(widget.emergency['id']);

      if (mounted) {
        setState(() {
          _emergencyData = response.data;
          _cotizaciones = cotList;
          _isLoading = false;
        });
      }
    } catch (e) {
      debugPrint('Error refreshing emergency: $e');
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _socketSubscription?.cancel();
    _audioPlayer.dispose();
    super.dispose();
  }

  String _fixUrl(String? url) {
    if (url == null) return '';
    if (url.startsWith('http')) return url;
    // Si la URL empieza con / la quitamos para no duplicar
    final cleanPath = url.startsWith('/') ? url.substring(1) : url;
    return '${ApiClient.serverUrl}/$cleanPath';
  }

  Future<void> _toggleAudio() async {
    final audioUrl = widget.emergency['audio_url'];
    if (audioUrl == null) return;

    final absoluteUrl = _fixUrl(audioUrl);
    debugPrint('Preparando audio: $absoluteUrl');

    try {
      if (isPlaying) {
        await _audioPlayer.stop();
        return;
      }

      // Estrategia: Descargar a temporal y reproducir (Más robusto que streaming HTTP en Android)
      final tempDir = await getTemporaryDirectory();
      final fileName = absoluteUrl.split('/').last;
      final file = File('${tempDir.path}/$fileName');

      if (!await file.exists()) {
        debugPrint('Descargando audio...');
        final storage = LocalStorage();
        final apiClient = ApiClient(localStorage: storage);
        await apiClient.dio.download(absoluteUrl, file.path);
        debugPrint('Descarga completada: ${file.path}');
      }

      await _audioPlayer.play(DeviceFileSource(file.path));
    } catch (e) {
      debugPrint('Error al procesar audio: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('No se pudo reproducir el audio: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: const Text('Cargando...')),
        body: const Center(child: TLoader()),
      );
    }

    final e = _emergencyData;
    final resIA = e['resumen_ia'];
    final vehiculo = e['vehiculo'];
    final lat = e['latitud'] as double?;
    final lng = e['longitud'] as double?;

    return Scaffold(
      appBar: AppBar(
        title: TText.h3('Detalle de Emergencia'),
        actions: [
          if (['PENDIENTE', 'INICIADA'].contains(e['estado_actual']?.toString().toUpperCase()))
            IconButton(
              icon: const Icon(Icons.cancel_outlined, color: AppColors.danger),
              tooltip: 'Cancelar Reporte',
              onPressed: () async {
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
                  try {
                    final storage = LocalStorage();
                    final apiClient = ApiClient(localStorage: storage);
                    await apiClient.dio.delete('/emergencias/${e['id']}');
                    if (mounted) {
                      Navigator.pop(context, true); // Retornar true para refrescar home
                    }
                  } catch (e) {
                    if (mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Error al cancelar: $e')),
                      );
                    }
                  }
                }
              },
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Encabezado de Estado
            TCard(
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      TText.h2('Estado Actual'),
                      _buildStatusBadge(e['estado_actual'] ?? 'PENDIENTE'),
                    ],
                  ),
                  TSpacing.verticalSmall(),
                  TText.body('Reportado el ${e['fecha']} a las ${e['hora']}'),
                ],
              ),
            ),
            TSpacing.verticalLarge(),

            // MAPA EN VIVO PARA EL CLIENTE
            if (['ASIGNADO', 'EN_CAMINO', 'ARREGLADO'].contains(e['estado_actual']?.toString().toUpperCase())) ...[
               TButton(
                 label: 'Rastrear Técnico en Vivo',
                 icon: Icons.map,
                 variant: TButtonVariant.primary,
                 onPressed: () {
                   Navigator.push(
                     context,
                     MaterialPageRoute(
                       builder: (_) => LiveTrackingScreen(
                         emergenciaId: e['id'],
                         destLat: e['latitud'] ?? 0.0,
                         destLng: e['longitud'] ?? 0.0,
                         statusInicial: e['estado_actual'] ?? 'PENDIENTE',
                       ),
                     ),
                   ).then((_) => _refreshData());
                 },
               ),
               TSpacing.verticalLarge(),
            ],

            // SECCIÓN DE PAGO (Solo si está finalizado y TIENE MONTO)
            if ((['ATENDIDO', 'FINALIZADA'].contains(e['estado_actual']?.toString().toUpperCase()) || e['idPago'] != null) && (e['monto_pago'] ?? e['pago']?['monto']) != null) ...[
              TText.h3('Factura y Pago del Servicio'),
              TSpacing.verticalSmall(),
              TCard(
                color: AppColors.successBg.withValues(alpha: 0.2),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        TText.body('Monto Total a Pagar:'),
                        TText.h2('\$${e['monto_pago'] ?? e['pago']?['monto'] ?? '--.--'}'),
                      ],
                    ),
                    TSpacing.verticalSmall(),

                    // MOSTRAR DETALLE FACTURA SI EXISTE
                    if (e['pago'] != null && e['pago']['detalle_factura'] != null) ...[
                      const Divider(color: AppColors.border),
                      TSpacing.verticalSmall(),
                      TText.h3('Detalle de Factura', color: AppColors.primary),
                      TSpacing.verticalSmall(),
                      ...((e['pago']['detalle_factura']['items'] as List?)?.map((item) {
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8.0),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Expanded(
                                child: Text(
                                  '${item['cantidad']}x ${item['descripcion']}',
                                  style: const TextStyle(color: Colors.white, fontSize: 14),
                                ),
                              ),
                              Text(
                                '\$${item['total']}',
                                style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
                              ),
                            ],
                          ),
                        );
                      }) ?? []),
                      const Divider(color: AppColors.border),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Subtotal:', style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
                          Text('\$${e['pago']['detalle_factura']['subtotal']}', style: const TextStyle(color: AppColors.textMuted, fontSize: 12)),
                        ],
                      ),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Impuestos:', style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
                          Text('\$${e['pago']['detalle_factura']['impuestos']}', style: const TextStyle(color: AppColors.textMuted, fontSize: 12)),
                        ],
                      ),
                      TSpacing.verticalMedium(),
                      TButton(
                        label: 'Descargar Factura PDF',
                        icon: Icons.picture_as_pdf,
                        variant: TButtonVariant.outline,
                        onPressed: () async {
                          final url = Uri.parse('${ApiClient.baseUrl}/facturacion/${e['id']}/pdf');
                          if (await canLaunchUrl(url)) {
                            await launchUrl(url, mode: LaunchMode.externalApplication);
                          } else {
                            if (context.mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('No se pudo abrir el enlace del PDF')),
                              );
                            }
                          }
                        },
                      ),
                      TSpacing.verticalMedium(),
                    ],

                    if (e['pago']?['estado'] == 'COMPLETADO') ...[
                      const Icon(Icons.check_circle, color: AppColors.success, size: 48),
                      TSpacing.verticalSmall(),
                      Center(child: TText.h3('SERVICIO PAGADO')),
                      Center(child: TText.body('El pago se realizó correctamente.')),
                      TSpacing.verticalMedium(),
                      _RatingSection(emergency: e),
                    ] else ...[
                      Center(child: TText.label('El servicio ha finalizado. Por favor, procede al pago.')),
                      TSpacing.verticalMedium(),
                      _PaymentButton(emergency: e),
                    ],
                  ],
                ),
              ),
              TSpacing.verticalLarge(),
            ],

            // Cotizaciones (Marketplace)
            if (_cotizaciones.isNotEmpty) ...[
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  TText.h3('Ofertas de Talleres (${_cotizaciones.length})'),
                  DropdownButton<String>(
                    value: _sortOption,
                    dropdownColor: AppColors.surface,
                    style: const TextStyle(color: Colors.white),
                    underline: Container(height: 1, color: AppColors.primary),
                    onChanged: (String? newValue) {
                      if (newValue != null && mounted) {
                        setState(() {
                          _sortOption = newValue;
                        });
                      }
                    },
                    items: <String>['Menor Precio', 'Mejor Calificación', 'Más Rápido']
                        .map<DropdownMenuItem<String>>((String value) {
                      return DropdownMenuItem<String>(
                        value: value,
                        child: Text(value),
                      );
                    }).toList(),
                  ),
                ],
              ),
              TSpacing.verticalSmall(),
              SizedBox(
                height: 230,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: _cotizaciones.length,
                  itemBuilder: (context, index) {
                    // Sorting localmente la copia
                    final sortedQuotes = List<Map<String, dynamic>>.from(_cotizaciones);
                    sortedQuotes.sort((a, b) {
                      if (_sortOption == 'Menor Precio') {
                        final totalA = (a['subtotal_servicios'] ?? 0) + (a['subtotal_productos'] ?? 0);
                        final totalB = (b['subtotal_servicios'] ?? 0) + (b['subtotal_productos'] ?? 0);
                        return totalA.compareTo(totalB);
                      } else if (_sortOption == 'Mejor Calificación') {
                        final califA = a['taller']?['calificacion_promedio'] ?? 0.0;
                        final califB = b['taller']?['calificacion_promedio'] ?? 0.0;
                        return califB.compareTo(califA); // Mayor a menor
                      } else if (_sortOption == 'Más Rápido') {
                        // Comparamos el ETA
                        final etaA = _calculateEta(a);
                        final etaB = _calculateEta(b);
                        return etaA.compareTo(etaB);
                      }
                      return 0;
                    });

                    final cot = sortedQuotes[index];
                    final double manoObra = (cot['subtotal_servicios'] ?? 0).toDouble();
                    final double repuestos = (cot['subtotal_productos'] ?? 0).toDouble();
                    final double total = manoObra + repuestos;
                    
                    int etaMinutos = _calculateEta(cot);
                    final double calificacion = cot['taller']?['calificacion_promedio'] ?? 5.0;
                    
                    return Container(
                      width: 280,
                      margin: const EdgeInsets.only(right: 16.0),
                      child: TCard(
                        color: cot['estado'] == 'ACEPTADA' ? AppColors.successBg.withValues(alpha: 0.1) : AppColors.surface,
                        padding: 16.0,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      TText.h3(
                                        cot['taller']?['nombre'] ?? 'Taller Desconocido',
                                        color: cot['estado'] == 'ACEPTADA' ? AppColors.success : Colors.white,
                                        maxLines: 1,
                                      ),
                                      Row(
                                        children: [
                                          const Icon(Icons.star, color: Colors.amber, size: 14),
                                          const SizedBox(width: 4),
                                          Text(calificacion.toStringAsFixed(1), style: const TextStyle(color: Colors.amber, fontSize: 12, fontWeight: FontWeight.bold)),
                                        ],
                                      )
                                    ],
                                  ),
                                ),
                                _buildStatusBadge(cot['estado']),
                              ],
                            ),
                            TSpacing.verticalSmall(),
                            TText.body(
                              cot['descripcion_servicio'] ?? '',
                              maxLines: 2,
                            ),
                            const Spacer(),
                            if (etaMinutos > 0)
                              Row(
                                children: [
                                  const Icon(Icons.electric_moped, size: 14, color: AppColors.primary),
                                  const SizedBox(width: 4),
                                  TText.label('Llega en aprox. $etaMinutos min'),
                                ],
                              ),
                            const Divider(color: AppColors.border),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                TText.label('Total Estimado:'),
                                TText.h2('\$${total.toStringAsFixed(2)}', color: AppColors.primary),
                              ],
                            ),
                            TSpacing.verticalSmall(),
                            if (cot['estado'] == 'PENDIENTE')
                              TButton(
                                label: 'Revisar y Aceptar',
                                variant: TButtonVariant.primary,
                                onPressed: () async {
                                  final changed = await Navigator.push(
                                    context,
                                    MaterialPageRoute(builder: (_) => QuoteReviewView(quote: cot, emergencyId: e['id']))
                                  );
                                  if (changed == true) {
                                    _refreshData();
                                  }
                                },
                              )
                            else if (cot['estado'] == 'ACEPTADA')
                              TButton(
                                label: 'Oferta Ganadora',
                                variant: TButtonVariant.outline,
                                icon: Icons.check_circle,
                                onPressed: () {},
                              )
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
              TSpacing.verticalLarge(),
            ],

            // Información del Vehículo
            TText.h3('Vehículo Afectado'),
            TSpacing.verticalSmall(),
            TCard(
              child: Row(
                children: [
                  const Icon(Icons.directions_car, color: AppColors.primary, size: 32),
                  TSpacing.horizontalMedium(),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        TText.h3(vehiculo != null ? '${vehiculo['marca']} ${vehiculo['modelo']}' : 'N/A'),
                        TText.label('Placa: ${e['placaVehiculo']}'),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            TSpacing.verticalLarge(),

            // Descripción y Multimedia
            TText.h3('Evidencia Enviada'),
            TSpacing.verticalSmall(),
            TCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  TText.body(e['descripcion'] ?? ''),
                  if (e['audio_url'] != null) ...[
                    TSpacing.verticalMedium(),
                    TButton(
                      label: isPlaying ? 'Detener Audio' : 'Escuchar mi Reporte',
                      icon: isPlaying ? Icons.stop : Icons.play_arrow,
                      onPressed: _toggleAudio,
                      variant: TButtonVariant.outline,
                    ),
                  ],
                  if (e['evidencias'] != null && (e['evidencias'] as List).isNotEmpty) ...[
                    TSpacing.verticalMedium(),
                    TText.label('Fotos adjuntas:'),
                    TSpacing.verticalSmall(),
                    SizedBox(
                      height: 100,
                      child: ListView.builder(
                        scrollDirection: Axis.horizontal,
                        itemCount: (e['evidencias'] as List).length,
                        itemBuilder: (context, index) {
                          final imgUrl = _fixUrl(e['evidencias'][index]['direccion']);
                          return Container(
                            margin: const EdgeInsets.only(right: 8),
                            width: 100,
                            decoration: BoxDecoration(
                              color: AppColors.neutral100,
                              borderRadius: BorderRadius.zero,
                            ),
                            child: ClipRRect(
                              borderRadius: BorderRadius.zero,
                              child: Image.network(
                                imgUrl,
                                fit: BoxFit.cover,
                                errorBuilder: (context, error, stackTrace) => const Icon(Icons.broken_image),
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ],
              ),
            ),
            TSpacing.verticalLarge(),

            // Minimapa
            if (lat != null && lng != null) ...[
              TText.h3('Ubicación del Reporte'),
              TSpacing.verticalSmall(),
              TCard(
                padding: 0,
                child: Column(
                  children: [
                    SizedBox(
                      height: 200,
                      child: ClipRRect(
                        borderRadius: BorderRadius.zero,
                        child: FlutterMap(
                          options: MapOptions(
                            initialCenter: LatLng(lat, lng),
                            initialZoom: 15.0,
                          ),
                          children: [
                            TileLayer(
                              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                              userAgentPackageName: 'com.example.tallermovil',
                            ),
                            MarkerLayer(
                              markers: [
                                Marker(
                                  point: LatLng(lat, lng),
                                  width: 40,
                                  height: 40,
                                  child: const Icon(Icons.location_on, color: AppColors.danger, size: 40),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: Row(
                        children: [
                          const Icon(Icons.map_outlined, size: 16, color: AppColors.textMuted),
                          TSpacing.horizontalSmall(),
                          Expanded(child: TText.label(e['direccion'] ?? 'Ubicación GPS')),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              TSpacing.verticalLarge(),
            ],

            // Resumen IA (Si existe)
            if (resIA != null) ...[
              TText.h3('Análisis Inteligente (IA)'),
              TSpacing.verticalSmall(),
              TCard(
                color: AppColors.primary900.withValues(alpha: 0.2),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.auto_awesome, color: AppColors.primary, size: 20),
                        TSpacing.horizontalSmall(),
                        TText.h3('Diagnóstico Preliminar'),
                      ],
                    ),
                    TSpacing.verticalSmall(),
                    TText.body(resIA['resumen'] ?? 'Analizando...'),
                  ],
                ),
              ),
            ],
            TSpacing.verticalXLarge(),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => ChatView(emergenciaId: e['id']),
            ),
          );
        },
        backgroundColor: AppColors.primary,
        icon: const Icon(Icons.chat_bubble, color: Colors.white),
        label: const Text('Chat con Taller', style: TextStyle(color: Colors.white)),
      ),
    );
  }

  Widget _buildStatusBadge(String status) {
    switch (status.toUpperCase()) {
      case 'PENDIENTE':
        return TBadge.warning('Pendiente');
      case 'ASIGNADO':
        return TBadge.info('Asignado');
      case 'EN PROCESO':
        return TBadge.info('En Proceso');
      case 'FINALIZADA':
      case 'COMPLETADO':
      case 'ATENDIDO':
        return TBadge.success('Finalizado');
      case 'CANCELADO':
        return TBadge.error('Cancelado');
      default:
        return TBadge.info(status);
    }
  }

  int _calculateEta(Map<String, dynamic> cot) {
    int etaMinutos = 999;
    final lat = _emergencyData['latitud'] as double?;
    final lng = _emergencyData['longitud'] as double?;
    if (cot['taller'] != null && cot['taller']['latitud'] != null && lat != null) {
      final distanciaHelper = const Distance();
      final km = distanciaHelper.as(LengthUnit.Kilometer, 
          LatLng(lat, lng!), 
          LatLng(cot['taller']['latitud'], cot['taller']['longitud']));
      etaMinutos = (km * 2).ceil();
      if (etaMinutos < 5) etaMinutos = 5; 
    }
    return etaMinutos;
  }
}

class _PaymentButton extends StatefulWidget {
  final Map<String, dynamic> emergency;
  const _PaymentButton({required this.emergency});

  @override
  State<_PaymentButton> createState() => _PaymentButtonState();
}

class _PaymentButtonState extends State<_PaymentButton> {
  bool _isPaying = false;

  @override
  Widget build(BuildContext context) {
    final e = widget.emergency;
    return TButton(
      label: 'Pagar ahora con Stripe',
      icon: Icons.payment,
      isLoading: _isPaying,
      onPressed: _isPaying ? null : () async {
        final montoStr = e['monto_pago'] ?? e['pago']?['monto'] ?? '0';
        final double monto = double.tryParse(montoStr.toString()) ?? 0.0;
        
        if (monto <= 0) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('El monto debe ser mayor a 0')),
          );
          return;
        }

        setState(() => _isPaying = true);
        try {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => PaymentSelectionView(
                emergenciaId: e['id'],
                monto: monto,
              ),
            ),
          );

          if (result == true && mounted) {
            Navigator.pop(context, true); 
          }
        } finally {
          if (mounted) setState(() => _isPaying = false);
        }
      },
      variant: TButtonVariant.primary,
    );
  }
}

class _RatingSection extends StatefulWidget {
  final Map<String, dynamic> emergency;
  const _RatingSection({required this.emergency});

  @override
  State<_RatingSection> createState() => _RatingSectionState();
}

class _RatingSectionState extends State<_RatingSection> {
  bool _isLoading = false;

  Future<void> _openRating() async {
    setState(() => _isLoading = true);
    Map<String, dynamic>? existingRating;
    try {
      final apiClient = ApiClient(localStorage: LocalStorage());
      final res = await apiClient.dio.get('/calificaciones/mi-calificacion/${widget.emergency['id']}');
      if (res.statusCode == 200) {
        existingRating = res.data;
      }
    } catch (e) {
      // 404 means no rating yet, which is fine
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }

    if (mounted) {
      final changed = await showDialog(
        context: context,
        builder: (_) => RatingDialog(
          idEmergencia: widget.emergency['id'],
          calificacionExistente: existingRating,
        ),
      );
      if (changed == true) {
        setState(() {}); // refresh if needed
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return TButton(
      label: 'Calificar Servicio',
      icon: Icons.star_rate,
      variant: TButtonVariant.primary,
      isLoading: _isLoading,
      onPressed: _openRating,
    );
  }
}
