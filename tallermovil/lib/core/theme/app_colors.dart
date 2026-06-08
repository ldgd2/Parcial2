import 'package:flutter/material.dart';

/// Tokens de color extraídos de la versión web (Angular SCSS)
/// Diseño Moderno Oscuro (Dark Mode) con Azul Cielo (Sky Blue) como color principal.
class AppColors {
  // Paleta Principal (Sky Blue)
  static const Color primary50 = Color(0xFFF0F9FF);
  static const Color primary100 = Color(0xFFE0F2FE);
  static const Color primary200 = Color(0xFFBAE6FD);
  static const Color primary300 = Color(0xFF7DD3FC);
  static const Color primary400 = Color(0xFF38BDF8);
  static const Color primary = Color(0xFF0EA5E9); // Brand Base (Primary 500)
  static const Color primary600 = Color(0xFF0284C7);
  static const Color primary700 = Color(0xFF0369A1);
  static const Color primary800 = Color(0xFF075985);
  static const Color primary900 = Color(0xFF0C4A6E);

  // Neutros (Slate) para Dark Mode
  static const Color neutral50 = Color(0xFFF8FAFC);
  static const Color neutral100 = Color(0xFFF1F5F9);
  static const Color neutral200 = Color(0xFFE2E8F0);
  static const Color neutral300 = Color(0xFFCBD5E1);
  static const Color neutral400 = Color(0xFF94A3B8);
  static const Color neutral500 = Color(0xFF64748B);
  static const Color neutral600 = Color(0xFF475569);
  static const Color neutral700 = Color(0xFF334155);
  static const Color neutral800 = Color(0xFF1E293B);
  static const Color neutral900 = Color(0xFF0F172A);
  static const Color neutral950 = Color(0xFF020617); // Extra oscuro

  // Semánticos
  static const Color success = Color(0xFF10B981); // Emerald
  static const Color successBg = Color(0xFF064E3B);
  
  static const Color danger = Color(0xFFEF4444); // Red
  static const Color dangerBg = Color(0xFF7F1D1D);
  
  static const Color warning = Color(0xFFF59E0B); // Amber
  static const Color warningBg = Color(0xFF78350F);
  
  static const Color info = Color(0xFF3B82F6); // Blue
  static const Color infoBg = Color(0xFF1E3A8A);

  // --- Mapeo Semántico para Dark Mode ---
  static const Color background = Color(0xFF050505);
  static const Color surface = Color(0xFF0A0A0A);
  static const Color neutral100_map = Color(0xFF111111); // Para compatibilidad de componentes en dark mode
  
  static const Color textPrimary = Color(0xFFF4F4F5); // zinc-50
  static const Color textSecondary = Color(0xFFA1A1AA); // zinc-400
  static const Color textMuted = Color(0xFF71717A); // zinc-500

  static const Color border = Color(0xFF222222);
  static const Color borderFocus = primary;
}
