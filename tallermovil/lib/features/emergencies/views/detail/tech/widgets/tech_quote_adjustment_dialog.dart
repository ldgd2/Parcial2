import 'package:flutter/material.dart';
import '../../../../../../core/network/api_client.dart';
import '../../../../../../core/storage/local_storage.dart';
import '../../../../../../shared/components/typography/t_text.dart';
import '../../../../../../shared/components/buttons/t_button.dart';
import '../../../../../../shared/components/loaders/t_loader.dart';

class TechQuoteAdjustmentDialog extends StatefulWidget {
  final int emergenciaId;

  const TechQuoteAdjustmentDialog({super.key, required this.emergenciaId});

  @override
  State<TechQuoteAdjustmentDialog> createState() => _TechQuoteAdjustmentDialogState();
}

class _TechQuoteAdjustmentDialogState extends State<TechQuoteAdjustmentDialog> {
  bool _isLoading = true;
  bool _isSaving = false;
  Map<String, dynamic>? _cotizacion;
  
  List<dynamic> _productos = [];
  List<dynamic> _servicios = [];

  final _nombreCtrl = TextEditingController();
  final _precioCtrl = TextEditingController();
  final _cantidadCtrl = TextEditingController(text: '1');
  bool _isProducto = false;

  @override
  void initState() {
    super.initState();
    _loadCotizacion();
  }

  Future<void> _loadCotizacion() async {
    try {
      final apiClient = ApiClient(localStorage: LocalStorage());
      final response = await apiClient.dio.get('/cotizaciones/emergencia/${widget.emergenciaId}');
      final List<dynamic> data = response.data;
      
      if (mounted) {
        setState(() {
          if (data.isNotEmpty) {
            _cotizacion = data.last; // Tomamos la más reciente o la única
            _productos = List.from(_cotizacion?['lista_productos'] ?? []);
            _servicios = List.from(_cotizacion?['lista_servicios'] ?? []);
          }
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Error cargando cotización. Puede que no exista.')));
      }
    }
  }

  void _addItem() {
    if (_nombreCtrl.text.isEmpty || _precioCtrl.text.isEmpty) return;
    
    final double? precio = double.tryParse(_precioCtrl.text);
    if (precio == null) return;

    setState(() {
      if (_isProducto) {
        final int cant = int.tryParse(_cantidadCtrl.text) ?? 1;
        _productos.add({
          'nombre': _nombreCtrl.text,
          'precio': precio,
          'cantidad': cant,
        });
      } else {
        _servicios.add({
          'nombre': _nombreCtrl.text,
          'precio': precio,
        });
      }
      _nombreCtrl.clear();
      _precioCtrl.clear();
      _cantidadCtrl.text = '1';
    });
  }

  void _removeItem(bool isProd, int index) {
    setState(() {
      if (isProd) {
        _productos.removeAt(index);
      } else {
        _servicios.removeAt(index);
      }
    });
  }

  Future<void> _saveAjuste() async {
    if (_cotizacion == null) return;
    setState(() => _isSaving = true);
    try {
      final apiClient = ApiClient(localStorage: LocalStorage());
      final response = await apiClient.dio.put(
        '/cotizaciones/${_cotizacion!['id']}/ajustar',
        data: {
          'lista_productos': _productos,
          'lista_servicios': _servicios,
          'descripcion_servicio': _cotizacion!['descripcion_servicio'],
        },
      );
      if (mounted) {
        Navigator.pop(context, response.data['total_general']);
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Cotización actualizada.')));
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isSaving = false);
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Error guardando ajuste.')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.zero),
      child: _isLoading
          ? const SizedBox(height: 200, child: Center(child: TLoader()))
          : _cotizacion == null
              ? Container(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.warning, size: 48, color: Colors.orange),
                      const SizedBox(height: 16),
                      TText.h3('Sin Cotización'),
                      TText.body('Esta emergencia no tiene una cotización inicial que ajustar.', textAlign: TextAlign.center),
                      const SizedBox(height: 24),
                      TButton(label: 'Cerrar', onPressed: () => Navigator.pop(context)),
                    ],
                  ),
                )
              : Container(
                  padding: const EdgeInsets.all(16),
                  width: double.maxFinite,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      TText.h2('Ajustar Cotización'),
                      const Divider(),
                      Expanded(
                        child: ListView(
                          shrinkWrap: true,
                          children: [
                            TText.h3('Servicios'),
                            ..._servicios.asMap().entries.map((e) => ListTile(
                              dense: true,
                              title: Text(e.value['nombre']),
                              subtitle: Text('Bs. ${e.value['precio']}'),
                              trailing: IconButton(icon: const Icon(Icons.delete, color: Colors.red), onPressed: () => _removeItem(false, e.key)),
                            )),
                            const SizedBox(height: 8),
                            TText.h3('Repuestos / Productos'),
                            ..._productos.asMap().entries.map((e) => ListTile(
                              dense: true,
                              title: Text(e.value['nombre']),
                              subtitle: Text('${e.value['cantidad']}x Bs. ${e.value['precio']}'),
                              trailing: IconButton(icon: const Icon(Icons.delete, color: Colors.red), onPressed: () => _removeItem(true, e.key)),
                            )),
                            const Divider(),
                            TText.h3('Agregar Ítem'),
                            Row(
                              children: [
                                Expanded(child: RadioListTile<bool>(
                                  title: const Text('Servicio'),
                                  value: false,
                                  groupValue: _isProducto,
                                  onChanged: (v) => setState(() => _isProducto = v!),
                                  contentPadding: EdgeInsets.zero,
                                )),
                                Expanded(child: RadioListTile<bool>(
                                  title: const Text('Repuesto'),
                                  value: true,
                                  groupValue: _isProducto,
                                  onChanged: (v) => setState(() => _isProducto = v!),
                                  contentPadding: EdgeInsets.zero,
                                )),
                              ],
                            ),
                            TextField(controller: _nombreCtrl, decoration: const InputDecoration(labelText: 'Descripción')),
                            const SizedBox(height: 8),
                            Row(
                              children: [
                                Expanded(child: TextField(controller: _precioCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Precio (Bs)'))),
                                const SizedBox(width: 8),
                                if (_isProducto)
                                  Expanded(child: TextField(controller: _cantidadCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Cantidad'))),
                              ],
                            ),
                            const SizedBox(height: 12),
                            TButton(label: 'Agregar a la lista', variant: TButtonVariant.outline, onPressed: _addItem),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(child: TButton(label: 'Cancelar', variant: TButtonVariant.outline, onPressed: () => Navigator.pop(context))),
                          const SizedBox(width: 8),
                          Expanded(
                            child: TButton(
                              label: _isSaving ? 'Enviando...' : 'Guardar y Finalizar',
                              onPressed: _isSaving ? null : _saveAjuste,
                            ),
                          ),
                        ],
                      )
                    ],
                  ),
                ),
    );
  }
}
