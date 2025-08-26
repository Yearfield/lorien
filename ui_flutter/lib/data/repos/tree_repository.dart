import 'package:dio/dio.dart';
import '../api_client.dart';
import '../dto/children_upsert_dto.dart';
import '../dto/child_slot_dto.dart';
import '../dto/incomplete_parent_dto.dart';

class TreeRepository {
  final ApiClient _apiClient;

  TreeRepository(this._apiClient);

  /// Get all children of a parent node
  Future<List<ChildSlotDTO>> getChildren(int parentId) async {
    try {
      final response = await _apiClient.get('/api/v1/tree/$parentId/children');
      
      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        final childrenList = data['children'] as List;
        
        return childrenList
            .map((child) => ChildSlotDTO.fromJson(child))
            .toList();
      }
      
      throw Exception('Failed to get children: ${response.statusCode}');
    } on DioException catch (e) {
      throw Exception('Network error: ${e.message}');
    }
  }

  /// Upsert children for a parent node
  Future<Map<String, dynamic>> upsertChildren(
    int parentId,
    List<ChildSlotDTO> children,
  ) async {
    try {
      final dto = ChildrenUpsertDTO(children: children);
      final response = await _apiClient.post(
        '/api/v1/tree/$parentId/children',
        data: dto.toJson(),
      );
      
      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>;
      }
      
      throw Exception('Failed to upsert children: ${response.statusCode}');
    } on DioException catch (e) {
      if (e.response?.statusCode == 400) {
        throw Exception('Validation error: ${e.response?.data?['detail']}');
      } else if (e.response?.statusCode == 409) {
        throw Exception('Conflict: ${e.response?.data?['detail']}');
      }
      throw Exception('Network error: ${e.message}');
    }
  }

  /// Get the next incomplete parent
  Future<IncompleteParentDTO?> getNextIncompleteParent() async {
    try {
      final response = await _apiClient.get('/api/v1/tree/next-incomplete-parent');
      
      if (response.statusCode == 200) {
        return IncompleteParentDTO.fromJson(response.data);
      } else if (response.statusCode == 404) {
        return null; // No incomplete parents found
      }
      
      throw Exception('Failed to get next incomplete parent: ${response.statusCode}');
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return null; // No incomplete parents found
      }
      throw Exception('Network error: ${e.message}');
    }
  }
}
