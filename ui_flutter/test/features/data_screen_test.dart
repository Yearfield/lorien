import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/testing.dart';
import 'package:http/http.dart' as http;

import 'package:lorien/features/workspace/data_screen.dart';

void main() {
  testWidgets('DataScreen renders headers and rows', (tester) async {
    final payload = {
      "items": [
        {
          "Vital Measurement":"BP",
          "Node 1":"High",
          "Node 2":"Headache",
          "Node 3":"",
          "Node 4":"",
          "Node 5":"",
          "Diagnostic Triage":"Emergent",
          "Actions":"IV labetalol"
        }
      ],
      "total": 1,
      "limit": 10,
      "offset": 0
    };
    final mock = MockClient((req) async => http.Response(jsonEncode(payload), 200));

    await tester.pumpWidget(MaterialApp(home: DataScreen(client: mock)));
    await tester.pump(); // let FutureBuilder/fetch settle

    // Headers
    expect(find.text('Vital Measurement'), findsOneWidget);
    expect(find.text('Node 1'), findsOneWidget);
    expect(find.text('Node 2'), findsOneWidget);
    expect(find.text('Node 3'), findsOneWidget);
    expect(find.text('Node 4'), findsOneWidget);
    expect(find.text('Node 5'), findsOneWidget);
    expect(find.text('Diagnostic Triage'), findsOneWidget);
    expect(find.text('Actions'), findsOneWidget);

    // Row cell
    expect(find.text('BP'), findsOneWidget);
    expect(find.text('High'), findsOneWidget);
    expect(find.text('Headache'), findsOneWidget);
    expect(find.text('Emergent'), findsOneWidget);
    expect(find.text('IV labetalol'), findsOneWidget);
  });
}
