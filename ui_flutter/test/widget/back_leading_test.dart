import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/widgets/app_back_leading.dart';

void main() {
  testWidgets('Back leading is hidden on root, visible after push',
      (tester) async {
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(appBar: AppBar(leading: const AppBackLeading())),
    ));
    expect(find.byType(IconButton), findsNothing);

    await tester.pumpWidget(MaterialApp(
      home: Navigator(
        onGenerateRoute: (s) => MaterialPageRoute(
          builder: (_) => Scaffold(
            appBar: AppBar(leading: const AppBackLeading()),
            body: Builder(
              builder: (context) => TextButton(
                onPressed: () => Navigator.of(context).push(MaterialPageRoute(
                    builder: (_) => Scaffold(
                        appBar: AppBar(leading: const AppBackLeading())))),
                child: const Text('go'),
              ),
            ),
          ),
        ),
      ),
    ));
    await tester.tap(find.text('go'));
    await tester.pumpAndSettle();
    expect(find.byType(IconButton), findsOneWidget);
  });
}
