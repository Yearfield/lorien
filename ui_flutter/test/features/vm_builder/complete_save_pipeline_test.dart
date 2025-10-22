import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/features/vm_builder/state/vm_provider.dart';
import 'package:lorien/features/vm_builder/data/vm_repo.dart';
import 'dart:typed_data';

class _MockVmRepo implements VmRepo {
  List<Map<String, dynamic>> _children = [];
  int _nextId = 1000;
  List<Map<String, dynamic>> _existingParents = [];
  List<String> _apiCalls = [];

  @override
  final String base = 'http://test';

  @override
  Future<List<Map<String, dynamic>>> getChildren(int parentId, {bool onlyRed = false}) async {
    _apiCalls.add('getChildren($parentId)');
    return _children.where((child) => child['parent_id'] == parentId).toList();
  }

  @override
  Future<List<Map<String, dynamic>>> getRoots() async {
    return [{'id': 1, 'label': 'Test Root', 'depth': 0}];
  }

  @override
  Future<void> addChild(int parentId, String label) async {
    _apiCalls.add('addChild($parentId, "$label")');

    // Check if parent already has 5 children
    final currentChildren = _children.where((child) => child['parent_id'] == parentId).toList();
    if (currentChildren.length >= 5) {
      throw Exception('add child failed: 422 {"error":{"message":"parent already has 5 children"}}');
    }

    _children.add({
      'id': _nextId++,
      'parent_id': parentId,
      'label': label,
      'depth': 1,
    });
  }

  @override
  Future<List<Map<String, dynamic>>> findParentsByLabel(String label) async {
    return _existingParents.where((parent) => parent['label'] == label).toList();
  }

  @override
  Future<Map<String, dynamic>> cloneSubtree({required int sourceId, required int destParentId}) async {
    _apiCalls.add('cloneSubtree($sourceId, $destParentId)');
    return {'success': true};
  }

  // Mock other required methods
  @override
  Future<void> deleteNode(int nodeId) async {}
  @override
  Future<void> deleteRoot(int rootId) async {}
  @override
  Future<void> putChildren(int parentId, List<String> labels) async {}
  @override
  Future<Map<String, dynamic>> getNode(int nodeId) async => {'id': nodeId, 'label': 'Test Node'};
  @override
  Future<void> renameParent(int parentId, String newName) async {}
  @override
  Future<void> mergeParents(int currentParentId, int existingParentId, List<String> selectedChildren) async {}
  @override
  Future<void> navigateToParentById(int parentId) async {}
  @override
  Future<List<Map<String, dynamic>>> findCloneCandidates(String label) async => [];
  @override
  Future<void> setEdgeFlag(int parentId, int childId, bool red) async {}
  @override
  Future<List<Map<String, dynamic>>> ancestors(int nodeId) async => [];
  @override
  Future<Map<String, dynamic>> createRoot(String label) async => {'id': 1, 'label': label};
  @override
  Future<Map<String, dynamic>> deleteNodeApply(int nodeId) async => {'success': true};
  @override
  Future<Map<String, dynamic>> deleteNodeDryRun(int nodeId) async => {'success': true};
  @override
  Future<String?> exportCsv({int? rootId}) async => 'csv,data';
  @override
  Future<Map<String, dynamic>?> getParentInfo(int parentId) async => {'id': parentId};
  @override
  Future<Map<String, dynamic>> importApply(Uint8List bytes, {bool enforceFive = true, String mode = 'append'}) async => {'success': true};
  @override
  Future<Map<String, dynamic>> importFile(String mode, Uint8List bytes, String filename) async => {'success': true};
  @override
  Future<Map<String, dynamic>> importPreview(Uint8List bytes) async => {'preview': true};
  @override
  Future<Map<String, dynamic>?> nextUnderfilled({int? rootId, int? afterId}) async => null;
  @override
  Future<Map<String, dynamic>> restoreSubtree(Map<String, dynamic> snapshot) async => {'success': true};

  // Helper methods for testing
  void setExistingParents(List<Map<String, dynamic>> parents) {
    _existingParents = parents;
  }

  List<String> getApiCalls() => List.from(_apiCalls);
  void clearApiCalls() => _apiCalls.clear();
}

