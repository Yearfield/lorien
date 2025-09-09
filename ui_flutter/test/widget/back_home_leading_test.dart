import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/widgets/app_back_leading.dart';

void main() {
  testWidgets('shows Home on root, Back when canPop', (tester) async {
    // Test Home icon on root page (no back navigation available)
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        appBar: AppBar(leading: const AppBackLeading()),
      ),
    ));

    expect(find.byIcon(Icons.home), findsOneWidget);
    expect(find.byIcon(Icons.arrow_back), findsNothing);

    // Test Back icon when navigation is available
    await tester.pumpWidget(MaterialApp(
      home: Builder(
        builder: (context) => ElevatedButton(
          onPressed: () {
            Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) => Scaffold(
                  appBar: AppBar(leading: const AppBackLeading()),
                ),
              ),
            );
          },
          child: const Text('navigate'),
        ),
      ),
    ));

    await tester.tap(find.text('navigate'));
    await tester.pumpAndSettle();

    expect(find.byIcon(Icons.arrow_back), findsOneWidget);
    expect(find.byIcon(Icons.home), findsNothing);
  });
}
