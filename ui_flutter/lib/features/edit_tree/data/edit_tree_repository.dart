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
      "query": query,
      "limit": limit,
      "offset": offset,
    };
    if (depth != null) params["depth"] = depth;

    final response = await dio.get(
      '$baseUrl/tree/parents/incomplete',
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

  Future<List<Map<String, dynamic>>> getChildren(int parentId) async {
    final response = await dio.get('$baseUrl/tree/$parentId/children');
    return List<Map<String, dynamic>>.from(response.data as List);
  }

  Future<BulkUpsertResult> upsertChildren(
    int parentId,
    List<SlotPatch> patches,
  ) async {
    final response = await dio.put(
      '$baseUrl/tree/parents/$parentId/children',
      data: {"slots": patches.map((e) => e.toJson()).toList(), "mode": "upsert"},
      options: Options(validateStatus: (_) => true),
    );

    if (response.statusCode == 200) {
      return BulkUpsertResult.fromJson(response.data);
    }
    if (response.statusCode == 409) {
      throw DioException(
        requestOptions: response.requestOptions,
        response: response,
        error: "slot_conflict",
      );
    }
    if (response.statusCode == 422) {
      throw DioException(
        requestOptions: response.requestOptions,
        response: response,
        error: "validation",
      );
    }
    throw DioException(
      requestOptions: response.requestOptions,
      response: response,
      error: "unexpected",
    );
  }
}
