import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';
import 'symptoms_models.dart';

class MaterializationService {
  final Dio _dio;

  MaterializationService(this._dio);

  Future<MaterializationResult> materializeParent(
    int parentId, {
    bool enforceFive = true,
    bool safePrune = true,
  }) async {
    final params = <String, dynamic>{
      'enforce_five': enforceFive,
      'safe_prune': safePrune,
    };

    final response = await _dio.post('/tree/parent/$parentId/materialize', queryParameters: params);
    return MaterializationResult.fromJson(response.data as Map<String, dynamic>);
  }

  Future<MaterializationResult> materializeMultipleParents(
    List<int> parentIds, {
    bool enforceFive = true,
    bool safePrune = true,
  }) async {
    final params = <String, dynamic>{
      'enforce_five': enforceFive,
      'safe_prune': safePrune,
      'parent_ids': parentIds.join(','),
    };

    final response = await _dio.post('/tree/materialize-batch', queryParameters: params);
    return MaterializationResult.fromJson(response.data as Map<String, dynamic>);
  }

  Future<MaterializationResult> materializeAllIncomplete({
    bool enforceFive = true,
    bool safePrune = true,
  }) async {
    final params = <String, dynamic>{
      'enforce_five': enforceFive,
      'safe_prune': safePrune,
    };

    final response = await _dio.post('/tree/materialize-all', queryParameters: params);
    return MaterializationResult.fromJson(response.data as Map<String, dynamic>);
  }

  Future<List<MaterializationHistoryItem>> getMaterializationHistory({
    int limit = 10,
    int offset = 0,
  }) async {
    final params = <String, dynamic>{
      'limit': limit,
      'offset': offset,
    };

    final response = await _dio.get('/tree/materialization-history', queryParameters: params);
    final data = response.data as List<dynamic>;
    return data.map((item) => MaterializationHistoryItem.fromJson(item as Map<String, dynamic>)).toList();
  }

  Future<void> undoLastMaterialization() async {
    await _dio.post('/tree/undo-last-materialization');
  }

  Future<MaterializationPreview> previewMaterialization(
    int parentId, {
    bool enforceFive = true,
    bool safePrune = true,
  }) async {
    final params = <String, dynamic>{
      'enforce_five': enforceFive,
      'safe_prune': safePrune,
    };

    final response = await _dio.get('/tree/parent/$parentId/materialize-preview', queryParameters: params);
    return MaterializationPreview.fromJson(response.data as Map<String, dynamic>);
  }

  Future<MaterializationStats> getMaterializationStats() async {
    final response = await _dio.get('/tree/materialization-stats');
    return MaterializationStats.fromJson(response.data as Map<String, dynamic>);
  }
}

final materializationServiceProvider = Provider<MaterializationService>((ref) {
  final dio = ref.read(dioProvider);
  return MaterializationService(dio);
});
