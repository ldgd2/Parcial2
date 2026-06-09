import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geolocator/geolocator.dart';

import 'package:tallermovil/core/network/web_socket_service.dart';
import 'package:tallermovil/core/storage/local_storage.dart';
import 'package:tallermovil/core/network/api_client.dart';

import 'package:tallermovil/shared/components/typography/t_text.dart';
import 'package:tallermovil/core/theme/app_colors.dart';

class LiveTrackingScreen extends StatefulWidget {
  final int emergenciaId;
  final double destLat;
  final double destLng;
  final String statusInicial;
  final bool showAppBar;

  const LiveTrackingScreen({
    super.key,
    required this.emergenciaId,
    required this.destLat,
    required this.destLng,
    required this.statusInicial,
    this.showAppBar = true,
  });

  @override
  State<LiveTrackingScreen> createState() => _LiveTrackingScreenState();
}

class _LiveTrackingScreenState extends State<LiveTrackingScreen> {
  late WebSocketService _wsService;
  StreamSubscription? _wsSubscription;
  Timer? _gpsTimer;
  final MapController _mapController = MapController();

  bool _isTecnico = false;
  LatLng _tecnicoPos = const LatLng(0, 0);
  String _eta = 'Calculando...';
  String _distancia = '';
  String _currentStatus = '';
  bool _autoFollow = true;
  
  List<LatLng> _routePoints = [];
  bool _isLoadingRoute = false;

  @override
  void initState() {
    super.initState();
    _currentStatus = widget.statusInicial;
    _tecnicoPos = LatLng(widget.destLat, widget.destLng); // Default to destination initially
    _initLiveTracking();
  }

