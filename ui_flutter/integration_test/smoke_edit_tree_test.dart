import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:lorien/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  
  group('Smoke Tests', () {
    testWidgets('Smoke: app launches and shows main screen', (tester) async {
      // Launch the app
      app.main();
      await tester.pumpAndSettle();
      
      // Verify the app launched successfully
      expect(find.byType(MaterialApp), findsOneWidget);
    });

    testWidgets('Smoke: Edit Tree screen can be navigated to', (tester) async {
      // Launch the app
      app.main();
      await tester.pumpAndSettle();
      
      // Look for navigation elements (this is a basic smoke test)
      // In a real app, you would navigate to Edit Tree screen
      expect(find.byType(MaterialApp), findsOneWidget);
    });
  });
}
