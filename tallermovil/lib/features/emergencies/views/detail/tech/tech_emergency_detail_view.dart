import 'dart:async';
import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../../../../../core/network/api_client.dart';
import '../../../../../core/storage/local_storage.dart';
import '../../../../../core/theme/app_colors.dart';
import '../../../../../shared/components/cards/t_card.dart';
import '../../../../../shared/components/layout/t_spacing.dart';
import '../../../../../shared/components/typography/t_text.dart';
import '../../../../../shared/components/buttons/t_button.dart';
import '../../../../chat/ui/chat_view.dart';
import 'live_tracking_screen.dart';
import 'widgets/tech_quote_adjustment_dialog.dart';

class TechEmergencyDetailView extends StatefulWidget {
  final Map<String, dynamic> emergency;

  const TechEmergencyDetailView({super.key, required this.emergency});

  @override
  State<TechEmergencyDetailView> createState() => _TechEmergencyDetailViewState();
}

class _TechEmergencyDetailViewState extends State<TechEmergencyDetailView> {
  final AudioPlayer _audioPlayer = AudioPlayer();
  bool isPlaying = false;
  Map<String, dynamic> _emergencyData = {};
  bool _isLoading = false;

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
  }

  Future<void> _refreshData() async {
    setState(() => _isLoading = true);
    try {
      final storage = LocalStorage();
      final apiClient = ApiClient(localStorage: storage);
      final response = await apiClient.dio.get('/emergencias/${widget.emergency['id']}');
      
      if (mounted) {
        setState(() {
          _emergencyData = response.data;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _updateState(int stateId) async {
    setState(() => _isLoading = true);
    try {
      final storage = LocalStorage();
      final apiClient = ApiClient(localStorage: storage);
      await apiClient.dio.patch(
        '/talleres/solicitudes/${widget.emergency['id']}/estado',
        data: {'idEstado': stateId},
      );
      await _refreshData();
    } catch (e) {
      debugPrint('Error updating state: $e');
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    super.dispose();
  }

  String _fixUrl(String? url) {
    if (url == null) return '';
    if (url.startsWith('http')) return url;
    final cleanPath = url.startsWith('/') ? url.substring(1) : url;
    return '${ApiClient.serverUrl}/$cleanPath';
  }

  Future<void> _toggleAudio() async {
    final audioUrl = _emergencyData['audio_url'];
    if (audioUrl == null) return;
    final absoluteUrl = _fixUrl(audioUrl);
    if (isPlaying) {
      await _audioPlayer.pause();
    } else {
      await _audioPlayer.play(UrlSource(absoluteUrl));
    }
  }

  Widget _buildStatusBadge(String status) {
    Color bg;
    switch (status.toUpperCase()) {
      case 'PENDIENTE': bg = Colors.grey; break;
      case 'ASIGNADO': bg = Colors.blue; break;
      case 'EN_RUTA': bg = Colors.orange; break;
      case 'ATENDIENDO': bg = Colors.green; break;
      case 'FINALIZADO': bg = AppColors.success; break;
      case 'PAGADO': bg = Colors.teal; break;
      default: bg = Colors.grey;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(color: bg.withOpacity(0.2), borderRadius: BorderRadius.zero, border: Border.all(color: bg)),
      child: Text(status, style: TextStyle(color: bg, fontWeight: FontWeight.bold, fontSize: 12)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final e = _emergencyData;
    final vehiculo = e['vehiculo'];
    final double? lat = e['latitud'] != null ? (e['latitud'] is String ? double.tryParse(e['latitud']) : (e['latitud'] as num).toDouble()) : null;
    final double? lng = e['longitud'] != null ? (e['longitud'] is String ? double.tryParse(e['longitud']) : (e['longitud'] as num).toDouble()) : null;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text('Detalle de Asignación'),
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _refreshData)
        ],
      ),
      body: _isLoading 
        ? const Center(child: CircularProgressIndicator()) 
        : RefreshIndicator(
        onRefresh: _refreshData,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              TCard(
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        TText.h2('Reporte #${e['id']}'),
                        _buildStatusBadge(e['estado_actual'] ?? 'DESCONOCIDO'),
                      ],
                    ),
                    TSpacing.verticalSmall(),
                    TText.body('Reportado el ${e['fecha']} a las ${e['hora']}'),
                  ],
                ),
              ),
              TSpacing.verticalLarge(),

              // BOTÓN PARA ENTRAR A OPERAR
              // ACCIONES DEL TÉCNICO SEGÚN ESTADO
              if (e['estado_actual']?.toString().toUpperCase() == 'ASIGNADO') ...[
                 TButton(
                   label: 'Comenzar Viaje',
                   icon: Icons.directions_car,
                   variant: TButtonVariant.primary,
                   onPressed: () async {
                     await _updateState(3); // 3 = EN_RUTA
                     if (mounted) {
                       Navigator.push(
                         context,
                         MaterialPageRoute(
                           builder: (_) => LiveTrackingScreen(
                             emergenciaId: e['id'],
                             destLat: lat ?? 0.0,
                             destLng: lng ?? 0.0,
                             statusInicial: 'EN_RUTA',
                           ),
                         ),
                       ).then((_) => _refreshData());
                     }
                   },
                 ),
                 TSpacing.verticalLarge(),
              ] else if (e['estado_actual']?.toString().toUpperCase() == 'EN_RUTA') ...[
                 TButton(
                   label: 'Llegué al lugar / Comenzar Trabajo',
                   icon: Icons.build,
                   variant: TButtonVariant.primary,
                   onPressed: () => _updateState(4), // 4 = ATENDIENDO
                 ),
                 TSpacing.verticalLarge(),
              ] else if (e['estado_actual']?.toString().toUpperCase() == 'ATENDIENDO') ...[
                 TButton(
                   label: 'Finalizar y Ajustar Cotización',
                   icon: Icons.check_circle,
                   variant: TButtonVariant.primary,
                   onPressed: () async {
                     final total = await showDialog<double>(
                       context: context,
                       builder: (_) => TechQuoteAdjustmentDialog(emergenciaId: e['id']),
                     );
                     
                     if (total != null) {
                       setState(() => _isLoading = true);
                       try {
                         final storage = LocalStorage();
                         final apiClient = ApiClient(localStorage: storage);
                         await apiClient.dio.post(
                           '/talleres/solicitudes/${e['id']}/finalizar',
                           data: {'monto_total': total},
                         );
                         await _refreshData();
                         if (mounted) {
                           ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Trabajo finalizado y enviado al cliente.')));
                         }
                       } catch (e) {
                         debugPrint('Error al finalizar: $e');
                         if (mounted) setState(() => _isLoading = false);
                       }
                     }
                   },
                 ),
                 TSpacing.verticalLarge(),
              ],

              if (['ASIGNADO', 'EN_RUTA', 'ATENDIENDO'].contains(e['estado_actual']?.toString().toUpperCase())) ...[
                 TButton(
                   label: 'Ver Mapa / Seguir Ruta',
                   icon: Icons.map,
                   variant: TButtonVariant.secondary,
                   onPressed: () {
                     Navigator.push(
                       context,
                       MaterialPageRoute(
                         builder: (_) => LiveTrackingScreen(
                           emergenciaId: e['id'],
                           destLat: lat ?? 0.0,
                           destLng: lng ?? 0.0,
                           statusInicial: e['estado_actual'] ?? 'PENDIENTE',
                         ),
                       ),
                     ).then((_) => _refreshData());
                   },
                 ),
                 TSpacing.verticalLarge(),
              ],

              // Vehículo
              TText.h3('Vehículo Afectado'),
              TSpacing.verticalSmall(),
              TCard(
                child: Row(
                  children: [
                    Icon(Icons.directions_car, color: Theme.of(context).colorScheme.primary, size: 32),
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

              // Evidencia
              TText.h3('Evidencia del Cliente'),
              TSpacing.verticalSmall(),
              TCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    TText.body(e['descripcion'] ?? 'Sin descripción'),
                    if (e['audio_url'] != null) ...[
                      TSpacing.verticalMedium(),
                      TButton(
                        label: isPlaying ? 'Detener Audio' : 'Escuchar Reporte',
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
                              decoration: BoxDecoration(color: AppColors.neutral100, borderRadius: BorderRadius.zero),
                              child: ClipRRect(
                                borderRadius: BorderRadius.zero,
                                child: Image.network(imgUrl, fit: BoxFit.cover, errorBuilder: (c, e, s) => const Icon(Icons.broken_image)),
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
                TText.h3('Ubicación del Incidente'),
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
                            options: MapOptions(initialCenter: LatLng(lat, lng), initialZoom: 15.0),
                            children: [
                              TileLayer(urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png', userAgentPackageName: 'com.example.tallermovil'),
                              MarkerLayer(markers: [Marker(point: LatLng(lat, lng), width: 40, height: 40, child: const Icon(Icons.location_on, color: AppColors.danger, size: 40))]),
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
                TSpacing.verticalXLarge(),
              ],
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.push(context, MaterialPageRoute(builder: (_) => ChatView(emergenciaId: e['id'])));
        },
        backgroundColor: Theme.of(context).colorScheme.primary,
        icon: const Icon(Icons.chat_bubble, color: Colors.white),
        label: const Text('Chat con Cliente', style: TextStyle(color: Colors.white)),
      ),
    );
  }
}