  Future<void> _initLiveTracking() async {
    final rol = await LocalStorage().getRol();
    setState(() {
      _isTecnico = rol == 'tecnico';
    });

    _wsService = WebSocketService();
    await _wsService.connect(widget.emergenciaId);

    _wsSubscription = _wsService.messages.listen((data) {
      final type = data['type'];
      if (type == 'gps_update') {
        if (!_isTecnico && mounted) {
          setState(() {
            _tecnicoPos = LatLng(data['lat'] as double, data['lng'] as double);
            // Si el cliente recibe ETA calculada por el técnico
            if (data['eta'] != null) _eta = data['eta'].toString();
          });
          if (_autoFollow) {
            _mapController.move(_tecnicoPos, 16.0);
          }
        }
      } else if (type == 'status_update') {
        if (mounted) {
          setState(() {
            _currentStatus = data['estado'] ?? _currentStatus;
          });
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(data['message'] ?? 'Estado actualizado a $_currentStatus')),
          );
        }
      }
    });

    if (_isTecnico) {
      final hasPermission = await _handleLocationPermission();
      if (hasPermission) {
        // Al obtener el primer GPS, centrar la cámara inmediatamente
        try {
          Position position = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high);
          if (mounted) {
            setState(() {
              _tecnicoPos = LatLng(position.latitude, position.longitude);
            });
            _mapController.move(_tecnicoPos, 16.0);
            await _fetchRoute(); // Calcular ruta de inmediato
          }
        } catch (e) {
          debugPrint('Error inicial GPS: $e');
        }
        _iniciarTransmisionGps();
      }
    } else {
      // Para el cliente, si queremos mostrarlo en el mapa podríamos pedir permiso, 
      // pero por ahora solo necesita ver al técnico avanzar.
      _mapController.move(LatLng(widget.destLat, widget.destLng), 15.0);
    }
  }

  Future<bool> _handleLocationPermission() async {
    bool serviceEnabled;
    LocationPermission permission;

    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
            content: Text('Los servicios de ubicación están deshabilitados. Habilítalos para trazar la ruta.')));
      }
      return false;
    }
    permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Permisos de ubicación denegados.')));
        return false;
      }
    }
    if (permission == LocationPermission.deniedForever) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Permisos de ubicación denegados permanentemente.')));
      return false;
    }
    return true;
  }

  void _iniciarTransmisionGps() {
    // Transmitir y recalcular ruta cada 5 segundos
    _gpsTimer = Timer.periodic(const Duration(seconds: 5), (timer) async {
      try {
        Position position = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high);
        if (!mounted) return;
        
        setState(() {
          _tecnicoPos = LatLng(position.latitude, position.longitude);
        });

        if (_autoFollow) {
          _mapController.move(_tecnicoPos, _mapController.camera.zoom);
        }

        _wsService.sendGpsUpdate(
          position.latitude,
          position.longitude,
          widget.destLat,
          widget.destLng,
        );
        
        await _fetchRoute();
      } catch (e) {
        debugPrint('Error obteniendo GPS: $e');
      }
    });
  }

  Future<void> _fetchRoute() async {
    if (_isLoadingRoute) return;
    _isLoadingRoute = true;
    try {
      final start = '${_tecnicoPos.longitude},${_tecnicoPos.latitude}';
      final end = '${widget.destLng},${widget.destLat}';
      final url = 'https://router.project-osrm.org/route/v1/driving/$start;$end?overview=full&geometries=geojson';
      
      final response = await Dio().get(url);
      if (response.statusCode == 200 && mounted) {
        final data = response.data;
        if (data['code'] == 'Ok' && data['routes'].isNotEmpty) {
          final geometry = data['routes'][0]['geometry']['coordinates'] as List;
          final durationSec = data['routes'][0]['duration'] as num;
          final distanceM = data['routes'][0]['distance'] as num;

          final points = geometry.map((p) => LatLng(p[1] as double, p[0] as double)).toList();
          
          final int mins = (durationSec / 60).ceil();
          final String distStr = distanceM > 1000 
              ? '${(distanceM / 1000).toStringAsFixed(1)} km'
              : '${distanceM.toStringAsFixed(0)} m';

          setState(() {
            _routePoints = points;
            _eta = '$mins min';
            _distancia = distStr;
          });
        }
      }
    } catch (e) {
      debugPrint('Error fetching route: $e');
    } finally {
      _isLoadingRoute = false;
    }
  }

  @override
  void dispose() {
    _gpsTimer?.cancel();
    _wsSubscription?.cancel();
    _wsService.dispose();
    _mapController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    Widget body = Stack(
      children: [
        // MAPA GRANDOTE AL 100% DE PANTALLA
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: LatLng(widget.destLat, widget.destLng),
              initialZoom: 15.0,
              onPositionChanged: (pos, hasGesture) {
                if (hasGesture && _autoFollow) {
                  setState(() => _autoFollow = false);
                }
              },
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.taller.os',
              ),
              PolylineLayer(
                polylines: [
                  Polyline(
                    points: _routePoints,
                    strokeWidth: 5.0,
                    color: AppColors.primary,
                  ),
                ],
              ),
              MarkerLayer(
                markers: [
                  // Marcador de destino (Cliente/Emergencia)
                  Marker(
                    point: LatLng(widget.destLat, widget.destLng),
                    width: 60,
                    height: 60,
                    child: const Icon(Icons.location_on, color: Colors.red, size: 50),
                  ),
                  // Marcador del Técnico
                  Marker(
                    point: _tecnicoPos,
                    width: 60,
                    height: 60,
                    child: const Icon(Icons.location_on, color: Colors.blueAccent, size: 50),
                  ),
                ],
              ),
            ],
          ),

          // PANEL FLOTANTE EN LA PARTE INFERIOR
          Positioned(
            left: 16,
            right: 16,
            bottom: 30,
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.zero,
                boxShadow: const [
                  BoxShadow(color: Colors.black26, blurRadius: 10, offset: Offset(0, 4)),
                ],
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: AppColors.primary.withOpacity(0.1),
                          shape: BoxShape.rectangle,
                        ),
                        child: const Icon(Icons.directions_car, color: AppColors.primary, size: 28),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            TText.h3('Estado: $_currentStatus'),
                            const SizedBox(height: 4),
                            TText.label('Tiempo est.: $_eta  •  Distancia: $_distancia'),
                          ],
                        ),
                      ),
                    ],
                  ),
                  if (_currentStatus.toUpperCase() == 'EN_RUTA' || _currentStatus.toUpperCase() == 'EN CAMINO') ...[
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                        icon: const Icon(Icons.build),
                        label: const Text('Llegué al lugar / Comenzar', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                        onPressed: () async {
                          try {
                            final storage = LocalStorage();
                            final apiClient = ApiClient(localStorage: storage);
                            await apiClient.dio.patch(
                              '/talleres/solicitudes/${widget.emergenciaId}/estado',
                              data: {'idEstado': 4}, // 4 = ATENDIENDO
                            );
                            if (mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Estado actualizado a Atendiendo')));
                              Navigator.pop(context); // Volver al detalle para ver el botón de finalizar
                            }
                          } catch (e) {
                            debugPrint('Error actualizando estado a atendiendo: $e');
                          }
                        },
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      );
    if (!widget.showAppBar) {
      return body;
    }

    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: const Text('Ruta de Asistencia'),
        backgroundColor: Colors.black.withOpacity(0.5),
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: Icon(_autoFollow ? Icons.my_location : Icons.location_disabled),
            onPressed: () {
              setState(() {
                _autoFollow = !_autoFollow;
                if (_autoFollow) {
                  _mapController.move(_tecnicoPos, 16.0);
                }
              });
              ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                content: Text(_autoFollow ? 'Centrado automático ACTIVADO' : 'Centrado automático DESACTIVADO'),
                duration: const Duration(seconds: 1),
              ));
            },
            tooltip: 'Centrar en mi ubicación',
          )
        ],
      ),
      body: body,
    );
  }
}
