import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';

final llmApiProvider = Provider((ref) => LlmApi(ref.read(dioProvider)));

class LlmApi {
  LlmApi(this._dio);
  final Dio _dio;

  Future<({bool usable, Map<String,dynamic> body})> health() async {
    try {
      final r = await _dio.get('/llm/health');
      return (usable: r.statusCode == 200, body: Map<String,dynamic>.from(r.data ?? {}));
    } on DioException catch (e) {
      if (e.response?.statusCode == 503) {
        return (usable: false, body: Map<String,dynamic>.from(e.response?.data ?? {}));
      }
      rethrow;
    }
  }

  Future<Map<String, dynamic>> fill(String id) async {
    final r = await _dio.post('/llm/fill-triage-actions', data: {'id': id});
    return Map<String, dynamic>.from(r.data);
  }
}
