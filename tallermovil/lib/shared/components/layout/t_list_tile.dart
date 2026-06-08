import 'package:flutter/material.dart';
import 'package:tallermovil/core/theme/app_colors.dart';
import 'package:tallermovil/shared/components/typography/t_text.dart';

class TListTile extends StatelessWidget {
  final String title;
  final String? subtitle;
  final Widget? leading;
  final Widget? trailing;
  final VoidCallback? onTap;

  const TListTile({
    super.key,
    required this.title,
    this.subtitle,
    this.leading,
    this.trailing,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
      tileColor: AppColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.zero,
        side: BorderSide(color: AppColors.border),
      ),
      leading: leading,
      title: TText.label(title),
      subtitle: subtitle != null ? TText.bodySmall(subtitle!) : null,
      trailing: trailing,
      onTap: onTap,
    );
  }
}
