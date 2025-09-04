import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http_mock_adapter/http_mock_adapter.dart';
import 'package:dio/dio.dart';
import 'package:lorien/features/edit_tree/ui/edit_tree_screen.dart';
import 'package:lorien/features/edit_tree/data/edit_tree_repository.dart';
import 'package:lorien/features/edit_tree/data/edit_tree_provider.dart';
import 'package:lorien/features/edit_tree/state/edit_tree_controller.dart';
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

  testWidgets('EditTreeScreen loads and displays incomplete parents list',
      (WidgetTester tester) async {
    // Mock the incomplete parents API response
    dioAdapter.onGet(
      'http://test.com/api/v1/tree/parents/incomplete',
      (server) => server.reply(
        200,
        {
          'items': [
            {
              'parent_id': 1,
              'label': 'Test Parent 1',
              'depth': 0,
              'missing_slots': '2,4',
            },
            {
              'parent_id': 2,
              'label': 'Test Parent 2',
              'depth': 1,
              'missing_slots': '1,3,5',
            },
          ],
          'total': 2,
          'limit': 50,
          'offset': 0,
        },
      ),
    );

    // Mock children API response for when a parent is selected
    dioAdapter.onGet(
      'http://test.com/api/v1/tree/1/children',
      (server) => server.reply(
        200,
        [
          {'id': 101, 'slot': 1, 'label': 'Existing Child 1'},
          {'id': null, 'slot': 2, 'label': ''},
          {'id': 103, 'slot': 3, 'label': 'Existing Child 3'},
          {'id': null, 'slot': 4, 'label': ''},
          {'id': 105, 'slot': 5, 'label': 'Existing Child 5'},
        ],
      ),
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

    // Verify the screen loads
    expect(find.text('Edit Tree'), findsOneWidget);

    // Verify the list items are displayed
    expect(find.text('Test Parent 1'), findsOneWidget);
    expect(find.text('Test Parent 2'), findsOneWidget);
    expect(find.text('Missing: 2,4'), findsOneWidget);
    expect(find.text('Missing: 1,3,5'), findsOneWidget);

    // Verify the search field is present
    expect(find.byType(TextField), findsOneWidget);

    // Verify Next Incomplete button is present
    expect(find.text('Next Incomplete'), findsOneWidget);
  });

  testWidgets('Tapping parent item loads children in right pane',
      (WidgetTester tester) async {
    // Mock the incomplete parents API response
    dioAdapter.onGet(
      'http://test.com/api/v1/tree/parents/incomplete',
      (server) => server.reply(
        200,
        {
          'items': [
            {
              'parent_id': 1,
              'label': 'Test Parent 1',
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

    // Mock children API response
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

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Tap on the parent item
    await tester.tap(find.text('Test Parent 1'));
    await tester.pumpAndSettle();

    // Verify the right pane shows the parent details
    expect(find.text('Parent: Test Parent 1 (Depth 0)'), findsOneWidget);
    expect(find.text('Missing: 2,4'), findsOneWidget);

    // Verify all 5 slot cards are displayed
    expect(find.text('Slot 1'), findsOneWidget);
    expect(find.text('Slot 2'), findsOneWidget);
    expect(find.text('Slot 3'), findsOneWidget);
    expect(find.text('Slot 4'), findsOneWidget);
    expect(find.text('Slot 5'), findsOneWidget);

    // Verify existing vs empty indicators
    expect(find.text('Existing'), findsNWidgets(3)); // Slots 1, 3, 5
    expect(find.text('Empty'), findsNWidgets(2)); // Slots 2, 4

    // Verify Save All button is present
    expect(find.text('Save All  (Ctrl+S)'), findsOneWidget);
  });
}
