import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:shelf/shelf.dart';
import 'package:shelf/shelf_io.dart' as io;
import 'package:lorien/main.dart' as app;

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
    
    // Note: In a real test, you'd need to set the API base URL as an environment variable
    // For now, we'll just verify the app can launch
  });

  tearDownAll(() async {
    await server.close();
  });

  group('Mobile Parity Basic Tests', () {
    testWidgets('app launches on mobile size', (tester) async {
      // Test mobile portrait size
      await tester.binding.setSurfaceSize(const Size(375, 667));
      
      // Launch the app
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Verify the app launched successfully by checking for any text
      expect(find.byType(Text), findsWidgets);
    });

    testWidgets('app launches on tablet size', (tester) async {
      // Test tablet portrait size
      await tester.binding.setSurfaceSize(const Size(768, 1024));
      
      // Launch the app
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Verify the app launched successfully
      expect(find.byType(Text), findsWidgets);
    });

    testWidgets('app launches on desktop size', (tester) async {
      // Test desktop size
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      
      // Launch the app
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Verify the app launched successfully
      expect(find.byType(Text), findsWidgets);
    });

    testWidgets('basic UI elements exist on mobile', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 5));

      // Check for basic UI elements
      expect(find.byType(Scaffold), findsWidgets);
      expect(find.byType(Text), findsWidgets);
    });

    testWidgets('orientation change works', (tester) async {
      // Test portrait
      await tester.binding.setSurfaceSize(const Size(375, 667));
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 3));
      expect(find.byType(Text), findsWidgets);

      // Test landscape
      await tester.binding.setSurfaceSize(const Size(667, 375));
      await tester.pumpAndSettle(const Duration(seconds: 3));
      expect(find.byType(Text), findsWidgets);
    });

    testWidgets('performance is acceptable', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      
      final stopwatch = Stopwatch()..start();
      app.main();
      await tester.pumpAndSettle(const Duration(seconds: 5));
      stopwatch.stop();

      // Verify app loads within reasonable time (15 seconds for mobile)
      expect(stopwatch.elapsedMilliseconds, lessThan(15000));
    });
  });

  group('Cross-Platform Consistency', () {
    testWidgets('app works across different screen sizes', (tester) async {
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
        await tester.pumpAndSettle(const Duration(seconds: 3));

        // Verify basic functionality works
        expect(find.byType(Text), findsWidgets);
        expect(find.byType(Scaffold), findsWidgets);
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
