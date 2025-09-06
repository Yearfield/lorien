import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';
import 'session_models.dart';

class SessionService {
  final Dio _dio;

  SessionService(this._dio);

  Future<SessionExport> exportSession() async {
    final response = await _dio.get('/session/export');
    return SessionExport.fromJson(response.data as Map<String, dynamic>);
  }

  Future<SessionImportResult> importSession(SessionExport sessionData) async {
    final response = await _dio.post('/session/import', data: sessionData.toJson());
    return SessionImportResult.fromJson(response.data as Map<String, dynamic>);
  }

  Future<WorkbookSnapshot> getWorkbookSnapshot(String workbookId) async {
    final response = await _dio.get('/session/workbooks/$workbookId');
    return WorkbookSnapshot.fromJson(response.data as Map<String, dynamic>);
  }

  Future<List<WorkbookSnapshot>> getWorkbookList() async {
    final response = await _dio.get('/session/workbooks');
    final data = response.data as List<dynamic>;
    return data.map((item) => WorkbookSnapshot.fromJson(item as Map<String, dynamic>)).toList();
  }

  Future<CsvPreview> previewCsv(String filePath, {bool hasHeaders = true}) async {
    final params = <String, dynamic>{'has_headers': hasHeaders};
    final response = await _dio.post('/session/csv-preview',
        data: {'file_path': filePath}, queryParameters: params);
    return CsvPreview.fromJson(response.data as Map<String, dynamic>);
  }

  Future<CsvImportResult> importCsv(String filePath, Map<String, String> headerMapping,
      {bool hasHeaders = true, String? sheetName}) async {
    final data = {
      'file_path': filePath,
      'header_mapping': headerMapping,
      'has_headers': hasHeaders,
      if (sheetName != null) 'sheet_name': sheetName,
    };
    final response = await _dio.post('/session/csv-import', data: data);
    return CsvImportResult.fromJson(response.data as Map<String, dynamic>);
  }

  Future<Map<String, String>> suggestHeaderMapping(List<String> csvHeaders) async {
    final response = await _dio.post('/session/suggest-headers',
        data: {'headers': csvHeaders});
    return (response.data as Map<String, dynamic>).cast<String, String>();
  }

  Future<PushLogSummary> getPushLog({int limit = 50, int offset = 0}) async {
    final params = <String, dynamic>{'limit': limit, 'offset': offset};
    final response = await _dio.get('/session/push-log', queryParameters: params);
    return PushLogSummary.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> clearPushLog({DateTime? before}) async {
    final params = <String, dynamic>{};
    if (before != null) {
      params['before'] = before.toIso8601String();
    }
    await _dio.delete('/session/push-log', queryParameters: params);
  }

  Future<SessionContext> getCurrentSession() async {
    final response = await _dio.get('/session/current');
    return SessionContext.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> updateSessionContext(SessionContext context) async {
    await _dio.put('/session/current', data: context.toJson());
  }

  Future<String> exportToJsonFile(SessionExport data) async {
    final jsonString = jsonEncode(data.toJson());
    // In a real implementation, this would save to a file
    // For now, we'll just return the JSON string
    return jsonString;
  }

  Future<SessionExport> importFromJsonFile(String jsonString) async {
    final jsonData = jsonDecode(jsonString) as Map<String, dynamic>;
    return SessionExport.fromJson(jsonData);
  }

  Future<List<String>> validateSessionImport(SessionExport data) async {
    final response = await _dio.post('/session/validate-import', data: data.toJson());
    return (response.data as List<dynamic>).cast<String>();
  }

  Future<Map<String, dynamic>> getImportConflicts(SessionExport data) async {
    final response = await _dio.post('/session/import-conflicts', data: data.toJson());
    return response.data as Map<String, dynamic>;
  }

  Future<void> resolveImportConflicts(Map<String, dynamic> resolutions) async {
    await _dio.post('/session/resolve-conflicts', data: resolutions);
  }

  Future<List<Map<String, dynamic>>> getAvailableSheets() async {
    final response = await _dio.get('/session/sheets');
    return (response.data as List<dynamic>).cast<Map<String, dynamic>>();
  }

  Future<void> switchSheet(String sheetId) async {
    await _dio.post('/session/switch-sheet', data: {'sheet_id': sheetId});
  }

  Future<Map<String, dynamic>> getSheetMetadata(String sheetId) async {
    final response = await _dio.get('/session/sheets/$sheetId/metadata');
    return response.data as Map<String, dynamic>;
  }
}

final sessionServiceProvider = Provider<SessionService>((ref) {
  final dio = ref.read(dioProvider);
  return SessionService(dio);
});
