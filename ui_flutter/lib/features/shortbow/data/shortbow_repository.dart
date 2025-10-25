import 'dart:io';
import 'package:dio/dio.dart';

import '../../../core/api_config.dart';
import 'shortbow_models.dart';

class ShortBowRepository {
  final String baseUrl;
  final Dio _dio;

  ShortBowRepository({String? baseUrl})
      : baseUrl = baseUrl ?? ApiConfig.base,
        _dio = Dio() {
    _dio.options.baseUrl = baseUrl ?? ApiConfig.base;
    _dio.options.connectTimeout = const Duration(seconds: 30);
    _dio.options.receiveTimeout = const Duration(seconds: 30);
  }

  /// Import symptom matrix from Excel file
  Future<ShortBowImportResult> importMatrix(File file) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(file.path),
      });

      final response = await _dio.post('/api/v1/shortbow/import', data: formData);

      return ShortBowImportResult.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to import matrix: $e');
    }
  }

  /// Get list of available symptoms
  Future<List<ShortBowSymptom>> getSymptoms({
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final response = await _dio.get(
        '/api/v1/shortbow/symptoms',
        queryParameters: {
          'limit': limit,
          'offset': offset,
        },
      );

      return (response.data as List)
          .map((json) => ShortBowSymptom.fromJson(json))
          .toList();
    } catch (e) {
      throw Exception('Failed to get symptoms: $e');
    }
  }

  /// Navigate to get top linked symptoms
  Future<ShortBowNavigationResponse> navigateSymptoms(
    ShortBowNavigationRequest request,
  ) async {
    try {
      final response = await _dio.post(
        '/api/v1/shortbow/navigate',
        data: request.toJson(),
      );

      return ShortBowNavigationResponse.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to navigate symptoms: $e');
    }
  }

  /// Get top symptoms by average linkage
  Future<List<ShortBowSymptomLink>> getTopSymptoms({
    int limit = 6,
  }) async {
    try {
      final response = await _dio.get(
        '/api/v1/shortbow/top-symptoms',
        queryParameters: {
          'limit': limit,
        },
      );

      return (response.data as List)
          .map((json) => ShortBowSymptomLink.fromJson(json))
          .toList();
    } catch (e) {
      throw Exception('Failed to get top symptoms: $e');
    }
  }

  /// Get statistics
  Future<ShortBowStats> getStats() async {
    try {
      final response = await _dio.get('/api/v1/shortbow/stats/summary');
      return ShortBowStats.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to get stats: $e');
    }
  }

  /// Create a new calculation
  Future<ShortBowCalculation> createCalculation(
    ShortBowCalculationRequest request,
  ) async {
    try {
      final response = await _dio.post(
        '/api/v1/shortbow/calculations',
        data: request.toJson(),
      );

      return ShortBowCalculation.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to create calculation: $e');
    }
  }

  /// Get list of calculations
  Future<List<ShortBowCalculation>> getCalculations({
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final response = await _dio.get(
        '/api/v1/shortbow/calculations',
        queryParameters: {
          'limit': limit,
          'offset': offset,
        },
      );

      return (response.data as List)
          .map((json) => ShortBowCalculation.fromJson(json))
          .toList();
    } catch (e) {
      throw Exception('Failed to get calculations: $e');
    }
  }

  /// Get specific calculation
  Future<ShortBowCalculation> getCalculation(int id) async {
    try {
      final response = await _dio.get('/api/v1/shortbow/calculations/$id');
      return ShortBowCalculation.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to get calculation: $e');
    }
  }

  /// Save a calculation
  Future<void> saveCalculation(int id) async {
    try {
      await _dio.post('/api/v1/shortbow/calculations/$id/save');
    } catch (e) {
      throw Exception('Failed to save calculation: $e');
    }
  }

  /// Create a root node in the decision tree
  Future<Map<String, dynamic>> createRootNode(String label) async {
    try {
      final response = await _dio.post('/api/v1/tree/roots', data: {'label': label});
      return response.data;
    } catch (e) {
      throw Exception('Failed to create root node: $e');
    }
  }

  /// Add a child node to a parent in the decision tree
  Future<Map<String, dynamic>> addChildNode(int parentId, String label) async {
    try {
      final response = await _dio.post('/api/v1/tree/child', data: {
        'parent_id': parentId,
        'label': label,
      });
      return response.data;
    } catch (e) {
      throw Exception('Failed to add child node: $e');
    }
  }

  /// Create a hierarchical decision tree from symptom path
  Future<Map<String, dynamic>> createDecisionTree(List<String> symptoms) async {
    try {
      final response = await _dio.post('/api/v1/shortbow/create-decision-tree', data: symptoms);
      return response.data;
    } catch (e) {
      throw Exception('Failed to create decision tree: $e');
    }
  }
}
