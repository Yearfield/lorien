import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mockito/mockito.dart';
import 'package:dio/dio.dart';

import '../../../lib/features/conflicts/state/conflicts_provider.dart';
import '../../../lib/features/conflicts/data/conflicts_repository.dart';

// Manual mocks
class MockConflictsRepository extends Mock implements ConflictsRepository {}
class MockDio extends Mock implements Dio {}

void main() {
  group('Conflicts Progress HUD Tests', () {
    late MockConflictsRepository mockRepository;
    late MockDio mockDio;

    setUp(() {
      mockDio = MockDio();
      mockRepository = MockConflictsRepository();
    });

    testWidgets('On initial list, shows "Resolved 0 of X"', (WidgetTester tester) async {
      final container = ProviderContainer(
        overrides: [
          conflictsRepositoryProvider.overrideWithValue(mockRepository),
        ],
      );

      final notifier = container.read(conflictsListProvider.notifier);
      
      // Mock initial response with 10 conflicts
      when(mockRepository.listConflicts(
        limit: anyNamed('limit'),
        offset: anyNamed('offset'),
        onlyExactFive: anyNamed('onlyExactFive'),
        onlyDuplicateParents: anyNamed('onlyDuplicateParents'),
      )).thenAnswer((_) async => ConflictsPage(
        items: List.generate(10, (i) => ConflictItem(
          parentId: i + 1,
          label: 'Conflict $i',
          depth: 1,
          childCount: 5,
          slotDupCount: 0,
          nullSlotCount: 0,
          overfilled: false,
          underfilled: false,
          duplicateParents: 1,
        )),
        total: 10,
        limit: 25,
        offset: 0,
      ));

      // Load conflicts
      await notifier.loadConflicts();
      
      // Check initial state
      expect(notifier.state.totalConflictsInitial, 10);
      expect(notifier.state.currentCount, 10);
      expect(notifier.state.resolvedCount, 0);
      expect(notifier.state.progress, 0.0);
    });

    testWidgets('After resolving one conflict, shows "Resolved 1 of X"', (WidgetTester tester) async {
      final container = ProviderContainer(
        overrides: [
          conflictsRepositoryProvider.overrideWithValue(mockRepository),
        ],
      );

      final listNotifier = container.read(conflictsListProvider.notifier);
      final groupNotifier = container.read(conflictsGroupProvider.notifier);
      
      // Mock initial response with 10 conflicts
      when(mockRepository.listConflicts(
        limit: anyNamed('limit'),
        offset: anyNamed('offset'),
        onlyExactFive: anyNamed('onlyExactFive'),
        onlyDuplicateParents: anyNamed('onlyDuplicateParents'),
      )).thenAnswer((_) async => ConflictsPage(
        items: List.generate(10, (i) => ConflictItem(
          parentId: i + 1,
          label: 'Conflict $i',
          depth: 1,
          childCount: 5,
          slotDupCount: 0,
          nullSlotCount: 0,
          overfilled: false,
          underfilled: false,
          duplicateParents: 1,
        )),
        total: 10,
        limit: 25,
        offset: 0,
      ));

      // Load initial conflicts
      await listNotifier.loadConflicts();
      
      // Mock resolve group (successful)
      when(mockRepository.resolveGroup(
        keepId: anyNamed('keepId'),
        chosen: anyNamed('chosen'),
      )).thenAnswer((_) async {});
      
      // Mock refresh after resolve (one fewer conflict)
      when(mockRepository.listConflicts(
        limit: anyNamed('limit'),
        offset: anyNamed('offset'),
        onlyExactFive: anyNamed('onlyExactFive'),
        onlyDuplicateParents: anyNamed('onlyDuplicateParents'),
      )).thenAnswer((_) async => ConflictsPage(
        items: List.generate(9, (i) => ConflictItem(
          parentId: i + 1,
          label: 'Conflict $i',
          depth: 1,
          childCount: 5,
          slotDupCount: 0,
          nullSlotCount: 0,
          overfilled: false,
          underfilled: false,
          duplicateParents: 1,
        )),
        total: 9,
        limit: 25,
        offset: 0,
      ));

      // Set up group state for resolution
      groupNotifier.state = groupNotifier.state.copyWith(
        selectedGroupNodeId: 1,
        selectedLabels: {'Label1', 'Label2', 'Label3', 'Label4', 'Label5'},
      );
      
      // Resolve group
      await groupNotifier.resolveGroup();
      
      // Check updated state
      expect(listNotifier.state.totalConflictsInitial, 10);
      expect(listNotifier.state.currentCount, 9);
      expect(listNotifier.state.resolvedCount, 1);
      expect(listNotifier.state.progress, 0.1); // 1/10 = 0.1
    });

    testWidgets('Progress bar shows correct value', (WidgetTester tester) async {
      final container = ProviderContainer(
        overrides: [
          conflictsRepositoryProvider.overrideWithValue(mockRepository),
        ],
      );

      final notifier = container.read(conflictsListProvider.notifier);
      
      // Set up state with 5 resolved out of 10 total
      notifier.state = notifier.state.copyWith(
        totalConflictsInitial: 10,
        currentCount: 5,
      );
      
      expect(notifier.state.resolvedCount, 5);
      expect(notifier.state.progress, 0.5); // 5/10 = 0.5
    });

    testWidgets('Progress bar shows 100% when all resolved', (WidgetTester tester) async {
      final container = ProviderContainer(
        overrides: [
          conflictsRepositoryProvider.overrideWithValue(mockRepository),
        ],
      );

      final notifier = container.read(conflictsListProvider.notifier);
      
      // Set up state with all conflicts resolved
      notifier.state = notifier.state.copyWith(
        totalConflictsInitial: 10,
        currentCount: 0,
      );
      
      expect(notifier.state.resolvedCount, 10);
      expect(notifier.state.progress, 1.0); // 10/10 = 1.0
    });

    testWidgets('Progress calculation handles edge cases', (WidgetTester tester) async {
      final container = ProviderContainer(
        overrides: [
          conflictsRepositoryProvider.overrideWithValue(mockRepository),
        ],
      );

      final notifier = container.read(conflictsListProvider.notifier);
      
      // Test with no initial total (fallback to current count)
      notifier.state = notifier.state.copyWith(
        totalConflictsInitial: null,
        currentCount: 5,
      );
      
      expect(notifier.state.resolvedCount, 0); // No resolved when no initial total
      expect(notifier.state.progress, 1.0); // 1.0 when total is 0
      
      // Test with more resolved than total (should clamp)
      notifier.state = notifier.state.copyWith(
        totalConflictsInitial: 10,
        currentCount: 3, // This would give 7 resolved, but we'll test edge case
      );
      
      // Manually set a state that would give more resolved than total
      notifier.state = ConflictsListState(
        totalConflictsInitial: 5,
        currentCount: 10, // This would give -5 resolved, should clamp to 0
      );
      
      expect(notifier.state.resolvedCount, 0); // Should clamp to 0
      expect(notifier.state.progress, 0.0); // Should be 0.0
    });

    testWidgets('Progress HUD widget displays correctly', (WidgetTester tester) async {
      final container = ProviderContainer(
        overrides: [
          conflictsRepositoryProvider.overrideWithValue(mockRepository),
        ],
      );

      // Set up state
      final notifier = container.read(conflictsListProvider.notifier);
      notifier.state = notifier.state.copyWith(
        totalConflictsInitial: 10,
        currentCount: 7,
      );
      
      // Build a simple widget that uses the progress HUD
      await tester.pumpWidget(
        ProviderScope(
          parent: container,
          child: MaterialApp(
            home: Scaffold(
              appBar: AppBar(
                actions: [
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      SizedBox(
                        width: 160,
                        child: LinearProgressIndicator(
                          value: notifier.state.progress,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text('Resolved ${notifier.state.resolvedCount} of ${notifier.state.totalConflictsInitial ?? notifier.state.currentCount}'),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      );
      
      // Verify progress bar and text are displayed
      expect(find.byType(LinearProgressIndicator), findsOneWidget);
      expect(find.text('Resolved 3 of 10'), findsOneWidget);
    });
  });
}
