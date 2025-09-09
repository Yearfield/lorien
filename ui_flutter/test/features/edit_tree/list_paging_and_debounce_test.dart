import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mockito/mockito.dart';
import 'package:lorien/features/edit_tree/ui/edit_tree_screen.dart';
import 'package:lorien/features/edit_tree/data/edit_tree_repository.dart';
import 'package:lorien/features/edit_tree/data/edit_tree_provider.dart';

class MockEditTreeRepository extends Mock implements EditTreeRepository {
  @override
  Future<IncompleteParentsPage> listIncomplete({
    String query = "",
    int? depth,
    int limit = 50,
    int offset = 0,
  }) async {
    // Simulate pagination: return 50 items for first page, 25 for second page, 0 for third
    if (offset == 0) {
      return IncompleteParentsPage(
        List.generate(50, (i) => IncompleteParent(i, 'Parent $i', 1, '')),
        75,
        50,
        0,
      );
    } else if (offset == 50) {
      return IncompleteParentsPage(
        List.generate(
            25, (i) => IncompleteParent(i + 50, 'Parent ${i + 50}', 1, '')),
        75,
        50,
        50,
      );
    } else {
      return IncompleteParentsPage([], 75, 50, 100);
    }
  }
}

void main() {
  late MockEditTreeRepository mockRepo;

  setUp(() {
    mockRepo = MockEditTreeRepository();
  });

  testWidgets('should debounce search input with 300ms delay', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(mockRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Type in search field
    await tester.enterText(find.byType(TextField), 'test query');

    // Should not trigger search immediately
    verifyNever(mockRepo.listIncomplete(query: 'test query'));

    // Wait for debounce delay
    await tester.pump(const Duration(milliseconds: 350));

    // Should trigger search after debounce
    verify(mockRepo.listIncomplete(query: 'test query')).called(1);
  });

  testWidgets('should load more data on scroll near bottom', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(mockRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Initial load should have 50 items
    expect(find.text('Parent 0'), findsOneWidget);
    expect(find.text('Parent 49'), findsOneWidget);

    // Simulate scrolling to near bottom (80% of maxScrollExtent)
    final listView = find.byType(ListView);
    await tester.scrollUntilVisible(
      find.text('Parent 40'), // Near the end of first page
      100,
      scrollable: listView,
    );

    // Wait for potential load more
    await tester.pump(const Duration(milliseconds: 500));

    // Should have loaded more items
    expect(find.text('Parent 50'), findsOneWidget);
    expect(find.text('Parent 74'), findsOneWidget);
  });

  testWidgets('should show loading indicator during infinite scroll',
      (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(mockRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Scroll to trigger loading more
    final listView = find.byType(ListView);
    await tester.scrollUntilVisible(
      find.text('Parent 40'),
      100,
      scrollable: listView,
    );

    // Should show loading indicator at bottom
    expect(find.byType(CircularProgressIndicator), findsWidgets);
  });

  testWidgets('should show ScrollToTop FAB when scrolled down', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(mockRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Initially no FAB should be visible
    expect(find.byIcon(Icons.arrow_upward), findsNothing);

    // Scroll down
    final listView = find.byType(ListView);
    await tester.scrollUntilVisible(
      find.text('Parent 30'),
      200,
      scrollable: listView,
    );

    await tester.pumpAndSettle();

    // FAB should now be visible
    expect(find.byIcon(Icons.arrow_upward), findsOneWidget);
  });

  testWidgets('should scroll to top when FAB is tapped', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(mockRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Scroll down to show FAB
    final listView = find.byType(ListView);
    await tester.scrollUntilVisible(
      find.text('Parent 30'),
      200,
      scrollable: listView,
    );

    await tester.pumpAndSettle();

    // Tap the FAB
    await tester.tap(find.byIcon(Icons.arrow_upward));
    await tester.pumpAndSettle();

    // Should be scrolled to top (first item should be visible)
    expect(find.text('Parent 0'), findsOneWidget);
  });

  testWidgets('should reset pagination on filter change', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(mockRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Change depth filter
    await tester.tap(find.byType(DropdownButton<int?>));
    await tester.pumpAndSettle();

    // Select depth 1
    await tester.tap(find.text('1').last);
    await tester.pumpAndSettle();

    // Should reset to first page
    verify(mockRepo.listIncomplete(depth: 1, offset: 0)).called(1);
  });

  testWidgets('should handle search query changes with debouncing',
      (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(mockRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Type search query
    await tester.enterText(find.byType(TextField), 'new search');

    // Should not search immediately
    verifyNever(mockRepo.listIncomplete(query: 'new search'));

    // Wait for debounce
    await tester.pump(const Duration(milliseconds: 350));

    // Should search with new query
    verify(mockRepo.listIncomplete(query: 'new search')).called(1);
  });

  testWidgets('should handle rapid search changes correctly', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          editTreeRepositoryProvider.overrideWithValue(mockRepo),
        ],
        child: const MaterialApp(
          home: EditTreeScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Type multiple search queries rapidly
    await tester.enterText(find.byType(TextField), 'first');
    await tester.pump(const Duration(milliseconds: 100));
    await tester.enterText(find.byType(TextField), 'second');
    await tester.pump(const Duration(milliseconds: 100));
    await tester.enterText(find.byType(TextField), 'final');

    // Wait for debounce
    await tester.pump(const Duration(milliseconds: 350));

    // Should only search with final query
    verify(mockRepo.listIncomplete(query: 'final')).called(1);
    verifyNever(mockRepo.listIncomplete(query: 'first'));
    verifyNever(mockRepo.listIncomplete(query: 'second'));
  });
}
