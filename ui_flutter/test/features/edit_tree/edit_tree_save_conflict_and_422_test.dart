import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http_mock_adapter/http_mock_adapter.dart';
import 'package:dio/dio.dart';
import 'package:lorien/features/edit_tree/ui/edit_tree_screen.dart';
import 'package:lorien/features/edit_tree/data/edit_tree_provider.dart';
import 'package:lorien/core/http/api_client.dart';

void main() {
  late DioAdapter dioAdapter;
  late ProviderContainer container;

  setUp(() {
    dioAdapter = DioAdapter(dio: Dio());
    container = ProviderContainer(
      overrides: [
        dioProvider.overrideWithValue(dioAdapter.dio),
        apiBaseUrlProvider.overrideWithValue('http://test.com/api/v1'),
      ],
    );
  });

  tearDown(() {
    container.dispose();
  });

  testWidgets('Save operation handles 409 conflict correctly',
      (WidgetTester tester) async {
    // Mock initial load
    dioAdapter.onGet(
      'http://test.com/api/v1/tree/parents/incomplete',
      (server) => server.reply(
        200,
        {
          'items': [
            {
              'parent_id': 1,
              'label': 'Test Parent',
              'depth': 0,
              'missing_slots': '2,4',
            },
          ],
          'total': 1,
          'limit': 50,
          'offset': 0,
        },
      ),
    );

    dioAdapter.onGet(
      'http://test.com/api/v1/tree/1/children',
      (server) => server.reply(
        200,
        [
          {'id': 101, 'slot': 1, 'label': 'Child 1'},
          {'id': null, 'slot': 2, 'label': ''},
          {'id': 103, 'slot': 3, 'label': 'Child 3'},
          {'id': null, 'slot': 4, 'label': ''},
          {'id': 105, 'slot': 5, 'label': 'Child 5'},
        ],
      ),
    );

    // Mock save with 409 conflict
    dioAdapter.onPut(
      'http://test.com/api/v1/tree/parents/1/children',
      (server) => server.reply(
        409,
        {
          'error': 'slot_conflict',
          'slot': 2,
          'hint': 'Concurrent edit',
        },
      ),
      data: {
        'slots': [
          {'slot': 1, 'label': 'Child 1'},
          {'slot': 2, 'label': 'New Child 2'},
          {'slot': 3, 'label': 'Child 3'},
          {'slot': 4, 'label': 'New Child 4'},
          {'slot': 5, 'label': 'Child 5'},
        ],
        'mode': 'upsert',
      },
    );

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Select the parent
    await tester.tap(find.text('Test Parent'));
    await tester.pumpAndSettle();

    // Enter text in slot 2
    final slot2Field = find.byKey(const ValueKey('slot_2'));
    await tester.enterText(slot2Field, 'New Child 2');
    await tester.pumpAndSettle();

    // Enter text in slot 4
    final slot4Field = find.byKey(const ValueKey('slot_4'));
    await tester.enterText(slot4Field, 'New Child 4');
    await tester.pumpAndSettle();

    // Tap Save All
    await tester.tap(find.text('Save All  (Ctrl+S)'));
    await tester.pumpAndSettle();

    // Verify error message appears on slot 2
    expect(
      find.text('Concurrent edit on slot 2. Reload and retry.'),
      findsOneWidget,
    );

    // Verify slot 4 field still has the entered text (user input preserved)
    final slot4TextField = tester.widget<TextField>(slot4Field);
    expect(slot4TextField.controller?.text, 'New Child 4');
  });

  testWidgets('Save operation handles 422 validation errors correctly',
      (WidgetTester tester) async {
    // Mock initial load
    dioAdapter.onGet(
      'http://test.com/api/v1/tree/parents/incomplete',
      (server) => server.reply(
        200,
        {
          'items': [
            {
              'parent_id': 1,
              'label': 'Test Parent',
              'depth': 0,
              'missing_slots': '2,4',
            },
          ],
          'total': 1,
          'limit': 50,
          'offset': 0,
        },
      ),
    );

    dioAdapter.onGet(
      'http://test.com/api/v1/tree/1/children',
      (server) => server.reply(
        200,
        [
          {'id': 101, 'slot': 1, 'label': 'Child 1'},
          {'id': null, 'slot': 2, 'label': ''},
          {'id': 103, 'slot': 3, 'label': 'Child 3'},
          {'id': null, 'slot': 4, 'label': ''},
          {'id': 105, 'slot': 5, 'label': 'Child 5'},
        ],
      ),
    );

    // Mock save with 422 validation error
    dioAdapter.onPut(
      'http://test.com/api/v1/tree/parents/1/children',
      (server) => server.reply(
        422,
        {
          'detail': [
            {
              'loc': ['body', 'slots'],
              'msg': 'label must be alnum/comma/hyphen/space',
              'type': 'value_error',
              'ctx': {'slot': 2},
            },
            {
              'loc': ['body', 'slots'],
              'msg': 'label cannot be empty',
              'type': 'value_error',
              'ctx': {'slot': 4},
            },
          ],
        },
      ),
      data: {
        'slots': [
          {'slot': 1, 'label': 'Child 1'},
          {'slot': 2, 'label': 'Invalid@Chars!'},
          {'slot': 3, 'label': 'Child 3'},
          {'slot': 4, 'label': ''},
          {'slot': 5, 'label': 'Child 5'},
        ],
        'mode': 'upsert',
      },
    );

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Select the parent
    await tester.tap(find.text('Test Parent'));
    await tester.pumpAndSettle();

    // Enter invalid text in slot 2
    final slot2Field = find.byKey(const ValueKey('slot_2'));
    await tester.enterText(slot2Field, 'Invalid@Chars!');
    await tester.pumpAndSettle();

    // Leave slot 4 empty
    final slot4Field = find.byKey(const ValueKey('slot_4'));
    await tester.enterText(slot4Field, '');
    await tester.pumpAndSettle();

    // Tap Save All
    await tester.tap(find.text('Save All  (Ctrl+S)'));
    await tester.pumpAndSettle();

    // Verify validation errors appear
    expect(
      find.text('label must be alnum/comma/hyphen/space'),
      findsOneWidget,
    );
    expect(find.text('label cannot be empty'), findsOneWidget);
  });
}
