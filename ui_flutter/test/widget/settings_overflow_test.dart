import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import '../../lib/screens/settings_screen.dart';

void main() {
  testWidgets('Settings page does not overflow at 800x600', (tester) async {
    tester.binding.window.physicalSizeTestValue = const Size(800, 600);
    tester.binding.window.devicePixelRatioTestValue = 1.0;
    addTearDown(() {
      tester.binding.window.clearPhysicalSizeTestValue();
      tester.binding.window.clearDevicePixelRatioTestValue();
    });
    
    await tester.pumpWidget(const MaterialApp(home: SettingsScreen()));
    await tester.pumpAndSettle();
    
    // Verify no overflow exceptions
    expect(tester.takeException(), isNull);
    
    // Verify the page uses ListView for scrollable content
    expect(find.byType(ListView), findsOneWidget);
    
    // Verify basic structure is present
    expect(find.byType(Scaffold), findsOneWidget);
    expect(find.byType(AppBar), findsOneWidget);
  });

  testWidgets('Settings page does not overflow at 1200x600', (tester) async {
    tester.binding.window.physicalSizeTestValue = const Size(1200, 600);
    tester.binding.window.devicePixelRatioTestValue = 1.0;
    addTearDown(() {
      tester.binding.window.clearPhysicalSizeTestValue();
      tester.binding.window.clearDevicePixelRatioTestValue();
    });
    
    await tester.pumpWidget(const MaterialApp(home: SettingsScreen()));
    await tester.pumpAndSettle();
    
    // Verify no overflow exceptions
    expect(tester.takeException(), isNull);
    
    // Verify the page uses ListView for scrollable content
    expect(find.byType(ListView), findsOneWidget);
    
    // Verify basic structure is present
    expect(find.byType(Scaffold), findsOneWidget);
    expect(find.byType(AppBar), findsOneWidget);
  });

  testWidgets('Settings page scrolls at 600x500', (tester) async {
    tester.binding.window.physicalSizeTestValue = const Size(600, 500);
    tester.binding.window.devicePixelRatioTestValue = 1.0;
    addTearDown(() {
      tester.binding.window.clearPhysicalSizeTestValue();
      tester.binding.window.clearDevicePixelRatioTestValue();
    });
    
    await tester.pumpWidget(const MaterialApp(home: SettingsScreen()));
    await tester.pumpAndSettle();
    
    // Verify no overflow exceptions even at very small height
    expect(tester.takeException(), isNull);
    
    // Verify scrolling is available via ListView
    expect(find.byType(ListView), findsOneWidget);
  });

  testWidgets('Settings page handles very small heights gracefully', (tester) async {
    // Test with a very small height to ensure scrolling works
    tester.binding.window.physicalSizeTestValue = const Size(800, 400);
    tester.binding.window.devicePixelRatioTestValue = 1.0;
    addTearDown(() {
      tester.binding.window.clearPhysicalSizeTestValue();
      tester.binding.window.clearDevicePixelRatioTestValue();
    });
    
    await tester.pumpWidget(const MaterialApp(home: SettingsScreen()));
    await tester.pumpAndSettle();
    
    // Verify no overflow exceptions even at very small height
    expect(tester.takeException(), isNull);
    
    // Verify scrolling is available via ListView
    expect(find.byType(ListView), findsOneWidget);
  });

  testWidgets('Settings page renders without throwing at tight constraints', (tester) async {
    // Test with very tight constraints to ensure no overflow
    tester.binding.window.physicalSizeTestValue = const Size(600, 400);
    tester.binding.window.devicePixelRatioTestValue = 1.0;
    addTearDown(() {
      tester.binding.window.clearPhysicalSizeTestValue();
      tester.binding.window.clearDevicePixelRatioTestValue();
    });
    
    await tester.pumpWidget(const MaterialApp(home: SettingsScreen()));
    await tester.pumpAndSettle();
    
    // Verify no exceptions are thrown
    expect(tester.takeException(), isNull);
    
    // Verify ListView is present for scrolling
    expect(find.byType(ListView), findsOneWidget);
  });
}