void main() {
  group('Complete Save Pipeline Tests', () {
    late VmState vmState;
    late _MockVmRepo mockRepo;
    List<String> toastMessages = [];

    setUp(() {
      mockRepo = _MockVmRepo();
      vmState = VmState(mockRepo);
      vmState.toast = (message) => toastMessages.add(message);
    });

    tearDown(() {
      toastMessages.clear();
      mockRepo.clearApiCalls();
    });

    test('Complete save pipeline: add new child to parent with room', () async {
      // Setup: Parent with 3 existing children (room for 2 more)
      mockRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
        {'id': 3, 'parent_id': 100, 'label': 'Child 3', 'depth': 1},
      ];

      // Setup VM state with new child
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Child 2', 'Child 3', 'New Child'];

      // Execute save
      await vmState.save();

      // Verify API calls were made
      final apiCalls = mockRepo.getApiCalls();
      expect(apiCalls.contains('getChildren(100)'), isTrue, reason: 'Should call getChildren to check existing children');
      expect(apiCalls.contains('addChild(100, "New Child")'), isTrue, reason: 'Should call addChild to add new child');
      expect(apiCalls.length, greaterThanOrEqualTo(2), reason: 'Should make at least 2 API calls');

      // Verify child was added to database
      final children = await mockRepo.getChildren(100);
      expect(children.length, equals(4));
      expect(children.any((child) => child['label'] == 'New Child'), isTrue);

      // Verify UI state is updated
      expect(vmState.children.length, equals(4));
      expect(vmState.children.contains('New Child'), isTrue);
      expect(vmState.childrenWithMeta.length, equals(4));

      // Verify success messages
      expect(toastMessages.any((msg) => msg.contains('1 child(ren) added successfully')), isTrue);
    });

    test('Complete save pipeline: add multiple children to parent with room', () async {
      // Setup: Parent with 2 existing children (room for 3 more)
      mockRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
      ];

      // Setup VM state with 2 new children
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Child 2', 'New Child 1', 'New Child 2'];

      // Execute save
      await vmState.save();

      // Verify API calls were made
      final apiCalls = mockRepo.getApiCalls();
      expect(apiCalls.contains('getChildren(100)'), isTrue);
      expect(apiCalls.contains('addChild(100, "New Child 1")'), isTrue);
      expect(apiCalls.contains('addChild(100, "New Child 2")'), isTrue);

      // Verify both children were added to database
      final children = await mockRepo.getChildren(100);
      expect(children.length, equals(4));
      expect(children.any((child) => child['label'] == 'New Child 1'), isTrue);
      expect(children.any((child) => child['label'] == 'New Child 2'), isTrue);

      // Verify UI state is updated
      expect(vmState.children.length, equals(4));
      expect(vmState.children.contains('New Child 1'), isTrue);
      expect(vmState.children.contains('New Child 2'), isTrue);

      // Verify success messages
      expect(toastMessages.any((msg) => msg.contains('2 child(ren) added successfully')), isTrue);
    });

    test('Complete save pipeline: handle parent with 5 children (should fail)', () async {
      // Setup: Parent with 5 existing children (no room)
      mockRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
        {'id': 3, 'parent_id': 100, 'label': 'Child 3', 'depth': 1},
        {'id': 4, 'parent_id': 100, 'label': 'Child 4', 'depth': 1},
        {'id': 5, 'parent_id': 100, 'label': 'Child 5', 'depth': 1},
      ];

      // Setup VM state with new child
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Child 2', 'Child 3', 'Child 4', 'Child 5', 'New Child'];

      // Execute save
      await vmState.save();

      // Verify API calls were made
      final apiCalls = mockRepo.getApiCalls();
      expect(apiCalls.contains('getChildren(100)'), isTrue);
      expect(apiCalls.contains('addChild(100, "New Child")'), isTrue);

      // Verify child was NOT added to database (should still be 5)
      final children = await mockRepo.getChildren(100);
      expect(children.length, equals(5));
      expect(children.any((child) => child['label'] == 'New Child'), isFalse);

      // Verify error message
      expect(toastMessages.any((msg) => msg.contains('Cannot add "New Child": Parent already has 5 children')), isTrue);
    });

    test('Complete save pipeline: handle subtree selection', () async {
      // Setup: Mock existing parents for the child label
      mockRepo.setExistingParents([
        {'id': 200, 'label': 'Existing Child', 'depth': 1},
        {'id': 201, 'label': 'Existing Child', 'depth': 2},
      ]);

      // Setup: Parent with 4 existing children
      mockRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
        {'id': 3, 'parent_id': 100, 'label': 'Child 3', 'depth': 1},
        {'id': 4, 'parent_id': 100, 'label': 'Child 4', 'depth': 1},
      ];

      // Setup VM state
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Child 2', 'Child 3', 'Child 4', 'Existing Child'];

      // Execute save
      await vmState.save();

      // Verify API calls were made
      final apiCalls = mockRepo.getApiCalls();
      expect(apiCalls.contains('getChildren(100)'), isTrue);
      expect(apiCalls.contains('findParentsByLabel("Existing Child")'), isTrue);
      expect(apiCalls.contains('cloneSubtree(200, 100)'), isTrue);

      // Verify subtree was cloned (the cloneSubtree call should have been made)
      final children = await mockRepo.getChildren(100);
      expect(children.length, equals(4)); // Original 4 children, clone doesn't add to mock
      // Note: The actual cloneSubtree implementation would add children, but our mock doesn't

      // Verify success messages
      expect(toastMessages.any((msg) => msg.contains('Cloned subtree for "Existing Child"')), isTrue);
      expect(toastMessages.any((msg) => msg.contains('1 child(ren) added successfully')), isTrue);
    });

    test('Complete save pipeline: no changes scenario', () async {
      // Setup: Parent with 4 existing children
      mockRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
        {'id': 3, 'parent_id': 100, 'label': 'Child 3', 'depth': 1},
        {'id': 4, 'parent_id': 100, 'label': 'Child 4', 'depth': 1},
      ];

      // Setup VM state with same children
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Child 2', 'Child 3', 'Child 4'];

      // Execute save
      await vmState.save();

      // Verify API calls were made
      final apiCalls = mockRepo.getApiCalls();
      expect(apiCalls.contains('getChildren(100)'), isTrue);
      expect(apiCalls.contains('addChild'), isFalse, reason: 'Should not call addChild when no changes');

      // Verify no changes message
      expect(toastMessages.any((msg) => msg.contains('No changes to save')), isTrue);
    });
  });
}
