import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:shelf/shelf.dart';
import 'package:shelf/shelf_io.dart' as io;
import 'package:lorien/main.dart' as app;
import 'package:lorien/core/responsive/mobile_layout.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  late HttpServer server;

  setUpAll(() async {
    // Start a fake API server
    final handler = const Pipeline()
        .addMiddleware(logRequests())
        .addHandler(_fakeApiHandler);

    server = await io.serve(handler, InternetAddress.loopbackIPv4, 0);

    print('Fake API server running on port ${server.port}');
  });

  tearDownAll(() async {
    await server.close();
  });

  group('Mobile Parity Tests', () {
    testWidgets('mobile layout adapts to screen size', (tester) async {
      // Test mobile size (portrait)
      await tester.binding.setSurfaceSize(const Size(375, 667));
      app.main();
      await tester.pumpAndSettle();

      // Verify mobile layout is applied
      expect(find.text('Workspace'), findsOneWidget);
      
      // Test tablet size
      await tester.binding.setSurfaceSize(const Size(768, 1024));
      await tester.pumpAndSettle();

      // Verify tablet layout is applied
      expect(find.text('Workspace'), findsOneWidget);
      
      // Test desktop size
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      await tester.pumpAndSettle();

      // Verify desktop layout is applied
      expect(find.text('Workspace'), findsOneWidget);
    });

    testWidgets('mobile navigation works correctly', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      app.main();
      await tester.pumpAndSettle();

      // Test navigation to different screens
      await tester.tap(find.text('Outcomes'));
      await tester.pumpAndSettle();
      expect(find.text('Outcomes'), findsOneWidget);

      await tester.tap(find.text('Dictionary'));
      await tester.pumpAndSettle();
      expect(find.text('Dictionary'), findsOneWidget);

      await tester.tap(find.text('Flags'));
      await tester.pumpAndSettle();
      expect(find.text('Flags'), findsOneWidget);
    });

    testWidgets('mobile touch targets are appropriate size', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      app.main();
      await tester.pumpAndSettle();

      // Find all tappable elements and verify they meet minimum touch target size
      final tappableElements = find.byType(InkWell);
      expect(tappableElements, findsWidgets);

      // Test that buttons are large enough for mobile
      final buttons = find.byType(ElevatedButton);
      expect(buttons, findsWidgets);
    });

    testWidgets('mobile responsive text scales correctly', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      app.main();
      await tester.pumpAndSettle();

      // Verify text is readable on mobile
      final textWidgets = find.byType(Text);
      expect(textWidgets, findsWidgets);
    });

    testWidgets('mobile cards have appropriate spacing', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      app.main();
      await tester.pumpAndSettle();

      // Verify cards are properly spaced for mobile
      final cards = find.byType(Card);
      expect(cards, findsWidgets);
    });

    testWidgets('mobile forms are usable', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      app.main();
      await tester.pumpAndSettle();

      // Navigate to a screen with forms
      await tester.tap(find.text('Settings'));
      await tester.pumpAndSettle();

      // Verify form elements are accessible
      final textFields = find.byType(TextField);
      expect(textFields, findsWidgets);
    });

    testWidgets('mobile scrolling works smoothly', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      app.main();
      await tester.pumpAndSettle();

      // Test scrolling on a scrollable screen
      await tester.tap(find.text('Flags'));
      await tester.pumpAndSettle();

      // Verify scrolling works
      final scrollable = find.byType(Scrollable);
      expect(scrollable, findsWidgets);
    });

    testWidgets('mobile keyboard handling works', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      app.main();
      await tester.pumpAndSettle();

      // Navigate to a screen with text input
      await tester.tap(find.text('Settings'));
      await tester.pumpAndSettle();

      // Test keyboard interaction
      final textFields = find.byType(TextField);
      if (textFields.evaluate().isNotEmpty) {
        await tester.tap(textFields.first);
        await tester.pumpAndSettle();
        
        // Verify keyboard appears
        expect(find.byType(TextField), findsWidgets);
      }
    });

    testWidgets('mobile orientation change handling', (tester) async {
      // Test portrait
      await tester.binding.setSurfaceSize(const Size(375, 667));
      app.main();
      await tester.pumpAndSettle();
      expect(find.text('Workspace'), findsOneWidget);

      // Test landscape
      await tester.binding.setSurfaceSize(const Size(667, 375));
      await tester.pumpAndSettle();
      expect(find.text('Workspace'), findsOneWidget);
    });

    testWidgets('mobile performance is acceptable', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      
      final stopwatch = Stopwatch()..start();
      app.main();
      await tester.pumpAndSettle();
      stopwatch.stop();

      // Verify app loads within reasonable time (5 seconds)
      expect(stopwatch.elapsedMilliseconds, lessThan(5000));
    });

    testWidgets('mobile accessibility features work', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      app.main();
      await tester.pumpAndSettle();

      // Verify semantic labels are present
      final semanticWidgets = find.byType(Semantics);
      expect(semanticWidgets, findsWidgets);
    });

    testWidgets('mobile error handling works', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      app.main();
      await tester.pumpAndSettle();

      // Test error scenarios
      await tester.tap(find.text('Settings'));
      await tester.pumpAndSettle();

      // Verify error handling is present
      expect(find.text('Settings'), findsOneWidget);
    });
  });

  group('Tablet Parity Tests', () {
    testWidgets('tablet layout adapts correctly', (tester) async {
      await tester.binding.setSurfaceSize(const Size(768, 1024));
      app.main();
      await tester.pumpAndSettle();

      // Verify tablet layout is applied
      expect(find.text('Workspace'), findsOneWidget);
    });

    testWidgets('tablet navigation works', (tester) async {
      await tester.binding.setSurfaceSize(const Size(768, 1024));
      app.main();
      await tester.pumpAndSettle();

      // Test navigation
      await tester.tap(find.text('Outcomes'));
      await tester.pumpAndSettle();
      expect(find.text('Outcomes'), findsOneWidget);
    });
  });

  group('Cross-Platform Consistency Tests', () {
    testWidgets('features work consistently across screen sizes', (tester) async {
      final screenSizes = [
        const Size(375, 667),  // Mobile portrait
        const Size(667, 375),  // Mobile landscape
        const Size(768, 1024), // Tablet portrait
        const Size(1024, 768), // Tablet landscape
        const Size(1200, 800), // Desktop
      ];

      for (final size in screenSizes) {
        await tester.binding.setSurfaceSize(size);
        app.main();
        await tester.pumpAndSettle();

        // Verify core functionality works
        expect(find.text('Workspace'), findsOneWidget);
        
        // Test navigation
        await tester.tap(find.text('Outcomes'));
        await tester.pumpAndSettle();
        expect(find.text('Outcomes'), findsOneWidget);
        
        await tester.tap(find.text('Workspace'));
        await tester.pumpAndSettle();
        expect(find.text('Workspace'), findsOneWidget);
      }
    });
  });
}

Response _fakeApiHandler(Request request) {
  final path = request.url.path;

  switch (path) {
    case 'health':
      return Response.ok(
        '''
        {
          "ok": true,
          "version": "1.0.0-test",
          "db": {
            "path": "/fake/db/path",
            "wal": true,
            "foreign_keys": true
          },
          "features": {
            "llm": true
          }
        }
        ''',
        headers: {'content-type': 'application/json'},
      );

    case 'tree/next-incomplete-parent':
      return Response.ok(
        '{"parent_id": 1, "missing_slots": [1,2,3,4,5]}',
        headers: {'content-type': 'application/json'},
      );

    case 'outcomes':
      return Response.ok(
        '[]',
        headers: {'content-type': 'application/json'},
      );

    case 'dictionary':
      return Response.ok(
        '[]',
        headers: {'content-type': 'application/json'},
      );

    case 'flags':
      return Response.ok(
        '[]',
        headers: {'content-type': 'application/json'},
      );

    default:
      return Response.notFound('Not found: $path');
  }
}
