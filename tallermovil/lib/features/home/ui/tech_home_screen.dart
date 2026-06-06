import 'package:flutter/material.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/storage/local_storage.dart';
import '../../emergencies/views/detail/tech_emergency_detail_view.dart';
import '../../../../shared/components/cards/t_card.dart';
import '../../../../shared/components/typography/t_text.dart';
import '../../../../shared/components/layout/t_spacing.dart';

class TechHomeScreen extends StatefulWidget {
  const TechHomeScreen({super.key});

  @override
  State<TechHomeScreen> createState() => _TechHomeScreenState();
}

class _TechHomeScreenState extends State<TechHomeScreen> {
  bool _isLoading = true;
  List<dynamic> _emergencies = [];
  String _errorMessage = '';

  @override
  void initState() {
    super.initState();
    _loadAssignedEmergencies();
  }

  Future<void> _loadAssignedEmergencies() async {
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });
    try {
      final storage = LocalStorage();
      final codTaller = await storage.getCodTaller();
      if (codTaller == null || codTaller.isEmpty) {
        throw Exception('No tienes un taller asignado.');
      }

      final apiClient = ApiClient(localStorage: storage);
      final response = await apiClient.dio.get('/talleres/$codTaller/solicitudes');
      
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        // Filtrar emergencias activas (ASIGNADO, EN_CAMINO, ARREGLADO)
        setState(() {
          _emergencies = data.where((e) {
            final estado = e['estado_actual']?.toString().toUpperCase() ?? '';
            return ['ASIGNADO', 'EN_CAMINO', 'ARREGLADO'].contains(estado);
          }).toList();
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString().replaceAll('Exception: ', '');
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[900], // Fondo oscuro para coincidir con el resto
      appBar: AppBar(
        title: const Text('Panel del Técnico'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadAssignedEmergencies,
          )
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage.isNotEmpty
              ? Center(child: Text(_errorMessage, style: const TextStyle(color: Colors.red)))
              : _emergencies.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.check_circle_outline, size: 64, color: Colors.green),
                          const SizedBox(height: 16),
                          TText.h3('Todo en orden'),
                          TText.body('No tienes emergencias activas en este momento.', color: Colors.grey),
                        ],
                      ),
                    )
                  : RefreshIndicator(
                      onRefresh: _loadAssignedEmergencies,
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16.0),
                        itemCount: _emergencies.length,
                        itemBuilder: (context, index) {
                          final e = _emergencies[index];
                          return Container(
                            margin: const EdgeInsets.only(bottom: 16.0),
                            child: TCard(
                              padding: 16.0,
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      TText.h3('Reporte #${e['id']}'),
                                      _buildStatusBadge(e['estado_actual'] ?? 'DESCONOCIDO'),
                                    ],
                                  ),
                                  TSpacing.verticalSmall(),
                                  TText.body(e['descripcion'] ?? 'Sin descripción', maxLines: 2),
                                  TSpacing.verticalMedium(),
                                  Row(
                                    children: [
                                      const Icon(Icons.location_on, size: 16, color: Colors.redAccent),
                                      const SizedBox(width: 4),
                                      Expanded(child: TText.label(e['direccion'] ?? 'GPS')),
                                    ],
                                  ),
                                  TSpacing.verticalMedium(),
                                  SizedBox(
                                    width: double.infinity,
                                    child: ElevatedButton(
                                      onPressed: () async {
                                        await Navigator.push(
                                          context,
                                          MaterialPageRoute(builder: (_) => TechEmergencyDetailView(emergency: e)),
                                        );
                                        _loadAssignedEmergencies();
                                      },
                                      child: const Text('VER DETALLE E IR AL LUGAR'),
                                    ),
                                  )
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                    ),
    );
  }

  Widget _buildStatusBadge(String status) {
    Color bg;
    switch (status.toUpperCase()) {
      case 'ASIGNADO': bg = Colors.blue; break;
      case 'EN_CAMINO': bg = Colors.orange; break;
      case 'ARREGLADO': bg = Colors.green; break;
      default: bg = Colors.grey;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: bg.withOpacity(0.2), border: Border.all(color: bg)),
      child: Text(status, style: TextStyle(color: bg, fontSize: 10, fontWeight: FontWeight.bold)),
    );
  }
}
