import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:typed_data';
import 'package:lorien/features/vm_builder/state/vm_provider.dart';
import 'package:lorien/features/vm_builder/ui/vm_builder_screen.dart';
import 'package:lorien/features/vm_builder/data/vm_repo.dart';

void main() {
  // Make the test viewport roomy to avoid spurious overflow on CI
  TestWidgetsFlutterBinding.ensureInitialized();
  setUp(() {
    // New test API (Flutter 3.16+):
    TestWidgetsFlutterBinding.instance.platformDispatcher.views.first
      ..physicalSize = const Size(1200, 2000)
      ..devicePixelRatio = 1.0;
  });
  tearDown(() {
    final view = TestWidgetsFlutterBinding.instance.platformDispatcher.views.first;
    view.resetPhysicalSize();
    view.resetDevicePixelRatio();
  });

  testWidgets('Shows banner on preview errors', (tester) async {
    // Fake repo that always returns an error in preview
    final fake = _FakeVmRepo();
    await tester.pumpWidget(
      MaterialApp(
        home: ChangeNotifierProvider(
          create: (_) => VmState(fake),
          child: const VmBuilderScreen(baseUrl: 'http://x'),
        ),
      ),
    );
    final state = tester.state(find.byType(VmBuilderScreen)) as State<VmBuilderScreen>;
    final vm = Provider.of<VmState>(state.context, listen: false);
    await vm.onImportPreview(Uint8List.fromList([1,2,3]));
    await tester.pumpAndSettle();
    expect(find.byType(MaterialBanner), findsOneWidget);
  });

  test('Refresh functionality works correctly', () async {
    final fake = _FakeVmRepo();
    final vm = VmState(fake);

    // Set up a toast callback to capture messages
    String? lastToastMessage;
    vm.toast = (String message) {
      lastToastMessage = message;
    };

    // Initially no roots loaded
    expect(vm.roots, isEmpty);

    // Call refreshAll
    await vm.refreshAll();

    // Should have loaded roots
    expect(vm.roots, isNotEmpty);
    expect(vm.roots.length, equals(2));
    expect(vm.roots.first['label'], equals('Test Root 1'));

    // Should show success message
    expect(lastToastMessage, equals('Database refreshed successfully'));
  });

  test('Drill down functionality works correctly', () async {
    final fake = _FakeVmRepo();
    final vm = VmState(fake);

    // Set up a toast callback to capture messages
    String? lastToastMessage;
    vm.toast = (String message) {
      lastToastMessage = message;
    };

    // Set up a current parent with children
    vm.currentParentId = 1;
    vm.currentDepth = 0; // Set initial depth
    vm.childrenWithMeta = [
      {"id": 10, "label": "Child 1", "red_flag": false},
      {"id": 11, "label": "Child 2", "red_flag": true},
    ];

    // Test drill down into first child
    await vm.drillIntoChildByIndex(0);
    expect(vm.currentParentId, equals(10));
    expect(vm.currentParentLabel, equals('Child 1'));
    expect(lastToastMessage, equals('Navigated to Child 1'));

    // Test drill down with invalid index
    await vm.drillIntoChildByIndex(5);
    expect(vm.currentParentId, equals(10)); // Should not change

    // Test drill down with child that has no ID
    vm.childrenWithMeta = [
      {"id": null, "label": "Child without ID", "red_flag": false},
    ];
    await vm.drillIntoChildByIndex(0);
    expect(lastToastMessage, equals('Child has no ID - please save changes first'));
  });
}

class _FakeVmRepo implements VmRepo {
  @override
  String get base => 'http://x';
  int _childrenCount = 2; // Default children count

  _FakeVmRepo();

  void setChildrenCount(int count) {
    _childrenCount = count;
  }

  @override
  Future<Map<String, dynamic>> importPreview(Uint8List bytes) async {
    return {"ok": true, "stats": {"found_paths": 10}, "errors": [{"row": 2, "msg":"max", "type":"value_error.max_children"}]};
  }

  @override
  Future<List<Map<String, dynamic>>> getRoots() async {
    return [
      {"id": 1, "label": "Test Root 1", "depth": 0},
      {"id": 2, "label": "Test Root 2", "depth": 0},
    ];
  }

  @override
  Future<List<Map<String, dynamic>>> getChildren(int parentId, {bool onlyRed = false}) async {
    final children = <Map<String, dynamic>>[];
    for (int i = 1; i <= _childrenCount; i++) {
      children.add({"id": 10 + i, "label": "Child $i", "red_flag": i % 2 == 0});
    }
    return children;
  }

  @override
  Future<List<Map<String, dynamic>>> findCloneCandidates(String label) async {
    if (label == 'NonExistent') {
      return [];
    }
    return [
      {"id": 100, "label": label, "depth": 1, "child_count": 2},
      {"id": 200, "label": label, "depth": 2, "child_count": 3},
    ];
  }

  @override
  Future<Map<String, dynamic>> cloneSubtree({required int sourceId, required int destParentId}) async {
    if (_childrenCount >= 5) {
      throw Exception('clone failed: 422 {"error":{"code":"VALIDATION_ERROR","message":"The request data is invalid: [{\'loc\': [\'dest_parent_id\'], \'msg\': \'destination parent already has 5 children\', \'type\': \'value_error.max_children\'}]"}}');
    }
    return {"ok": true, "created": 3};
  }

  // Unused members
  @override noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}
