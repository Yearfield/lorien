import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mockito/mockito.dart';
import 'package:dio/dio.dart';

import '../../../lib/features/conflicts/ui/conflicts_screen.dart';
import '../../../lib/features/conflicts/data/conflicts_repository.dart';
import '../../../lib/features/conflicts/state/conflicts_provider.dart';

// Mock classes
class MockConflictsRepository extends Mock implements ConflictsRepository {}
class MockDio extends Mock implements Dio {}

void main() {
  group('ConflictsScreen Resolve Tests', () {
    late MockConflictsRepository mockRepository;
    late MockDio mockDio;

    setUp(() {
      mockDio = MockDio();
      mockRepository = MockConflictsRepository();
    });

    Widget createTestWidget() {
      return ProviderScope(
        overrides: [
          conflictsRepositoryProvider.overrideWithValue(mockRepository),
        ],
        child: const MaterialApp(
          home: ConflictsScreen(),
        ),
      );
    }

    testWidgets('renders group children and can select labels', (tester) async {
      // Mock repository responses
      when(mockRepository.listConflicts(limit: 25, offset: 0))
          .thenAnswer((_) async => ConflictsPage(
                items: [
                  ConflictItem(
                    parentId: 1,
                    label: 'Test Parent',
                    depth: 0,
                    childCount: 4,
                    slotDupCount: 0,
                    nullSlotCount: 0,
                    overfilled: false,
                    underfilled: true,
                    duplicateParents: 0,
                  ),
                ],
                total: 1,
                limit: 25,
                offset: 0,
              ));

      when(mockRepository.loadGroup(1))
          .thenAnswer((_) async => GroupPayload(
                group: [GroupItem(id: 1)],
                children: [
                  ChildItem(childId: 1, fromId: 1, slot: 1, label: 'Label 1'),
                  ChildItem(childId: 2, fromId: 1, slot: 2, label: 'Label 2'),
                  ChildItem(childId: 3, fromId: 1, slot: 3, label: 'Label 3'),
                  ChildItem(childId: 4, fromId: 1, slot: 4, label: 'Label 4'),
                ],
                summary: GroupSummary(uniqueChildren: 4, totalChildren: 4),
              ));

      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Tap on a conflict item
      await tester.tap(find.text('Test Parent (id=1)'));
      await tester.pumpAndSettle();

      // Verify group children are displayed
      expect(find.text('Label 1'), findsOneWidget);
      expect(find.text('Label 2'), findsOneWidget);
      expect(find.text('Label 3'), findsOneWidget);
      expect(find.text('Label 4'), findsOneWidget);

      // Verify confirm button is disabled (not 5 selected)
      final confirmButton = find.widgetWithText(ElevatedButton, 'Confirm');
      expect(confirmButton, findsOneWidget);
      expect(tester.widget<ElevatedButton>(confirmButton).onPressed, isNull);
    });

    testWidgets('inline add works and adds to list', (tester) async {
      // Mock repository responses
      when(mockRepository.listConflicts(limit: 25, offset: 0))
          .thenAnswer((_) async => ConflictsPage(
                items: [
                  ConflictItem(
                    parentId: 1,
                    label: 'Test Parent',
                    depth: 0,
                    childCount: 4,
                    slotDupCount: 0,
                    nullSlotCount: 0,
                    overfilled: false,
                    underfilled: true,
                    duplicateParents: 0,
                  ),
                ],
                total: 1,
                limit: 25,
                offset: 0,
              ));

      when(mockRepository.loadGroup(1))
          .thenAnswer((_) async => GroupPayload(
                group: [GroupItem(id: 1)],
                children: [
                  ChildItem(childId: 1, fromId: 1, slot: 1, label: 'Label 1'),
                  ChildItem(childId: 2, fromId: 1, slot: 2, label: 'Label 2'),
                  ChildItem(childId: 3, fromId: 1, slot: 3, label: 'Label 3'),
                  ChildItem(childId: 4, fromId: 1, slot: 4, label: 'Label 4'),
                ],
                summary: GroupSummary(uniqueChildren: 4, totalChildren: 4),
              ));

      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Tap on a conflict item
      await tester.tap(find.text('Test Parent (id=1)'));
      await tester.pumpAndSettle();

      // Add inline label
      await tester.enterText(find.byType(TextField), 'New Label');
      await tester.tap(find.widgetWithText(ElevatedButton, 'Add'));
      await tester.pumpAndSettle();

      // Verify new label is added
      expect(find.text('New Label'), findsOneWidget);
    });

    testWidgets('confirm button enabled when 5 labels selected', (tester) async {
      // Mock repository responses
      when(mockRepository.listConflicts(limit: 25, offset: 0))
          .thenAnswer((_) async => ConflictsPage(
                items: [
                  ConflictItem(
                    parentId: 1,
                    label: 'Test Parent',
                    depth: 0,
                    childCount: 4,
                    slotDupCount: 0,
                    nullSlotCount: 0,
                    overfilled: false,
                    underfilled: true,
                    duplicateParents: 0,
                  ),
                ],
                total: 1,
                limit: 25,
                offset: 0,
              ));

      when(mockRepository.loadGroup(1))
          .thenAnswer((_) async => GroupPayload(
                group: [GroupItem(id: 1)],
                children: [
                  ChildItem(childId: 1, fromId: 1, slot: 1, label: 'Label 1'),
                  ChildItem(childId: 2, fromId: 1, slot: 2, label: 'Label 2'),
                  ChildItem(childId: 3, fromId: 1, slot: 3, label: 'Label 3'),
                  ChildItem(childId: 4, fromId: 1, slot: 4, label: 'Label 4'),
                ],
                summary: GroupSummary(uniqueChildren: 4, totalChildren: 4),
              ));

      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Tap on a conflict item
      await tester.tap(find.text('Test Parent (id=1)'));
      await tester.pumpAndSettle();

      // Add one more label to make 5 total
      await tester.enterText(find.byType(TextField), 'Label 5');
      await tester.tap(find.widgetWithText(ElevatedButton, 'Add'));
      await tester.pumpAndSettle();

      // Select all 5 labels
      for (int i = 1; i <= 5; i++) {
        await tester.tap(find.text('Label $i'));
        await tester.pumpAndSettle();
      }

      // Verify confirm button is enabled
      final confirmButton = find.widgetWithText(ElevatedButton, 'Confirm');
      expect(confirmButton, findsOneWidget);
      expect(tester.widget<ElevatedButton>(confirmButton).onPressed, isNotNull);
    });

    testWidgets('shows validation error on resolve failure', (tester) async {
      // Mock repository responses
      when(mockRepository.listConflicts(limit: 25, offset: 0))
          .thenAnswer((_) async => ConflictsPage(
                items: [
                  ConflictItem(
                    parentId: 1,
                    label: 'Test Parent',
                    depth: 0,
                    childCount: 4,
                    slotDupCount: 0,
                    nullSlotCount: 0,
                    overfilled: false,
                    underfilled: true,
                    duplicateParents: 0,
                  ),
                ],
                total: 1,
                limit: 25,
                offset: 0,
              ));

      when(mockRepository.loadGroup(1))
          .thenAnswer((_) async => GroupPayload(
                group: [GroupItem(id: 1)],
                children: [
                  ChildItem(childId: 1, fromId: 1, slot: 1, label: 'Label 1'),
                  ChildItem(childId: 2, fromId: 1, slot: 2, label: 'Label 2'),
                  ChildItem(childId: 3, fromId: 1, slot: 3, label: 'Label 3'),
                  ChildItem(childId: 4, fromId: 1, slot: 4, label: 'Label 4'),
                ],
                summary: GroupSummary(uniqueChildren: 4, totalChildren: 4),
              ));

      // Mock resolve to throw validation error
      when(mockRepository.resolveGroup(
        keepId: 1,
        chosen: anyNamed('chosen'),
      )).thenThrow(ValidationException('must_choose_five', 'Choose exactly 5 labels.'));

      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Tap on a conflict item
      await tester.tap(find.text('Test Parent (id=1)'));
      await tester.pumpAndSettle();

      // Add labels to make 5 total
      await tester.enterText(find.byType(TextField), 'Label 5');
      await tester.tap(find.widgetWithText(ElevatedButton, 'Add'));
      await tester.pumpAndSettle();

      // Select all 5 labels
      for (int i = 1; i <= 5; i++) {
        await tester.tap(find.text('Label $i'));
        await tester.pumpAndSettle();
      }

      // Tap confirm
      await tester.tap(find.widgetWithText(ElevatedButton, 'Confirm'));
      await tester.pumpAndSettle();

      // Verify error message is shown
      expect(find.text('Choose exactly 5 labels.'), findsOneWidget);
    });

    testWidgets('shows conflict banner on 409 error', (tester) async {
      // Mock repository responses
      when(mockRepository.listConflicts(limit: 25, offset: 0))
          .thenAnswer((_) async => ConflictsPage(
                items: [
                  ConflictItem(
                    parentId: 1,
                    label: 'Test Parent',
                    depth: 0,
                    childCount: 4,
                    slotDupCount: 0,
                    nullSlotCount: 0,
                    overfilled: false,
                    underfilled: true,
                    duplicateParents: 0,
                  ),
                ],
                total: 1,
                limit: 25,
                offset: 0,
              ));

      when(mockRepository.loadGroup(1))
          .thenAnswer((_) async => GroupPayload(
                group: [GroupItem(id: 1)],
                children: [
                  ChildItem(childId: 1, fromId: 1, slot: 1, label: 'Label 1'),
                  ChildItem(childId: 2, fromId: 1, slot: 2, label: 'Label 2'),
                  ChildItem(childId: 3, fromId: 1, slot: 3, label: 'Label 3'),
                  ChildItem(childId: 4, fromId: 1, slot: 4, label: 'Label 4'),
                ],
                summary: GroupSummary(uniqueChildren: 4, totalChildren: 4),
              ));

      // Mock resolve to throw conflict error
      when(mockRepository.resolveGroup(
        keepId: 1,
        chosen: anyNamed('chosen'),
      )).thenThrow(ConflictException('Conflict on save. Reload latest?'));

      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Tap on a conflict item
      await tester.tap(find.text('Test Parent (id=1)'));
      await tester.pumpAndSettle();

      // Add labels to make 5 total
      await tester.enterText(find.byType(TextField), 'Label 5');
      await tester.tap(find.widgetWithText(ElevatedButton, 'Add'));
      await tester.pumpAndSettle();

      // Select all 5 labels
      for (int i = 1; i <= 5; i++) {
        await tester.tap(find.text('Label $i'));
        await tester.pumpAndSettle();
      }

      // Tap confirm
      await tester.tap(find.widgetWithText(ElevatedButton, 'Confirm'));
      await tester.pumpAndSettle();

      // Verify conflict dialog is shown
      expect(find.text('Conflict'), findsOneWidget);
      expect(find.text('Conflict on save. Reload latest?'), findsOneWidget);
      expect(find.text('Reload Latest'), findsOneWidget);
    });
  });
}
