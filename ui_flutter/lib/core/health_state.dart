import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'api_config.dart';

class HealthState extends ChangeNotifier {
  final Dio _dio = Dio(BaseOptions(
    connectTimeout: const Duration(seconds: 3),
    receiveTimeout: const Duration(seconds: 3),
  ));

  bool online = true;
  DateTime? lastChecked;

  Future<void> check() async {
    try {
      final r = await _dio.get('${ApiConfig.base}/health');
      online = r.statusCode == 200;
    } catch (_) {
      online = false;
    }
    lastChecked = DateTime.now();
    notifyListeners();
  }
}
