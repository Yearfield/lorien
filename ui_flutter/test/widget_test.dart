// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../lib/widgets/connection_banner.dart';

void main() {
  testWidgets('Connection banner smoke test', (WidgetTester tester) async {
    // Build our connection banner and trigger a frame.
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: ConnectionBanner(),
        ),
      ),
    );

    // Verify that our banner builds without errors
    expect(find.byType(ConnectionBanner), findsOneWidget);
    
    // Verify that the basic structure is present
    expect(find.byType(TextButton), findsOneWidget);
    expect(find.byType(Icon), findsOneWidget);
  });
}
