import 'package:flutter/material.dart';
import 'package:tallermovil/core/theme/app_colors.dart';

class TSnackbar {
  static void show(
    BuildContext context, {
    required String message,
    bool isError = false,
    bool isSuccess = false,
  }) {
    Color bgColor = AppColors.neutral800;
    if (isError) bgColor = AppColors.danger;
    if (isSuccess) bgColor = AppColors.success;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          message.toUpperCase(),
          style: const TextStyle(color: Colors.white, fontFamily: 'monospace', fontWeight: FontWeight.bold, letterSpacing: 1.5),
        ),
        backgroundColor: bgColor,
        behavior: SnackBarBehavior.floating,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.zero,
        ),
      ),
    );
  }

  static void error(BuildContext context, String message) {
    show(context, message: message, isError: true);
  }

  static void success(BuildContext context, String message) {
    show(context, message: message, isSuccess: true);
  }

  static void info(BuildContext context, String message) {
    show(context, message: message);
  }
}
