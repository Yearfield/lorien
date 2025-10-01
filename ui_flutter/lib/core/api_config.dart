class ApiConfig {
  static const String base =
      String.fromEnvironment('API_BASE', defaultValue: 'http://127.0.0.1:8000/api/v1');
}
