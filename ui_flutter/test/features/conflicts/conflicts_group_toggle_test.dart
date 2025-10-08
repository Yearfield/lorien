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
  group('ConflictsGroupNotifier Toggle Tests', () {
    late MockConflictsRepository mockRepository;
    late MockDio mockDio;

    setUp(() {
      mockDio = MockDio();
      mockRepository = MockConflictsRepository();
    });

    testWidgets('Selecting a label makes it selected', (WidgetTester tester) async {
      final container = ProviderContainer(
        overrides: [
          conflictsRepositoryProvider.overrideWithValue(mockRepository),
        ],
      );

      final notifier = container.read(conflictsGroupProvider.notifier);

      // Initial state should have no selected labels
      expect(notifier.state.selectedLabels, isEmpty);

      // Toggle a label on
      notifier.toggleLabel('Test Label');

      // Should be selected
      expect(notifier.state.selectedLabels, contains('Test Label'));
      expect(notifier.state.selectedLabels.length, 1);
    });

    testWidgets('Selecting a label again deselects it', (WidgetTester tester) async {
      final container = ProviderContainer(
        overrides: [
          conflictsRepositoryProvider.overrideWithValue(mockRepository),
        ],
      );

      final notifier = container.read(conflictsGroupProvider.notifier);

      // Toggle a label on
      notifier.toggleLabel('Test Label');
      expect(notifier.state.selectedLabels, contains('Test Label'));

      // Toggle the same label off
      notifier.toggleLabel('Test Label');

      // Should be deselected
      expect(notifier.state.selectedLabels, isEmpty);
    });

    testWidgets('Cannot select more than 5 labels', (WidgetTester tester) async {
      final container = ProviderContainer(
        overrides: [
          conflictsRepositoryProvider.overrideWithValue(mockRepository),
        ],
      );

      final notifier = container.read(conflictsGroupProvider.notifier);

      // Select 5 labels
      for (int i = 0; i < 5; i++) {
        notifier.toggleLabel('Label $i');
      }

      expect(notifier.state.selectedLabels.length, 5);

      // Try to select a 6th label
      notifier.toggleLabel('Label 6');

      // Should still only have 5 labels
      expect(notifier.state.selectedLabels.length, 5);
      expect(notifier.state.selectedLabels, isNot(contains('Label 6')));
    });

    testWidgets('Can deselect any selected label', (WidgetTester tester) async {
      final container = ProviderContainer(
        overrides: [
          conflictsRepositoryProvider.overrideWithValue(mockRepository),
        ],
      );

      final notifier = container.read(conflictsGroupProvider.notifier);

      // Select 5 labels
      for (int i = 0; i < 5; i++) {
        notifier.toggleLabel('Label $i');
      }

      expect(notifier.state.selectedLabels.length, 5);

      // Deselect the middle label
      notifier.toggleLabel('Label 2');

      // Should have 4 labels now
      expect(notifier.state.selectedLabels.length, 4);
      expect(notifier.state.selectedLabels, isNot(contains('Label 2')));

      // Can now select a new label
      notifier.toggleLabel('New Label');
      expect(notifier.state.selectedLabels.length, 5);
      expect(notifier.state.selectedLabels, contains('New Label'));
    });

    testWidgets('Confirm remains disabled until exactly 5 selected', (WidgetTester tester) async {
      final container = ProviderContainer(
        overrides: [
          conflictsRepositoryProvider.overrideWithValue(mockRepository),
        ],
      );

      final notifier = container.read(conflictsGroupProvider.notifier);

      // With no labels selected
      expect(notifier.state.canConfirm, false);

      // With 1 label selected
      notifier.toggleLabel('Label 1');
      expect(notifier.state.canConfirm, false);

      // With 4 labels selected
      for (int i = 2; i <= 4; i++) {
        notifier.toggleLabel('Label $i');
      }
      expect(notifier.state.canConfirm, false);

      // With exactly 5 labels selected
      notifier.toggleLabel('Label 5');
      expect(notifier.state.canConfirm, true);

      // Deselecting one makes it false again
      notifier.toggleLabel('Label 1');
      expect(notifier.state.canConfirm, false);
    });

    testWidgets('Toggle works with mixed selection and deselection', (WidgetTester tester) async {
      final container = ProviderContainer(
        overrides: [
          conflictsRepositoryProvider.overrideWithValue(mockRepository),
        ],
      );

      final notifier = container.read(conflictsGroupProvider.notifier);

      // Select some labels
      notifier.toggleLabel('A');
      notifier.toggleLabel('B');
      notifier.toggleLabel('C');
      expect(notifier.state.selectedLabels, {'A', 'B', 'C'});

      // Deselect one
      notifier.toggleLabel('B');
      expect(notifier.state.selectedLabels, {'A', 'C'});

      // Select more
      notifier.toggleLabel('D');
      notifier.toggleLabel('E');
      notifier.toggleLabel('F');
      expect(notifier.state.selectedLabels, {'A', 'C', 'D', 'E', 'F'});
      expect(notifier.state.canConfirm, true);

      // Deselect and reselect
      notifier.toggleLabel('A');
      expect(notifier.state.selectedLabels, {'C', 'D', 'E', 'F'});
      expect(notifier.state.canConfirm, false);

      notifier.toggleLabel('A');
      expect(notifier.state.selectedLabels, {'A', 'C', 'D', 'E', 'F'});
      expect(notifier.state.canConfirm, true);
    });
  });
}
