import '../http/api_client.dart';

/// Health API interface
abstract class HealthApi {
  Future<Map<String, dynamic>> getHealth();
}

/// Default implementation using ApiClient
class DefaultHealthApi implements HealthApi {
  final ApiClient _client;

  DefaultHealthApi(this._client);

  @override
  Future<Map<String, dynamic>> getHealth() async {
    return await _client.get('/health');
  }
}
