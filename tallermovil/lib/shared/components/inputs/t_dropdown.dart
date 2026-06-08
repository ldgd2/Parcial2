import 'package:flutter/material.dart';
import 'package:tallermovil/core/theme/app_colors.dart';
import 'package:tallermovil/shared/components/typography/t_text.dart';

class TDropdownItem<T> {
  final T value;
  final String label;

  TDropdownItem({required this.value, required this.label});
}

class TDropdown<T> extends StatelessWidget {
  final String label;
  final String? hint;
  final T? value;
  final List<TDropdownItem<T>> items;
  final ValueChanged<T?> onChanged;
  final String? Function(T?)? validator;

  const TDropdown({
    super.key,
    required this.label,
    required this.items,
    required this.onChanged,
    this.hint,
    this.value,
    this.validator,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: DropdownButtonFormField<T>(
        initialValue: value,
        decoration: InputDecoration(
          labelText: label,
          hintText: hint,
        ),
        dropdownColor: AppColors.surface,
        validator: validator,
        items: items.map((item) {
          return DropdownMenuItem<T>(
            value: item.value,
            child: TText.body(item.label),
          );
        }).toList(),
        onChanged: onChanged,
      ),
    );
  }
}
