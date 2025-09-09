import 'dart:typed_data';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';

final workspaceApiProvider =
    Provider((ref) => WorkspaceApi(ref.read(dioProvider)));

class WorkspaceApi {
  WorkspaceApi(this._dio);
  final Dio _dio;

  Future<Map<String, dynamic>> importExcel(MultipartFile file) async {
    final form = FormData.fromMap({'file': file});
    try {
      final r = await _dio.post('/import', data: form);
      return Map<String, dynamic>.from(r.data);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        final r =
            await _dio.post('/import/excel', data: form); // legacy fallback
        return Map<String, dynamic>.from(r.data);
      }
      rethrow;
    }
  }

  Future<Uint8List> exportCsv() async {
    final r = await _dio.get('/tree/export',
        options: Options(responseType: ResponseType.bytes),
        queryParameters: {'format': 'csv'});
    return Uint8List.fromList((r.data as List<int>));
  }

  Future<Uint8List> exportXlsx() async {
    final r = await _dio.get('/tree/export.xlsx',
        options: Options(responseType: ResponseType.bytes));
    return Uint8List.fromList((r.data as List<int>));
  }
}
