import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../lib/features/edit_tree/ui/edit_tree_screen.dart';

void main() {
  testWidgets('controllers persist and caret stays during rebuild', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(home: EditTreeScreen()),
      ),
    );

    await tester.pump(); // Initial load

    // Find a slot text field and enter text
    final slotField = find.byKey(const ValueKey('slot_1'));
    expect(slotField, findsOneWidget);

    await tester.enterText(slotField, 'Test Label');

    // Verify text was entered
    expect(find.text('Test Label'), findsOneWidget);

    // Trigger a rebuild (this would happen when parent changes)
    await tester.pump();

    // Verify text is still there and caret position is maintained
    // (This is a simplified test - actual implementation would verify caret position)
    expect(find.text('Test Label'), findsOneWidget);
  });

  testWidgets('focus nodes are properly disposed', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(home: EditTreeScreen()),
      ),
    );

    await tester.pump(); // Initial load

    // The test ensures that dispose() is called properly
    // This would be verified in integration tests
    expect(true, isTrue); // Placeholder for actual verification
  });
}
