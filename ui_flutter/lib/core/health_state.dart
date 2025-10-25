import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'api_config.dart';
import 'settings_provider.dart';

class HealthState extends ChangeNotifier {
  final Dio _dio = Dio(BaseOptions(
    connectTimeout: const Duration(seconds: 3),
    receiveTimeout: const Duration(seconds: 3),
  ));

  bool online = true;
  DateTime? lastChecked;
  String? _apiBaseUrl;

  void setApiBaseUrl(String url) {
    _apiBaseUrl = url;
  }

  Future<void> check() async {
    try {
      // Use stored API base URL if available, otherwise use environment variable
      final baseUrl = _apiBaseUrl ?? ApiConfig.base;
      final r = await _dio.get('$baseUrl/health');
      online = r.statusCode == 200;
    } catch (_) {
      online = false;
    }
    lastChecked = DateTime.now();
    notifyListeners();
  }
}
