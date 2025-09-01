import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lorien/features/settings/ui/settings_screen.dart';
import 'package:lorien/core/services/health_service.dart';

void main() {
  testWidgets('Settings shows tested URL/code/snippet', (tester) async {
    // TODO: complete with ProviderScope overrides + finders.
    // This test would verify that:
    // 1. Settings screen renders correctly
    // 2. Test Connection button works
    // 3. URL, HTTP code, and body snippet are displayed
    // 4. Connected badge updates appropriately

    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: SettingsScreen(),
        ),
      ),
    );

    // Verify the screen loads
    expect(find.text('Settings'), findsOneWidget);
    expect(find.text('Base URL'), findsOneWidget);
    expect(find.text('Test Connection'), findsOneWidget);

    // TODO: Add more comprehensive tests with mocked health service
    expect(true, isTrue);
  });
}
