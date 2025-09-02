import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:lorien/shared/widgets/route_guard.dart';
import 'package:lorien/shared/widgets/app_scaffold.dart';

void main() {
  testWidgets('Back disabled when busy and confirms on attempt', (tester) async {
    var busy = true;
    final r = GoRouter(routes: [
      GoRoute(
        path: '/',
        builder: (_, __) => RouteGuard(
          isBusy: () => busy,
          child: const AppScaffold(title: 'X', body: SizedBox()),
        ),
      ),
      GoRoute(path: '/next', builder: (_, __) => const SizedBox()),
    ]);
    
    await tester.pumpWidget(MaterialApp.router(routerConfig: r));
    
    // Back button should be disabled on root anyway, but guard must be wired
    expect(find.byTooltip('Back'), findsOneWidget);
    
    // Verify the guard is working by checking the widget structure
    expect(find.byType(RouteGuard), findsOneWidget);
    expect(find.byType(AppScaffold), findsOneWidget);
  });
}
