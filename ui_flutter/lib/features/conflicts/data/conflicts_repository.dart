import 'package:dio/dio.dart';
import '../../../core/http/api_client.dart';

class ConflictsRepository {
  final Dio _dio;

  ConflictsRepository(this._dio);

  /// List conflicts with pagination and filtering
  Future<ConflictsPage> listConflicts({
    int limit = 25,
    int offset = 0,
    bool onlyExactFive = true,
    bool onlyDuplicateParents = true,
    bool requireVariantSets = true,
  }) async {
    try {
      final response = await _dio.get(
        '/tree/conflicts/conflicts',
        queryParameters: {
          'limit': limit,
          'offset': offset,
          'only_exact_five': onlyExactFive,
          'only_duplicate_parents': onlyDuplicateParents,
          'require_variant_sets': requireVariantSets,
        },
      );
      
      return ConflictsPage.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw _handleDioException(e);
    }
  }

  /// Load a conflict group by node ID
  Future<GroupPayload> loadGroup(int nodeId) async {
    try {
      final response = await _dio.get(
        '/tree/conflicts/group',
        queryParameters: {'node_id': nodeId},
      );
      
      return GroupPayload.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw _handleDioException(e);
    }
  }

  /// Resolve a conflict group by choosing exactly 5 labels
  Future<void> resolveGroup({
    required int keepId,
    required List<String> chosen,
  }) async {
    if (chosen.length != 5) {
      throw ValidationException('must_choose_five', 'Choose exactly 5 labels.');
    }
    
    if (chosen.toSet().length != chosen.length) {
      throw ValidationException('duplicate_labels', 'Labels must be unique.');
    }

    try {
      await _dio.post(
        '/tree/conflicts/group/resolve',
        data: {
          'keep_id': keepId,
          'chosen': chosen,
        },
      );
    } on DioException catch (e) {
      throw _handleDioException(e);
    }
  }

  /// Handle Dio exceptions and map to appropriate error types
  Exception _handleDioException(DioException e) {
    switch (e.response?.statusCode) {
      case 422:
        final data = e.response?.data as Map<String, dynamic>?;
        final details = data?['detail'] as List<dynamic>?;
        if (details != null && details.isNotEmpty) {
          final error = details.first as Map<String, dynamic>;
          final type = error['type'] as String?;
          final message = error['msg'] as String?;
          
          switch (type) {
            case 'value_error.must_choose_five':
              return ValidationException('must_choose_five', message ?? 'Choose exactly 5 labels.');
            case 'value_error.duplicate_labels':
              return ValidationException('duplicate_labels', message ?? 'Labels must be unique.');
            case 'value_error.keep_id':
              return ValidationException('keep_id', message ?? 'Invalid keeper for this group.');
            default:
              return ValidationException('validation_error', message ?? 'Validation error.');
          }
        }
        return ValidationException('validation_error', 'Validation error.');
      case 409:
        return ConflictException('Conflict on save. Reload latest?');
      default:
        return NetworkException('Network error: ${e.message}');
    }
  }
}

/// Data models for conflicts
class ConflictsPage {
  final List<ConflictItem> items;
  final int total;
  final int limit;
  final int offset;

  ConflictsPage({
    required this.items,
    required this.total,
    required this.limit,
    required this.offset,
  });

  factory ConflictsPage.fromJson(Map<String, dynamic> json) {
    return ConflictsPage(
      items: (json['items'] as List<dynamic>? ?? [])
          .map((item) => ConflictItem.fromJson(item as Map<String, dynamic>))
          .toList(),
      total: ConflictItem._asInt(json['total']),
      limit: ConflictItem._asInt(json['limit']),
      offset: ConflictItem._asInt(json['offset']),
    );
  }
}

class ConflictItem {
  final int parentId;
  final String label;
  final int depth;
  final int childCount;
  final int slotDupCount;
  final int nullSlotCount;
  final bool overfilled;
  final bool underfilled;
  final int duplicateParents;
  final int variantSets;

  ConflictItem({
    required this.parentId,
    required this.label,
    required this.depth,
    required this.childCount,
    required this.slotDupCount,
    required this.nullSlotCount,
    required this.overfilled,
    required this.underfilled,
    required this.duplicateParents,
    required this.variantSets,
  });

  factory ConflictItem.fromJson(Map<String, dynamic> json) {
    return ConflictItem(
      parentId: _asInt(json['parent_id']),
      label: json['label'] as String? ?? '',
      depth: _asInt(json['depth']),
      childCount: _asInt(json['child_count']),
      slotDupCount: _asInt(json['slot_dup_count']),
      nullSlotCount: _asInt(json['null_slot_count']),
      overfilled: json['overfilled'] as bool? ?? false,
      underfilled: json['underfilled'] as bool? ?? false,
      duplicateParents: _asInt(json['duplicate_parents']),
      variantSets: _asInt(json['variant_sets']),
    );
  }

  static int _asInt(dynamic value) {
    if (value is int) return value;
    if (value is String) return int.tryParse(value) ?? 0;
    return 0; // coalesce null/other
  }
}

class GroupPayload {
  final List<GroupItem> group;
  final List<ChildItem> children;
  final GroupSummary summary;

  GroupPayload({
    required this.group,
    required this.children,
    required this.summary,
  });

  factory GroupPayload.fromJson(Map<String, dynamic> json) {
    return GroupPayload(
      group: (json['group'] as List<dynamic>)
          .map((item) => GroupItem.fromJson(item as Map<String, dynamic>))
          .toList(),
      children: (json['children'] as List<dynamic>)
          .map((item) => ChildItem.fromJson(item as Map<String, dynamic>))
          .toList(),
      summary: GroupSummary.fromJson(json['summary'] as Map<String, dynamic>),
    );
  }
}

class GroupItem {
  final int id;

  GroupItem({required this.id});

  factory GroupItem.fromJson(Map<String, dynamic> json) {
    return GroupItem(id: ConflictItem._asInt(json['id']));
  }
}

class ChildItem {
  final int childId;
  final int fromId;
  final int slot;
  final String label;

  ChildItem({
    required this.childId,
    required this.fromId,
    required this.slot,
    required this.label,
  });

  factory ChildItem.fromJson(Map<String, dynamic> json) {
    return ChildItem(
      childId: ConflictItem._asInt(json['child_id']),
      fromId: ConflictItem._asInt(json['from_id']),
      slot: ConflictItem._asInt(json['slot']),
      label: json['label'] as String? ?? '',
    );
  }
}

class GroupSummary {
  final int uniqueChildren;
  final int totalChildren;

  GroupSummary({
    required this.uniqueChildren,
    required this.totalChildren,
  });

  factory GroupSummary.fromJson(Map<String, dynamic> json) {
    return GroupSummary(
      uniqueChildren: ConflictItem._asInt(json['unique_children']),
      totalChildren: ConflictItem._asInt(json['total_children']),
    );
  }
}

/// Custom exceptions for conflicts
class ValidationException implements Exception {
  final String type;
  final String message;

  ValidationException(this.type, this.message);

  @override
  String toString() => 'ValidationException($type): $message';
}

class ConflictException implements Exception {
  final String message;

  ConflictException(this.message);

  @override
  String toString() => 'ConflictException: $message';
}

class NetworkException implements Exception {
  final String message;

  NetworkException(this.message);

  @override
  String toString() => 'NetworkException: $message';
}
