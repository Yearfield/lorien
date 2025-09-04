import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';

final outcomesApiProvider =
    Provider((ref) => OutcomesApi(ref.read(dioProvider)));

class OutcomesApi {
  OutcomesApi(this._dio);
  final Dio _dio;

  Future<Map<String, dynamic>> getDetail(String id) async {
    final res = await _dio.get('/outcomes/$id');
    return Map<String, dynamic>.from(res.data);
  }

  Future<Map<String, dynamic>> getTreePath(String id) async {
    final res = await _dio.get('/tree/path/$id');
    return Map<String, dynamic>.from(res.data);
  }

  Future<Map<String, dynamic>> copyFromVm(String vm) async {
    final res = await _dio.get('/triage/search',
        queryParameters: {'vm': vm, 'leaf_only': true, 'sort': 'updated_at:desc', 'limit': 1});
    return Map<String, dynamic>.from(res.data);
  }

  Future<void> updateDetail(String id,
      {required String triage, required String actions}) async {
    Future<void> put(String path) => _dio.put(path, data: {
      'diagnostic_triage': triage.trim(),
      'actions': actions.trim(),
    });
    try { await put('/outcomes/$id'); }
    on DioException catch (e) {
      if (e.response?.statusCode == 404) { await put('/triage/$id'); }
      else { rethrow; }
    }
  }

  Future<Map<String, dynamic>> search(
      {String? vm, String? q, int page = 1}) async {
    Future<Response> get(String path) => _dio.get(path, queryParameters: {
      if (vm?.isNotEmpty == true) 'vm': vm,
      if (q?.isNotEmpty == true) 'q': q,
      'page': page,
    });
    try {
      final r = await get('/outcomes/search');
      return Map<String, dynamic>.from(r.data);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        final r = await get('/triage/search');
        return Map<String, dynamic>.from(r.data);
      }
      rethrow;
    }
  }
}
