import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lorien/features/workspace/ui/workspace_screen.dart';

void main() {
  testWidgets('Workspace renders and shows buttons', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(home: WorkspaceScreen()),
      ),
    );
    expect(find.text('Import Data'), findsOneWidget);
    expect(find.text('Export Data'), findsOneWidget);
    expect(find.text('Export CSV'), findsOneWidget);
    expect(find.text('Export XLSX'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('Workspace does not overflow at 600x500', (tester) async {
    tester.view.physicalSize = const Size(600, 500);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(home: WorkspaceScreen()),
      ),
    );
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
    expect(find.byType(ListView), findsOneWidget); // Verify ListView is used
  });
}
