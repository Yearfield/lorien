import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';

class SymptomsRepository {
  final Dio _dio;

  SymptomsRepository(this._dio);

  Future<List<String>> getRoots() async {
    final response = await _dio.get('/tree/roots');
    return List<String>.from(response.data ?? []);
  }

  Future<Map<String, dynamic>> getOptions({
    required String? root,
    required String? n1,
    required String? n2,
    required String? n3,
    required String? n4,
  }) async {
    final params = <String, dynamic>{};
    if (root != null) params['root'] = root;
    if (n1 != null) params['n1'] = n1;
    if (n2 != null) params['n2'] = n2;
    if (n3 != null) params['n3'] = n3;
    if (n4 != null) params['n4'] = n4;

    final response = await _dio.get('/calc/options', queryParameters: params);
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getLeafPreview(String leafId) async {
    final response = await _dio.get('/triage/$leafId');
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>?> nextIncompleteParent() async {
    final response = await _dio.get('/tree/next-incomplete-parent',
        options: Options(validateStatus: (s) => s != null && (s == 200 || s == 204)));
    if (response.statusCode == 204) return null;
    final data = response.data as Map<String, dynamic>;
    if (data['parent_id'] == null) return null;
    return data;
  }
}

final symptomsRepositoryProvider = Provider<SymptomsRepository>((ref) {
  final dio = ref.read(dioProvider);
  return SymptomsRepository(dio);
});
