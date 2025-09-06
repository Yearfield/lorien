import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../api/lorien_api.dart';
import '../../../providers/lorien_api_provider.dart';

final llmApiProvider = Provider((ref) => LlmApi(ref.read(lorienApiProvider)));

class LlmApi {
  LlmApi(this._api);
  final LorienApi _api;

  Future<({bool ready, String? checkedAt})> health() async {
    try {
      final health = await _api.llmHealth();
      return (
        ready: (health['ready'] as bool?) ?? false,
        checkedAt: health['checked_at'] as String?
      );
    } catch (e) {
      return (ready: false, checkedAt: null);
    }
  }

  Future<Map<String, dynamic>> fill(String id) async {
    final r = await _api._client.postJson('llm/fill-triage-actions', body: {'id': id});
    return r;
  }
}
