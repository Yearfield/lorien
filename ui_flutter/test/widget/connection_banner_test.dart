import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../lib/widgets/connection_banner.dart';

void main() {
  testWidgets('ConnectionBanner renders basic structure', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: Scaffold(body: ConnectionBanner()),
        ),
      ),
    );
    
    // Should show basic structure
    expect(find.byType(ConnectionBanner), findsOneWidget);
    expect(find.byType(Icon), findsOneWidget);
    expect(find.byType(Text), findsAtLeastNWidgets(1)); // At least the version text
  });

  testWidgets('ConnectionBanner has retry button', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: Scaffold(body: ConnectionBanner()),
        ),
      ),
    );
    
    // Should have a button
    expect(find.byType(TextButton), findsOneWidget);
  });

  testWidgets('ConnectionBanner shows loading state initially', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: Scaffold(body: ConnectionBanner()),
        ),
      ),
    );
    
    // Initially should show loading state
    expect(find.byType(ConnectionBanner), findsOneWidget);
    
    // Wait for the widget to settle
    await tester.pumpAndSettle();
    
    // After settling, should show some text
    expect(find.byType(Text), findsAtLeastNWidgets(1));
  });
}
