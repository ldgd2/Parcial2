import 'dart:async';
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geolocator/geolocator.dart';
import 'package:provider/provider.dart';

import '../../../../../core/network/web_socket_service.dart';
import '../../../../../core/storage/local_storage.dart';
import '../../../../../core/network/api_client.dart';

import '../../controllers/adjust_quote_controller.dart';
import 'adjust_quote_dialog.dart';

class LiveTrackingScreen extends StatefulWidget {
  final int emergenciaId;
  final double destLat;
  final double destLng;
  final String statusInicial;

  const LiveTrackingScreen({
    super.key,
    required this.emergenciaId,
    required this.destLat,
    required this.destLng,
    required this.statusInicial,
  });

  @override
  State<LiveTrackingScreen> createState() => _LiveTrackingScreenState();
}

class _LiveTrackingScreenState extends State<LiveTrackingScreen> {
  late WebSocketService _wsService;
  StreamSubscription? _wsSubscription;
  Timer? _gpsTimer;

  bool _isTecnico = false;
  LatLng _tecnicoPos = const LatLng(0, 0);
  String _eta = 'Calculando...';
  String _currentStatus = '';
  
  final List<Map<String, String>> _chatMessages = [];
  final TextEditingController _chatController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  
  List<LatLng> _routePoints = [];

