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
  final bool cascade;

  RedFlagAssignmentDTO({
    required this.nodeId,
    required this.redFlagName,
    this.cascade = false,
  });

  Map<String, dynamic> toJson() {
    return {
      'node_id': nodeId,
      'red_flag_name': redFlagName,
      'cascade': cascade,
    };
  }
}

class FlagsPage {
  final List<FlagItem> items;
  final int total;
  final int limit;
  final int offset;

  FlagsPage({
    required this.items,
    required this.total,
    required this.limit,
    required this.offset,
  });

  factory FlagsPage.fromJson(Map<String, dynamic> json) {
    return FlagsPage(
      items: (json['items'] as List)
          .map((item) => FlagItem.fromJson(item))
          .toList(),
      total: json['total'] as int,
      limit: json['limit'] as int,
      offset: json['offset'] as int,
    );
  }
}

class FlagItem {
  final int id;
  final String label;

  FlagItem({
    required this.id,
    required this.label,
  });

  factory FlagItem.fromJson(Map<String, dynamic> json) {
    return FlagItem(
      id: json['id'] as int,
      label: json['label'] as String,
    );
  }
}

class FlagAssignmentResponse {
  final int affected;
  final List<int> nodeIds;

  FlagAssignmentResponse({
    required this.affected,
    required this.nodeIds,
  });

  factory FlagAssignmentResponse.fromJson(Map<String, dynamic> json) {
    return FlagAssignmentResponse(
      affected: json['affected'] as int,
      nodeIds: (json['node_ids'] as List).cast<int>(),
    );
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

  /// List flags with paging
  Future<FlagsPage> listFlags({
    String query = '',
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.get(
        ApiPaths.flags,
        queryParameters: {
          'query': query,
          'limit': limit,
          'offset': offset,
        },
      );

      if (response.statusCode == 200) {
        return FlagsPage.fromJson(response.data);
      }

      throw Exception('Failed to list flags: ${response.statusCode}');
    } on DioException catch (e) {
      throw Exception('Network error: ${e.message}');
    }
  }

  /// Assign a red flag to a node with cascade support
  Future<FlagAssignmentResponse> assignFlag(
    int nodeId,
    String redFlagName, {
    bool cascade = false,
  }) async {
    try {
      final assignment = RedFlagAssignmentDTO(
        nodeId: nodeId,
        redFlagName: redFlagName,
        cascade: cascade,
      );

      final response = await _apiClient.post(
        ApiPaths.flagsAssign,
        data: assignment.toJson(),
      );

      if (response.statusCode == 200) {
        return FlagAssignmentResponse.fromJson(response.data);
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
