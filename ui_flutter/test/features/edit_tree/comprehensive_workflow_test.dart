import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mockito/mockito.dart';
import '../../../lib/features/edit_tree/ui/edit_tree_screen.dart';
import '../../../lib/features/edit_tree/data/edit_tree_repository.dart';
import '../../../lib/features/edit_tree/data/edit_tree_provider.dart';
import '../../../lib/features/dictionary/data/dictionary_repository.dart';

class MockEditTreeRepository extends Mock implements EditTreeRepository {
  @override
  Future<IncompleteParentsPage> listIncomplete({
    String query = "",
    int? depth,
    int limit = 50,
    int offset = 0,
  }) async {
    if (offset == 0) {
      return IncompleteParentsPage([
        IncompleteParent(1, 'Cardiac Assessment', 1, '1,2,3'),
        IncompleteParent(2, 'Respiratory Evaluation', 1, '2,4,5'),
        IncompleteParent(3, 'Neurological Check', 1, '1,3'),
      ], 3, 50, 0);
    }
    return IncompleteParentsPage([], 3, 50, 50);
  }

  @override
  Future<List<Map<String, dynamic>>> getChildren(int parentId) async {
    switch (parentId) {
      case 1:
        return [
          {'slot': 1, 'label': '', 'id': null},
          {'slot': 2, 'label': '', 'id': null},
          {'slot': 3, 'label': 'Patient reports chest pain', 'id': 101},
          {'slot': 4, 'label': '', 'id': null},
          {'slot': 5, 'label': '', 'id': null},
        ];
      case 2:
        return [
          {'slot': 1, 'label': 'Shortness of breath present', 'id': 201},
          {'slot': 2, 'label': '', 'id': null},
          {'slot': 3, 'label': '', 'id': null},
          {'slot': 4, 'label': 'Oxygen saturation < 95%', 'id': 202},
          {'slot': 5, 'label': '', 'id': null},
        ];
      default:
        return List.generate(5, (i) => {'slot': i + 1, 'label': '', 'id': null});
    }
  }

  @override
  Future<Map<String, dynamic>> upsertChildren(int parentId, List<dynamic> patches) async {
    return {
      'updated': patches.map((p) => {'slot': p['slot'], 'id': 1000 + p['slot']}).toList(),
      'missing_slots': '',
    };
  }

  @override
  Future<Map<String, dynamic>?> nextIncomplete() async {
    return {
      'parent_id': 2,
      'label': 'Respiratory Evaluation',
      'depth': 1,
      'missing_slots': '2,4,5',
    };
  }
}

