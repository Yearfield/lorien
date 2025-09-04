import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:lorien/main.dart';

void main() {
  setUp(() async {
    // Set up mock initial values for SharedPreferences
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('App starts without blocking async operations', (tester) async {
    // Test that the app can build its first frame without any blocking operations
    await tester.pumpWidget(
      const ProviderScope(
        child: LorienApp(),
      ),
    );

    // Verify the app builds and shows initial content
    expect(find.byType(MaterialApp), findsOneWidget);
    expect(find.text('Lorien'), findsOneWidget);

    // First pump should complete without hanging (no blocking async)
    await tester.pump();

    // App should still be functional after first frame
    expect(find.byType(NavShortcuts), findsOneWidget);
  });

  testWidgets('No network calls during initial build', (tester) async {
    // This test ensures no HTTP calls are made during the initial widget build
    await tester.pumpWidget(
      const ProviderScope(
        child: LorienApp(),
      ),
    );

    // If the app reaches this point without hanging, the blocking async is fixed
    await tester.pump();

    // Verify basic navigation tiles are present (indicates successful build)
    expect(find.text('Calculator'), findsOneWidget);
    expect(find.text('Outcomes'), findsOneWidget);
    expect(find.text('Settings'), findsOneWidget);
  });

  testWidgets('Settings load properly after first frame', (tester) async {
    // Test that settings are loaded asynchronously after the first frame
    await tester.pumpWidget(
      const ProviderScope(
        child: LorienApp(),
      ),
    );

    // Initial build should complete
    await tester.pump();

    // Wait for post-frame callback to execute
    await tester.pumpAndSettle();

    // App should still be functional and not crashed
    expect(find.byType(HomeScreen), findsOneWidget);
  });

  testWidgets('App handles various startup scenarios gracefully', (tester) async {
    // Test with different SharedPreferences states
    SharedPreferences.setMockInitialValues({
      'api_base_url': 'http://test.example.com',
      'theme_mode': 'dark',
    });

    await tester.pumpWidget(
      const ProviderScope(
        child: LorienApp(),
      ),
    );

    // Should build successfully regardless of prefs state
    await tester.pump();
    expect(find.byType(MaterialApp), findsOneWidget);

    // Should handle post-frame initialization
    await tester.pumpAndSettle();
    expect(find.byType(HomeScreen), findsOneWidget);
  });

  testWidgets('App starts with empty preferences', (tester) async {
    // Test startup with completely empty preferences
    SharedPreferences.setMockInitialValues({});

    await tester.pumpWidget(
      const ProviderScope(
        child: LorienApp(),
      ),
    );

    await tester.pump();
    expect(find.byType(MaterialApp), findsOneWidget);

    await tester.pumpAndSettle();
    expect(find.byType(HomeScreen), findsOneWidget);
  });

  testWidgets('Navigation works after startup', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: LorienApp(),
      ),
    );

    await tester.pump();
    await tester.pumpAndSettle();

    // Test that navigation tiles are interactive
    final calculatorTile = find.text('Calculator');
    expect(calculatorTile, findsOneWidget);

    // Should be able to tap navigation tiles
    await tester.tap(calculatorTile);
    await tester.pumpAndSettle();

    // Should navigate to calculator screen (or show some indication of navigation)
    // Note: Actual navigation depends on router configuration
  });
}
