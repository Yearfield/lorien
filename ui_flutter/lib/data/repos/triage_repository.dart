import 'package:dio/dio.dart';
import '../api_client.dart';
import '../api_paths.dart';
import '../dto/triage_dto.dart';

class TriageRepository {
  final ApiClient _apiClient;

  TriageRepository(this._apiClient);

  /// Get triage information for a node
  Future<TriageDTO?> getTriage(int nodeId) async {
    try {
      final response = await _apiClient.get(ApiPaths.triage(nodeId));

      if (response.statusCode == 200) {
        return TriageDTO.fromJson(response.data);
      } else if (response.statusCode == 404) {
        return null; // No triage found for this node
      }

      throw Exception('Failed to get triage: ${response.statusCode}');
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return null; // No triage found for this node
      }
      throw Exception('Network error: ${e.message}');
    }
  }

  /// Update triage information for a node
  Future<void> updateTriage(int nodeId, TriageDTO triage) async {
    try {
      final response = await _apiClient.put(
        ApiPaths.triage(nodeId),
        data: triage.toJson(),
      );

      if (response.statusCode == 200) {
        return; // Success
      }

      throw Exception('Failed to update triage: ${response.statusCode}');
    } on DioException catch (e) {
      if (e.response?.statusCode == 400) {
        throw Exception('Validation error: ${e.response?.data?['detail']}');
      } else if (e.response?.statusCode == 404) {
        throw Exception('Node not found');
      }
      throw Exception('Network error: ${e.message}');
    }
  }
}
