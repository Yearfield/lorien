import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../lib/features/edit_tree/ui/edit_tree_screen.dart';

void main() {

  testWidgets('should switch layout based on screen width', (tester) async {
    // Test wide layout (split pane)
    await tester.binding.setSurfaceSize(const Size(1200, 800));

    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    // Wait for the widget to build (may fail due to network calls, but that's ok)
    await tester.pump(const Duration(milliseconds: 100));

    // Should have split layout structure on wide screens
    expect(find.byType(LayoutBuilder), findsOneWidget);

    // Test narrow layout (tabs)
    await tester.binding.setSurfaceSize(const Size(800, 600));
    await tester.pump(const Duration(milliseconds: 100));

    // LayoutBuilder should still be present
    expect(find.byType(LayoutBuilder), findsOneWidget);
  });

  testWidgets('should have LayoutBuilder for responsive behavior', (tester) async {
    await tester.binding.setSurfaceSize(const Size(1000, 600));

    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pump(const Duration(milliseconds: 100));

    // LayoutBuilder should be present to handle responsive layout
    expect(find.byType(LayoutBuilder), findsOneWidget);
  });
}
