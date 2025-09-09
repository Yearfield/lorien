import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http_mock_adapter/http_mock_adapter.dart';
import 'package:dio/dio.dart';
import 'package:go_router/go_router.dart';
import 'package:lorien/features/symptoms/ui/symptoms_screen.dart';
import 'package:lorien/core/http/api_client.dart';
import 'package:lorien/state/app_settings_provider.dart';

void main() {
  late DioAdapter dioAdapter;
  late ProviderContainer container;
  late GoRouter router;

  setUp(() {
    dioAdapter = DioAdapter(dio: Dio());
    container = ProviderContainer(
      overrides: [
        dioProvider.overrideWithValue(dioAdapter.dio),
        apiBaseUrlProvider.overrideWithValue('http://test.com/api/v1'),
      ],
    );

    router = GoRouter(
      initialLocation: '/symptoms',
      routes: [
        GoRoute(
          path: '/symptoms',
          builder: (_, __) => const SymptomsScreen(),
        ),
        GoRoute(
          path: '/edit-tree',
          builder: (ctx, st) => Scaffold(
            body: Center(
              child: Text('Edit Tree Screen - Parent ID: ${st.extra}'),
            ),
          ),
        ),
      ],
    );
  });

  tearDown(() {
    container.dispose();
  });

  testWidgets('Next Incomplete navigates to edit-tree with parent ID',
      (WidgetTester tester) async {
    // Mock the next incomplete API response
    dioAdapter.onGet(
      'http://test.com/api/v1/tree/next-incomplete-parent',
      (server) => server.reply(
        200,
        {
          'parent_id': 7,
          'label': 'Test Parent',
          'depth': 1,
          'missing_slots': '2,4',
        },
      ),
    );

    // Mock the roots API response for reset
    dioAdapter.onGet(
      'http://test.com/api/v1/tree/roots',
      (server) => server.reply(
        200,
        {
          'count': 5,
          'roots': ['Root 1', 'Root 2', 'Root 3'],
        },
      ),
    );

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: MaterialApp.router(
          routerConfig: router,
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Find and tap the "Next Incomplete Parent" button
    final nextIncompleteButton = find.text('Next Incomplete Parent');
    expect(nextIncompleteButton, findsOneWidget);

    await tester.tap(nextIncompleteButton);
    await tester.pumpAndSettle();

    // Verify navigation occurred to edit-tree route
    expect(find.text('Edit Tree Screen - Parent ID: 7'), findsOneWidget);
  });

  testWidgets('Next Incomplete handles no incomplete parents gracefully',
      (WidgetTester tester) async {
    // Mock the next incomplete API response with no results
    dioAdapter.onGet(
      'http://test.com/api/v1/tree/next-incomplete-parent',
      (server) => server.reply(204, null),
    );

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: MaterialApp.router(
          routerConfig: router,
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Find and tap the "Next Incomplete Parent" button
    final nextIncompleteButton = find.text('Next Incomplete Parent');
    expect(nextIncompleteButton, findsOneWidget);

    await tester.tap(nextIncompleteButton);
    await tester.pumpAndSettle();

    // Verify snackbar message is shown
    expect(find.text('All parents complete.'), findsOneWidget);

    // Verify we stayed on the symptoms screen
    expect(find.text('Symptoms'), findsOneWidget);
  });
}
