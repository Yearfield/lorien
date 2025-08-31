import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:lorien/providers/settings_provider.dart';
import 'package:lorien/screens/outcomes/outcomes_detail_screen.dart';

void main() {
  testWidgets('instantiates without errors', (tester) async {
    // This is a smoke structure test; in practice inject a fake repo or mock Dio in your screen via DI.
    await tester.pumpWidget(
      ChangeNotifierProvider(
        create: (_) => SettingsProvider(),
        child: const MaterialApp(
          home: OutcomesDetailScreen(nodeId: 1, llmEnabled: false)
        )
      )
    );
    
    // Should build without throwing
    expect(tester.takeException(), isNull);
  });

  testWidgets('has correct constructor parameters', (tester) async {
    // Test that the widget can be instantiated with required parameters
    const screen = OutcomesDetailScreen(nodeId: 1, llmEnabled: false);
    expect(screen.nodeId, 1);
    expect(screen.llmEnabled, false);
  });
}
