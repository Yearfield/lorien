import 'package:dio/dio.dart';
import 'http_client.dart';

class LorienApi {
  LorienApi({required Dio dio, required this.baseUrl})
      : client = HttpClient(dio, baseUrl: baseUrl);
  final String baseUrl;
  final HttpClient client;

  // --- Health ---
  Future<Map<String, dynamic>> health() => client.getJson('health');
  Future<Map<String, dynamic>> llmHealth() async {
    final response = await client.dio.get(
        client.baseUrl.endsWith('/')
            ? '${client.baseUrl}llm/health'
            : '${client.baseUrl}/llm/health',
        options: Options(validateStatus: (_) => true));
    return response.data as Map<String, dynamic>;
  }

  // --- Calculator / Roots / Export ---
  Future<Map<String, dynamic>> getRoots() => client.getJson('tree/roots');
  Future<Map<String, dynamic>> getPath(int nodeId) =>
      client.getJson('tree/path', query: {'node_id': nodeId});
  Future<Response<List<int>>> exportCalcCsv() =>
      client.postBytes('calc/export');
  Future<Response<List<int>>> exportCalcXlsx() =>
      client.postBytes('calc/export.xlsx');

  // --- Edit Tree helpers ---
  Future<Map<String, dynamic>> readParentChildren(int parentId) =>
      client.getJson('tree/parent/$parentId/children');
  Future<Map<String, dynamic>> updateParentChildren(
      int parentId, Map<String, dynamic> body,
      {String? etag}) async {
    final r = await client.dio.put(
        client.baseUrl.endsWith('/')
            ? '${client.baseUrl}tree/parent/$parentId/children'
            : '${client.baseUrl}/tree/parent/$parentId/children',
        data: body,
        options: Options(headers: etag == null ? null : {'If-Match': etag}));
    return (r.data as Map).cast<String, dynamic>();
  }

  // --- Outcomes ---
  Future<Map<String, dynamic>> getOutcome(int id) =>
      client.getJson('outcomes/$id');
  Future<Response> putOutcome(int id, Map<String, dynamic> body) =>
      client.dio.put(
          client.baseUrl.endsWith('/')
              ? '${client.baseUrl}outcomes/$id'
              : '${client.baseUrl}/outcomes/$id',
          data: body);

  // --- LLM Fill ---
  Future<Map<String, dynamic>> llmFill(Map<String, dynamic> body) =>
      client.postJson('llm/fill-triage-actions', body: body);

  // --- Dictionary ---
  Future<Map<String, dynamic>> dictionaryList(
      {String? type,
      String query = "",
      int limit = 50,
      int offset = 0,
      bool onlyRedFlags = false,
      String? sort,
      String? direction}) async {
    final qp = {
      "query": query,
      "limit": limit,
      "offset": offset,
      if (type != null) "type": type,
      if (onlyRedFlags) "only_red_flags": onlyRedFlags,
      if (sort != null) "sort": sort,
      if (direction != null) "direction": direction
    };
    return client.getJson('dictionary', query: qp);
  }

  Future<List<dynamic>> dictionarySuggest(
      {required String type,
      required String query,
      int limit = 10,
      int offset = 0}) async {
    final res = await client.dio.get(
      client.baseUrl.endsWith('/')
          ? '${client.baseUrl}dictionary'
          : '${client.baseUrl}/dictionary',
      queryParameters: {
        'type': type,
        'query': query,
        'limit': limit,
        'offset': offset
      },
    );
    return res.data as List<dynamic>;
  }

  Future<Map<String, dynamic>> dictionaryCreate(
          Map<String, dynamic> data) async =>
      client.postJson('dictionary', body: data);

  Future<Map<String, dynamic>> dictionaryUpdate(
      int id, Map<String, dynamic> data) async {
    final response = await client.dio.put(
        client.baseUrl.endsWith('/')
            ? '${client.baseUrl}dictionary/$id'
            : '${client.baseUrl}/dictionary/$id',
        data: data);
    return response.data as Map<String, dynamic>;
  }

  Future<void> dictionaryDelete(int id) async =>
      client.dio.delete(client.baseUrl.endsWith('/')
          ? '${client.baseUrl}dictionary/$id'
          : '${client.baseUrl}/dictionary/$id');

  Future<Map<String, dynamic>> dictionaryGet(int id) async =>
      client.getJson('dictionary/$id');

  Future<String> dictionaryNormalize(String type, String term) async =>
      client.getJson('dictionary/normalize', query: {
        'type': type,
        'term': term
      }).then((data) => data['normalized'] as String);

  /// Import from an on-disk file path (Dio 5)
  Future<Response> dictionaryImportFromPath(String filePath) async {
    final file = await MultipartFile.fromFile(filePath);
    final form = FormData.fromMap({'file': file});
    return client.postMultipart('dictionary/import', formData: form);
  }

  // Shared helper used by controllers to surface FastAPI errors
  static List<Map<String, dynamic>> extractDetailErrors(Object err) {
    if (err is DioException) {
      final data = err.response?.data;
      if (data is Map && data['detail'] is List) {
        return List<Map<String, dynamic>>.from(data['detail'] as List);
      }
    }
    return const [];
  }
}
