import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/testing.dart';
import 'package:http/http.dart' as http;

import 'package:lorien/features/workspace/maintenance_screen.dart';

void main() {
  testWidgets('MaintenanceScreen confirm->clear flow updates stats', (tester) async {
    // First stats (non-zero), POST clear OK, then stats zeros
    int statsCalls = 0;
    final mock = MockClient((req) async {
      if (req.url.path.endsWith('/tree/stats')) {
        statsCalls++;
        if (statsCalls == 1) {
          return http.Response(jsonEncode({"nodes": 5, "roots": 2, "leaves": 3, "complete_paths": 0, "incomplete_parents": 2}), 200);
        } else {
          return http.Response(jsonEncode({"nodes": 0, "roots": 0, "leaves": 0, "complete_paths": 0, "incomplete_parents": 0}), 200);
        }
      }
      if (req.url.path.endsWith('/admin/clear') && req.method == 'POST') {
        return http.Response(jsonEncode({"ok": true, "dictionary_cleared": false, "summary": {"nodes":0,"outcomes":0}}), 200);
      }
      return http.Response('Not Found', 404);
    });

    await tester.pumpWidget(MaterialApp(home: MaintenanceScreen(client: mock)));
    await tester.pump();

    // Toggle confirm
    await tester.tap(find.byType(Checkbox));
    await tester.pump();

    // Tap clear
    await tester.tap(find.text('Clear Workspace'));
    await tester.pump();

    // After clear, message appears and stats refresh to zeros
    expect(find.textContaining('Workspace cleared.'), findsOneWidget);
    expect(find.textContaining('Nodes: 0'), findsOneWidget);
  });
}
