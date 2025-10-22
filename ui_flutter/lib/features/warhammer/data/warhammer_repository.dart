import 'dart:io';

import 'package:dio/dio.dart';

import '../../../core/api_config.dart';
import 'warhammer_models.dart';

class WarhammerRepository {
  final Dio _dio;

  WarhammerRepository({Dio? dio}) : _dio = dio ?? Dio();

  /// Get list of available symptoms
  Future<List<Symptom>> getSymptoms({
    int limit = 100,
    int offset = 0,
    String? search,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
      };

      if (search != null && search.isNotEmpty) {
        queryParams['search'] = search;
      }

      final response = await _dio.get(
        '${ApiConfig.base}/warhammer/symptoms',
        queryParameters: queryParams,
      );

      final List<dynamic> data = response.data;
      return data.map((json) => Symptom.fromJson(json)).toList();
    } catch (e) {
      throw Exception('Failed to fetch symptoms: $e');
    }
  }

  /// Get list of available diseases
  Future<List<Disease>> getDiseases({
    int limit = 100,
    int offset = 0,
    String? search,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
      };

      if (search != null && search.isNotEmpty) {
        queryParams['search'] = search;
      }

      final response = await _dio.get(
        '${ApiConfig.base}/warhammer/diseases',
        queryParameters: queryParams,
      );

      final List<dynamic> data = response.data;
      return data.map((json) => Disease.fromJson(json)).toList();
    } catch (e) {
      throw Exception('Failed to fetch diseases: $e');
    }
  }

  /// Calculate disease probabilities based on symptoms
  Future<CalculationResponse> calculateDiseaseProbabilities(
    List<String> symptoms,
  ) async {
    try {
      final request = CalculationRequest(symptoms: symptoms);

      final response = await _dio.post(
        '${ApiConfig.base}/warhammer/calculate',
        data: request.toJson(),
      );

      // Adapt snake_case API to camelCase model keys and provide safe defaults
      final raw = Map<String, dynamic>.from(response.data as Map);
      final mapped = <String, dynamic>{
        'calculationId': raw['calculation_id'],
        'inputSymptoms': (raw['input_symptoms'] as List?)?.cast<String>() ?? <String>[],
        'results': (raw['results'] as List? ?? <dynamic>[]) as List,
        'timestamp': raw['timestamp'] ?? '',
        'errors': (raw['errors'] as List? ?? <dynamic>[]) as List,
      };

      return CalculationResponse.fromJson(mapped);
    } catch (e) {
      throw Exception('Failed to calculate disease probabilities: $e');
    }
  }

  /// Calculate disease probabilities and return raw payload (includes explanations)
  Future<Map<String, dynamic>> calculateDiseaseProbabilitiesRaw(
    List<String> symptoms,
  ) async {
    try {
      final request = CalculationRequest(symptoms: symptoms);
      final response = await _dio.post(
        '${ApiConfig.base}/warhammer/calculate',
        data: request.toJson(),
      );
      return Map<String, dynamic>.from(response.data as Map);
    } catch (e) {
      throw Exception('Failed to calculate disease probabilities (raw): $e');
    }
  }

  /// Save a calculation result
  Future<void> saveCalculation(int calculationId) async {
    try {
      await _dio.post(
        '${ApiConfig.base}/warhammer/calculations/$calculationId/save',
      );
    } catch (e) {
      throw Exception('Failed to save calculation: $e');
    }
  }

  /// Get list of saved calculations
  Future<List<SavedCalculation>> getSavedCalculations({
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
      };

      final response = await _dio.get(
        '${ApiConfig.base}/warhammer/calculations',
        queryParameters: queryParams,
      );

      final List<dynamic> data = response.data;
      return data.map((json) => SavedCalculation.fromJson(json)).toList();
    } catch (e) {
      throw Exception('Failed to fetch saved calculations: $e');
    }
  }

  /// Get a specific saved calculation
  Future<SavedCalculation> getSavedCalculation(int calculationId) async {
    try {
      final response = await _dio.get(
        '${ApiConfig.base}/warhammer/calculations/$calculationId',
      );

      return SavedCalculation.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to fetch calculation: $e');
    }
  }

  /// Import disease data from CSV/XLSX file
  Future<ImportResultResponse> importDiseases(File file) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          file.path,
          filename: file.path.split('/').last,
        ),
      });

      final response = await _dio.post(
        '${ApiConfig.base}/warhammer/import/diseases',
        data: formData,
        options: Options(
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        ),
      );

      return ImportResultResponse.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to import diseases: $e');
    }
  }

  /// Import symptom data from CSV/XLSX file
  Future<ImportResultResponse> importSymptoms(File file) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          file.path,
          filename: file.path.split('/').last,
        ),
      });

      final response = await _dio.post(
        '${ApiConfig.base}/warhammer/import/symptoms',
        data: formData,
        options: Options(
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        ),
      );

      return ImportResultResponse.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to import symptoms: $e');
    }
  }

  /// Import conditional probability data from CSV/XLSX file
  Future<ImportResultResponse> importConditionals(File file) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          file.path,
          filename: file.path.split('/').last,
        ),
      });

      final response = await _dio.post(
        '${ApiConfig.base}/warhammer/import/conditionals',
        data: formData,
        options: Options(
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        ),
      );

      return ImportResultResponse.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to import conditionals: $e');
    }
  }

  /// Get Warhammer statistics
  Future<WarhammerStats> getStats() async {
    try {
      final response = await _dio.get(
        '${ApiConfig.base}/warhammer/stats/summary',
      );

      return WarhammerStats.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to fetch Warhammer stats: $e');
    }
  }

  /// Get symptom comparison between decision tree and Warhammer database
  Future<SymptomComparison> getSymptomComparison() async {
    try {
      final response = await _dio.get(
        '${ApiConfig.base}/warhammer/symptoms/comparison',
      );

      return SymptomComparison.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to fetch symptom comparison: $e');
    }
  }

  /// Get all symptom synonym mappings
  Future<List<SymptomSynonym>> getSynonyms() async {
    try {
      final response = await _dio.get(
        '${ApiConfig.base}/warhammer/synonyms',
      );

      final List<dynamic> data = response.data;
      return data.map((json) => SymptomSynonym.fromJson(json)).toList();
    } catch (e) {
      throw Exception('Failed to fetch synonyms: $e');
    }
  }

  /// Create a new symptom synonym mapping
  Future<SymptomSynonym> createSynonym(CreateSynonymRequest request) async {
    try {
      final response = await _dio.post(
        '${ApiConfig.base}/warhammer/synonyms',
        data: request.toJson(),
      );

      return SymptomSynonym.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to create synonym: $e');
    }
  }

  /// Delete a symptom synonym mapping
  Future<void> deleteSynonym(int synonymId) async {
    try {
      await _dio.delete(
        '${ApiConfig.base}/warhammer/synonyms/$synonymId',
      );
    } catch (e) {
      throw Exception('Failed to delete synonym: $e');
    }
  }
}
