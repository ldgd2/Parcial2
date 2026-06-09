import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_app_installer/flutter_app_installer.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:path_provider/path_provider.dart';
import '../network/api_client.dart';
import '../storage/local_storage.dart';
import '../../shared/components/buttons/t_button.dart';
import '../../shared/components/typography/t_text.dart';

class UpdateService {
  static Future<void> checkForUpdates(BuildContext context) async {
    try {
      final storage = LocalStorage();
      final apiClient = ApiClient(localStorage: storage);

      // 1. Obtener información de la versión actual
      final PackageInfo packageInfo = await PackageInfo.fromPlatform();
      final String currentVersion = packageInfo.version;

      // 2. Obtener la última versión del backend
      final response = await apiClient.dio.get('/apps/latest');
      final data = response.data;

      if (data != null && data['version'] != null) {
        final remoteVersion = data['version'];
        final changelog = data['changelog'] ?? 'Mejoras y correcciones de errores.';

        // Comparamos versiones (lógica simple asumiendo semver x.y.z)
        if (_isNewerVersion(currentVersion, remoteVersion)) {
          if (context.mounted) {
            _showUpdateDialog(context, remoteVersion, changelog, apiClient);
          }
        }
      }
    } catch (e) {
      debugPrint('Error comprobando actualizaciones: $e');
    }
  }

  static bool _isNewerVersion(String current, String remote) {
    List<int> currentParts = current.split('.').map((e) => int.tryParse(e) ?? 0).toList();
    List<int> remoteParts = remote.split('.').map((e) => int.tryParse(e) ?? 0).toList();

    for (int i = 0; i < 3; i++) {
      int c = i < currentParts.length ? currentParts[i] : 0;
      int r = i < remoteParts.length ? remoteParts[i] : 0;
      if (r > c) return true;
      if (r < c) return false;
    }
    return false;
  }

  static void _showUpdateDialog(
    BuildContext context, 
    String version, 
    String changelog, 
    ApiClient apiClient
  ) {
    showDialog(
      context: context,
      barrierDismissible: false, // Forzar decisión
      builder: (BuildContext ctx) {
        return _UpdateDialogWidget(
          version: version,
          changelog: changelog,
          apiClient: apiClient,
        );
      },
    );
  }
}

class _UpdateDialogWidget extends StatefulWidget {
  final String version;
  final String changelog;
  final ApiClient apiClient;

  const _UpdateDialogWidget({
    required this.version,
    required this.changelog,
    required this.apiClient,
  });

  @override
  State<_UpdateDialogWidget> createState() => _UpdateDialogWidgetState();
}

class _UpdateDialogWidgetState extends State<_UpdateDialogWidget> {
  bool _isDownloading = false;
  double _progress = 0.0;

  Future<void> _downloadAndInstall() async {
    setState(() {
      _isDownloading = true;
    });

    try {
      final tempDir = await getTemporaryDirectory();
      final savePath = '${tempDir.path}/update_${widget.version}.apk';

      await widget.apiClient.dio.download(
        '/apps/download/latest',
        savePath,
        onReceiveProgress: (received, total) {
          if (total != -1) {
            setState(() {
              _progress = received / total;
            });
          }
        },
      );

      // Instalar APK
      final FlutterAppInstaller flutterAppInstaller = FlutterAppInstaller();
      await flutterAppInstaller.installApk(
        filePath: savePath,
      );

    } catch (e) {
      debugPrint('Error en la descarga/instalación: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al actualizar: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isDownloading = false;
        });
        Navigator.pop(context); // Cerrar diálogo tras intento
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: TText.h3('¡Nueva actualización disponible!'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          TText.body('Versión ${widget.version} ya está disponible.'),
          const SizedBox(height: 12),
          TText.label('Novedades:'),
          TText.body(widget.changelog),
          const SizedBox(height: 24),
          if (_isDownloading) ...[
            LinearProgressIndicator(value: _progress),
            const SizedBox(height: 8),
            Center(child: TText.label('${(_progress * 100).toStringAsFixed(1)}% completado')),
          ]
        ],
      ),
      actions: [
        if (!_isDownloading)
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Más tarde'),
          ),
        if (!_isDownloading)
          TButton(
            label: 'Actualizar Ahora',
            onPressed: _downloadAndInstall,
            variant: TButtonVariant.primary,
          ),
      ],
    );
  }
}
