import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';

final calculatorApiProvider = Provider((ref) => CalculatorApi(ref.read(dioProvider)));

class CalculatorApi {
  CalculatorApi(this._dio);
  final Dio _dio;
  
  Future<Map<String, dynamic>> getOptions({String? root, List<String>? nodes}) async {
    final res = await _dio.get('/calc/options', queryParameters: {
      if (root != null) 'root': root,
      if (nodes != null) 'nodes': nodes,
    });
    return Map<String, dynamic>.from(res.data);
  }
  
  Future<Response<dynamic>> exportCsv({required String root, required List<String> nodes}) =>
    _dio.get('/calc/export', queryParameters: {'format': 'csv','root': root,'nodes': nodes});
  
  Future<Response<dynamic>> exportXlsx({required String root, required List<String> nodes}) =>
    _dio.get('/calc/export.xlsx', queryParameters: {'root': root,'nodes': nodes});
}
