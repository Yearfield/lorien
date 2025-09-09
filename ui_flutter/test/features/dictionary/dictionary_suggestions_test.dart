import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mockito/mockito.dart';
import 'package:lorien/features/dictionary/ui/dictionary_suggestions_overlay.dart';
import 'package:lorien/features/dictionary/data/dictionary_repository.dart';

class MockDictionaryRepository extends Mock implements DictionaryRepository {
  @override
  Future<List<String>> getSuggestions(String type, String query,
      {int limit = 10}) async {
    if (query == 'test') {
      return ['test case', 'test scenario', 'testing framework'];
    }
    return [];
  }
}

void main() {
  late MockDictionaryRepository mockRepo;

  setUp(() {
    mockRepo = MockDictionaryRepository();
  });

  testWidgets('should show suggestions overlay when typing >= 2 characters',
      (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          dictionaryRepositoryProvider.overrideWithValue(mockRepo),
        ],
        child: MaterialApp(
          home: Scaffold(
            body: DictionarySuggestionsOverlay(
              type: 'node_label',
              currentText: 'test',
              onSuggestionSelected: (_) {},
              onDismiss: () {},
            ),
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Should show suggestions
    expect(find.text('test case'), findsOneWidget);
    expect(find.text('test scenario'), findsOneWidget);
    expect(find.text('testing framework'), findsOneWidget);
  });

  testWidgets('should not show suggestions when typing < 2 characters',
      (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          dictionaryRepositoryProvider.overrideWithValue(mockRepo),
        ],
        child: MaterialApp(
          home: Scaffold(
            body: DictionarySuggestionsOverlay(
              type: 'node_label',
              currentText: 't',
              onSuggestionSelected: (_) {},
              onDismiss: () {},
            ),
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Should not show any suggestions
    expect(find.text('test case'), findsNothing);
  });

  testWidgets('should call onSuggestionSelected when suggestion is tapped',
      (tester) async {
    String? selectedSuggestion;

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          dictionaryRepositoryProvider.overrideWithValue(mockRepo),
        ],
        child: MaterialApp(
          home: Scaffold(
            body: DictionarySuggestionsOverlay(
              type: 'node_label',
              currentText: 'test',
              onSuggestionSelected: (suggestion) {
                selectedSuggestion = suggestion;
              },
              onDismiss: () {},
            ),
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Tap on first suggestion
    await tester.tap(find.text('test case'));
    await tester.pumpAndSettle();

    // Should have called onSuggestionSelected with the correct suggestion
    expect(selectedSuggestion, 'test case');
  });

  testWidgets('should show loading indicator while fetching suggestions',
      (tester) async {
    // Create a repository that takes time to respond
    final slowRepo = MockDictionaryRepository();
    when(slowRepo.getSuggestions(any, any, limit: anyNamed('limit')))
        .thenAnswer((_) async {
      await Future.delayed(const Duration(seconds: 1));
      return ['slow suggestion'];
    });

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          dictionaryRepositoryProvider.overrideWithValue(slowRepo),
        ],
        child: MaterialApp(
          home: Scaffold(
            body: DictionarySuggestionsOverlay(
              type: 'node_label',
              currentText: 'slow',
              onSuggestionSelected: (_) {},
              onDismiss: () {},
            ),
          ),
        ),
      ),
    );

    // Should show loading indicator initially
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await tester.pumpAndSettle();

    // Should show suggestions after loading
    expect(find.text('slow suggestion'), findsOneWidget);
  });

  testWidgets('should show error state when suggestions fail to load',
      (tester) async {
    final failingRepo = MockDictionaryRepository();
    when(failingRepo.getSuggestions(any, any, limit: anyNamed('limit')))
        .thenThrow(Exception('Network error'));

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          dictionaryRepositoryProvider.overrideWithValue(failingRepo),
        ],
        child: MaterialApp(
          home: Scaffold(
            body: DictionarySuggestionsOverlay(
              type: 'node_label',
              currentText: 'fail',
              onSuggestionSelected: (_) {},
              onDismiss: () {},
            ),
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Should show error message
    expect(find.text('Failed to load suggestions'), findsOneWidget);
    expect(find.byIcon(Icons.error_outline), findsOneWidget);
  });

  testWidgets('should have proper visual styling', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          dictionaryRepositoryProvider.overrideWithValue(mockRepo),
        ],
        child: MaterialApp(
          home: Scaffold(
            body: DictionarySuggestionsOverlay(
              type: 'node_label',
              currentText: 'test',
              onSuggestionSelected: (_) {},
              onDismiss: () {},
            ),
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Should have proper styling
    expect(find.byIcon(Icons.lightbulb_outline), findsWidgets);
    final container = tester.widget<Container>(
      find
          .descendant(
            of: find.byType(DictionarySuggestionsOverlay),
            matching: find.byType(Container),
          )
          .first,
    );
    expect(container.decoration, isNotNull);
  });
}
