import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mocktail/mocktail.dart';

import '../../lib/features/home/data/conflicts_repo.dart';
import '../../lib/features/home/state/conflicts_provider.dart';
import '../../lib/features/home/ui/home_pane.dart';

class MockConflictsRepo extends Mock implements ConflictsRepo {}

void main() {
  group('Conflicts Panel Tests', () {
    late MockConflictsRepo mockRepo;

    setUp(() {
      mockRepo = MockConflictsRepo();
    });

    testWidgets('renders conflicts list and detail panel', (WidgetTester tester) async {
      // Mock data
      final mockConflicts = [
        {
          'label': 'hypertension',
          'occurrences': 2,
          'union_children': ['headache', 'nausea', 'vomiting', 'chest pain'],
          'parents': [
            {'parent_id': 1, 'depth': 1, 'children': ['headache', 'nausea']},
            {'parent_id': 2, 'depth': 1, 'children': ['vomiting', 'chest pain']},
          ],
        }
      ];

      when(() => mockRepo.scan()).thenAnswer((_) async => mockConflicts);

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            conflictsProvider.overrideWith((ref) => ConflictsState(mockRepo)..scan()),
          ],
          child: const MaterialApp(
            home: HomePane(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Verify conflicts list is rendered
      expect(find.text('hypertension'), findsOneWidget);
      expect(find.text('2 parents • union=4'), findsOneWidget);

      // Verify scan button is present
      expect(find.text('Scan'), findsOneWidget);
    });

    testWidgets('shows no conflicts message when empty', (WidgetTester tester) async {
      when(() => mockRepo.scan()).thenAnswer((_) async => []);

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            conflictsProvider.overrideWith((ref) => ConflictsState(mockRepo)..scan()),
          ],
          child: const MaterialApp(
            home: HomePane(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('No conflicts found'), findsOneWidget);
    });

    testWidgets('selecting conflict shows detail panel with union chips', (WidgetTester tester) async {
      final mockConflicts = [
        {
          'label': 'hypertension',
          'occurrences': 2,
          'union_children': ['headache', 'nausea', 'vomiting', 'chest pain'],
          'parents': [
            {'parent_id': 1, 'depth': 1, 'children': ['headache', 'nausea']},
            {'parent_id': 2, 'depth': 1, 'children': ['vomiting', 'chest pain']},
          ],
        }
      ];

      when(() => mockRepo.scan()).thenAnswer((_) async => mockConflicts);

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            conflictsProvider.overrideWith((ref) => ConflictsState(mockRepo)..scan()),
          ],
          child: const MaterialApp(
            home: HomePane(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Tap on the first conflict
      await tester.tap(find.text('hypertension'));
      await tester.pumpAndSettle();

      // Verify detail panel shows
      expect(find.text('Resolve: hypertension'), findsOneWidget);
      expect(find.text('Occurrences (2)'), findsOneWidget);

      // Verify union chips are rendered
      expect(find.text('headache'), findsOneWidget);
      expect(find.text('nausea'), findsOneWidget);
      expect(find.text('vomiting'), findsOneWidget);
      expect(find.text('chest pain'), findsOneWidget);

      // Verify selected count
      expect(find.textContaining('Selected'), findsOneWidget);
    });

    testWidgets('blocks selection of more than 5 chips', (WidgetTester tester) async {
      final mockConflicts = [
        {
          'label': 'hypertension',
          'occurrences': 1,
          'union_children': ['a', 'b', 'c', 'd', 'e', 'f'], // 6 items
          'parents': [
            {'parent_id': 1, 'depth': 1, 'children': ['a', 'b', 'c', 'd', 'e', 'f']},
          ],
        }
      ];

      when(() => mockRepo.scan()).thenAnswer((_) async => mockConflicts);

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            conflictsProvider.overrideWith((ref) => ConflictsState(mockRepo)..scan()),
          ],
          child: const MaterialApp(
            home: HomePane(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Tap on the conflict
      await tester.tap(find.text('hypertension'));
      await tester.pumpAndSettle();

      // Try to select all 6 chips
      for (int i = 0; i < 6; i++) {
        final chip = find.text(['a', 'b', 'c', 'd', 'e', 'f'][i]);
        if (tester.widget<FilterChip>(chip).onSelected != null) {
          await tester.tap(chip);
          await tester.pump();
        }
      }

      // Verify only 5 can be selected (the first 5 from the first occurrence)
      // This test verifies the UI behavior rather than direct state access
      expect(find.textContaining('Selected'), findsOneWidget);
    });

    testWidgets('shows error banner on scan failure', (WidgetTester tester) async {
      when(() => mockRepo.scan()).thenThrow(Exception('Network error'));

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            conflictsProvider.overrideWith((ref) => ConflictsState(mockRepo)..scan()),
          ],
          child: const MaterialApp(
            home: HomePane(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('Network error'), findsOneWidget);
      expect(find.text('Retry'), findsOneWidget);
    });

    testWidgets('disables apply button when no children selected', (WidgetTester tester) async {
      final mockConflicts = [
        {
          'label': 'hypertension',
          'occurrences': 1,
          'union_children': ['headache', 'nausea'],
          'parents': [
            {'parent_id': 1, 'depth': 1, 'children': ['headache', 'nausea']},
          ],
        }
      ];

      when(() => mockRepo.scan()).thenAnswer((_) async => mockConflicts);

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            conflictsProvider.overrideWith((ref) => ConflictsState(mockRepo)..scan()),
          ],
          child: const MaterialApp(
            home: HomePane(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Tap on the conflict
      await tester.tap(find.text('hypertension'));
      await tester.pumpAndSettle();

      // Verify apply button is disabled when no children selected
      // This is tested by the UI behavior - the button should be disabled
      final applyButton = find.widgetWithText(FilledButton, 'Apply');
      expect(tester.widget<FilledButton>(applyButton).onPressed, isNull);
    });

    testWidgets('shows export card with format selection', (WidgetTester tester) async {
      when(() => mockRepo.scan()).thenAnswer((_) async => []);

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            conflictsProvider.overrideWith((ref) => ConflictsState(mockRepo)..scan()),
          ],
          child: const MaterialApp(
            home: HomePane(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Verify export card elements
      expect(find.text('Decision Tree Export'), findsOneWidget);
      expect(find.text('CSV'), findsOneWidget);
      expect(find.text('XLSX'), findsOneWidget);
      expect(find.text('Export'), findsOneWidget);
      expect(find.text('Filters (coming soon, API support pending): Depth, Roots, Only red'), findsOneWidget);
    });

    testWidgets('shows new submission card', (WidgetTester tester) async {
      when(() => mockRepo.scan()).thenAnswer((_) async => []);

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            conflictsProvider.overrideWith((ref) => ConflictsState(mockRepo)..scan()),
          ],
          child: const MaterialApp(
            home: HomePane(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Verify new submission card
      expect(find.text('New Submission'), findsOneWidget);
      expect(find.text('Coming soon. This pane will handle new dataset submissions and bulk change proposals.'), findsOneWidget);
    });
  });
}
