import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';

final llmApiProvider = Provider((ref) => LlmApi(ref.read(dioProvider)));

class LlmApi {
  LlmApi(this._dio);
  final Dio _dio;

  Future<({bool ready, String? checkedAt})> health() async {
    try {
      final r = await _dio.get('/llm/health');
      if (r.statusCode == 200) {
        return (
          ready: r.data?['ready'] ?? true,
          checkedAt: r.data?['checked_at'] as String?
        );
      } else if (r.statusCode == 503) {
        return (
          ready: r.data?['ready'] ?? false,
          checkedAt: r.data?['checked_at'] as String?
        );
      }
      return (ready: false, checkedAt: null);
    } on DioException catch (e) {
      return (ready: false, checkedAt: null);
    }
  }

  Future<Map<String, dynamic>> fill(String id) async {
    final r = await _dio.post('/llm/fill-triage-actions', data: {'id': id});
    return Map<String, dynamic>.from(r.data);
  }
}
