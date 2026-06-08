import 'package:flutter/material.dart';

/// TTextInput: Campo de texto altamente reutilizable con propiedades simples.
/// Equivalente a un TextBox en C# WinForms/WPF, pero con soporte para Material Design.
class TTextInput extends StatefulWidget {
  /// Etiqueta visible encima del campo o dentro de él
  final String label;

  /// Texto de ayuda mostrado cuando está vacío
  final String? hint;

  /// Controlador del texto (como el .Text property en C#)
  final TextEditingController? controller;

  /// Función que valida el contenido del campo
  final String? Function(String?)? validator;

  /// Tipo de teclado (email, números, texto normal)
  final TextInputType keyboardType;

  /// Si es true, oculta el texto (para contraseñas)
  final bool isPassword;

  /// Icono inicial del campo
  final IconData? prefixIcon;

  /// Si el campo es solo lectura
  final bool readOnly;

  /// Valor inicial (si no se usa controller)
  final String? initialValue;

  /// Evento lanzado cuando el texto cambia
  final void Function(String)? onChanged;

  /// Número de líneas (por defecto 1, aumentar para TextArea)
  final int maxLines;

  const TTextInput({
    super.key,
    required this.label,
    this.hint,
    this.controller,
    this.validator,
    this.keyboardType = TextInputType.text,
    this.isPassword = false,
    this.prefixIcon,
    this.readOnly = false,
    this.initialValue,
    this.onChanged,
    this.maxLines = 1,
  });

  @override
  State<TTextInput> createState() => _TTextInputState();
}

class _TTextInputState extends State<TTextInput> {
  bool _obscureText = false;

  @override
  void initState() {
    super.initState();
    _obscureText = widget.isPassword;
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0), // Margen inferior por defecto
      child: TextFormField(
        controller: widget.controller,
        initialValue: widget.initialValue,
        obscureText: _obscureText,
        keyboardType: widget.keyboardType,
        validator: widget.validator,
        readOnly: widget.readOnly,
        onChanged: widget.onChanged,
        maxLines: widget.isPassword ? 1 : widget.maxLines,
        decoration: InputDecoration(
          labelText: widget.label,
          hintText: widget.hint,
          prefixIcon: widget.prefixIcon != null ? Icon(widget.prefixIcon) : null,
          // Botón de alternar visibilidad para contraseñas
          suffixIcon: widget.isPassword
              ? IconButton(
                  icon: Icon(
                    _obscureText ? Icons.visibility_off : Icons.visibility,
                    color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5),
                  ),
                  onPressed: () {
                    setState(() {
                      _obscureText = !_obscureText;
                    });
                  },
                )
              : null,
          focusedBorder: Theme.of(context).inputDecorationTheme.focusedBorder?.copyWith(
                borderSide: BorderSide(
                  color: Theme.of(context).colorScheme.primary,
                  width: 2,
                ),
              ),
        ),
      ),
    );
  }
}
