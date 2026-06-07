import 'package:flutter/material.dart';

class AdjustQuoteController extends ChangeNotifier {
  List<Map<String, dynamic>> listaProductos = [];
  List<Map<String, dynamic>> listaServicios = [];

  double get subtotalProductos {
    return listaProductos.fold(0.0, (sum, item) => sum + (item['precio'] * item['cantidad']));
  }

  double get subtotalServicios {
    return listaServicios.fold(0.0, (sum, item) => sum + item['precio']);
  }

  double get totalGeneral => subtotalProductos + subtotalServicios;

  void initFromCotizacion(Map<String, dynamic> cotizacion) {
    if (cotizacion['lista_productos'] != null) {
      listaProductos = List<Map<String, dynamic>>.from(cotizacion['lista_productos']);
    }
    if (cotizacion['lista_servicios'] != null) {
      listaServicios = List<Map<String, dynamic>>.from(cotizacion['lista_servicios']);
    }
    notifyListeners();
  }

  void addProducto(String nombre, double precio, int cantidad) {
    listaProductos.add({
      'nombre': nombre,
      'precio': precio,
      'cantidad': cantidad,
    });
    notifyListeners();
  }

  void removeProducto(int index) {
    listaProductos.removeAt(index);
    notifyListeners();
  }

  void addServicio(String nombre, double precio) {
    listaServicios.add({
      'nombre': nombre,
      'precio': precio,
      'cantidad': 1, // Los servicios suelen tener cantidad 1 por convención actual
    });
    notifyListeners();
  }

  void removeServicio(int index) {
    listaServicios.removeAt(index);
    notifyListeners();
  }

  Map<String, dynamic> toJson() {
    return {
      'lista_productos': listaProductos,
      'lista_servicios': listaServicios,
    };
  }
}
