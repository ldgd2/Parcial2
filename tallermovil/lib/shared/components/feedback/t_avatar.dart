import 'package:flutter/material.dart';
import 'package:tallermovil/core/theme/app_colors.dart';
import 'package:tallermovil/core/theme/app_text_styles.dart';

class TAvatar extends StatelessWidget {
  final String? url;
  final String fallback;
  final double size;

  const TAvatar({
    super.key,
    this.url,
    required this.fallback,
    this.size = 40.0,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.rectangle,
        color: AppColors.neutral800,
        border: Border.all(color: AppColors.primary, width: 1.5),
      ),
      child: ClipOval(
        child: url != null && url!.isNotEmpty
            ? Image.network(
                url!,
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) => _buildFallback(),
              )
            : _buildFallback(),
      ),
    );
  }

  Widget _buildFallback() {
    return Center(
      child: Text(
        fallback.isNotEmpty ? fallback.substring(0, 1).toUpperCase() : '?',
        style: AppTextStyles.h4.copyWith(
          color: AppColors.primary,
        ),
      ),
    );
  }
}
