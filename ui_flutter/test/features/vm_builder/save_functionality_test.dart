import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/features/vm_builder/state/vm_provider.dart';
import 'package:lorien/features/vm_builder/data/vm_repo.dart';
import 'dart:typed_data';

class _FakeVmRepo implements VmRepo {
  List<Map<String, dynamic>> _children = [];
  int _nextId = 1000;
  List<Map<String, dynamic>> _existingParents = [];

  @override
  final String base = 'http://test';

  @override
  Future<List<Map<String, dynamic>>> getChildren(int parentId, {bool onlyRed = false}) async {
    return _children.where((child) => child['parent_id'] == parentId).toList();
  }

  @override
  Future<List<Map<String, dynamic>>> getRoots() async {
    return [
      {'id': 1, 'label': 'Test Root', 'depth': 0}
    ];
  }

  @override
  Future<void> addChild(int parentId, String label) async {
    // Simulate a small delay like a real API call
    await Future.delayed(const Duration(milliseconds: 100));
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
    // Simulate cloning by adding a child with the source label
    _children.add({
      'id': _nextId++,
      'parent_id': destParentId,
      'label': 'Cloned Child',
      'depth': 1,
    });
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

  // Helper method to set existing parents for testing
  void setExistingParents(List<Map<String, dynamic>> parents) {
    _existingParents = parents;
  }
}

void main() {
  group('Save Functionality Tests', () {
    late VmState vmState;
    late _FakeVmRepo fakeRepo;
    List<String> toastMessages = [];

    setUp(() {
      fakeRepo = _FakeVmRepo();
      vmState = VmState(fakeRepo);
      vmState.toast = (message) => toastMessages.add(message);
    });

    tearDown(() {
      toastMessages.clear();
    });

    test('should add new child when no existing parents found', () async {
      // Setup: Parent with 4 existing children
      fakeRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
        {'id': 3, 'parent_id': 100, 'label': 'Child 3', 'depth': 1},
        {'id': 4, 'parent_id': 100, 'label': 'Child 4', 'depth': 1},
      ];

      // Setup VM state
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Child 2', 'Child 3', 'Child 4', 'New Child'];

      // Execute save
      await vmState.save();

      // Verify child was added to database
      final children = await fakeRepo.getChildren(100);
      expect(children.length, equals(5));
      expect(children.any((child) => child['label'] == 'New Child'), isTrue);

      // Verify UI state is updated after save
      expect(vmState.children.length, equals(5));
      expect(vmState.children.contains('New Child'), isTrue);
      expect(vmState.childrenWithMeta.length, equals(5));

      // Verify success messages
      expect(toastMessages.any((msg) => msg.contains('1 child(ren) added successfully')), isTrue);
    });

    test('should persist UI state after save and reload', () async {
      // Setup: Parent with 4 existing children
      fakeRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
        {'id': 3, 'parent_id': 100, 'label': 'Child 3', 'depth': 1},
        {'id': 4, 'parent_id': 100, 'label': 'Child 4', 'depth': 1},
      ];

      // Setup VM state
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Child 2', 'Child 3', 'Child 4', 'New Child'];

      // Execute save
      await vmState.save();

      // Verify the save operation completed
      expect(vmState.loading, isFalse);

      // Verify UI state after save
      expect(vmState.children.length, equals(5));
      expect(vmState.children.contains('New Child'), isTrue);

      // Verify childrenWithMeta is also updated
      expect(vmState.childrenWithMeta.length, equals(5));
      expect(vmState.childrenWithMeta.any((child) => child['label'] == 'New Child'), isTrue);
    });

    test('should handle reloadChildren after save', () async {
      // Setup: Parent with 4 existing children
      fakeRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
        {'id': 3, 'parent_id': 100, 'label': 'Child 3', 'depth': 1},
        {'id': 4, 'parent_id': 100, 'label': 'Child 4', 'depth': 1},
      ];

      // Setup VM state
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Child 2', 'Child 3', 'Child 4', 'New Child'];

      // Execute save
      await vmState.save();

      // Manually call reloadChildren to simulate what happens after save
      await vmState.reloadChildren();

      // Verify UI state after reload
      expect(vmState.children.length, equals(5));
      expect(vmState.children.contains('New Child'), isTrue);
      expect(vmState.childrenWithMeta.length, equals(5));
      expect(vmState.childrenWithMeta.any((child) => child['label'] == 'New Child'), isTrue);
    });

