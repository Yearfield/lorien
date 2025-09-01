import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';

final llmApiProvider = Provider((ref) => LlmApi(ref.read(dioProvider)));

class LlmApi {
  LlmApi(this._dio); 
  final Dio _dio;
  
  Future<bool> health() async {
    try { 
      final r = await _dio.get('/llm/health'); 
      return r.statusCode == 200; 
    } catch (_) { 
      return false; 
    }
  }
  
  Future<Map<String, dynamic>> fill(String id) async {
    final r = await _dio.post('/llm/fill-triage-actions', data: {'id': id});
    return Map<String, dynamic>.from(r.data);
  }
}
