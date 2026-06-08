import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'app_colors.dart';

/// Tipografía Global alineada con la Web (Inter font)
class AppTextStyles {
  // Configuración base de la fuente
  static TextStyle get _baseStyle => GoogleFonts.spaceMono(
        color: AppColors.textPrimary,
      );

  // --- Encabezados (Títulos) ---
  static TextStyle get h1 => _baseStyle.copyWith(
        fontSize: 36, // --t-size-4xl
        fontWeight: FontWeight.w700,
        height: 1.25, // --t-line-tight
        letterSpacing: -0.5,
      );

  static TextStyle get h2 => _baseStyle.copyWith(
        fontSize: 30, // --t-size-3xl
        fontWeight: FontWeight.w700,
        height: 1.25,
        letterSpacing: -0.5,
      );

  static TextStyle get h3 => _baseStyle.copyWith(
        fontSize: 24, // --t-size-2xl
        fontWeight: FontWeight.w600,
        height: 1.25,
      );

  static TextStyle get h4 => _baseStyle.copyWith(
        fontSize: 16,
        fontWeight: FontWeight.bold,
        letterSpacing: 1.0,
      );

  // --- Cuerpo de Texto (Body) ---
  static TextStyle get bodyLarge => _baseStyle.copyWith(
        fontSize: 18, // --t-size-lg
        fontWeight: FontWeight.w400,
        height: 1.5, // --t-line-base
      );

  static TextStyle get bodyMedium => _baseStyle.copyWith(
        fontSize: 16, // --t-size-base
        fontWeight: FontWeight.w400,
        height: 1.5,
      );

  static TextStyle get bodySmall => _baseStyle.copyWith(
        fontSize: 14, // --t-size-sm
        fontWeight: FontWeight.w400,
        height: 1.5,
        color: AppColors.textSecondary,
      );

  // --- Elementos de Interfaz (Botones, Labels, etc) ---
  static TextStyle get label => _baseStyle.copyWith(
        fontSize: 10, // Angular uses text-[9px] or similar
        fontWeight: FontWeight.bold,
        letterSpacing: 2.5,
      );

  static TextStyle get button => _baseStyle.copyWith(
        fontSize: 11, // Angular uses text-[11px] for main buttons
        fontWeight: FontWeight.bold,
        letterSpacing: 2.5,
      );

  static TextStyle get overline => _baseStyle.copyWith(
        fontSize: 12, // --t-size-xs
        fontWeight: FontWeight.w600,
        letterSpacing: 1.0,
        color: AppColors.textMuted,
        height: 1.5,
      );
}
