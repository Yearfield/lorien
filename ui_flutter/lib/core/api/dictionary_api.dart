import '../http/api_client.dart';

/// Dictionary API interface
abstract class DictionaryApi {
  Future<Map<String, dynamic>> listTerms({
    String? type,
    String? query,
    int? limit,
    int? offset,
  });
  Future<Map<String, dynamic>> createTerm(Map<String, dynamic> data);
  Future<Map<String, dynamic>> updateTerm(int id, Map<String, dynamic> data);
  Future<Map<String, dynamic>> deleteTerm(int id);
  Future<Map<String, dynamic>> normalizeTerm(String type, String term);
}

/// Default implementation using ApiClient
class DefaultDictionaryApi implements DictionaryApi {
  final ApiClient _client;

  DefaultDictionaryApi(this._client);

  @override
  Future<Map<String, dynamic>> listTerms({
    String? type,
    String? query,
    int? limit,
    int? offset,
  }) async {
    final queryParams = <String, dynamic>{};
    if (type != null) queryParams['type'] = type;
    if (query != null) queryParams['query'] = query;
    if (limit != null) queryParams['limit'] = limit;
    if (offset != null) queryParams['offset'] = offset;

    return await _client.get('/dictionary', query: queryParams);
  }

  @override
  Future<Map<String, dynamic>> createTerm(Map<String, dynamic> data) async {
    return await _client.post('/dictionary', body: data);
  }

  @override
  Future<Map<String, dynamic>> updateTerm(int id, Map<String, dynamic> data) async {
    return await _client.put('/dictionary/$id', body: data);
  }

  @override
  Future<Map<String, dynamic>> deleteTerm(int id) async {
    return await _client.delete('/dictionary/$id');
  }

  @override
  Future<Map<String, dynamic>> normalizeTerm(String type, String term) async {
    return await _client.get('/dictionary/normalize', query: {
      'type': type,
      'term': term,
    });
  }
}
