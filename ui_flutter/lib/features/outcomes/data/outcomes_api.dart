import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';

final outcomesApiProvider = Provider((ref) => OutcomesApi(ref.read(dioProvider)));

class OutcomesApi {
  OutcomesApi(this._dio);
  final Dio _dio;
  
  Future<Map<String, dynamic>> getDetail(String id) async {
    final res = await _dio.get('/triage/$id');
    return Map<String, dynamic>.from(res.data);
  }
  
  Future<void> updateDetail(String id, {required String triage, required String actions}) async {
    await _dio.put('/triage/$id', data: {
      'diagnostic_triage': triage.trim(),
      'actions': actions.trim(),
    });
  }
  
  Future<Map<String, dynamic>> search({String? vm, String? q, int page = 1}) async {
    final res = await _dio.get('/triage/search', queryParameters: {
      if (vm?.isNotEmpty == true) 'vm': vm,
      if (q?.isNotEmpty == true) 'q': q,
      'page': page,
    });
    return Map<String, dynamic>.from(res.data);
  }
}
