class AuthResponse {
  final String accessToken;
  final String tokenType;
  final String rol;
  final int userId;
  final String? taller;

  AuthResponse({
    required this.accessToken,
    required this.tokenType,
    required this.rol,
    required this.userId,
    this.taller,
  });

  /// Inicializa el objeto a partir del JSON devuelto por el backend.
  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access_token'] as String,
      tokenType: json['token_type'] as String,
      rol: json['rol'] as String,
      userId: json['user_id'] as int,
      taller: json['cod_taller'] as String? ?? json['taller'] as String?,
    );
  }
}
