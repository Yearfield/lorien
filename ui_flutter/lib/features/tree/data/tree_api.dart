import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';

final treeApiProvider = Provider((ref) => TreeApi(ref.read(dioProvider)));

class TreeApi {
  TreeApi(this._dio);
  final Dio _dio;

  /// Returns `null` when none (supports 204 or 200 with parent_id:null)
  Future<Map<String,dynamic>?> nextIncompleteParent() async {
    try {
      final r = await _dio.get('/tree/next-incomplete-parent',
          validateStatus: (s) => s != null && (s == 200 || s == 204));
      if (r.statusCode == 204) return null;
      final data = Map<String,dynamic>.from(r.data ?? const {});
      if (data['parent_id'] == null) return null;
      return data;
    } on DioException {
      rethrow;
    }
  }
}