    test('should verify API returns correct children after addChild', () async {
      // Setup: Parent with 4 existing children
      fakeRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
        {'id': 3, 'parent_id': 100, 'label': 'Child 3', 'depth': 1},
        {'id': 4, 'parent_id': 100, 'label': 'Child 4', 'depth': 1},
      ];

      // Setup VM state
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Child 2', 'Child 3', 'Child 4', 'New Child'];

      // Execute save
      await vmState.save();

      // Verify that the API call returns the correct children
      final apiChildren = await fakeRepo.getChildren(100);
      expect(apiChildren.length, equals(5));
      expect(apiChildren.any((child) => child['label'] == 'New Child'), isTrue);

      // Verify that reloadChildren uses the same API call
      await vmState.reloadChildren();
      expect(vmState.children.length, equals(5));
      expect(vmState.children.contains('New Child'), isTrue);
    });

    test('should handle case where API returns stale data', () async {
      // This test simulates the real-world issue where the API might return stale data
      // Setup: Parent with 4 existing children
      fakeRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
        {'id': 3, 'parent_id': 100, 'label': 'Child 3', 'depth': 1},
        {'id': 4, 'parent_id': 100, 'label': 'Child 4', 'depth': 1},
      ];

      // Setup VM state
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Child 2', 'Child 3', 'Child 4', 'New Child'];

      // Execute save
      await vmState.save();

      // Simulate API returning stale data (only 4 children instead of 5)
      fakeRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
        {'id': 3, 'parent_id': 100, 'label': 'Child 3', 'depth': 1},
        {'id': 4, 'parent_id': 100, 'label': 'Child 4', 'depth': 1},
        // Note: 'New Child' is missing from the API response
      ];

      // Call reloadChildren - this should show the stale data
      await vmState.reloadChildren();

      // This test should fail if the API is returning stale data
      expect(vmState.children.length, equals(4)); // Should be 4, not 5
      expect(vmState.children.contains('New Child'), isFalse); // Should be false
    });

    test('should handle timing issues with API calls', () async {
      // This test simulates the real-world timing issue
      // Setup: Parent with 4 existing children
      fakeRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
        {'id': 3, 'parent_id': 100, 'label': 'Child 3', 'depth': 1},
        {'id': 4, 'parent_id': 100, 'label': 'Child 4', 'depth': 1},
      ];

      // Setup VM state
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Child 2', 'Child 3', 'Child 4', 'New Child'];

      // Execute save
      await vmState.save();

      // Immediately check if the child was added (before any delay)
      final immediateCheck = await fakeRepo.getChildren(100);
      expect(immediateCheck.length, equals(5));
      expect(immediateCheck.any((child) => child['label'] == 'New Child'), isTrue);

      // Wait a bit to simulate real-world timing
      await Future.delayed(const Duration(milliseconds: 200));

      // Check again after delay
      final delayedCheck = await fakeRepo.getChildren(100);
      expect(delayedCheck.length, equals(5));
      expect(delayedCheck.any((child) => child['label'] == 'New Child'), isTrue);
    });

    test('should save child to parent with less than 5 children', () async {
      // Setup: Parent with only 2 existing children (room for 3 more)
      fakeRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
      ];

      // Setup VM state with new child
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Child 2', 'New Child'];

      // Execute save
      await vmState.save();

      // Verify child was added to database
      final children = await fakeRepo.getChildren(100);
      expect(children.length, equals(3));
      expect(children.any((child) => child['label'] == 'New Child'), isTrue);

      // Verify UI state is updated
      expect(vmState.children.length, equals(3));
      expect(vmState.children.contains('New Child'), isTrue);
      expect(vmState.childrenWithMeta.length, equals(3));

      // Verify success messages
      expect(toastMessages.any((msg) => msg.contains('1 child(ren) added successfully')), isTrue);
    });

    test('should save multiple children to parent with room', () async {
      // Setup: Parent with only 1 existing child (room for 4 more)
      fakeRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
      ];

      // Setup VM state with 2 new children
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'New Child 1', 'New Child 2'];

      // Execute save
      await vmState.save();

      // Verify both children were added to database
      final children = await fakeRepo.getChildren(100);
      expect(children.length, equals(3));
      expect(children.any((child) => child['label'] == 'New Child 1'), isTrue);
      expect(children.any((child) => child['label'] == 'New Child 2'), isTrue);

      // Verify UI state is updated
      expect(vmState.children.length, equals(3));
      expect(vmState.children.contains('New Child 1'), isTrue);
      expect(vmState.children.contains('New Child 2'), isTrue);

      // Verify success messages
      expect(toastMessages.any((msg) => msg.contains('2 child(ren) added successfully')), isTrue);
    });

    test('should handle subtree selection when existing parents found', () async {
      // Setup: Mock existing parents for the child label
      fakeRepo.setExistingParents([
        {'id': 200, 'label': 'Existing Child', 'depth': 1},
        {'id': 201, 'label': 'Existing Child', 'depth': 2},
      ]);

      // Setup: Parent with 4 existing children
      fakeRepo._children = [
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

      // Verify subtree was cloned
      final children = await fakeRepo.getChildren(100);
      expect(children.length, equals(5));
      expect(children.any((child) => child['label'] == 'Cloned Child'), isTrue);

      // Verify success messages
      expect(toastMessages.any((msg) => msg.contains('Cloned subtree for "Existing Child"')), isTrue);
      expect(toastMessages.any((msg) => msg.contains('1 child(ren) added successfully')), isTrue);
    });

    test('should handle multiple new children', () async {
      // Setup: Parent with 3 existing children
      fakeRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
        {'id': 3, 'parent_id': 100, 'label': 'Child 3', 'depth': 1},
      ];

      // Setup VM state with 2 new children
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Child 2', 'Child 3', 'New Child 1', 'New Child 2'];

      // Execute save
      await vmState.save();

      // Verify both children were added
      final children = await fakeRepo.getChildren(100);
      expect(children.length, equals(5));
      expect(children.any((child) => child['label'] == 'New Child 1'), isTrue);
      expect(children.any((child) => child['label'] == 'New Child 2'), isTrue);

      // Verify success messages
      expect(toastMessages.any((msg) => msg.contains('2 child(ren) added successfully')), isTrue);
    });

    test('should handle no changes scenario', () async {
      // Setup: Parent with 4 existing children
      fakeRepo._children = [
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

      // Verify no changes message
      expect(toastMessages.any((msg) => msg.contains('No changes to save')), isTrue);
    });

    test('should handle unsafe modifications scenario', () async {
      // Setup: Parent with 4 existing children
      fakeRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
        {'id': 3, 'parent_id': 100, 'label': 'Child 3', 'depth': 1},
        {'id': 4, 'parent_id': 100, 'label': 'Child 4', 'depth': 1},
      ];

      // Setup VM state with modified children (not just additions)
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Modified Child', 'Child 3', 'Child 4'];

      // Execute save
      await vmState.save();

      // Verify warning message
      expect(toastMessages.any((msg) => msg.contains('WARNING: This will replace all children')), isTrue);
    });
  });
}
