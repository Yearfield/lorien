import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:lorien/shared/widgets/nav_shortcuts.dart';
import 'package:lorien/shared/widgets/app_scaffold.dart';

void main() {
  testWidgets('Ctrl+/ opens Help dialog', (tester) async {
    final r = GoRouter(routes: [
      GoRoute(
          path: '/',
          builder: (_, __) => const NavShortcuts(
              child: AppScaffold(title: 'Test', body: SizedBox())))
    ]);

    await tester.pumpWidget(MaterialApp.router(routerConfig: r));

    await tester.sendKeyDownEvent(LogicalKeyboardKey.control);
    await tester.sendKeyEvent(LogicalKeyboardKey.slash);
    await tester.sendKeyUpEvent(LogicalKeyboardKey.control);
    await tester.pumpAndSettle();

    expect(find.text('Keyboard Shortcuts'), findsOneWidget);
  });
}
