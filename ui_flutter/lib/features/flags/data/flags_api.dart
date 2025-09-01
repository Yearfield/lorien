import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';

final flagsApiProvider = Provider((ref) => FlagsApi(ref.read(dioProvider)));

class FlagsApi {
  FlagsApi(this._dio); 
  final Dio _dio;
  
  Future<List<dynamic>> search(String q) async {
    final r = await _dio.get('/flags/search', queryParameters: {'q': q});
    return (r.data as List?) ?? [];
  }
  
  Future<Map<String, dynamic>> previewAssign(List<String> ids, {required bool cascade}) async {
    final r = await _dio.post('/flags/preview-assign', data: {'ids': ids, 'cascade': cascade});
    return Map<String, dynamic>.from(r.data);
  }
  
  Future<void> assign(List<String> ids, {required bool cascade}) async {
    await _dio.post('/flags/assign', data: {'ids': ids, 'cascade': cascade});
  }
}
