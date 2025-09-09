import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../api/lorien_api.dart';
import '../../../providers/lorien_api_provider.dart';

final outcomesApiProvider =
    Provider((ref) => OutcomesApi(ref.read(lorienApiProvider)));

class OutcomesApi {
  OutcomesApi(this._api);
  final LorienApi _api;

  Future<Map<String, dynamic>> getDetail(String id) async {
    final res = await _api.getOutcome(int.parse(id));
    return res;
  }

  Future<Map<String, dynamic>> getTreePath(String id) async {
    final path = await _api.getPath(int.parse(id));
    return path;
  }

  Future<Map<String, dynamic>> copyFromVm(String vm) async {
    final res = await _api.client.getJson('triage/search', query: {
      'vm': vm,
      'leaf_only': true,
      'sort': 'updated_at:desc',
      'limit': 1
    });
    return res;
  }

  Future<void> updateDetail(String id,
      {required String triage, required String actions}) async {
    await _api.putOutcome(int.parse(id), {
      'diagnostic_triage': triage.trim(),
      'actions': actions.trim(),
    });
  }

  Future<Map<String, dynamic>> search(
      {String? vm, String? q, int page = 1}) async {
    final query = {
      if (vm?.isNotEmpty == true) 'vm': vm,
      if (q?.isNotEmpty == true) 'q': q,
      'page': page,
    };
    try {
      final r = await _api.client.getJson('outcomes/search', query: query);
      return r;
    } catch (e) {
      // Fallback to triage search
      final r = await _api.client.getJson('triage/search', query: query);
      return r;
    }
  }
}
