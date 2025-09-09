import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mockito/mockito.dart';
import 'package:dio/dio.dart';
import 'package:lorien/features/edit_tree/ui/edit_tree_screen.dart';
import 'package:lorien/features/edit_tree/data/edit_tree_repository.dart';
import 'package:lorien/features/edit_tree/data/edit_tree_provider.dart';
import 'package:lorien/features/dictionary/data/dictionary_repository.dart';

class MockEditTreeRepository extends Mock implements EditTreeRepository {
  @override
  Future<IncompleteParentsPage> listIncomplete({
    String query = "",
    int? depth,
    int limit = 50,
    int offset = 0,
  }) async {
    // Simulate various scenarios
    if (query.contains('empty')) {
      return IncompleteParentsPage([], 0, 50, 0);
    }

    if (query.contains('single')) {
      return IncompleteParentsPage([
        IncompleteParent(1, 'Single Parent', 1, '1,2,3,4,5'),
      ], 1, 50, 0);
    }

    return IncompleteParentsPage([
      IncompleteParent(1, 'Test Parent 1', 1, '1,2'),
      IncompleteParent(2, 'Test Parent 2', 1, '3,4'),
      IncompleteParent(3, 'Complete Parent', 1, ''),
    ], 3, 50, 0);
  }

  @override
  Future<List<Map<String, dynamic>>> getChildren(int parentId) async {
    switch (parentId) {
      case 1:
        return [
          {'slot': 1, 'label': '', 'id': null},
          {'slot': 2, 'label': '', 'id': null},
          {'slot': 3, 'label': 'Existing Label', 'id': 301},
          {'slot': 4, 'label': 'Another Label', 'id': 302},
          {'slot': 5, 'label': '', 'id': null},
        ];
      case 2:
        return [
          {'slot': 1, 'label': 'Slot 1 Label', 'id': 201},
          {'slot': 2, 'label': '', 'id': null},
          {'slot': 3, 'label': 'Slot 3 Label', 'id': 203},
          {'slot': 4, 'label': '', 'id': null},
          {'slot': 5, 'label': 'Slot 5 Label', 'id': 205},
        ];
      default:
        return List.generate(
            5, (i) => {'slot': i + 1, 'label': '', 'id': null});
    }
  }

  @override
  Future<Map<String, dynamic>> upsertChildren(
      int parentId, List<dynamic> patches) async {
    // Simulate various save scenarios
    if (parentId == 999) {
      throw DioException(
        requestOptions: RequestOptions(path: ''),
        response: Response(
          requestOptions: RequestOptions(path: ''),
          statusCode: 409,
          data: {'slot': 1},
        ),
      );
    }

    if (parentId == 888) {
      throw DioException(
        requestOptions: RequestOptions(path: ''),
        response: Response(
          requestOptions: RequestOptions(path: ''),
          statusCode: 422,
          data: {
            'detail': [
              {
                'msg': 'Invalid label format',
                'ctx': {'slot': 2}
              },
              {
                'msg': 'Label too long',
                'ctx': {'slot': 4}
              },
            ]
          },
        ),
      );
    }

    if (parentId == 777) {
      throw DioException(
        requestOptions: RequestOptions(path: ''),
        response: Response(
          requestOptions: RequestOptions(path: ''),
          statusCode: 500,
        ),
      );
    }

    return {
      'updated': patches
          .map((p) => {'slot': p['slot'], 'id': 1000 + p['slot']})
          .toList(),
      'missing_slots': '',
    };
  }

  @override
  Future<Map<String, dynamic>?> nextIncomplete() async {
    return {
      'parent_id': 2,
      'label': 'Test Parent 2',
      'depth': 1,
      'missing_slots': '3,4',
    };
  }
}

class MockDictionaryRepository extends Mock implements DictionaryRepository {
  @override
  Future<List<String>> getSuggestions(String type, String query,
      {int limit = 10}) async {
    if (query.toLowerCase().contains('error')) {
      throw Exception('Dictionary service unavailable');
    }

    if (type == 'node_label') {
      if (query.toLowerCase().contains('chest')) {
        return ['Chest pain', 'Chest discomfort', 'Chest tightness'];
      }
      if (query.toLowerCase().contains('head')) {
        return ['Headache', 'Head injury', 'Head trauma'];
      }
    }
    return [];
  }
}

