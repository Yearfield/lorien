import 'package:dio/dio.dart';
import '../data/api_client.dart';

/// Typed API client for Lorien backend endpoints
class LorienApi {
  final ApiClient _client;

  LorienApi(this._client);

  /// Health endpoints
  Future<Map<String, dynamic>> health() async =>
      _client.getJson('health');

  Future<Map<String, dynamic>> llmHealth() async =>
      _client.getJson('llm/health');

  /// Tree endpoints
  Future<Map<String, dynamic>> getParentChildren(int parentId) async =>
      _client.getJson('tree/parent/$parentId/children');

  Future<Map<String, dynamic>> updateParentChildren(
    int parentId,
    Map<String, dynamic> body, {
    String? etag
  }) async {
    final options = etag != null
        ? Options(headers: {'If-Match': etag})
        : null;
    return _client.postJson('tree/parent/$parentId/children', body: body);
  }

  Future<Map<String, dynamic>?> nextIncompleteParent() async {
    try {
      final response = await _client.get('tree/next-incomplete-parent');
      if (response.statusCode == 204) return null;
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      if (e.response?.statusCode == 204) return null;
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getPath(int nodeId) async =>
      _client.getJson('tree/path', query: {'node_id': nodeId});

  /// Dictionary endpoints
  Future<List<dynamic>> dictionarySuggest(
    String query, {
    int limit = 10
  }) async =>
      _client.getJson('dictionary',
          query: {'type': 'node_label', 'query': query, 'limit': limit})
          .then((data) => data as List<dynamic>);

  Future<Map<String, dynamic>> dictionaryImport(MultipartFile file) async =>
      _client.postMultipart('dictionary/import', extras: {'file': file.path});

  /// Outcomes endpoints
  Future<Response> putOutcome(int nodeId, Map<String, dynamic> body) async =>
      _client.put('outcomes/$nodeId', data: body);

  /// Utility methods for error handling
  static List<Map<String, dynamic>> extractDetailErrors(Object error) {
    if (error is DioException && error.response?.data is Map) {
      final data = error.response!.data as Map;
      if (data['detail'] is List) {
        return List<Map<String, dynamic>>.from(data['detail']);
      }
    }
    return [];
  }
}
