import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/features/vm_builder/state/vm_provider.dart';
import 'package:lorien/features/vm_builder/data/vm_repo.dart';
import 'dart:typed_data';

class _SimpleMockRepo implements VmRepo {
  List<Map<String, dynamic>> _children = [];
  int _nextId = 1000;
  List<String> _apiCalls = [];

  @override
  final String base = 'http://test';

  @override
  Future<List<Map<String, dynamic>>> getChildren(int parentId, {bool onlyRed = false}) async {
    _apiCalls.add('getChildren($parentId)');
    return _children.where((child) => child['parent_id'] == parentId).toList();
  }

  @override
  Future<void> addChild(int parentId, String label) async {
    _apiCalls.add('addChild($parentId, "$label")');
    _children.add({
      'id': _nextId++,
      'parent_id': parentId,
      'label': label,
      'depth': 1,
    });
  }

  @override
  Future<List<Map<String, dynamic>>> findParentsByLabel(String label) async {
    _apiCalls.add('findParentsByLabel("$label")');
    return []; // No existing parents
  }

  // Mock other required methods
  @override
  Future<List<Map<String, dynamic>>> getRoots() async => [];
  @override
  Future<Map<String, dynamic>> cloneSubtree({required int sourceId, required int destParentId}) async => {'success': true};
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

  List<String> getApiCalls() => List.from(_apiCalls);
  void clearApiCalls() => _apiCalls.clear();
}

void main() {
  group('Simple Save Tests', () {
    late VmState vmState;
    late _SimpleMockRepo mockRepo;
    List<String> toastMessages = [];

    setUp(() {
      mockRepo = _SimpleMockRepo();
      vmState = VmState(mockRepo);
      vmState.toast = (message) => toastMessages.add(message);
    });

    tearDown(() {
      toastMessages.clear();
      mockRepo.clearApiCalls();
    });

    test('Should call addChild when adding new child', () async {
      // Setup: Parent with 2 existing children
      mockRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
      ];

      // Setup VM state with new child
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Child 2', 'New Child'];

      // Execute save
      await vmState.save();

      // Verify API calls were made
      final apiCalls = mockRepo.getApiCalls();
      print('API calls made: $apiCalls');
      print('Toast messages: $toastMessages');

      expect(apiCalls.contains('getChildren(100)'), isTrue);
      expect(apiCalls.contains('addChild(100, "New Child")'), isTrue);

      // Verify child was added to database
      final children = await mockRepo.getChildren(100);
      expect(children.length, equals(3));
      expect(children.any((child) => child['label'] == 'New Child'), isTrue);

      // CRITICAL: Verify UI state is updated after save
      expect(vmState.children.length, equals(3), reason: 'UI should show 3 children after save');
      expect(vmState.children.contains('New Child'), isTrue, reason: 'UI should contain the new child');
      expect(vmState.childrenWithMeta.length, equals(3), reason: 'childrenWithMeta should have 3 items');
    });

    test('Should persist UI state after save and reload', () async {
      // Setup: Parent with 2 existing children
      mockRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
      ];

      // Setup VM state with new child
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Child 2', 'New Child'];

      // Execute save
      await vmState.save();

      // Verify the save operation completed
      expect(vmState.loading, isFalse, reason: 'Loading should be false after save');

      // CRITICAL: Verify UI state immediately after save
      expect(vmState.children.length, equals(3), reason: 'UI should show 3 children immediately after save');
      expect(vmState.children.contains('New Child'), isTrue, reason: 'UI should contain new child immediately after save');

      // CRITICAL: Verify childrenWithMeta is also updated
      expect(vmState.childrenWithMeta.length, equals(3), reason: 'childrenWithMeta should have 3 items');
      expect(vmState.childrenWithMeta.any((child) => child['label'] == 'New Child'), isTrue, reason: 'childrenWithMeta should contain new child');
    });

    test('Should handle reloadChildren after save', () async {
      // Setup: Parent with 2 existing children
      mockRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
      ];

      // Setup VM state with new child
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Child 2', 'New Child'];

      // Execute save
      await vmState.save();

      // Manually call reloadChildren to simulate what happens after save
      await vmState.reloadChildren();

      // CRITICAL: Verify UI state after reload
      expect(vmState.children.length, equals(3), reason: 'UI should show 3 children after reload');
      expect(vmState.children.contains('New Child'), isTrue, reason: 'UI should contain new child after reload');
      expect(vmState.childrenWithMeta.length, equals(3), reason: 'childrenWithMeta should have 3 items after reload');
      expect(vmState.childrenWithMeta.any((child) => child['label'] == 'New Child'), isTrue, reason: 'childrenWithMeta should contain new child after reload');
    });

    test('Should handle case where API returns stale data', () async {
      // This test simulates the real-world issue where the API might return stale data
      // Setup: Parent with 2 existing children
      mockRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
      ];

      // Setup VM state with new child
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Child 2', 'New Child'];

      // Execute save
      await vmState.save();

      // Simulate API returning stale data (only 2 children instead of 3)
      mockRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
        // Note: 'New Child' is missing from the API response
      ];

      // Call reloadChildren - this should show the stale data
      await vmState.reloadChildren();

      // This test should fail if the API is returning stale data
      expect(vmState.children.length, equals(2), reason: 'Should show 2 children if API returns stale data');
      expect(vmState.children.contains('New Child'), isFalse, reason: 'Should not contain new child if API returns stale data');
    });
  });
}
