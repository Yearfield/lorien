import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http_mock_adapter/http_mock_adapter.dart';
import 'package:dio/dio.dart';
import 'package:lorien/features/outcomes/ui/outcomes_detail_screen.dart';
import 'package:lorien/core/http/api_client.dart';
import 'package:lorien/state/app_settings_provider.dart';

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

  testWidgets('vm param pre-fills fields from search results',
      (WidgetTester tester) async {
    // Mock the breadcrumb API
    dioAdapter.onGet(
      'http://test.com/api/v1/tree/path?node_id=test_id',
      (server) => server.reply(
        200,
        {
          'node_id': 'test_id',
          'is_leaf': true,
          'depth': 5,
          'vital_measurement': 'Hypertension',
          'nodes': ['Node 1', 'Node 2', 'Node 3', 'Node 4', 'Node 5'],
          'csv_header': [
            'Vital Measurement',
            'Node 1',
            'Node 2',
            'Node 3',
            'Node 4',
            'Node 5',
            'Diagnostic Triage',
            'Actions'
          ],
        },
      ),
    );

    // Mock the LLM health check
    dioAdapter.onGet(
      'http://test.com/api/v1/llm/health',
      (server) => server.reply(
        200,
        {
          'ok': true,
          'llm_enabled': true,
          'ready': true,
          'checked_at': '2024-01-01T12:00:00.000Z',
        },
      ),
    );

    // Mock the search API with vm parameter
    dioAdapter.onGet(
      'http://test.com/api/v1/outcomes/search?vm=Hypertension&limit=1',
      (server) => server.reply(
        200,
        [
          {
            'id': 'outcome_123',
            'diagnostic_triage': 'Hypertension diagnosis with elevated BP',
            'actions': 'Prescribe medication and lifestyle changes',
            'created_at': '2024-01-01T10:00:00.000Z',
          },
        ],
      ),
    );

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(
          home: OutcomesDetailScreen(
            outcomeId: 'test_id',
            vm: 'Hypertension',
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Verify the fields are pre-filled with data from the VM search
    final triageField = find.byType(TextField).first;
    final actionsField = find.byType(TextField).last;

    // Check that the triage field contains the expected text
    expect(
        find.text('Hypertension diagnosis with elevated BP'), findsOneWidget);

    // Check that the actions field contains the expected text
    expect(find.text('Prescribe medication and lifestyle changes'),
        findsOneWidget);
  });

  testWidgets('without vm param loads existing outcome data',
      (WidgetTester tester) async {
    // Mock the breadcrumb API
    dioAdapter.onGet(
      'http://test.com/api/v1/tree/path?node_id=test_id',
      (server) => server.reply(
        200,
        {
          'node_id': 'test_id',
          'is_leaf': true,
          'depth': 5,
          'vital_measurement': 'Diabetes',
          'nodes': ['Node 1', 'Node 2', 'Node 3', 'Node 4', 'Node 5'],
          'csv_header': [
            'Vital Measurement',
            'Node 1',
            'Node 2',
            'Node 3',
            'Node 4',
            'Node 5',
            'Diagnostic Triage',
            'Actions'
          ],
        },
      ),
    );

    // Mock the LLM health check
    dioAdapter.onGet(
      'http://test.com/api/v1/llm/health',
      (server) => server.reply(
        200,
        {
          'ok': true,
          'llm_enabled': true,
          'ready': true,
          'checked_at': '2024-01-01T12:00:00.000Z',
        },
      ),
    );

    // Mock the detail API (existing outcome data)
    dioAdapter.onGet(
      'http://test.com/api/v1/outcomes/test_id',
      (server) => server.reply(
        200,
        {
          'id': 'test_id',
          'diagnostic_triage': 'Existing triage data',
          'actions': 'Existing actions data',
        },
      ),
    );

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(
          home: OutcomesDetailScreen(
            outcomeId: 'test_id',
            // No vm parameter
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Verify the fields contain the existing outcome data (not pre-filled from VM)
    expect(find.text('Existing triage data'), findsOneWidget);
    expect(find.text('Existing actions data'), findsOneWidget);
  });

  testWidgets('vm param with no search results falls back gracefully',
      (WidgetTester tester) async {
    // Mock the breadcrumb API
    dioAdapter.onGet(
      'http://test.com/api/v1/tree/path?node_id=test_id',
      (server) => server.reply(
        200,
        {
          'node_id': 'test_id',
          'is_leaf': true,
          'depth': 5,
          'vital_measurement': 'Unknown Condition',
          'nodes': ['Node 1', 'Node 2', 'Node 3', 'Node 4', 'Node 5'],
          'csv_header': [
            'Vital Measurement',
            'Node 1',
            'Node 2',
            'Node 3',
            'Node 4',
            'Node 5',
            'Diagnostic Triage',
            'Actions'
          ],
        },
      ),
    );

    // Mock the LLM health check
    dioAdapter.onGet(
      'http://test.com/api/v1/llm/health',
      (server) => server.reply(
        200,
        {
          'ok': true,
          'llm_enabled': true,
          'ready': true,
          'checked_at': '2024-01-01T12:00:00.000Z',
        },
      ),
    );

    // Mock the search API with no results
    dioAdapter.onGet(
      'http://test.com/api/v1/outcomes/search?vm=Unknown%20Condition&limit=1',
      (server) => server.reply(200, []),
    );

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(
          home: OutcomesDetailScreen(
            outcomeId: 'test_id',
            vm: 'Unknown Condition',
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Verify the fields are empty (graceful fallback)
    final triageField = find.byType(TextField).first;
    final actionsField = find.byType(TextField).last;

    // The fields should be empty or have placeholder text
    // This test verifies that no crash occurs and the screen loads properly
    expect(find.byType(TextField), findsNWidgets(2));
  });
}
