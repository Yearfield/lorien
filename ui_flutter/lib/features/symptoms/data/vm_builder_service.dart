import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';
import 'vm_builder_models.dart';

class VmBuilderService {
  final Dio _dio;

  VmBuilderService(this._dio);

  Future<List<String>> getExistingVitalMeasurements() async {
    final response = await _dio.get('/tree/roots');
    final data = response.data as Map<String, dynamic>;
    return List<String>.from(data['roots'] ?? []);
  }

  Future<DuplicateCheckResult> checkForDuplicates(SheetDraft draft) async {
    final response = await _dio.post('/vm-builder/check-duplicates', data: draft.toJson());
    return DuplicateCheckResult.fromJson(response.data as Map<String, dynamic>);
  }

  Future<ValidationResult> validateDraft(SheetDraft draft) async {
    final response = await _dio.post('/vm-builder/validate', data: draft.toJson());
    return ValidationResult.fromJson(response.data as Map<String, dynamic>);
  }

  Future<CreationResult> createSheet(SheetDraft draft, {bool autoMaterialize = true}) async {
    final params = <String, dynamic>{'auto_materialize': autoMaterialize};
    final response = await _dio.post('/vm-builder/create',
        data: draft.toJson(), queryParameters: params);
    return CreationResult.fromJson(response.data as Map<String, dynamic>);
  }

  Future<List<String>> getSuggestedNodeLabels(String type, String prefix) async {
    final params = <String, dynamic>{
      'type': type,
      'prefix': prefix,
      'limit': 10,
    };
    final response = await _dio.get('/vm-builder/suggestions', queryParameters: params);
    return List<String>.from(response.data as List<dynamic>);
  }

  Future<SheetDraft> loadTemplate(String templateId) async {
    final response = await _dio.get('/vm-builder/templates/$templateId');
    return SheetDraft.fromJson(response.data as Map<String, dynamic>);
  }

  Future<List<Map<String, dynamic>>> getAvailableTemplates() async {
    final response = await _dio.get('/vm-builder/templates');
    return List<Map<String, dynamic>>.from(response.data as List<dynamic>);
  }

  Future<void> saveAsTemplate(SheetDraft draft, String templateName) async {
    final data = {
      'draft': draft.toJson(),
      'name': templateName,
    };
    await _dio.post('/vm-builder/templates', data: data);
  }

  Future<List<String>> getCommonVitalMeasurementPrefixes() async {
    final response = await _dio.get('/vm-builder/common-prefixes');
    return List<String>.from(response.data as List<dynamic>);
  }
}

final vmBuilderServiceProvider = Provider<VmBuilderService>((ref) {
  final dio = ref.read(dioProvider);
  return VmBuilderService(dio);
});
