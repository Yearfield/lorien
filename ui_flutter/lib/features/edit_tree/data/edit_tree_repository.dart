import 'package:dio/dio.dart';

class IncompleteParent {
  final int parentId;
  final String label;
  final int depth;
  final String missingSlots;

  IncompleteParent(this.parentId, this.label, this.depth, this.missingSlots);

  factory IncompleteParent.fromJson(Map<String, dynamic> json) {
    return IncompleteParent(
      json['parent_id'],
      json['label'],
      json['depth'],
      json['missing_slots'] ?? "",
    );
  }
}

class IncompleteParentsPage {
  final List<IncompleteParent> items;
  final int total;
  final int limit;
  final int offset;

  IncompleteParentsPage(this.items, this.total, this.limit, this.offset);

  factory IncompleteParentsPage.fromJson(Map<String, dynamic> json) {
    final items = (json['items'] as List)
        .map((e) => IncompleteParent.fromJson(e))
        .toList();
    return IncompleteParentsPage(
      items,
      json['total'],
      json['limit'],
      json['offset'],
    );
  }
}

class ChildInfo {
  final int id;
  final String label;
  final int slot;
  final int depth;
  final bool isLeaf;

  ChildInfo(this.id, this.label, this.slot, this.depth, this.isLeaf);

  factory ChildInfo.fromJson(Map<String, dynamic> json) {
    return ChildInfo(
      json['id'],
      json['label'],
      json['slot'],
      json['depth'],
      json['is_leaf'] == 1,
    );
  }
}

class ParentChildrenData {
  final int parentId;
  final int version;
  final List<int> missingSlots;
  final List<ChildInfo> children;
  final Map<String, dynamic> path;
  final String etag;

  ParentChildrenData(
    this.parentId,
    this.version,
    this.missingSlots,
    this.children,
    this.path,
    this.etag,
  );

  factory ParentChildrenData.fromJson(Map<String, dynamic> json) {
    final children = (json['children'] as List)
        .map((e) => ChildInfo.fromJson(e))
        .toList();

    return ParentChildrenData(
      json['parent_id'],
      json['version'],
      List<int>.from((json['missing_slots'] as String).split(',').where((s) => s.isNotEmpty).map(int.parse)),
      children,
      json['path'],
      json['etag'],
    );
  }
}

class SlotPatch {
  final int slot;
  String label;

  SlotPatch(this.slot, this.label);

  Map<String, dynamic> toJson() => {"slot": slot, "label": label};
}

class BulkUpsertResult {
  final List<Map<String, dynamic>> updated;
  final String missingSlots;

  BulkUpsertResult(this.updated, this.missingSlots);

  factory BulkUpsertResult.fromJson(Map<String, dynamic> json) {
    return BulkUpsertResult(
      List<Map<String, dynamic>>.from(json['updated'] ?? []),
      json['missing_slots'] ?? "",
    );
  }
}

class EditTreeRepository {
  final Dio dio;
  final String baseUrl;

  EditTreeRepository(this.dio, this.baseUrl);

  Future<IncompleteParentsPage> listIncomplete({
    String query = "",
    int? depth,
    int limit = 50,
    int offset = 0,
  }) async {
    final params = <String, dynamic>{
      "q": query,
      "limit": limit,
      "offset": offset,
    };
    if (depth != null) params["depth"] = depth;

    final response = await dio.get(
      '$baseUrl/tree/missing-slots',
      queryParameters: params,
    );
    return IncompleteParentsPage.fromJson(response.data);
  }

  Future<Map<String, dynamic>?> nextIncomplete() async {
    final response = await dio.get(
      '$baseUrl/tree/next-incomplete-parent',
      options: Options(validateStatus: (_) => true),
    );
    if (response.statusCode == 204) return null;
    return response.data as Map<String, dynamic>;
  }

  Future<ParentChildrenData> getParentChildren(int parentId) async {
    final response = await dio.get('$baseUrl/tree/parent/$parentId/children');
    return ParentChildrenData.fromJson(response.data);
  }

  Future<Map<String, dynamic>> updateParentChildren(
    int parentId,
    Map<String, dynamic> body, {
    String? etag
  }) async {
    final options = etag != null
        ? Options(headers: {'If-Match': etag})
        : null;

    final response = await dio.put(
      '$baseUrl/tree/parent/$parentId/children',
      data: body,
      options: options,
    );

    return response.data;
  }
}
