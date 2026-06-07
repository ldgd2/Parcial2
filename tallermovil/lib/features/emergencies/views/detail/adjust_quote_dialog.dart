import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/storage/local_storage.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/components/typography/t_text.dart';
import '../../controllers/adjust_quote_controller.dart';

class AdjustQuoteDialog extends StatefulWidget {
  final int emergenciaId;
  
  const AdjustQuoteDialog({super.key, required this.emergenciaId});

  @override
  State<AdjustQuoteDialog> createState() => _AdjustQuoteDialogState();
}

class _AdjustQuoteDialogState extends State<AdjustQuoteDialog> {
  bool _isLoading = true;
  bool _isSaving = false;
  int? _cotizacionId;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _fetchCotizacionAceptada();
  }

  Future<void> _fetchCotizacionAceptada() async {
    try {
      final apiClient = ApiClient(localStorage: LocalStorage());
      final response = await apiClient.dio.get('/cotizaciones/emergencia/${widget.emergenciaId}');
      
      final cotizaciones = response.data as List;
      // Buscamos la cotización ACEPTADA (asumiendo que hay una)
      final aceptada = cotizaciones.firstWhere(
        (c) => c['estado'] == 'ACEPTADA',
        orElse: () => null,
      );

      if (aceptada != null) {
        _cotizacionId = aceptada['id'];
        if (mounted) {
          context.read<AdjustQuoteController>().initFromCotizacion(aceptada);
        }
      } else {
        _errorMessage = "No se encontró una cotización ACEPTADA para esta emergencia.";
      }
    } catch (e) {
      _errorMessage = "Error cargando la cotización: $e";
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _guardarAjuste() async {
    if (_cotizacionId == null) return;
    
    setState(() {
      _isSaving = true;
    });

    try {
      final controller = context.read<AdjustQuoteController>();
      final payload = controller.toJson();
      
      final apiClient = ApiClient(localStorage: LocalStorage());
      await apiClient.dio.put('/cotizaciones/$_cotizacionId/ajustar', data: payload);
      
      if (mounted) {
        Navigator.of(context).pop(true); // Retorna true si se guardó con éxito
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Cotización ajustada y notificada al cliente.')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al guardar ajuste: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSaving = false;
        });
      }
    }
  }

  void _mostrarDialogoNuevoProducto(BuildContext context) {
    final nombreCtrl = TextEditingController();
    final precioCtrl = TextEditingController();
    final cantCtrl = TextEditingController(text: "1");

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Agregar Repuesto/Producto'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(controller: nombreCtrl, decoration: const InputDecoration(labelText: 'Nombre del producto')),
            TextField(controller: precioCtrl, keyboardType: const TextInputType.numberWithOptions(decimal: true), decoration: const InputDecoration(labelText: 'Precio Unitario')),
            TextField(controller: cantCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Cantidad')),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
          ElevatedButton(
            onPressed: () {
              final nombre = nombreCtrl.text.trim();
              final precio = double.tryParse(precioCtrl.text) ?? 0.0;
              final cant = int.tryParse(cantCtrl.text) ?? 1;
              if (nombre.isNotEmpty && precio > 0) {
                context.read<AdjustQuoteController>().addProducto(nombre, precio, cant);
                Navigator.pop(ctx);
              }
            },
            child: const Text('Agregar'),
          ),
        ],
      ),
    );
  }

  void _mostrarDialogoNuevoServicio(BuildContext context) {
    final nombreCtrl = TextEditingController();
    final precioCtrl = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Agregar Servicio Adicional'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(controller: nombreCtrl, decoration: const InputDecoration(labelText: 'Descripción del servicio')),
            TextField(controller: precioCtrl, keyboardType: const TextInputType.numberWithOptions(decimal: true), decoration: const InputDecoration(labelText: 'Costo extra')),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
          ElevatedButton(
            onPressed: () {
              final nombre = nombreCtrl.text.trim();
              final precio = double.tryParse(precioCtrl.text) ?? 0.0;
              if (nombre.isNotEmpty && precio > 0) {
                context.read<AdjustQuoteController>().addServicio(nombre, precio);
                Navigator.pop(ctx);
              }
            },
            child: const Text('Agregar'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const AlertDialog(
        content: SizedBox(height: 100, child: Center(child: CircularProgressIndicator())),
      );
    }

    if (_errorMessage != null) {
      return AlertDialog(
        title: const Text('Error'),
        content: Text(_errorMessage!),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cerrar')),
        ],
      );
    }

    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Container(
        constraints: BoxConstraints(maxHeight: MediaQuery.of(context).size.height * 0.8),
        padding: const EdgeInsets.all(16),
        child: Consumer<AdjustQuoteController>(
          builder: (context, controller, child) {
            return Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    TText.h2('Ajustar Cotización'),
                    IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.pop(context)),
                  ],
                ),
                const Divider(),
                Expanded(
                  child: ListView(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          TText.h3('Productos/Repuestos'),
                          IconButton(
                            icon: const Icon(Icons.add_circle, color: AppColors.primary),
                            onPressed: () => _mostrarDialogoNuevoProducto(context),
                          ),
                        ],
                      ),
                      if (controller.listaProductos.isEmpty)
                        const Padding(padding: EdgeInsets.all(8.0), child: Text('No hay productos.')),
                      ...controller.listaProductos.asMap().entries.map((entry) {
                        final i = entry.key;
                        final p = entry.value;
                        return ListTile(
                          title: Text(p['nombre']),
                          subtitle: Text('${p['cantidad']} x \$${p['precio']}'),
                          trailing: IconButton(
                            icon: const Icon(Icons.delete, color: Colors.red),
                            onPressed: () => controller.removeProducto(i),
                          ),
                        );
                      }),
                      const Divider(),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          TText.h3('Mano de Obra/Servicios'),
                          IconButton(
                            icon: const Icon(Icons.add_circle, color: AppColors.primary),
                            onPressed: () => _mostrarDialogoNuevoServicio(context),
                          ),
                        ],
                      ),
                      if (controller.listaServicios.isEmpty)
                        const Padding(padding: EdgeInsets.all(8.0), child: Text('No hay servicios adicionales.')),
                      ...controller.listaServicios.asMap().entries.map((entry) {
                        final i = entry.key;
                        final s = entry.value;
                        return ListTile(
                          title: Text(s['nombre']),
                          subtitle: Text('Costo: \$${s['precio']}'),
                          trailing: IconButton(
                            icon: const Icon(Icons.delete, color: Colors.red),
                            onPressed: () => controller.removeServicio(i),
                          ),
                        );
                      }),
                    ],
                  ),
                ),
                const Divider(),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Sub. Prod:', style: TextStyle(fontWeight: FontWeight.bold)),
                    Text('\$${controller.subtotalProductos.toStringAsFixed(2)}'),
                  ],
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Sub. Serv:', style: TextStyle(fontWeight: FontWeight.bold)),
                    Text('\$${controller.subtotalServicios.toStringAsFixed(2)}'),
                  ],
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    TText.h2('TOTAL:'),
                    TText.h2('\$${controller.totalGeneral.toStringAsFixed(2)}', color: AppColors.primary),
                  ],
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: _isSaving ? null : _guardarAjuste,
                  style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary, padding: const EdgeInsets.symmetric(vertical: 16)),
                  child: _isSaving 
                    ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white))
                    : const Text('Guardar y Notificar', style: TextStyle(color: Colors.white)),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}
