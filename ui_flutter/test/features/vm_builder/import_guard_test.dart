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
}

class _FakeVmRepo implements VmRepo {
  @override
  String get base => 'http://x';
  _FakeVmRepo();
  @override
  Future<Map<String, dynamic>> importPreview(Uint8List bytes) async {
    return {"ok": true, "stats": {"found_paths": 10}, "errors": [{"row": 2, "msg":"max", "type":"value_error.max_children"}]};
  }
  // Unused members
  @override noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}
