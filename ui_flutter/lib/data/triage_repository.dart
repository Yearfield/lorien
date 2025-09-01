import 'package:dio/dio.dart';
import '../models/triage_models.dart';

class TriageRepository {
  final Dio dio;
  final String baseUrl; // must include /api/v1

  TriageRepository({required this.dio, required this.baseUrl});

  Future<(List<TriageLeaf>, int)> searchLeaves({
    String? query,
    bool leafOnly = true,
    String? vm,
    String? sort,
    int? limit,
  }) async {
    final resp = await dio.get('$baseUrl/triage/search', queryParameters: {
      if (query != null) 'query': query,
      'leaf_only': leafOnly.toString(),
      if (vm != null) 'vm': vm,
      if (sort != null) 'sort': sort,
      if (limit != null) 'limit': limit.toString(),
    });

    final items = (resp.data['items'] ?? resp.data) as List;
    final total = (resp.data['total_count'] ?? items.length) as int;

    return (items.map((j) => TriageLeaf.fromJson(j)).toList(), total);
  }

  Future<TriageDetail> getLeaf(int nodeId) async {
    final resp = await dio.get('$baseUrl/triage/$nodeId');
    return TriageDetail.fromJson(resp.data);
  }

  Future<bool> saveLeaf(int nodeId, String triage, String actions) async {
    try {
      await dio.put('$baseUrl/triage/$nodeId', data: {
        'diagnostic_triage': triage,
        'actions': actions,
      });
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<bool> llmEnabled() async {
    try {
      final resp = await dio.get('$baseUrl/llm/health');
      return resp.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  Future<(String triage, String actions)> llmFill(
      LlmFillRequest request) async {
    final resp = await dio.post('$baseUrl/llm/fill-triage-actions',
        data: request.toJson());
    final triage = (resp.data['diagnostic_triage'] ?? '') as String;
    final actions = (resp.data['actions'] ?? '') as String;
    return (triage, actions);
  }

  Future<(String triage, String actions)?> copyFromLastVm(String vm) async {
    final resp = await dio.get('$baseUrl/triage/search', queryParameters: {
      'vm': vm,
      'leaf_only': 'true',
      'sort': 'updated_at:desc',
      'limit': 1
    });

    final items = (resp.data['items'] ?? resp.data) as List;
    if (items.isEmpty) return null;

    final j = items.first as Map<String, dynamic>;
    final triage = (j['diagnostic_triage'] ?? '') as String;
    final actions = (j['actions'] ?? '') as String;
    return (triage, actions);
  }
}
