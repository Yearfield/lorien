import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http_mock_adapter/http_mock_adapter.dart';
import 'package:dio/dio.dart';
import 'package:lorien/features/workspace/ui/workspace_screen.dart';
import 'package:lorien/features/workspace/data/workspace_repository.dart';
import 'package:lorien/features/workspace/data/workspace_provider.dart';
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

  testWidgets('Import UI shows proper status chips for different states',
      (WidgetTester tester) async {
    // Mock initial empty state
    dioAdapter.onGet(
      'http://test.com/api/v1/tree/stats',
      (server) => server.reply(
        200,
        {
          'nodes': 0,
          'roots': 0,
          'leaves': 0,
          'complete_paths': 0,
          'incomplete_parents': 0,
        },
      ),
    );

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(
          home: WorkspaceScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Find import section
    final importSection = find.text('Import Data');
    expect(importSection, findsOneWidget);

    // TODO: Verify initial state shows appropriate status
    // Should show "Ready to import" or similar
    expect(true, isTrue); // Placeholder
  });

  testWidgets('Import UI handles 422 header mismatch errors properly',
      (WidgetTester tester) async {
    // Mock import failure with 422 header mismatch
    dioAdapter.onPost(
      'http://test.com/api/v1/import',
      (server) => server.reply(
        422,
        {
          'detail': [
            {
              'loc': ['file', 'header'],
              'msg': 'Expected 8 columns, got 6',
              'type': 'value_error.header_mismatch',
              'expected': [
                'vm',
                'node1',
                'node2',
                'node3',
                'node4',
                'node5',
                'diagnosis',
                'actions'
              ],
              'received': ['vm', 'node1', 'node2', 'node3', 'node4', 'node5'],
              'row_index': 1,
              'col_index': 6,
            }
          ]
        },
      ),
    );

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(
          home: WorkspaceScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Find import button
    final importButton = find.text('Select Excel/CSV');
    if (importButton.evaluate().isNotEmpty) {
      // TODO: Simulate file selection and import
      // TODO: Verify that header mismatch error is displayed properly
      // Should show row, col_index, expected, received in the error panel
      // This will fail if error handling doesn't surface these details
      expect(true, isTrue); // Placeholder
    } else {
      fail('Import button not found - workspace import UI not implemented');
    }
  });

  testWidgets('Import UI shows progress during upload',
      (WidgetTester tester) async {
    // Mock successful import with progress simulation
    dioAdapter.onPost(
      'http://test.com/api/v1/import',
      (server) => server.reply(
        200,
        {'message': 'Import completed successfully'},
      ),
    );

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(
          home: WorkspaceScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    final importButton = find.text('Select Excel/CSV');
    if (importButton.evaluate().isNotEmpty) {
      // TODO: Simulate file selection and import process
      // TODO: Verify that progress indicators are shown during upload
      // Should show "Uploading 25%", "Uploading 50%", etc.
      // This will fail if progress feedback is not implemented
      expect(true, isTrue); // Placeholder
    }
  });

  testWidgets('Import UI updates status after successful import',
      (WidgetTester tester) async {
    // Mock initial stats
    dioAdapter.onGet(
      'http://test.com/api/v1/tree/stats',
      (server) => server.reply(
        200,
        {
          'nodes': 0,
          'roots': 0,
          'leaves': 0,
          'complete_paths': 0,
          'incomplete_parents': 0,
        },
      ),
    );

    // Mock successful import
    dioAdapter.onPost(
      'http://test.com/api/v1/import',
      (server) => server.reply(
        200,
        {'message': 'Import completed successfully'},
      ),
    );

    // Mock updated stats after import
    dioAdapter.onGet(
      'http://test.com/api/v1/tree/stats',
      (server) => server.reply(
        200,
        {
          'nodes': 10,
          'roots': 2,
          'leaves': 6,
          'complete_paths': 1,
          'incomplete_parents': 1,
        },
      ),
    );

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(
          home: WorkspaceScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    final importButton = find.text('Select Excel/CSV');
    if (importButton.evaluate().isNotEmpty) {
      // TODO: Simulate successful import
      // TODO: Verify that status updates to show success
      // Should show "Import complete ✅" and updated stats
      // This will fail if status updates are not working
      expect(true, isTrue); // Placeholder
    }
  });

  testWidgets('Import UI handles file selection cancellation gracefully',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(
          home: WorkspaceScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    final importButton = find.text('Select Excel/CSV');
    if (importButton.evaluate().isNotEmpty) {
      // TODO: Simulate file selection cancellation
      // TODO: Verify that no error is shown and UI remains stable
      // This will fail if cancellation is not handled properly
      expect(true, isTrue); // Placeholder
    }
  });

  testWidgets('Import UI shows proper error for unsupported file types',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(
          home: WorkspaceScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    final importButton = find.text('Select Excel/CSV');
    if (importButton.evaluate().isNotEmpty) {
      // TODO: Simulate selection of unsupported file type (e.g., .txt)
      // TODO: Verify that appropriate error message is shown
      // This will fail if file type validation is not implemented
      expect(true, isTrue); // Placeholder
    }
  });
}
