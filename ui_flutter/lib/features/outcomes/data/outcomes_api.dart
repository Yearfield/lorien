import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../api/lorien_api.dart';
import '../../../providers/lorien_api_provider.dart';

final outcomesApiProvider =
    Provider((ref) => OutcomesApi(ref.read(lorienApiProvider)));

class OutcomesApi {
  OutcomesApi(this._api);
  final LorienApi _api;

  Future<Map<String, dynamic>> getDetail(String id) async {
    final res = await _api._client.getJson('outcomes/$id');
    return res;
  }

  Future<Map<String, dynamic>> getTreePath(String id) async {
    final path = await _api.getPath(int.parse(id));
    return path;
  }

  Future<Map<String, dynamic>> copyFromVm(String vm) async {
    final res = await _dio.get('/triage/search',
        queryParameters: {'vm': vm, 'leaf_only': true, 'sort': 'updated_at:desc', 'limit': 1});
    return Map<String, dynamic>.from(res.data);
  }

  Future<void> updateDetail(String id,
      {required String triage, required String actions}) async {
    await _api.putOutcome(int.parse(id), {
      'diagnostic_triage': triage.trim(),
      'actions': actions.trim(),
    });
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
