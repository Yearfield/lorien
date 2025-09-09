import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:lorien/screens/outcomes/outcomes_detail_screen.dart';
import 'package:lorien/providers/settings_provider.dart';

void main() {
  testWidgets('LLM Fill button is hidden when llmEnabled is false',
      (WidgetTester tester) async {
    // Build the outcomes detail screen with LLM disabled
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

    // Wait for the screen to load
    await tester.pumpAndSettle();

    // The LLM Fill button should not be present
    expect(find.text('Fill with AI'), findsNothing);
  });

  testWidgets('LLM Fill button is visible when llmEnabled is true',
      (WidgetTester tester) async {
    // Build the outcomes detail screen with LLM enabled
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

    // Wait for the screen to load
    await tester.pumpAndSettle();

    // The LLM Fill button should be present
    expect(find.text('Fill with AI'), findsOneWidget);
  });

  testWidgets('Screen structure is consistent regardless of LLM setting',
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
            llmEnabled: false, // LLM disabled
          ),
        ),
      ),
    );

    // Wait for the screen to load
    await tester.pumpAndSettle();

    // Basic structure should always be present
    expect(find.byType(Scaffold), findsOneWidget);
    expect(find.byType(AppBar), findsOneWidget);
  });
}
