import 'package:dio/dio.dart';
import '../api_client.dart';
import '../api_paths.dart';

class RedFlagDTO {
  final int id;
  final String name;
  final String? description;
  final String severity;

  RedFlagDTO({
    required this.id,
    required this.name,
    this.description,
    required this.severity,
  });

  factory RedFlagDTO.fromJson(Map<String, dynamic> json) {
    return RedFlagDTO(
      id: json['id'] as int,
      name: json['name'] as String,
      description: json['description'] as String?,
      severity: json['severity'] as String,
    );
  }
}

class RedFlagAssignmentDTO {
  final int nodeId;
  final String redFlagName;

  RedFlagAssignmentDTO({
    required this.nodeId,
    required this.redFlagName,
  });

  Map<String, dynamic> toJson() {
    return {
      'node_id': nodeId,
      'red_flag_name': redFlagName,
    };
  }
}

class FlagsRepository {
  final ApiClient _apiClient;

  FlagsRepository(this._apiClient);

  /// Search red flags by name
  Future<List<RedFlagDTO>> searchFlags(String query) async {
    try {
      final response = await _apiClient.get(
        ApiPaths.flagsSearch,
        queryParameters: {'q': query},
      );

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        final flagsList = data['flags'] as List;

        return flagsList.map((flag) => RedFlagDTO.fromJson(flag)).toList();
      }

      throw Exception('Failed to search flags: ${response.statusCode}');
    } on DioException catch (e) {
      if (e.response?.statusCode == 400) {
        throw Exception('Invalid search query: ${e.response?.data?['detail']}');
      }
      throw Exception('Network error: ${e.message}');
    }
  }

  /// Assign a red flag to a node
  Future<void> assignFlag(int nodeId, String redFlagName) async {
    try {
      final assignment = RedFlagAssignmentDTO(
        nodeId: nodeId,
        redFlagName: redFlagName,
      );

      final response = await _apiClient.post(
        ApiPaths.flagsAssign,
        data: assignment.toJson(),
      );

      if (response.statusCode == 200) {
        return; // Success
      }

      throw Exception('Failed to assign flag: ${response.statusCode}');
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw Exception(
            'Red flag or node not found: ${e.response?.data?['detail']}');
      }
      throw Exception('Network error: ${e.message}');
    }
  }
}
