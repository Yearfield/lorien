import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../lib/features/edit_tree/ui/edit_tree_screen.dart';

void main() {
  testWidgets('should show split layout on wide screens (>= 1000px)', (tester) async {
    await tester.binding.setSurfaceSize(const Size(1200, 800));

    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    // Wait for the widget to build
    await tester.pumpAndSettle();

    // Should have both list and editor panes
    expect(find.byType(Flexible), findsWidgets);
    expect(find.text('Search parents'), findsOneWidget);
    expect(find.text('Select a parent'), findsOneWidget);
  });

  testWidgets('should show tabbed layout on narrow screens (< 1000px)', (tester) async {
    await tester.binding.setSurfaceSize(const Size(800, 600));

    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    // Wait for the widget to build
    await tester.pumpAndSettle();

    // Should have segmented button for tabs
    expect(find.byType(SegmentedButton<int>), findsOneWidget);
    expect(find.text('List'), findsOneWidget);
    expect(find.text('Editor'), findsOneWidget);
  });

  testWidgets('should switch between tabs on mobile layout', (tester) async {
    await tester.binding.setSurfaceSize(const Size(800, 600));

    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Initially should show editor (default tab index 1)
    expect(find.text('Select a parent'), findsOneWidget);

    // Switch to list tab
    await tester.tap(find.text('List'));
    await tester.pumpAndSettle();

    // Should show list pane
    expect(find.text('Search parents'), findsOneWidget);
  });

  testWidgets('should maintain functionality in both layouts', (tester) async {
    // Test wide layout
    await tester.binding.setSurfaceSize(const Size(1200, 800));

    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Should have search functionality
    expect(find.byType(TextField), findsOneWidget);
    expect(find.byType(DropdownButton<int?>), findsOneWidget);

    // Test narrow layout
    await tester.binding.setSurfaceSize(const Size(800, 600));
    await tester.pumpAndSettle();

    // Should still have search functionality after layout switch
    expect(find.byType(TextField), findsOneWidget);
    expect(find.byType(DropdownButton<int?>), findsOneWidget);
  });
}
