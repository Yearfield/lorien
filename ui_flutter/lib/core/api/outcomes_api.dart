import '../http/api_client.dart';

/// Outcomes API interface
abstract class OutcomesApi {
  Future<Map<String, dynamic>> getTriage(int nodeId);
  Future<Map<String, dynamic>> updateTriage(
      int nodeId, Map<String, dynamic> data);
}

/// Default implementation using ApiClient
class DefaultOutcomesApi implements OutcomesApi {
  final ApiClient _client;

  DefaultOutcomesApi(this._client);

  @override
  Future<Map<String, dynamic>> getTriage(int nodeId) async {
    return await _client.get('/triage/$nodeId');
  }

  @override
  Future<Map<String, dynamic>> updateTriage(
      int nodeId, Map<String, dynamic> data) async {
    return await _client.put('/triage/$nodeId', body: data);
  }
}
