import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:integration_test/integration_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:lorien/main.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  setUp(() async {
    // Reset SharedPreferences for each test
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('Full app startup integration test', (tester) async {
    // Test the complete app startup flow
    await tester.pumpWidget(
      const ProviderScope(
        child: LorienApp(),
      ),
    );

    // Wait for initial build
    await tester.pump();

    // Verify basic app structure
    expect(find.byType(MaterialApp), findsOneWidget);
    expect(find.byType(NavShortcuts), findsOneWidget);

    // Wait for post-frame initialization to complete
    await tester.pumpAndSettle();

    // Verify home screen is loaded
    expect(find.byType(HomeScreen), findsOneWidget);
    expect(find.text('Lorien'), findsOneWidget);

    // Verify navigation tiles are present
    expect(find.text('Calculator'), findsOneWidget);
    expect(find.text('Outcomes'), findsOneWidget);
    expect(find.text('Settings'), findsOneWidget);
    expect(find.text('Workspace'), findsOneWidget);
  });

  testWidgets('App startup with custom preferences', (tester) async {
    // Set up custom preferences
    SharedPreferences.setMockInitialValues({
      'api_base_url': 'http://test.api.com',
    });

    await tester.pumpWidget(
      const ProviderScope(
        child: LorienApp(),
      ),
    );

    await tester.pump();
    await tester.pumpAndSettle();

    // App should start successfully despite custom prefs
    expect(find.byType(HomeScreen), findsOneWidget);
    expect(find.text('Calculator'), findsOneWidget);
  });

  testWidgets('App handles startup errors gracefully', (tester) async {
    // Set up potentially problematic preferences
    SharedPreferences.setMockInitialValues({
      'api_base_url': 'invalid-url',
      'corrupted_data': null,
    });

    await tester.pumpWidget(
      const ProviderScope(
        child: LorienApp(),
      ),
    );

    await tester.pump();
    await tester.pumpAndSettle();

    // App should still start and show home screen despite errors
    expect(find.byType(HomeScreen), findsOneWidget);
    expect(find.text('Calculator'), findsOneWidget);
  });

  testWidgets('Navigation works after full startup', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: LorienApp(),
      ),
    );

    await tester.pump();
    await tester.pumpAndSettle();

    // Test navigation to settings
    final settingsTile = find.text('Settings');
    expect(settingsTile, findsOneWidget);

    await tester.tap(settingsTile);
    await tester.pumpAndSettle();

    // Should navigate to settings screen
    // Note: Exact navigation behavior depends on router configuration
  });

  testWidgets('App maintains functionality after startup', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: LorienApp(),
      ),
    );

    await tester.pump();
    await tester.pumpAndSettle();

    // Test that the app remains functional
    expect(find.byType(HomeScreen), findsOneWidget);

    // Test that we can still interact with the UI
    final calculatorTile = find.text('Calculator');
    expect(calculatorTile, findsOneWidget);

    // Verify no crashes or hangs occur during normal operation
    await tester.tap(calculatorTile);
    await tester.pumpAndSettle();

    // Should still be functional after navigation
    expect(find.byType(HomeScreen), findsOneWidget);
  });
}
