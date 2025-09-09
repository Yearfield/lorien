import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';

final treeApiProvider = Provider((ref) => TreeApi(ref.read(dioProvider)));

class TreeApi {
  TreeApi(this._dio);
  final Dio _dio;

  /// Returns `null` when none (supports 204 or 200 with parent_id:null)
  Future<Map<String, dynamic>?> nextIncompleteParent() async {
    try {
      final r = await _dio.get('/tree/next-incomplete-parent',
          options: Options(
              validateStatus: (s) => s != null && (s == 200 || s == 204)));
      if (r.statusCode == 204) return null;
      final data = Map<String, dynamic>.from(r.data ?? const {});
      if (data['parent_id'] == null) return null;
      return data;
    } on DioException {
      rethrow;
    }
  }

  /// Read children for a parent with fallback to legacy endpoint
  Future<Map<String, dynamic>> readChildren(int parentId) async {
    try {
      final r = await _dio.get('/tree/$parentId/children');
      return (r.data as Map).cast<String, dynamic>();
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        // Fallback to legacy endpoint
        final r = await _dio.get('/tree/parent/$parentId/children');
        return (r.data as Map).cast<String, dynamic>();
      }
      rethrow;
    }
  }

  /// Update children for a parent with fallback to legacy endpoint
  Future<Map<String, dynamic>> updateChildren(
    int parentId,
    Map<String, dynamic> body, {
    String? etag,
  }) async {
    try {
      final r = await _dio.put(
        '/tree/$parentId/children',
        data: body,
        options: Options(headers: etag == null ? null : {'If-Match': etag}),
      );
      return (r.data as Map).cast<String, dynamic>();
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        // Fallback to legacy endpoint
        final r = await _dio.put(
          '/tree/parent/$parentId/children',
          data: body,
          options: Options(headers: etag == null ? null : {'If-Match': etag}),
        );
        return (r.data as Map).cast<String, dynamic>();
      }
      rethrow;
    }
  }
}
