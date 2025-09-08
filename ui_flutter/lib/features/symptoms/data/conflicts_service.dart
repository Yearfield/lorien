import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';
import 'conflicts_models.dart';

class ConflictsService {
  final Dio _dio;

  ConflictsService(this._dio);

  Future<ConflictsReport> getConflictsReport({
    List<ConflictType>? types,
    int? depth,
    String? query,
    int limit = 100,
    int offset = 0,
  }) async {
    final params = <String, dynamic>{
      'limit': limit,
      'offset': offset,
    };

    if (types != null && types.isNotEmpty) {
      params['types'] = types.map((t) => t.name).join(',');
    }

    if (depth != null) {
      params['depth'] = depth;
    }

    if (query != null && query.isNotEmpty) {
      params['query'] = query;
    }

    final response = await _dio.get('/tree/conflicts', queryParameters: params);
    return ConflictsReport.fromJson(response.data as Map<String, dynamic>);
  }

  Future<List<ConflictItem>> getConflictsByType(
    ConflictType type, {
    int? depth,
    String? query,
    int limit = 50,
    int offset = 0,
  }) async {
    final params = <String, dynamic>{
      'type': type.name,
      'limit': limit,
      'offset': offset,
    };

    if (depth != null) {
      params['depth'] = depth;
    }

    if (query != null && query.isNotEmpty) {
      params['query'] = query;
    }

    final response = await _dio.get('/tree/conflicts/${type.name}', queryParameters: params);
    final data = response.data as List<dynamic>;
    return data.map((item) => ConflictItem.fromJson(item as Map<String, dynamic>)).toList();
  }

  Future<void> resolveConflict(ConflictResolution resolution) async {
    await _dio.post('/tree/conflicts/${resolution.conflictId}/resolve',
        data: resolution.toJson());
  }

  Future<void> resolveMultipleConflicts(List<ConflictResolution> resolutions) async {
    final data = resolutions.map((r) => r.toJson()).toList();
    await _dio.post('/tree/conflicts/batch-resolve', data: data);
  }

  Future<ConflictItem> getConflictDetails(int conflictId) async {
    final response = await _dio.get('/tree/conflicts/$conflictId');
    return ConflictItem.fromJson(response.data as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> jumpToConflictLocation(int conflictId) async {
    final response = await _dio.get('/tree/conflicts/$conflictId/location');
    final data = response.data as Map<String, dynamic>;

    // This would typically navigate to the edit tree screen with the appropriate parent
    // For now, we'll just return the location data
    return data;
  }

  Future<Map<String, int>> getConflictsSummary() async {
    final response = await _dio.get('/tree/conflicts/summary');
    return (response.data as Map<String, dynamic>).cast<String, int>();
  }

  Future<void> autoResolveConflicts({
    required List<ConflictType> types,
    bool dryRun = true,
  }) async {
    final params = <String, dynamic>{
      'types': types.map((t) => t.name).join(','),
      'dry_run': dryRun,
    };

    await _dio.post('/tree/conflicts/auto-resolve', queryParameters: params);
  }

  Future<List<String>> getSuggestedResolutions(int conflictId) async {
    final response = await _dio.get('/tree/conflicts/$conflictId/suggestions');
    return (response.data as List<dynamic>).cast<String>();
  }
}

final conflictsServiceProvider = Provider<ConflictsService>((ref) {
  final dio = ref.read(dioProvider);
  return ConflictsService(dio);
});
