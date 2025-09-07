import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/testing.dart';
import 'package:http/http.dart' as http;

import '../../lib/features/workspace/calculator_screen.dart';

void main() {
  testWidgets('Calculator loads and shows basic UI', (tester) async {
    final client = MockClient((req) async {
      if (req.url.path.endsWith('/tree/root-options')) {
        return http.Response(jsonEncode({"items":["BP"]}), 200);
      }
      return http.Response('Not found', 404);
    });

    await tester.pumpWidget(MaterialApp(home: TreeNavigatorScreen(client: client)));
    await tester.pump();

    // Verify the screen loads
    expect(find.text('Calculator'), findsOneWidget);
    expect(find.text('Select Vital Measurement'), findsOneWidget);
  });
}
