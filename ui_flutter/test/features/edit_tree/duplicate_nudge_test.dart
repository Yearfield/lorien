import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import '../../../lib/features/edit_tree/state/edit_tree_controller.dart';
import '../../../lib/features/edit_tree/state/edit_tree_state.dart';
import '../../../lib/features/edit_tree/data/edit_tree_repository.dart';

class MockBulkUpsertResult extends BulkUpsertResult {
  MockBulkUpsertResult() : super([], '');
}

class MockRepo implements EditTreeRepository {
  MockRepo() : super();

  @override
  Dio get dio => throw UnimplementedError();

  @override
  String get baseUrl => '';

  @override
  Future<List<Map<String, dynamic>>> getChildren(int parentId) async {
    return [];
  }

  @override
  Future<IncompleteParentsPage> listIncomplete({
    String query = "",
    int? depth,
    int limit = 50,
    int offset = 0,
  }) async {
    throw UnimplementedError();
  }

  @override
  Future<Map<String, dynamic>?> nextIncomplete() async {
    throw UnimplementedError();
  }

  @override
  Future<BulkUpsertResult> upsertChildren(int parentId, List<dynamic> patches) async {
    // Mock successful response
    return MockBulkUpsertResult();
  }
}

void main() {
  late EditTreeController controller;
  late MockRepo mockRepo;

  setUp(() {
    mockRepo = MockRepo();
    controller = EditTreeController(mockRepo);
  });

  test('should show duplicate warning when two slots have same label', () {
    // Start with initial state
    expect(controller.state.slots.length, 5);

    // Set slot 1 to "Test Label"
    controller.putSlot(1, "Test Label");
    expect(controller.state.slots[0].warning, isNull); // No warning yet

    // Set slot 2 to same label
    controller.putSlot(2, "Test Label");

    // Should now show warnings on both slots
    expect(controller.state.slots[0].warning, contains('Duplicate label'));
    expect(controller.state.slots[1].warning, contains('Duplicate label'));
  });

  test('should clear duplicate warning when labels become unique', () {
    // Set up duplicates first
    controller.putSlot(1, "Test Label");
    controller.putSlot(2, "Test Label");

    // Verify warnings are present
    expect(controller.state.slots[0].warning, contains('Duplicate'));
    expect(controller.state.slots[1].warning, contains('Duplicate'));

    // Change one label to be unique
    controller.putSlot(2, "Different Label");

    // Should clear warnings
    expect(controller.state.slots[0].warning, isNull);
    expect(controller.state.slots[1].warning, isNull);
  });

  test('should handle case insensitive duplicate detection', () {
    controller.putSlot(1, "Test Label");
    controller.putSlot(2, "test label");

    // Should detect as duplicates despite case difference
    expect(controller.state.slots[0].warning, contains('Duplicate'));
    expect(controller.state.slots[1].warning, contains('Duplicate'));
  });

  test('should handle trimmed whitespace in duplicate detection', () {
    controller.putSlot(1, "Test Label");
    controller.putSlot(2, "  Test Label  ");

    // Should detect as duplicates despite whitespace
    expect(controller.state.slots[0].warning, contains('Duplicate'));
    expect(controller.state.slots[1].warning, contains('Duplicate'));
  });

  test('should not show warnings for empty labels', () {
    controller.putSlot(1, "");
    controller.putSlot(2, "");

    // Empty labels should not trigger warnings
    expect(controller.state.slots[0].warning, isNull);
    expect(controller.state.slots[1].warning, isNull);
  });

  test('should show warnings for multiple duplicates', () {
    controller.putSlot(1, "Same Label");
    controller.putSlot(2, "Same Label");
    controller.putSlot(3, "Same Label");

    // All three should show warnings
    expect(controller.state.slots[0].warning, contains('Duplicate'));
    expect(controller.state.slots[1].warning, contains('Duplicate'));
    expect(controller.state.slots[2].warning, contains('Duplicate'));
  });
}
