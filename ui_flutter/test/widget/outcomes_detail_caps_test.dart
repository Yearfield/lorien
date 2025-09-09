import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:lorien/screens/outcomes/outcomes_detail_screen.dart';
import 'package:lorien/providers/settings_provider.dart';

void main() {
  testWidgets('Outcomes detail screen basic structure',
      (WidgetTester tester) async {
    // Build the outcomes detail screen with providers
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider(create: (_) => SettingsProvider()),
        ],
        child: const MaterialApp(
          home: OutcomesDetailScreen(
            nodeId: 1,
            llmEnabled: true,
          ),
        ),
      ),
    );

    // Wait for all async operations to complete (including API calls)
    await tester.pumpAndSettle();

    // The screen should show some content after loading
    expect(find.byType(Scaffold), findsOneWidget);
    expect(find.byType(AppBar), findsOneWidget);
  });

  testWidgets('Outcomes detail screen respects llmEnabled parameter',
      (WidgetTester tester) async {
    // Test with LLM disabled
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider(create: (_) => SettingsProvider()),
        ],
        child: const MaterialApp(
          home: OutcomesDetailScreen(
            nodeId: 1,
            llmEnabled: false,
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Should not show LLM-related buttons when disabled
    expect(find.text('Fill with AI'), findsNothing);
  });
}
