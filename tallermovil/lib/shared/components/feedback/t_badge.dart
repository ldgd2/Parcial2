import 'package:flutter/material.dart';
import 'package:tallermovil/core/theme/app_colors.dart';
import 'package:tallermovil/core/theme/app_text_styles.dart';

enum TBadgeVariant { success, error, warning, info, neutral }

class TBadge extends StatelessWidget {
  final String text;
  final TBadgeVariant variant;
  final IconData? icon;

  const TBadge({
    super.key,
    required this.text,
    this.variant = TBadgeVariant.neutral,
    this.icon,
  });

  factory TBadge.success(String text, {Key? key, IconData? icon}) {
    return TBadge(key: key, text: text, variant: TBadgeVariant.success, icon: icon);
  }

  factory TBadge.error(String text, {Key? key, IconData? icon}) {
    return TBadge(key: key, text: text, variant: TBadgeVariant.error, icon: icon);
  }

  factory TBadge.warning(String text, {Key? key, IconData? icon}) {
    return TBadge(key: key, text: text, variant: TBadgeVariant.warning, icon: icon);
  }

  factory TBadge.info(String text, {Key? key, IconData? icon}) {
    return TBadge(key: key, text: text, variant: TBadgeVariant.info, icon: icon);
  }

  @override
  Widget build(BuildContext context) {
    Color bgColor;
    Color textColor;

    switch (variant) {
      case TBadgeVariant.success:
        bgColor = AppColors.successBg;
        textColor = AppColors.success;
        break;
      case TBadgeVariant.error:
        bgColor = AppColors.dangerBg;
        textColor = AppColors.danger;
        break;
      case TBadgeVariant.warning:
        bgColor = AppColors.warningBg;
        textColor = AppColors.warning;
        break;
      case TBadgeVariant.info:
        bgColor = AppColors.infoBg;
        textColor = AppColors.info;
        break;
      case TBadgeVariant.neutral:
        bgColor = AppColors.neutral800;
        textColor = AppColors.neutral300;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.zero,
        border: Border.all(color: textColor.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 12.0, color: textColor),
            const SizedBox(width: 4.0),
          ],
          Text(
            text,
            style: AppTextStyles.overline.copyWith(
              color: textColor,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
