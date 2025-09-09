import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/testing.dart';
import 'package:http/http.dart' as http;
import 'package:lorien/features/workspace/edit_tree_screen.dart';

void main() {
  testWidgets('EditTreeScreen shows parent list and handles slot editing',
      (tester) async {
    int getCount = 0;
    int putCount = 0;
    late int capturedParent;
    late int capturedSlot;
    late Map<String, dynamic> capturedBody;

    final mock = MockClient((req) async {
      // GET parents list
      if (req.method == 'GET' && req.url.path.endsWith('/tree/parents')) {
        getCount++;
        return http.Response(
            jsonEncode({
              "items": [
                {
                  "parent_id": 42,
                  "label": "BP",
                  "depth": 0,
                  "child_count": 2,
                  "missing_slots": [3, 4, 5]
                }
              ],
              "total": 1,
              "limit": 20,
              "offset": 0
            }),
            200);
      }
      // GET children
      if (req.method == 'GET' && req.url.path.contains('/tree/children/')) {
        getCount++;
        return http.Response(
            jsonEncode({
              "parent": {"id": 42, "label": "BP", "depth": 0},
              "children": [
                {"id": 1, "slot": 1, "label": "High", "depth": 1},
                {"id": 2, "slot": 2, "label": "Low", "depth": 1}
              ]
            }),
            200);
      }
      // PUT slot
      if (req.method == 'PUT' && req.url.path.contains('/slot/')) {
        putCount++;
        capturedParent = 42;
        capturedSlot = 3;
        capturedBody = jsonDecode(req.body);
        return http.Response(
            jsonEncode({
              "action": "created",
              "node_id": 99,
              "parent_id": 42,
              "slot": 3,
              "label": capturedBody["label"]
            }),
            200);
      }
      return http.Response('Not Found', 404);
    });

    await tester.pumpWidget(MaterialApp(home: EditTreeScreen(client: mock)));
    await tester.pump();

    // Should show parent list
    expect(find.text('BP'), findsOneWidget);
    expect(find.text('id=42 • depth=0 • missing=3,4,5'), findsOneWidget);

    // Tap on parent to select it
    await tester.tap(find.text('BP'));
    await tester.pump();

    // Should show children and slot inputs
    expect(find.text('Existing children:'), findsOneWidget);
    expect(find.text('S1: High'), findsOneWidget);
    expect(find.text('S2: Low'), findsOneWidget);
    expect(
        find.text('Fill missing slots (leave blank to skip):'), findsOneWidget);

    // Should have slot 3 input field
    expect(find.byType(TextField), findsOneWidget);

    // Enter text in slot 3
    await tester.enterText(find.byType(TextField), 'Headache');
    await tester.pump();

    // Tap Save & Next
    await tester.tap(find.text('Save & Next'));
    await tester.pump();

    // Verify API calls were made
    expect(getCount, 2); // parents + children
    expect(putCount, 1); // slot update
    expect(capturedParent, 42);
    expect(capturedSlot, 3);
    expect(capturedBody["label"], "Headache");
  });
}
