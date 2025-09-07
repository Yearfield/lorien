import '../http/api_client.dart';

/// Tree API interface
abstract class TreeApi {
  Future<Map<String, dynamic>> getStats();
  Future<Map<String, dynamic>> createRoot(String label);
  Future<Map<String, dynamic>> getChildren(int parentId);
  Future<Map<String, dynamic>> getNextIncompleteParent();
}

/// Default implementation using ApiClient
class DefaultTreeApi implements TreeApi {
  final ApiClient _client;

  DefaultTreeApi(this._client);

  @override
  Future<Map<String, dynamic>> getStats() async {
    return await _client.get('/tree/stats');
  }

  @override
  Future<Map<String, dynamic>> createRoot(String label) async {
    return await _client.post('/tree/roots', body: {'label': label});
  }

  @override
  Future<Map<String, dynamic>> getChildren(int parentId) async {
    return await _client.get('/tree/$parentId/children');
  }

  @override
  Future<Map<String, dynamic>> getNextIncompleteParent() async {
    return await _client.get('/tree/next-incomplete-parent');
  }
}
