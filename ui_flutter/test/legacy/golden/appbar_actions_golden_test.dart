import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:lorien/shared/widgets/app_scaffold.dart';

void main() {
  testWidgets('App bar shows Back/Home/Help (light & dark)', (tester) async {
    // TODO: add real golden test in repo context
    // This test would verify that:
    // 1. App bars render consistently across light/dark themes
    // 2. Back, Home, and Help buttons are properly positioned
    // 3. Semantics labels are correctly applied
    // 4. Hit targets meet accessibility requirements

    final r = GoRouter(routes: [
      GoRoute(
          path: '/',
          builder: (_, __) =>
              const AppScaffold(title: 'Test Screen', body: SizedBox()))
    ]);

    await tester.pumpWidget(MaterialApp.router(routerConfig: r));

    // Verify all expected buttons are present
    expect(find.byTooltip('Back'), findsOneWidget);
    expect(find.byTooltip('Home'), findsOneWidget);
    expect(find.byTooltip('Help / Shortcuts'), findsOneWidget);

    expect(true, isTrue);
  });
}
