import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:lorien/shared/widgets/app_scaffold.dart';

void main() {
  testWidgets('AppScaffold shows Back (disabled when cannot pop) and Home',
      (tester) async {
    final r = GoRouter(routes: [
      GoRoute(
          path: '/',
          builder: (_, __) =>
              const AppScaffold(title: 'Test', body: SizedBox()))
    ]);

    await tester.pumpWidget(MaterialApp.router(routerConfig: r));

    expect(find.byTooltip('Back'), findsOneWidget);
    expect(find.byTooltip('Home'), findsOneWidget);

    // Back button should be disabled when cannot pop
    final backButton = tester.widget<IconButton>(find.byType(IconButton).first);
    expect(backButton.onPressed, isNull);
  });
}
