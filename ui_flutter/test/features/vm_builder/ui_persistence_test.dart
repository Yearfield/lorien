import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/features/vm_builder/state/vm_provider.dart';
import 'package:lorien/features/vm_builder/data/vm_repo.dart';
import 'dart:typed_data';

class _PersistenceMockRepo implements VmRepo {
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
  group('UI Persistence Tests', () {
    late VmState vmState;
    late _PersistenceMockRepo mockRepo;
    List<String> toastMessages = [];

    setUp(() {
      mockRepo = _PersistenceMockRepo();
      vmState = VmState(mockRepo);
      vmState.toast = (message) => toastMessages.add(message);
    });

    tearDown(() {
      toastMessages.clear();
      mockRepo.clearApiCalls();
    });

    test('Should persist UI state after save - exact scenario from real app', () async {
      // Setup: Parent with 2 existing children
      mockRepo._children = [
        {'id': 1, 'parent_id': 100, 'label': 'Child 1', 'depth': 1},
        {'id': 2, 'parent_id': 100, 'label': 'Child 2', 'depth': 1},
      ];

      // Setup VM state with new child (exactly like in real app)
      vmState.currentParentId = 100;
      vmState.children = ['Child 1', 'Child 2', 'New Child'];

      print('Before save:');
      print('  children: ${vmState.children}');
      print('  childrenWithMeta: ${vmState.childrenWithMeta.length}');

      // Execute save
      await vmState.save();

      print('After save:');
      print('  children: ${vmState.children}');
      print('  childrenWithMeta: ${vmState.childrenWithMeta.length}');
      print('  API calls: ${mockRepo.getApiCalls()}');
      print('  Toast messages: $toastMessages');

      // CRITICAL: Verify UI state is updated
      expect(vmState.children.length, equals(3), reason: 'UI should show 3 children after save');
      expect(vmState.children.contains('New Child'), isTrue, reason: 'UI should contain the new child');
      expect(vmState.childrenWithMeta.length, equals(3), reason: 'childrenWithMeta should have 3 items');

      // Verify API calls were made
      final apiCalls = mockRepo.getApiCalls();
      expect(apiCalls.contains('getChildren(100)'), isTrue);
      expect(apiCalls.contains('addChild(100, "New Child")'), isTrue);

      // Verify success message
      expect(toastMessages.any((msg) => msg.contains('1 child(ren) added successfully')), isTrue);
    });
  });
}