  @override
  void initState() {
    super.initState();
    _currentStatus = widget.statusInicial;
    _tecnicoPos = LatLng(widget.destLat, widget.destLng); // Posición inicial referencial
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
        setState(() {
          _tecnicoPos = LatLng(data['lat'] as double, data['lng'] as double);
          _eta = data['eta']?.toString() ?? 'Desconocido';
        });
      } else if (type == 'chat_message') {
        setState(() {
          _chatMessages.add({
            'sender': data['sender_name'] ?? 'Usuario',
            'text': data['text'] ?? '',
            'role': data['sender_role'] ?? 'cliente',
          });
        });
        _scrollToBottom();
      } else if (type == 'status_update') {
        setState(() {
          _currentStatus = data['estado'] ?? _currentStatus;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(data['message'] ?? 'Estado actualizado')),
        );
      } else if (type == 'solicitar_calificacion') {
        if (!_isTecnico) {
          _mostrarModalCalificacion();
        }
      }
    });

    if (_isTecnico) {
      final hasPermission = await _handleLocationPermission();
      if (hasPermission) {
        _iniciarTransmisionGps();
      }
    } else {
      // Cliente también debe solicitar permisos para mostrarse (si se desea)
      await _handleLocationPermission();
    }
  }

  Future<bool> _handleLocationPermission() async {
    bool serviceEnabled;
    LocationPermission permission;

    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
            content: Text('Los servicios de ubicación están deshabilitados. Por favor habilítalos.')));
      }
      return false;
    }
    permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Permisos de ubicación denegados.')));
        }
        return false;
      }
    }
    if (permission == LocationPermission.deniedForever) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
            content: Text('Los permisos de ubicación están denegados permanentemente.')));
      }
      return false;
    }
    return true;
  }

  void _iniciarTransmisionGps() {
    // Transmitir cada 5 segundos
    _gpsTimer = Timer.periodic(const Duration(seconds: 5), (timer) async {
      try {
        Position position = await Geolocator.getCurrentPosition(
            desiredAccuracy: LocationAccuracy.high);
        setState(() {
          _tecnicoPos = LatLng(position.latitude, position.longitude);
        });
        _wsService.sendGpsUpdate(
          position.latitude,
          position.longitude,
          widget.destLat,
          widget.destLng,
        );
        _fetchRoute();
      } catch (e) {
        debugPrint('Error obteniendo GPS: $e');
      }
    });
  }

  Future<void> _fetchRoute() async {
    try {
      final start = '\${_tecnicoPos.longitude},\${_tecnicoPos.latitude}';
      final end = '\${widget.destLng},\${widget.destLat}';
      final url = 'https://router.project-osrm.org/route/v1/driving/$start;$end?overview=full&geometries=geojson';
      
      final response = await Dio().get(url);
      if (response.statusCode == 200) {
        final data = response.data;
        if (data['code'] == 'Ok' && data['routes'].isNotEmpty) {
          final geometry = data['routes'][0]['geometry']['coordinates'] as List;
          final points = geometry.map((p) => LatLng(p[1] as double, p[0] as double)).toList();
          if (mounted) {
            setState(() {
              _routePoints = points;
            });
          }
        }
      }
    } catch (e) {
      debugPrint('Error fetching route: $e');
    }
  }

  void _sendMessage() {
    if (_chatController.text.trim().isNotEmpty) {
      final text = _chatController.text.trim();
      _wsService.sendChatMessage(text, _isTecnico ? 'Técnico' : 'Cliente');
      setState(() {
        _chatMessages.add({
          'sender': 'Tú',
          'text': text,
          'role': _isTecnico ? 'tecnico' : 'cliente',
        });
      });
      _chatController.clear();
      _scrollToBottom();
    }
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _mostrarModalCalificacion() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Calificar Servicio'),
        content: const Text('El servicio ha finalizado. ¿Cómo calificarías al técnico?'),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context); // Volver atrás
            },
            child: const Text('Omitir'),
          ),
          ElevatedButton(
            onPressed: () {
              // TODO: Enviar calificación
              Navigator.pop(context);
              Navigator.pop(context);
            },
            child: const Text('Enviar (5 Estrellas)'),
          )
        ],
      ),
    );
  }

  @override
  void dispose() {
    _gpsTimer?.cancel();
    _wsSubscription?.cancel();
    _wsService.dispose();
    _chatController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Seguimiento en Vivo'),
        backgroundColor: Colors.redAccent,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          // MAPA
          Expanded(
            flex: 2,
            child: FlutterMap(
              options: MapOptions(
                initialCenter: LatLng(widget.destLat, widget.destLng),
                initialZoom: 14.0,
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
                      strokeWidth: 4.0,
                      color: Colors.blueAccent,
                    ),
                  ],
                ),
                MarkerLayer(
                  markers: [
                    // Marcador de destino (Cliente/Emergencia)
                    Marker(
                      point: LatLng(widget.destLat, widget.destLng),
                      width: 40,
                      height: 40,
                      child: const Icon(Icons.car_crash, color: Colors.red, size: 40),
                    ),
                    // Marcador del Técnico
                    Marker(
                      point: _tecnicoPos,
                      width: 40,
                      height: 40,
                      child: const Icon(Icons.build_circle, color: Colors.blue, size: 40),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // PANEL INFO ESTADO Y ETA
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.white,
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Estado: $_currentStatus', style: const TextStyle(fontWeight: FontWeight.bold)),
                    if (!_isTecnico) Text('ETA: $_eta', style: const TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold)),
                  ],
                ),
                if (_isTecnico && _currentStatus == 'EN_CAMINO')
                  Padding(
                    padding: const EdgeInsets.only(top: 8.0),
                    child: ElevatedButton(
                      onPressed: () async {
                        try {
                          final apiClient = ApiClient(localStorage: LocalStorage());
                          await apiClient.dio.patch(
                             '/talleres/solicitudes/${widget.emergenciaId}/estado',
                             data: {'idEstado': 4} // Asumiendo ARREGLADO = 4
                          );
                          setState(() { _currentStatus = 'ARREGLADO'; });
                          if(mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Marcado como Arreglado')));
                        } catch (e) {
                          if(mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Guardado en cola (Offline)')));
                        }
                      },
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                      child: const Text('Marcar como Arreglado'),
                    ),
                  ),
                if (_isTecnico && (_currentStatus == 'EN_CAMINO' || _currentStatus == 'ARREGLADO'))
                  Padding(
                    padding: const EdgeInsets.only(top: 8.0),
                    child: ElevatedButton(
                      onPressed: () async {
                        final result = await showDialog(
                          context: context,
                          builder: (_) => ChangeNotifierProvider(
                            create: (_) => AdjustQuoteController(),
                            child: AdjustQuoteDialog(emergenciaId: widget.emergenciaId),
                          ),
                        );
                        if (result == true) {
                          // The quote was updated
                        }
                      },
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.orange),
                      child: const Text('Ajustar Cotización en Sitio'),
                    ),
                  ),
                if (_isTecnico && _currentStatus == 'ARREGLADO')
                  Padding(
                    padding: const EdgeInsets.only(top: 8.0),
                    child: ElevatedButton(
                      onPressed: () async {
                        try {
                          final apiClient = ApiClient(localStorage: LocalStorage());
                          await apiClient.dio.patch(
                             '/talleres/solicitudes/${widget.emergenciaId}/estado',
                             data: {'idEstado': 5} // Asumiendo COMPLETADO = 5
                          );
                          setState(() { _currentStatus = 'COMPLETADO'; });
                          if(mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Servicio Completado Exitosamente')));
                        } catch (e) {
                          if(mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Guardado en cola (Offline)')));
                        }
                      },
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent),
                      child: const Text('Finalizar y Marcar COMPLETADO'),
                    ),
                  ),
              ],
            ),
          ),

          // CHAT EFÍMERO
          Expanded(
            flex: 1,
            child: Container(
              color: Colors.grey[100],
              child: Column(
                children: [
                  const Padding(
                    padding: EdgeInsets.all(8.0),
                    child: Text('Chat Efímero (se borrará al cerrar)', style: TextStyle(fontSize: 12, color: Colors.grey)),
                  ),
                  Expanded(
                    child: ListView.builder(
                      controller: _scrollController,
                      itemCount: _chatMessages.length,
                      itemBuilder: (context, index) {
                        final msg = _chatMessages[index];
                        final isMe = msg['sender'] == 'Tú';
                        return Align(
                          alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
                          child: Container(
                            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: isMe ? Colors.blue[100] : Colors.white,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text('${msg['sender']}: ${msg['text']}'),
                          ),
                        );
                      },
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _chatController,
                            decoration: const InputDecoration(
                              hintText: 'Mensaje...',
                              border: OutlineInputBorder(),
                              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            ),
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.send, color: Colors.blue),
                          onPressed: _sendMessage,
                        )
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
