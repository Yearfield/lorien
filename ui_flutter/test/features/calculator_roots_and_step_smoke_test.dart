import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import '../../lib/features/workspace/calculator_screen.dart';

void main() {
  testWidgets('Calculator loads roots and steps', (tester) async {
    final client = MockClient((req) async {
      if (req.url.path.endsWith('/tree/root-options')) {
        return http.Response(jsonEncode({"items":["Pulse"],"total":1,"limit":200,"offset":0}), 200);
      }
      if (req.url.path.endsWith('/tree/navigate') && 
          req.url.queryParameters["root"]=="Pulse" && 
          !req.url.queryParameters.containsKey("n1")) {
        return http.Response(jsonEncode({
          "root":{"label":"Pulse","id":1},
          "node_id":1,
          "depth":0,
          "path":["Pulse"],
          "options":[{"slot":1,"label":"Low"}],
          "outcome":null
        }), 200);
      }
      return http.Response('404', 404);
    });

    await tester.pumpWidget(
      MaterialApp(
        home: CalculatorScreen(client: client),
      ),
    );
    await tester.pumpAndSettle();
    
    // Tap the dropdown to open it
    await tester.tap(find.byType(DropdownButtonFormField<String>).first);
    await tester.pumpAndSettle();
    
    // Select Pulse
    await tester.tap(find.text('Pulse').last);
    await tester.pumpAndSettle();
    
    // Verify Low option appears
    expect(find.text('Low'), findsOneWidget);
  });
}
