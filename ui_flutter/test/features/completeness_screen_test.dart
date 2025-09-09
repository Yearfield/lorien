import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/testing.dart';
import 'package:http/http.dart' as http;

import 'package:lorien/features/workspace/completeness_screen.dart';

void main() {
  testWidgets('CompletenessScreen shows counts and table', (tester) async {
    final stats = {
      "nodes": 10,
      "roots": 2,
      "leaves": 3,
      "complete_paths": 1,
      "incomplete_parents": 7
    };
    final missing = {
      "items": [
        {
          "parent_id": 1,
          "label": "BP",
          "depth": 0,
          "missing_slots": [3, 4, 5]
        },
        {
          "parent_id": 2,
          "label": "High",
          "depth": 1,
          "missing_slots": [2, 3, 4, 5]
        },
      ],
      "total": 2,
      "limit": 10,
      "offset": 0
    };

    int callCount = 0;
    final mock = MockClient((req) async {
      if (req.url.path.endsWith('/tree/stats')) {
        callCount++;
        return http.Response(jsonEncode(stats), 200);
      }
      if (req.url.path.endsWith('/tree/missing-slots-json')) {
        callCount++;
        return http.Response(jsonEncode(missing), 200);
      }
      return http.Response('Not Found', 404);
    });

    await tester
        .pumpWidget(MaterialApp(home: CompletenessScreen(client: mock)));
    await tester.pump();

    expect(find.textContaining('Nodes:'), findsOneWidget);
    expect(find.text('Parent ID'), findsOneWidget);
    expect(find.text('BP'), findsOneWidget);
    expect(find.text('3, 4, 5'), findsOneWidget);
    expect(callCount, 2); // stats + missing-slots called
  });
}
