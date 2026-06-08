import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_text_styles.dart';

enum BadgeStatus { success, warning, error, info, neutral }

class StatusBadge extends StatelessWidget {
  final String text;
  final BadgeStatus status;

  const StatusBadge({
    super.key,
    required this.text,
    this.status = BadgeStatus.neutral,
  });

  @override
  Widget build(BuildContext context) {
    Color bgColor;
    Color textColor;

    switch (status) {
      case BadgeStatus.success:
        bgColor = AppColors.successBg.withAlpha(128); // 0.5 opacity aprox
        textColor = AppColors.success;
        break;
      case BadgeStatus.warning:
        bgColor = AppColors.warningBg.withAlpha(128);
        textColor = AppColors.warning;
        break;
      case BadgeStatus.error:
        bgColor = AppColors.dangerBg.withAlpha(128);
        textColor = AppColors.danger;
        break;
      case BadgeStatus.info:
        bgColor = AppColors.infoBg.withAlpha(128);
        textColor = AppColors.info;
        break;
      case BadgeStatus.neutral:
        bgColor = AppColors.neutral100;
        textColor = AppColors.textSecondary;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.zero,
        border: Border.all(color: textColor.withAlpha(76)), // 0.3 opacity aprox
      ),
      child: Text(
        text.toUpperCase(),
        style: AppTextStyles.overline.copyWith(color: textColor),
      ),
    );
  }
}
