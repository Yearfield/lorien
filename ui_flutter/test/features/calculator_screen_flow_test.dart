import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

import '../../lib/features/workspace/calculator_screen.dart';

void main() {
  testWidgets('Calculator: pick root → see options → choose next', (tester) async {
    final client = MockClient((req) async {
      if (req.url.path.endsWith('/tree/root-options')) {
        return http.Response(jsonEncode({"items":["BP"],"total":1,"limit":200,"offset":0}), 200);
      }
      if (req.url.path.endsWith('/tree/navigate') && req.url.queryParameters["root"]=="BP" && !req.url.queryParameters.containsKey("n1")) {
        return http.Response(jsonEncode({"root":{"label":"BP","id":1},"node_id":1,"depth":0,"path":["BP"],"options":[{"slot":1,"label":"High"},{"slot":2,"label":"Low"}],"outcome":null}),200);
      }
      if (req.url.path.endsWith('/tree/navigate') && req.url.queryParameters["n1"]=="High") {
        return http.Response(jsonEncode({"root":{"label":"BP","id":1},"node_id":2,"depth":1,"path":["BP","High"],"options":[{"slot":1,"label":"Headache"}],"outcome":null}),200);
      }
      return http.Response('Not found', 404);
    });

    await tester.pumpWidget(MaterialApp(home: CalculatorScreen(client: client)));
    await tester.pumpAndSettle();

    // Open root dropdown and pick BP
    await tester.tap(find.byType(DropdownButtonFormField<String>).first);
    await tester.pumpAndSettle();
    await tester.tap(find.text('BP').last);
    await tester.pumpAndSettle();

    // Expect options
    expect(find.text('High'), findsOneWidget);
    await tester.tap(find.text('High'));
    await tester.pumpAndSettle();

    // Next level shows Headache option
    expect(find.text('Headache'), findsOneWidget);
  });
}
