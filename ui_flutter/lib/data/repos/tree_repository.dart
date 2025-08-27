import 'package:dio/dio.dart';
import '../api_client.dart';
import '../api_paths.dart';
import '../dto/children_upsert_dto.dart';
import '../dto/child_slot_dto.dart';
import '../dto/incomplete_parent_dto.dart';

class TreeRepository {
  final ApiClient _apiClient;

  TreeRepository(this._apiClient);

  /// Get all children of a parent node
  Future<List<ChildSlotDTO>> getChildren(int parentId) async {
    try {
      final response = await _apiClient.get(ApiPaths.treeChildren(parentId));
      final sc = response.statusCode ?? 0;
      if (sc == 204) return const <ChildSlotDTO>[];
      final body = response.data;
      if (body == null) return const <ChildSlotDTO>[];

      // Accept either a bare list or a wrapped object with 'children'
      List<dynamic> list;
      if (body is List) {
        list = body;
      } else if (body is Map && body['children'] is List) {
        list = body['children'] as List;
      } else if (body is Map && body['data'] is List) {
        // fallback if backend uses 'data'
        list = body['data'] as List;
      } else {
        // ignore: avoid_print
        print('[getChildren] Unexpected body shape: $body');
        return const <ChildSlotDTO>[];
      }
      return list
          .map((e) => Map<String, dynamic>.from(e as Map))
          .map(ChildSlotDTO.fromJson)
          .toList();
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
        ApiPaths.treeUpsertChildren(parentId),
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
      final response = await _apiClient.get(ApiPaths.treeNextIncomplete);
      final sc = response.statusCode ?? 0;
      if (sc == 204) return null;
      final body = response.data;
      if (body == null) return null;
      if (body is String && body.trim().isEmpty) return null;
      try {
        final map = Map<String, dynamic>.from(body as Map);
        return IncompleteParentDTO.fromJson(map);
      } catch (e, st) {
        // Fallback: manual tolerant parse if codegen disagrees
        // ignore: avoid_print
        print('[next-incomplete] parse error: $e\n$st\nbody=$body');
        try {
          final map = (body as Map).map((k, v) => MapEntry(k.toString(), v));
          final parentId = (map['parent_id'] ?? map['parentId']) as int;
          final slots = map['missing_slots'] ?? map['missingSlots'];
          List<int> missing;
          if (slots is List) {
            missing = slots.map((e) => e is int ? e : int.tryParse('$e') ?? 0).where((x) => x > 0).toList();
          } else if (slots is String) {
            missing = slots.split(',').map((s) => int.tryParse(s.trim()) ?? 0).where((x) => x > 0).toList();
          } else {
            missing = const <int>[];
          }
          return IncompleteParentDTO(parentId: parentId, missingSlots: missing);
        } catch (_) {
          rethrow;
        }
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return null; // No incomplete parents found
      }
      throw Exception('Network error: ${e.message}');
    }
  }
}
