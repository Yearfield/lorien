import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:http_mock_adapter/http_mock_adapter.dart';
import 'package:mockito/mockito.dart';
import 'package:lorien/features/symptoms/ui/symptoms_screen.dart';
import 'package:lorien/core/http/api_client.dart';

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

  testWidgets('Selections reset when root changes', (tester) async {
    // Mock initial roots response
    dioAdapter.onGet(
        '/tree/roots', (server) => server.reply(200, ['Root A', 'Root B']));

    // Mock options response when root changes
    dioAdapter.onGet(
        '/calc/options',
        (server) => server.reply(200, {
              'n1': ['Option 1A', 'Option 1B'],
              'n2': [],
              'n3': [],
              'n4': [],
              'n5': [],
              'remaining': 10
            }),
        queryParameters: {'root': 'Root A'});

    await tester.pumpWidget(
      ProviderScope(
        parent: container,
        child: const MaterialApp(home: SymptomsScreen()),
      ),
    );

    await tester.pump(); // Load roots

    // Select root
    await tester.tap(find.text('Vital Measurement'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Root A'));
    await tester.pumpAndSettle();

    // Select Node 1
    await tester.tap(find.text('Node 1'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Option 1A'));
    await tester.pumpAndSettle();

    // Change root - should reset Node 1 and below
    await tester.tap(find.text('Root A'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Root B'));
    await tester.pumpAndSettle();

    // Verify Node 1 is reset
    expect(find.text('Option 1A'), findsNothing);
  });

  testWidgets('Leaf preview shows when at leaf', (tester) async {
    // Mock responses
    dioAdapter.onGet('/tree/roots', (server) => server.reply(200, ['Root A']));

    dioAdapter.onGet(
        '/calc/options',
        (server) => server.reply(200, {
              'n1': ['Option 1A'],
              'n2': ['Option 2A'],
              'n3': ['Option 3A'],
              'n4': ['Option 4A'],
              'n5': ['Option 5A'],
              'remaining': 1,
              'leaf_id': '123'
            }),
        queryParameters: {
          'root': 'Root A',
          'n1': 'Option 1A',
          'n2': 'Option 2A',
          'n3': 'Option 3A',
          'n4': 'Option 4A'
        });

    dioAdapter.onGet(
        '/triage/123',
        (server) => server.reply(200,
            {'diagnostic_triage': 'Test triage', 'actions': 'Test actions'}));

    await tester.pumpWidget(
      ProviderScope(
        parent: container,
        child: const MaterialApp(home: SymptomsScreen()),
      ),
    );

    await tester.pump();

    // Select all levels to reach leaf
    await tester.tap(find.text('Vital Measurement'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Root A'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Node 1'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Option 1A'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Node 2'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Option 2A'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Node 3'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Option 3A'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Node 4'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Option 4A'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Node 5'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Option 5A'));
    await tester.pumpAndSettle();

    // Verify preview appears
    expect(find.text('Outcomes (preview)'), findsOneWidget);
    expect(find.text('Test triage'), findsOneWidget);
    expect(find.text('Test actions'), findsOneWidget);
  });
}