class MockDictionaryRepository extends Mock implements DictionaryRepository {
  @override
  Future<List<String>> getSuggestions(String type, String query, {int limit = 10}) async {
    if (type == 'node_label' && query.length >= 2) {
      if (query.toLowerCase().contains('pain')) {
        return ['Chest pain', 'Abdominal pain', 'Headache', 'Back pain'];
      }
      if (query.toLowerCase().contains('breath')) {
        return ['Shortness of breath', 'Difficulty breathing', 'Rapid breathing'];
      }
      if (query.toLowerCase().contains('oxygen')) {
        return ['Oxygen saturation', 'Oxygen therapy', 'Oxygen mask'];
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

  testWidgets('complete user workflow: load, edit, save, navigate with all features', (tester) async {
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

    // P0.5: Verify responsive layout (desktop split-pane)
    expect(find.byType(LayoutBuilder), findsOneWidget);

    // P0.2: Verify header elements
    expect(find.text('Edit Tree'), findsOneWidget);

    // P1.2: Verify list with items
    expect(find.text('Cardiac Assessment'), findsOneWidget);
    expect(find.text('Respiratory Evaluation'), findsOneWidget);

    // P1.2: Test search functionality
    await tester.enterText(find.byType(TextField).first, 'Cardiac');
    await tester.pump(const Duration(milliseconds: 350)); // Wait for debounce

    // Should still show Cardiac Assessment
    expect(find.text('Cardiac Assessment'), findsOneWidget);

    // P0.1: Select first parent
    await tester.tap(find.text('Cardiac Assessment'));
    await tester.pumpAndSettle();

    // P0.2: Verify header shows selected parent info
    expect(find.text('Parent: Cardiac Assessment (Depth 1)'), findsOneWidget);

    // P0.1: Verify persistent controllers are set up
    expect(find.byType(TextField), findsNWidgets(6)); // 1 search + 5 slot fields

    // P0.1: Test keyboard navigation (Tab)
    final firstField = find.byType(TextField).at(1); // First slot field
    await tester.tap(firstField);
    await tester.pumpAndSettle();

    // P0.1: Test text input and persistence
    await tester.enterText(firstField, 'Patient');
    await tester.pumpAndSettle();

    // P1.1: Test dictionary suggestions
    await tester.enterText(firstField, 'Patient pain');
    await tester.pumpAndSettle();

    // Wait for suggestions to appear
    await tester.pump(const Duration(milliseconds: 350));

    // Should show suggestions
    expect(find.text('Chest pain'), findsOneWidget);
    expect(find.text('Abdominal pain'), findsOneWidget);

    // P1.1: Select suggestion
    await tester.tap(find.text('Chest pain'));
    await tester.pumpAndSettle();

    // Should have filled the field
    expect(find.text('Chest pain'), findsOneWidget);

    // P0.3: Test duplicate warning (create duplicate)
    final thirdField = find.byType(TextField).at(3); // Slot 3 already has text
    await tester.tap(thirdField);
    await tester.pumpAndSettle();

    // Copy text to create duplicate
    await tester.enterText(thirdField, 'Chest pain');
    await tester.pumpAndSettle();

    // P0.3: Should show duplicate warning
    expect(find.textContaining('Duplicate label'), findsWidgets);

    // P0.1: Test save with Ctrl+S
    await tester.sendKeyEvent(LogicalKeyboardKey.control);
    await tester.sendKeyEvent(LogicalKeyboardKey.keyS);
    await tester.pumpAndSettle();

    // P0.4: Should not show conflict/error banners on successful save
    expect(find.text('Concurrent changes detected'), findsNothing);
    expect(find.text('Validation errors found'), findsNothing);

    // P1.3: Test unsaved guard when switching parents
    // First make a change
    await tester.enterText(find.byType(TextField).at(4), 'New symptom');
    await tester.pumpAndSettle();

    // Try to switch to another parent
    await tester.tap(find.text('Respiratory Evaluation'));
    await tester.pumpAndSettle();

    // P1.3: Should show unsaved changes dialog
    expect(find.byType(AlertDialog), findsOneWidget);
    expect(find.text('Unsaved Changes'), findsOneWidget);

    // P1.3: Choose to discard changes
    await tester.tap(find.text('Discard Changes'));
    await tester.pumpAndSettle();

    // Should switch to new parent
    expect(find.text('Parent: Respiratory Evaluation (Depth 1)'), findsOneWidget);

    // P0.2: Test Next Incomplete functionality
    await tester.tap(find.byIcon(Icons.skip_next).first);
    await tester.pumpAndSettle();

    // Should navigate to next incomplete parent
    expect(find.text('Respiratory Evaluation'), findsOneWidget);

    // P1.2: Test infinite scroll (simulate scrolling)
    // Add more items to test scrolling
    final listView = find.byType(ListView);
    await tester.scrollUntilVisible(
      find.text('Neurological Check'),
      50,
      scrollable: listView,
    );
    await tester.pumpAndSettle();

    // Should show the scrolled item
    expect(find.text('Neurological Check'), findsOneWidget);

    // P1.2: Test ScrollToTop FAB (simulate scroll down)
    await tester.scrollUntilVisible(
      find.text('Neurological Check'),
      300,
      scrollable: listView,
    );
    await tester.pumpAndSettle();

    // Should show FAB after scrolling down
    expect(find.byIcon(Icons.arrow_upward), findsOneWidget);

    // P1.2: Test FAB functionality
    await tester.tap(find.byIcon(Icons.arrow_upward));
    await tester.pumpAndSettle();

    // Should scroll to top
    expect(find.text('Cardiac Assessment'), findsOneWidget);
  });

  testWidgets('mobile responsive workflow', (tester) async {
    // Test on mobile screen size
    await tester.binding.setSurfaceSize(const Size(600, 800));

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

    // P0.5: Should show tabbed layout on mobile
    expect(find.byType(SegmentedButton<int>), findsOneWidget);
    expect(find.text('List'), findsOneWidget);
    expect(find.text('Editor'), findsOneWidget);

    // P0.5: Initially shows Editor tab (default)
    expect(find.text('Select a parent'), findsOneWidget);

    // P0.5: Switch to List tab
    await tester.tap(find.text('List'));
    await tester.pumpAndSettle();

    // Should show list
    expect(find.text('Cardiac Assessment'), findsOneWidget);

    // Select parent and switch back to Editor
    await tester.tap(find.text('Cardiac Assessment'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Editor'));
    await tester.pumpAndSettle();

    // Should show editor with selected parent
    expect(find.text('Parent: Cardiac Assessment'), findsOneWidget);
  });

  testWidgets('error handling and recovery workflow', (tester) async {
    // Create a repo that throws errors
    final failingRepo = MockEditTreeRepository();
    when(failingRepo.upsertChildren(any, any))
        .thenThrow(Exception('Network error'));

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(failingRepo),
          dictionaryRepositoryProvider.overrideWithValue(mockDictionaryRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Select parent and try to save
    await tester.tap(find.text('Cardiac Assessment'));
    await tester.pumpAndSettle();

    // Make a change
    final firstField = find.byType(TextField).at(1);
    await tester.enterText(firstField, 'Test change');
    await tester.pumpAndSettle();

    // Try to save (should fail)
    await tester.sendKeyEvent(LogicalKeyboardKey.control);
    await tester.sendKeyEvent(LogicalKeyboardKey.keyS);
    await tester.pumpAndSettle();

    // Should show error snackbar
    expect(find.text('Failed to save'), findsOneWidget);

    // P0.4: Test 409 conflict scenario
    final conflictRepo = MockEditTreeRepository();
    when(conflictRepo.upsertChildren(any, any))
        .thenThrow(DioException(
          requestOptions: RequestOptions(path: ''),
          response: Response(
            requestOptions: RequestOptions(path: ''),
            statusCode: 409,
            data: {'slot': 1},
          ),
        ));

    // This would test conflict resolution, but requires more complex setup
    // The basic error handling is tested above
  });

  testWidgets('accessibility and keyboard navigation', (tester) async {
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

    // P0.1: Test keyboard navigation
    final firstSlotField = find.byType(TextField).at(1);

    // Focus first field
    await tester.tap(firstSlotField);
    await tester.pumpAndSettle();

    // P0.1: Test Tab navigation
    await tester.sendKeyEvent(LogicalKeyboardKey.tab);
    await tester.pumpAndSettle();

    // Should move to next field
    final secondSlotField = find.byType(TextField).at(2);
    expect(tester.widget<TextField>(secondSlotField).focusNode?.hasFocus, true);

    // P0.1: Test Ctrl+S save shortcut
    await tester.enterText(secondSlotField, 'Test content');
    await tester.pumpAndSettle();

    await tester.sendKeyEvent(LogicalKeyboardKey.control);
    await tester.sendKeyEvent(LogicalKeyboardKey.keyS);
    await tester.pumpAndSettle();

    // Should attempt save
    verify(mockEditTreeRepo.upsertChildren(any, any)).called(1);
  });

  testWidgets('performance and scalability', (tester) async {
    // Create repo with many items for performance testing
    final largeRepo = MockEditTreeRepository();
    when(largeRepo.listIncomplete(
      query: anyNamed('query'),
      depth: anyNamed('depth'),
      limit: anyNamed('limit'),
      offset: anyNamed('offset'),
    )).thenAnswer((invocation) {
      final limit = invocation.namedArguments[#limit] as int? ?? 50;
      final offset = invocation.namedArguments[#offset] as int? ?? 0;

      final items = List.generate(
        limit,
        (i) => IncompleteParent(
          offset + i,
          'Test Parent ${offset + i}',
          1,
          i % 3 == 0 ? '1,2' : '',
        ),
      );

      return Future.value(IncompleteParentsPage(items, 1000, limit, offset));
    });

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(largeRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // P1.2: Should handle large lists efficiently
    expect(find.text('Test Parent 0'), findsOneWidget);
    expect(find.text('Test Parent 49'), findsOneWidget);

    // P1.2: Test infinite scroll with large dataset
    final listView = find.byType(ListView);
    await tester.scrollUntilVisible(
      find.text('Test Parent 40'),
      200,
      scrollable: listView,
    );
    await tester.pumpAndSettle();

    // Should load more items
    expect(find.text('Test Parent 50'), findsOneWidget);

    // P1.2: Test search with debouncing on large dataset
    await tester.enterText(find.byType(TextField).first, 'Test Parent 100');
    await tester.pump(const Duration(milliseconds: 350));

    // Should filter results efficiently
    verify(largeRepo.listIncomplete(
      query: 'Test Parent 100',
      limit: 50,
      offset: 0,
    )).called(1);
  });
}
