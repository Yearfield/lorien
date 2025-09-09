import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:lorien/features/edit_tree/state/edit_tree_controller.dart';
import 'package:lorien/features/edit_tree/state/edit_tree_state.dart';
import 'package:lorien/features/edit_tree/data/edit_tree_repository.dart';

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
    return [
      {'slot': 1, 'label': 'Server Label 1', 'id': 1},
      {'slot': 2, 'label': 'Server Label 2', 'id': 2},
      {'slot': 3, 'label': '', 'id': null},
      {'slot': 4, 'label': '', 'id': null},
      {'slot': 5, 'label': '', 'id': null},
    ];
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
  Future<BulkUpsertResult> upsertChildren(
      int parentId, List<dynamic> patches) async {
    // Mock successful response by default
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

  test('should show conflict banner on 409 response and preserve input',
      () async {
    // Load a parent first
    await controller.loadParent(1, label: 'Test Parent', depth: 1, missing: '');

    // Modify a slot
    controller.putSlot(1, 'User Changed Label');

    // Mock a 409 conflict response
    final mockRepo409 = MockRepo409();
    final controller409 = EditTreeController(mockRepo409);

    // Load same parent in new controller
    await controller409.loadParent(1,
        label: 'Test Parent', depth: 1, missing: '');
    controller409.putSlot(1, 'User Changed Label');

    // Attempt save - should get 409
    await controller409.save();

    // Verify banner is shown
    expect(controller409.state.banner, isNotNull);
    expect(controller409.state.banner!.message,
        contains('Concurrent changes detected'));
    expect(controller409.state.banner!.actionLabel, 'Reload Latest');

    // Verify user input is preserved
    expect(controller409.state.slots[0].text, 'User Changed Label');
  });

  test('should reload latest data when banner action is triggered', () async {
    // Load a parent
    await controller.loadParent(1, label: 'Test Parent', depth: 1, missing: '');

    // Modify a slot
    controller.putSlot(1, 'User Changed Label');

    // Set up a conflict banner
    final banner = EditBanner.conflict(action: () => controller.reloadLatest());
    controller.state = controller.state.copyWith(banner: banner);

    // Trigger reload
    controller.state.banner!.action!();

    // Verify banner is cleared after reload
    expect(controller.state.banner, isNull);

    // Verify fresh server data is loaded
    expect(controller.state.slots[0].text, 'Server Label 1');
    expect(controller.state.slots[0].existing, true);
  });

  test('should handle 422 validation errors with specific slot mapping',
      () async {
    // Mock a 422 response
    final mockRepo422 = MockRepo422();
    final controller422 = EditTreeController(mockRepo422);

    // Load parent
    await controller422.loadParent(1,
        label: 'Test Parent', depth: 1, missing: '');

    // Attempt save - should get 422
    await controller422.save();

    // Verify banner is shown
    expect(controller422.state.banner, isNotNull);
    expect(controller422.state.banner!.message,
        contains('Validation errors found'));
    expect(controller422.state.banner!.actionLabel, 'Dismiss');

    // Verify specific slot error is mapped
    expect(controller422.state.slots[0].error, contains('Invalid label'));
  });

  test('should dismiss 422 banner when action is triggered', () async {
    // Load parent
    await controller.loadParent(1, label: 'Test Parent', depth: 1, missing: '');

    // Set up a 422 banner
    final banner = EditBanner(
      message: 'Validation errors found. Please fix the highlighted fields.',
      actionLabel: 'Dismiss',
      action: () => controller.state = controller.state.copyWith(banner: null),
    );
    controller.state = controller.state.copyWith(banner: banner);

    // Trigger dismiss
    controller.state.banner!.action!();

    // Verify banner is cleared
    expect(controller.state.banner, isNull);
  });

  test('should handle reload failure gracefully', () async {
    // Mock a failing repo
    final mockRepoFail = MockRepoFail();
    final controllerFail = EditTreeController(mockRepoFail);

    // Load parent
    await controllerFail.loadParent(1,
        label: 'Test Parent', depth: 1, missing: '');

    // Set up conflict banner
    final banner =
        EditBanner.conflict(action: () => controllerFail.reloadLatest());
    controllerFail.state = controllerFail.state.copyWith(banner: banner);

    // Trigger reload - should fail
    controllerFail.state.banner!.action!();

    // Verify error banner is shown
    expect(controllerFail.state.banner, isNotNull);
    expect(controllerFail.state.banner!.message, contains('Failed to reload'));
    expect(controllerFail.state.banner!.actionLabel, 'Retry');
  });
}

// Mock repos for different error scenarios
class MockRepo409 implements EditTreeRepository {
  @override
  Dio get dio => throw UnimplementedError();

  @override
  String get baseUrl => '';

  @override
  Future<List<Map<String, dynamic>>> getChildren(int parentId) async => [];

  @override
  Future<IncompleteParentsPage> listIncomplete({
    String query = "",
    int? depth,
    int limit = 50,
    int offset = 0,
  }) async =>
      throw UnimplementedError();

  @override
  Future<Map<String, dynamic>?> nextIncomplete() async =>
      throw UnimplementedError();

  @override
  Future<BulkUpsertResult> upsertChildren(
      int parentId, List<dynamic> patches) async {
    throw DioException(
      requestOptions: RequestOptions(path: ''),
      response: Response(
        requestOptions: RequestOptions(path: ''),
        statusCode: 409,
        data: {'slot': 1},
      ),
    );
  }
}

class MockRepo422 implements EditTreeRepository {
  @override
  Dio get dio => throw UnimplementedError();

  @override
  String get baseUrl => '';

  @override
  Future<List<Map<String, dynamic>>> getChildren(int parentId) async => [];

  @override
  Future<IncompleteParentsPage> listIncomplete({
    String query = "",
    int? depth,
    int limit = 50,
    int offset = 0,
  }) async =>
      throw UnimplementedError();

  @override
  Future<Map<String, dynamic>?> nextIncomplete() async =>
      throw UnimplementedError();

  @override
  Future<BulkUpsertResult> upsertChildren(
      int parentId, List<dynamic> patches) async {
    throw DioException(
      requestOptions: RequestOptions(path: ''),
      response: Response(
        requestOptions: RequestOptions(path: ''),
        statusCode: 422,
        data: {
          'detail': [
            {
              'msg': 'Invalid label',
              'ctx': {'slot': 1}
            }
          ]
        },
      ),
    );
  }
}

class MockRepoFail implements EditTreeRepository {
  @override
  Dio get dio => throw UnimplementedError();

  @override
  String get baseUrl => '';

  @override
  Future<List<Map<String, dynamic>>> getChildren(int parentId) async {
    throw DioException(requestOptions: RequestOptions(path: ''));
  }

  @override
  Future<IncompleteParentsPage> listIncomplete({
    String query = "",
    int? depth,
    int limit = 50,
    int offset = 0,
  }) async =>
      throw UnimplementedError();

  @override
  Future<Map<String, dynamic>?> nextIncomplete() async =>
      throw UnimplementedError();

  @override
  Future<BulkUpsertResult> upsertChildren(
      int parentId, List<dynamic> patches) async {
    return MockBulkUpsertResult();
  }
}
