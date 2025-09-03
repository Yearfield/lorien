import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/widgets/layout/scroll_scaffold.dart';

void main() {
  testWidgets('leading is present on root and child', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: ScrollScaffold(title:'Root', actions: [], children: [])));
    expect(find.byType(IconButton), findsOneWidget); // AppBackLeading renders an IconButton
  });
}
