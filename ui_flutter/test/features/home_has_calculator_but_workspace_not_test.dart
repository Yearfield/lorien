import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ui_flutter/features/home/ui/home_screen.dart';
import 'package:ui_flutter/features/workspace/ui/workspace_screen.dart';

void main() {
  testWidgets('Home shows Calculator button', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(home: HomeScreen()),
      ),
    );
    expect(find.text('Calculator'), findsOneWidget);
  });

  testWidgets('Workspace does NOT show Calculator button', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(home: WorkspaceScreen()),
      ),
    );
    expect(find.text('Calculator'), findsNothing);
  });
}
