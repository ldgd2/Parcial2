import 'package:flutter/material.dart';

/// Define los diferentes estilos visuales del botón (como un Enum de C#)
enum TButtonVariant {
  primary,
  secondary,
  outline,
  text,
  danger,
}

/// TButton: Componente de botón estandarizado y fácil de usar.
/// Propiedades similares a las de un control C#.
class TButton extends StatelessWidget {
  /// Texto a mostrar en el botón
  final String label;

  /// Función a ejecutar al hacer clic. Si es null, el botón se deshabilita.
  final VoidCallback? onPressed;

  /// Estilo visual del botón (por defecto es primary)
  final TButtonVariant variant;

  /// Si está en true, deshabilita el botón y muestra un spinner
  final bool isLoading;

  /// Icono opcional a la izquierda del texto
  final IconData? icon;

  /// Si está en true, el botón ocupará todo el ancho disponible
  final bool isFullWidth;

  const TButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.variant = TButtonVariant.primary,
    this.isLoading = false,
    this.icon,
    this.isFullWidth = true,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    // Seleccionamos el widget base según la variante
    Widget buttonContent = Row(
      mainAxisSize: isFullWidth ? MainAxisSize.max : MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (isLoading) ...[
          SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(
              strokeWidth: 2.5,
              color: _getLoadingColor(theme),
            ),
          ),
          const SizedBox(width: 12),
        ] else if (icon != null) ...[
          Icon(icon, size: 20),
          const SizedBox(width: 8),
        ],
        Text(label),
      ],
    );

    Widget buttonWidget;

    // Resolvemos la acción teniendo en cuenta si está cargando
    final action = isLoading ? null : onPressed;

    switch (variant) {
      case TButtonVariant.primary:
        buttonWidget = ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: theme.colorScheme.primary,
          ),
          onPressed: action,
          child: buttonContent,
        );
        break;
      case TButtonVariant.danger:
        buttonWidget = ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: theme.colorScheme.error,
            foregroundColor: theme.colorScheme.onError,
          ),
          onPressed: action,
          child: buttonContent,
        );
        break;
      case TButtonVariant.secondary:
        buttonWidget = ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: theme.colorScheme.primary.withValues(alpha: 0.1),
            foregroundColor: theme.colorScheme.primary,
            elevation: 0,
          ),
          onPressed: action,
          child: buttonContent,
        );
        break;
      case TButtonVariant.outline:
        buttonWidget = OutlinedButton(
          style: OutlinedButton.styleFrom(
            side: BorderSide(color: theme.colorScheme.primary),
            foregroundColor: theme.colorScheme.primary,
          ),
          onPressed: action,
          child: buttonContent,
        );
        break;
      case TButtonVariant.text:
        buttonWidget = TextButton(
          style: TextButton.styleFrom(
            foregroundColor: theme.colorScheme.primary,
          ),
          onPressed: action,
          child: buttonContent,
        );
        break;
    }

    if (isFullWidth) {
      return SizedBox(
        width: double.infinity,
        child: buttonWidget,
      );
    }

    return buttonWidget;
  }

  Color _getLoadingColor(ThemeData theme) {
    if (variant == TButtonVariant.primary || variant == TButtonVariant.danger) {
      return Colors.white;
    }
    return theme.colorScheme.primary;
  }
}