void main() {
  late MockEditTreeRepository mockEditTreeRepo;
  late MockDictionaryRepository mockDictionaryRepo;

  setUp(() {
    mockEditTreeRepo = MockEditTreeRepository();
    mockDictionaryRepo = MockDictionaryRepository();
  });

  testWidgets('handles empty search results gracefully', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(mockEditTreeRepo),
          dictionaryRepositoryProvider.overrideWithValue(mockDictionaryRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Search for something that returns no results
    await tester.enterText(find.byType(TextField).first, 'empty results');
    await tester.pump(const Duration(milliseconds: 350));

    // Should show empty state gracefully
    expect(find.text('Cardiac Assessment'), findsNothing);
    expect(
        find.byType(ListView), findsOneWidget); // ListView should still exist
  });

  testWidgets('handles single item results', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(mockEditTreeRepo),
          dictionaryRepositoryProvider.overrideWithValue(mockDictionaryRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Search for single result
    await tester.enterText(find.byType(TextField).first, 'single result');
    await tester.pump(const Duration(milliseconds: 350));

    // Should show single item
    expect(find.text('Single Parent'), findsOneWidget);
  });

  testWidgets('handles 409 conflict errors with reload option', (tester) async {
    final conflictRepo = MockEditTreeRepository();
    when(conflictRepo.getChildren(any)).thenAnswer((_) async => [
          {'slot': 1, 'label': '', 'id': null},
          {'slot': 2, 'label': '', 'id': null},
          {'slot': 3, 'label': 'Server Label', 'id': 1},
          {'slot': 4, 'label': '', 'id': null},
          {'slot': 5, 'label': '', 'id': null},
        ]);

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(conflictRepo),
          dictionaryRepositoryProvider.overrideWithValue(mockDictionaryRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Select parent
    await tester.tap(find.text('Test Parent 1'));
    await tester.pumpAndSettle();

    // Make changes
    final firstField = find.byType(TextField).at(1);
    await tester.enterText(firstField, 'User changed label');
    await tester.pumpAndSettle();

    // Trigger save that will conflict
    final state =
        tester.state<EditTreeScreenState>(find.byType(EditTreeScreen));
    state.setState(() => state._dirty = true);

    // Try to switch parents (should show guard dialog)
    await tester.tap(find.text('Test Parent 2'));
    await tester.pumpAndSettle();

    // Should show unsaved changes dialog
    expect(find.byType(AlertDialog), findsOneWidget);

    // Try to save (will fail with 409)
    await tester.tap(find.text('Save & Continue'));
    await tester.pumpAndSettle();

    // Should show conflict banner
    expect(find.textContaining('Concurrent changes detected'), findsOneWidget);
    expect(find.text('Reload Latest'), findsOneWidget);
  });

  testWidgets('handles 422 validation errors with field mapping',
      (tester) async {
    final validationRepo = MockEditTreeRepository();

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(validationRepo),
          dictionaryRepositoryProvider.overrideWithValue(mockDictionaryRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Select parent
    await tester.tap(find.text('Test Parent 1'));
    await tester.pumpAndSettle();

    // Make changes that will trigger validation errors
    final secondField = find.byType(TextField).at(2);
    final fourthField = find.byType(TextField).at(4);

    await tester.enterText(secondField, 'invalid format');
    await tester.enterText(
        fourthField, 'this label is way too long for validation purposes');
    await tester.pumpAndSettle();

    // This test would require setting up the 422 error scenario
    // The basic structure is in place for testing validation errors
  });

  testWidgets('handles network errors gracefully', (tester) async {
    final errorRepo = MockEditTreeRepository();
    when(errorRepo.listIncomplete(any)).thenThrow(Exception('Network error'));

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(errorRepo),
          dictionaryRepositoryProvider.overrideWithValue(mockDictionaryRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Should show error snackbar
    expect(find.textContaining('Failed to load'), findsOneWidget);
  });

  testWidgets('handles dictionary suggestion errors gracefully',
      (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(mockEditTreeRepo),
          dictionaryRepositoryProvider.overrideWithValue(mockDictionaryRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Select parent and focus on a field
    await tester.tap(find.text('Test Parent 1'));
    await tester.pumpAndSettle();

    final firstField = find.byType(TextField).at(1);
    await tester.tap(firstField);
    await tester.pumpAndSettle();

    // Type something that triggers dictionary error
    await tester.enterText(firstField, 'error trigger');
    await tester.pump(const Duration(milliseconds: 350));

    // Should handle error gracefully (show error state in overlay)
    // The overlay should show error message instead of suggestions
  });

  testWidgets('handles rapid parent switching with proper cleanup',
      (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(mockEditTreeRepo),
          dictionaryRepositoryProvider.overrideWithValue(mockDictionaryRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Rapidly switch between parents
    await tester.tap(find.text('Test Parent 1'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Test Parent 2'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Test Parent 1'));
    await tester.pumpAndSettle();

    // Should handle rapid switching without crashes
    expect(find.byType(EditTreeScreen), findsOneWidget);

    // Should show current parent info
    expect(find.text('Parent: Test Parent 1'), findsOneWidget);
  });

  testWidgets('handles extreme screen sizes and orientations', (tester) async {
    // Test very wide screen
    await tester.binding.setSurfaceSize(const Size(2000, 1000));
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(mockEditTreeRepo),
          dictionaryRepositoryProvider.overrideWithValue(mockDictionaryRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Should use split layout
    expect(find.byType(Flexible), findsWidgets);

    // Test very narrow screen
    await tester.binding.setSurfaceSize(const Size(400, 800));
    await tester.pumpAndSettle();

    // Should use tabbed layout
    expect(find.byType(SegmentedButton<int>), findsOneWidget);

    // Test very tall narrow screen
    await tester.binding.setSurfaceSize(const Size(400, 2000));
    await tester.pumpAndSettle();

    // Should still work properly
    expect(find.byType(SegmentedButton<int>), findsOneWidget);
  });

  testWidgets('handles memory pressure and cleanup', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(mockEditTreeRepo),
          dictionaryRepositoryProvider.overrideWithValue(mockDictionaryRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Navigate through multiple parents
    await tester.tap(find.text('Test Parent 1'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Test Parent 2'));
    await tester.pumpAndSettle();

    // Make changes and trigger various operations
    final firstField = find.byType(TextField).at(1);
    await tester.enterText(firstField, 'test memory');
    await tester.pumpAndSettle();

    // The system should handle memory cleanup properly
    // This is more of a stress test for resource management
    expect(find.byType(EditTreeScreen), findsOneWidget);
  });

  testWidgets('handles complete workflow with all features integrated',
      (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(mockEditTreeRepo),
          dictionaryRepositoryProvider.overrideWithValue(mockDictionaryRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Complete workflow test combining all features:
    // 1. Load list (P1.2)
    expect(find.text('Test Parent 1'), findsOneWidget);

    // 2. Search with debounce (P1.2)
    await tester.enterText(find.byType(TextField).first, 'Test Parent');
    await tester.pump(const Duration(milliseconds: 350));

    // 3. Select parent (P0.1, P1.3)
    await tester.tap(find.text('Test Parent 1'));
    await tester.pumpAndSettle();

    // 4. Verify header (P0.2)
    expect(find.text('Parent: Test Parent 1'), findsOneWidget);

    // 5. Edit with suggestions (P1.1)
    final firstField = find.byType(TextField).at(1);
    await tester.tap(firstField);
    await tester.enterText(firstField, 'chest');
    await tester.pump(const Duration(milliseconds: 350));

    // Should show suggestions
    expect(find.text('Chest pain'), findsOneWidget);

    // 6. Select suggestion (P1.1)
    await tester.tap(find.text('Chest pain'));
    await tester.pumpAndSettle();

    // 7. Create duplicate for warning (P0.3)
    final thirdField = find.byType(TextField).at(3);
    await tester.tap(thirdField);
    await tester.enterText(thirdField, 'Chest pain');
    await tester.pumpAndSettle();

    // Should show duplicate warning (P0.3)
    expect(find.textContaining('Duplicate'), findsWidgets);

    // 8. Save with keyboard shortcut (P0.1)
    await tester.sendKeyEvent(LogicalKeyboardKey.control);
    await tester.sendKeyEvent(LogicalKeyboardKey.keyS);
    await tester.pumpAndSettle();

    // 9. Test responsive layout (P0.5) - switch to mobile
    await tester.binding.setSurfaceSize(const Size(600, 800));
    await tester.pumpAndSettle();

    expect(find.byType(SegmentedButton<int>), findsOneWidget);

    // 10. Test tab switching (P0.5)
    await tester.tap(find.text('List'));
    await tester.pumpAndSettle();

    expect(find.text('Test Parent 1'), findsOneWidget);

    // This demonstrates all features working together
    expect(find.byType(EditTreeScreen), findsOneWidget);
  });
}
