import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/screens/outcomes/outcomes_list_screen.dart';

void main() {
  testWidgets('OutcomesListScreen can be instantiated', (WidgetTester tester) async {
    // Just verify the widget can be created without crashing
    expect(() => const OutcomesListScreen(llmEnabled: false), returnsNormally);
  });
}
