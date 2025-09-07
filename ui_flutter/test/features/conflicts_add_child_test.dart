import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/testing.dart';
import 'package:http/http.dart' as http;

import '../../lib/features/workspace/conflicts_screen.dart';

void main() {
  testWidgets('Conflicts: basic screen loads', (tester) async {
    final client = MockClient((req) async {
      return http.Response('Not found', 404);
    });

    await tester.pumpWidget(MaterialApp(home: ConflictsScreen(client: client)));
    await tester.pump();

    // Verify the screen loads
    expect(find.text('Conflicts'), findsOneWidget);
  });
}
