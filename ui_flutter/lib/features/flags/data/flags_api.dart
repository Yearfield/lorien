import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';

final flagsApiProvider = Provider((ref) => FlagsApi(ref.read(dioProvider)));

class FlagsApi {
  FlagsApi(this._dio);
  final Dio _dio;

  Future<List<dynamic>> list(
      {String query = '', int limit = 50, int offset = 0}) async {
    final r = await _dio.get('/flags', queryParameters: {
      if (query.isNotEmpty) 'query': query,
      'limit': limit,
      'offset': offset,
    });
    return (r.data as List?) ?? [];
  }

  Future<Map<String, dynamic>> previewAssign(List<String> ids,
      {required bool cascade}) async {
    final r = await _dio
        .post('/flags/preview-assign', data: {'ids': ids, 'cascade': cascade});
    return Map<String, dynamic>.from(r.data);
  }

  Future<Map<String, dynamic>> assign(
      {required int nodeId, required int flagId, required bool cascade}) async {
    final r = await _dio.post('/flags/assign',
        data: {'node_id': nodeId, 'flag_id': flagId, 'cascade': cascade});
    return Map<String, dynamic>.from(r.data);
  }

  Future<Map<String, dynamic>> remove(
      {required int nodeId, required int flagId}) async {
    final r = await _dio
        .post('/flags/remove', data: {'node_id': nodeId, 'flag_id': flagId});
    return Map<String, dynamic>.from(r.data);
  }

  Future<List<dynamic>> audit(
      {required int nodeId, int limit = 50, int offset = 0}) async {
    final r = await _dio.get('/flags/audit',
        queryParameters: {'node_id': nodeId, 'limit': limit, 'offset': offset});
    return (r.data as List?) ?? [];
  }
}
