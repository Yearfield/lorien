import 'package:lorien/features/edit_tree/data/edit_tree_repository.dart';
import 'package:lorien/data/dto/child_slot_dto.dart';

class EditTreeRepositoryStub extends EditTreeRepository {
  EditTreeRepositoryStub(super.api);

  @override
  Future<IncompleteParentsPage> listIncomplete({
    String query = "",
    int? depth,
    int limit = 50,
    int offset = 0,
  }) async {
    return IncompleteParentsPage([
      IncompleteParent(1, 'Test Parent 1', 1, '1,2,3'),
      IncompleteParent(2, 'Test Parent 2', 1, '2,4,5'),
      IncompleteParent(3, 'Complete Parent', 1, ''),
    ], 3, 50, 0);
  }

  @override
  Future<Map<String, dynamic>?> nextIncomplete() async {
    return {
      'parent_id': 2,
      'label': 'Test Parent 2',
      'depth': 1,
      'missing_slots': '2,4,5',
    };
  }

  @override
  Future<ParentChildrenData> getParentChildren(int parentId) async {
    return ParentChildrenData(
      parentId,
      7,
      [2, 5],
      [
        ChildInfo(101, 'Label 1', 1, 1, false),
        ChildInfo(102, '', 2, 1, false),
        ChildInfo(103, 'Label 3', 3, 1, false),
        ChildInfo(104, 'Label 4', 4, 1, false),
        ChildInfo(105, '', 5, 1, false),
      ],
      {'vitalMeasurement': 'Test VM', 'nodes': ['', '', '', '', '']},
      'etag-123',
    );
  }

  @override
  Future<Map<String, dynamic>> updateParentChildren(
    int parentId,
    List<ChildSlotDTO> slots, {
    int? version,
    String? etag,
  }) async {
    return {
      'parent_id': parentId,
      'version': (version ?? 7) + 1,
      'missing_slots': '',
      'updated': [1, 2, 3, 4, 5],
    };
  }
}

class BulkUpsertResultStub {
  static BulkUpsertResult create() {
    return BulkUpsertResult(
      [
        {'slot': 1, 'id': 1001},
        {'slot': 2, 'id': 1002},
        {'slot': 3, 'id': 1003},
        {'slot': 4, 'id': 1004},
        {'slot': 5, 'id': 1005},
      ],
      '',
    );
  }
}
