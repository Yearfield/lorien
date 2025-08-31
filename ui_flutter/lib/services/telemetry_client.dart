import 'package:dio/dio.dart';

class TelemetryClient {
  final Dio dio;
  final String baseUrl;
  final bool enabled;
  
  TelemetryClient({required this.dio, required this.baseUrl, required this.enabled});

  Future<void> event(String name, {Map<String, String>? props}) async {
    if (!enabled) return;
    try {
      // Try optional endpoint; no-op if 404
      await dio.post('$baseUrl/metrics/event', data: {'name': name, 'props': props ?? {}});
    } catch (_) {/* swallow */}
  }
}
