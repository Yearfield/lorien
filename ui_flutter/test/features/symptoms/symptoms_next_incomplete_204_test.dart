import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:http_mock_adapter/http_mock_adapter.dart';
import 'package:mockito/mockito.dart';
import '../../../lib/features/symptoms/ui/symptoms_screen.dart';
import '../../../lib/features/symptoms/data/symptoms_repository.dart';
import '../../../lib/core/http/api_client.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late DioAdapter dioAdapter;
  late ProviderContainer container;
  late Dio mockDio;

  setUp(() {
    mockDio = MockDio();
    dioAdapter = DioAdapter(dio: mockDio);
    container = ProviderContainer(overrides: [
      dioProvider.overrideWithValue(mockDio),
    ]);
  });

  tearDown(() {
    container.dispose();
  });

  testWidgets('Shows snackbar when all parents complete (204)', (tester) async {
    // Mock 204 response for next incomplete
    dioAdapter.onGet('/tree/next-incomplete-parent',
      (server) => server.reply(204, null));

    await tester.pumpWidget(
      ProviderScope(
        parent: container,
        child: const MaterialApp(home: SymptomsScreen()),
      ),
    );

    await tester.pump();

    // Tap Next Incomplete button
    await tester.tap(find.text('Next Incomplete Parent'));
    await tester.pumpAndSettle();

    // Verify snackbar appears
    expect(find.text('All parents complete.'), findsOneWidget);
  });

  testWidgets('Shows dialog with next incomplete parent details', (tester) async {
    // Mock response with parent details
    dioAdapter.onGet('/tree/next-incomplete-parent',
      (server) => server.reply(200, {
        'parent_id': 42,
        'label': 'Test Parent',
        'missing_slots': 2,
        'depth': 3
      }));

    await tester.pumpWidget(
      ProviderScope(
        parent: container,
        child: const MaterialApp(home: SymptomsScreen()),
      ),
    );

    await tester.pump();

    // Tap Next Incomplete button
    await tester.tap(find.text('Next Incomplete Parent'));
    await tester.pumpAndSettle();

    // Verify dialog appears with details
    expect(find.text('Next incomplete parent'), findsOneWidget);
    expect(find.text('ID: 42'), findsOneWidget);
    expect(find.text('Label: Test Parent'), findsOneWidget);
    expect(find.text('Missing slots: 2'), findsOneWidget);
    expect(find.text('Depth: 3'), findsOneWidget);
  });

  testWidgets('Handles 200 response with null parent_id as empty', (tester) async {
    // Mock response with null parent_id
    dioAdapter.onGet('/tree/next-incomplete-parent',
      (server) => server.reply(200, {'parent_id': null}));

    await tester.pumpWidget(
      ProviderScope(
        parent: container,
        child: const MaterialApp(home: SymptomsScreen()),
      ),
    );

    await tester.pump();

    // Tap Next Incomplete button
    await tester.tap(find.text('Next Incomplete Parent'));
    await tester.pumpAndSettle();

    // Verify snackbar appears
    expect(find.text('All parents complete.'), findsOneWidget);
  });

  testWidgets('Shows error snackbar on API failure', (tester) async {
    // Mock error response
    dioAdapter.onGet('/tree/next-incomplete-parent',
      (server) => server.reply(500, {'error': 'Server error'}));

    await tester.pumpWidget(
      ProviderScope(
        parent: container,
        child: const MaterialApp(home: SymptomsScreen()),
      ),
    );

    await tester.pump();

    // Tap Next Incomplete button
    await tester.tap(find.text('Next Incomplete Parent'));
    await tester.pumpAndSettle();

    // Verify error snackbar appears
    expect(find.textContaining('Failed to find next incomplete'), findsOneWidget);
  });
}
