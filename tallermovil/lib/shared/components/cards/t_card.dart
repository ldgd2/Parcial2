import 'package:flutter/material.dart';

/// TCard: Contenedor tipo Tarjeta estándar de la aplicación.
/// Mantiene bordes, padding y diseño visual coherente de manera automática.
class TCard extends StatelessWidget {
  /// Contenido principal de la tarjeta
  final Widget child;

  /// Título opcional superior
  final String? title;

  /// Relleno interno (Padding). Por defecto es 20.
  final double padding;

  /// Margen externo.
  final EdgeInsetsGeometry? margin;

  /// Acción al presionar la tarjeta
  final VoidCallback? onTap;

  /// Color de fondo personalizado
  final Color? color;

  const TCard({
    super.key,
    required this.child,
    this.title,
    this.padding = 20.0,
    this.margin,
    this.onTap,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: margin ?? EdgeInsets.zero,
        decoration: BoxDecoration(
          color: color ?? const Color(0xFF0A0A0A),
          border: Border.all(color: const Color(0xFF222222)),
        ),
        child: Stack(
          children: [
            // Contenido Principal
            Padding(
              padding: EdgeInsets.all(padding),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min, // Ajustar al contenido
                children: [
                  if (title != null) ...[
                    Row(
                      children: [
                        Container(
                          width: 4,
                          height: 16,
                          color: Theme.of(context).colorScheme.primary,
                          margin: const EdgeInsets.only(right: 8),
                        ),
                        Expanded(
                          child: Text(
                            title!.toUpperCase(),
                            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                              letterSpacing: 2.0,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    const Divider(height: 1, color: Color(0xFF222222)),
                    const SizedBox(height: 16),
                  ],
                  child,
                ],
              ),
            ),
            
            // Esquinas Arquitectónicas (Cyber style)
            Positioned(top: 0, left: 0, child: _buildCorner(top: true, left: true, context: context)),
            Positioned(top: 0, right: 0, child: _buildCorner(top: true, left: false, context: context)),
            Positioned(bottom: 0, left: 0, child: _buildCorner(top: false, left: true, context: context)),
            Positioned(bottom: 0, right: 0, child: _buildCorner(top: false, left: false, context: context)),
          ],
        ),
      ),
    );
  }

  Widget _buildCorner({required bool top, required bool left, required BuildContext context}) {
    return Container(
      width: 8,
      height: 8,
      decoration: BoxDecoration(
        border: Border(
          top: top ? BorderSide(color: Theme.of(context).colorScheme.primary, width: 1.5) : BorderSide.none,
          bottom: !top ? BorderSide(color: Theme.of(context).colorScheme.primary, width: 1.5) : BorderSide.none,
          left: left ? BorderSide(color: Theme.of(context).colorScheme.primary, width: 1.5) : BorderSide.none,
          right: !left ? BorderSide(color: Theme.of(context).colorScheme.primary, width: 1.5) : BorderSide.none,
        ),
      ),
    );
  }
}
