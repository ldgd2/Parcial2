import 'package:intl/intl.dart';

class EmergencyReport {
  final String descripcion;
  final String direccion;
  final double latitud;
  final double longitud;
  final String placaVehiculo;
  final String? audioUrl;
  final List<String> evidenciasUrls;
  final String? textoAdicional;
  final String? uuidLocal;

  EmergencyReport({
    required this.descripcion,
    required this.direccion,
    required this.latitud,
    required this.longitud,
    required this.placaVehiculo,
    this.audioUrl,
    this.evidenciasUrls = const [],
    this.textoAdicional,
    this.uuidLocal,
  });

  factory EmergencyReport.fromJson(Map<String, dynamic> json) {
    return EmergencyReport(
      descripcion: json['descripcion'] ?? '',
      direccion: json['direccion'] ?? '',
      latitud: (json['latitud'] as num?)?.toDouble() ?? 0.0,
      longitud: (json['longitud'] as num?)?.toDouble() ?? 0.0,
      placaVehiculo: json['placaVehiculo'] ?? '',
      audioUrl: json['audio_url'],
      evidenciasUrls: json['evidencias_urls'] != null 
          ? List<String>.from(json['evidencias_urls']) 
          : [],
      textoAdicional: json['texto_adicional'],
      uuidLocal: json['uuid_local'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'descripcion': descripcion,
      'direccion': direccion,
      'latitud': latitud,
      'longitud': longitud,
      'placaVehiculo': placaVehiculo,
      'audio_url': audioUrl,
      'evidencias_urls': evidenciasUrls,
      'texto_adicional': textoAdicional,
      'uuid_local': uuidLocal,
      'hora': DateFormat('HH:mm:ss').format(DateTime.now()),
    };
  }
}
