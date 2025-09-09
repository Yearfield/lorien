import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';
import 'symptoms_models.dart';

class SymptomsRepository {
  final Dio _dio;

  SymptomsRepository(this._dio);

  // Legacy methods for backward compatibility
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
        options: Options(
            validateStatus: (s) => s != null && (s == 200 || s == 204)));
    if (response.statusCode == 204) return null;
    final data = response.data as Map<String, dynamic>;
    if (data['parent_id'] == null) return null;
    return data;
  }

  // Enhanced methods for Phase-6E
  Future<List<IncompleteParent>> getIncompleteParents({
    int? depth,
    String? query,
    int limit = 50,
    int offset = 0,
    SortMode sortMode = SortMode.issuesFirst,
  }) async {
    final params = <String, dynamic>{
      'limit': limit,
      'offset': offset,
      'sort': sortMode.name,
    };

    if (depth != null) params['depth'] = depth;
    if (query != null && query.isNotEmpty) params['query'] = query;

    final response =
        await _dio.get('/tree/parents/incomplete', queryParameters: params);
    final data = response.data as Map<String, dynamic>;
    final items = data['items'] as List<dynamic>;

    return items
        .map((item) => IncompleteParent.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<ParentChildren> getParentChildren(int parentId) async {
    final response = await _dio.get('/tree/parent/$parentId/children');
    return ParentChildren.fromJson(response.data as Map<String, dynamic>);
  }

  Future<ParentChildren> updateParentChildren(
      int parentId, List<ChildSlot> children,
      {String? version}) async {
    final headers = <String, dynamic>{};
    if (version != null) {
      headers['If-Match'] = version;
    }

    final request = ChildrenUpdateIn(
      version: version,
      children: children,
    );

    final response = await _dio.put(
      '/tree/parent/$parentId/children',
      data: request.toJson(),
      options: Options(headers: headers),
    );

    return ParentChildren.fromJson(response.data as Map<String, dynamic>);
  }

  Future<List<DictionarySuggestion>> getDictionarySuggestions(
      String type, String query) async {
    final params = <String, dynamic>{
      'type': type,
      'query': query,
      'limit': 10,
    };

    final response = await _dio.get('/dictionary', queryParameters: params);
    final data = response.data as List<dynamic>;

    return data
        .map((item) =>
            DictionarySuggestion.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<String> normalizeTerm(String type, String term) async {
    final params = <String, dynamic>{
      'type': type,
      'term': term,
    };

    final response =
        await _dio.get('/dictionary/normalize', queryParameters: params);
    final data = response.data as Map<String, dynamic>;
    return data['normalized'] as String;
  }

  Future<void> batchAddChildren(int parentId, List<String> labels,
      {bool replaceExisting = false}) async {
    final request = BatchAddRequest(
      labels: labels,
      replaceExisting: replaceExisting,
    );

    await _dio.post('/tree/parent/$parentId/batch-add', data: request.toJson());
  }

  Future<MaterializationResult> materializeParent(int parentId,
      {bool enforceFive = true, bool safePrune = true}) async {
    final params = <String, dynamic>{
      'enforce_five': enforceFive,
      'safe_prune': safePrune,
    };

    final response = await _dio.post('/tree/parent/$parentId/materialize',
        queryParameters: params);
    return MaterializationResult.fromJson(
        response.data as Map<String, dynamic>);
  }
}

final symptomsRepositoryProvider = Provider<SymptomsRepository>((ref) {
  final dio = ref.read(dioProvider);
  return SymptomsRepository(dio);
});
