import 'package:dio/dio.dart';
import '../api_client.dart';
import '../api_paths.dart';
import '../dto/triage_dto.dart';

class OutcomesRepository {
  final ApiClient _apiClient;

  OutcomesRepository(this._apiClient);

  /// Get outcomes (triage) information for a node with fallback
  Future<TriageDTO?> getOutcomes(int nodeId) async {
    try {
      // Try /outcomes first
      final response = await _apiClient.get(ApiPaths.outcomes(nodeId));

      if (response.statusCode == 200) {
        return TriageDTO.fromJson(response.data);
      } else if (response.statusCode == 404) {
        return null; // No outcomes found for this node
      }

      throw Exception('Failed to get outcomes: ${response.statusCode}');
    } on DioException catch (e) {
      if (e.response?.statusCode == 404 || e.response?.statusCode == 405) {
        // Fallback to triage endpoint
        try {
          final response = await _apiClient.get(ApiPaths.triage(nodeId));

          if (response.statusCode == 200) {
            return TriageDTO.fromJson(response.data);
          } else if (response.statusCode == 404) {
            return null; // No triage found for this node
          }

          throw Exception(
              'Failed to get triage fallback: ${response.statusCode}');
        } on DioException catch (fallbackE) {
          if (fallbackE.response?.statusCode == 404) {
            return null; // No triage found for this node
          }
          throw Exception('Network error in fallback: ${fallbackE.message}');
        }
      }
      throw Exception('Network error: ${e.message}');
    }
  }

  /// Update outcomes (triage) information for a node with fallback
  Future<void> updateOutcomes(int nodeId, TriageDTO outcomes) async {
    try {
      // Try /outcomes first
      final response = await _apiClient.put(
        ApiPaths.outcomes(nodeId),
        data: outcomes.toJson(),
      );

      if (response.statusCode == 200) {
        return; // Success
      }

      throw Exception('Failed to update outcomes: ${response.statusCode}');
    } on DioException catch (e) {
      if (e.response?.statusCode == 404 || e.response?.statusCode == 405) {
        // Fallback to triage endpoint
        try {
          final response = await _apiClient.put(
            ApiPaths.triage(nodeId),
            data: outcomes.toJson(),
          );

          if (response.statusCode == 200) {
            return; // Success
          }

          throw Exception(
              'Failed to update triage fallback: ${response.statusCode}');
        } on DioException catch (fallbackE) {
          if (fallbackE.response?.statusCode == 400) {
            throw Exception(
                'Validation error: ${fallbackE.response?.data?['detail']}');
          } else if (fallbackE.response?.statusCode == 404) {
            throw Exception('Node not found');
          }
          throw Exception('Network error in fallback: ${fallbackE.message}');
        }
      } else if (e.response?.statusCode == 400) {
        throw Exception('Validation error: ${e.response?.data?['detail']}');
      } else if (e.response?.statusCode == 404) {
        throw Exception('Node not found');
      }
      throw Exception('Network error: ${e.message}');
    }
  }
}
