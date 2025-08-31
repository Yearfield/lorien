import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:dio/dio.dart';
import 'package:lorien/providers/settings_provider.dart';
import 'package:lorien/screens/outcomes/outcomes_detail_screen.dart';
import 'package:lorien/data/triage_repository.dart';
import 'package:lorien/models/triage_models.dart';

// Generate mocks
@GenerateMocks([Dio, TriageRepository])
import 'outcomes_detail_screen_test.mocks.dart';

void main() {
  group('OutcomesDetailScreen Tests', () {
    late MockDio mockDio;
    late MockTriageRepository mockRepo;

    setUp(() {
      mockDio = MockDio();
      mockRepo = MockTriageRepository();
    });

    testWidgets('shows guidance text and Save button after loading', (WidgetTester tester) async {
      // Mock the repository to return a leaf node
      when(mockRepo.getLeaf(1)).thenAnswer((_) async => TriageDetail(
        nodeId: 1,
        diagnosticTriage: 'Test triage',
        actions: 'Test actions',
        isLeaf: true,
      ));

      await tester.pumpWidget(
        ChangeNotifierProvider(
          create: (_) => SettingsProvider(),
          child: MaterialApp(
            home: Builder(
              builder: (context) {
                // Create the screen with mocked dependencies
                return OutcomesDetailScreen(
                  nodeId: 1,
                  llmEnabled: false,
                );
              },
            ),
          ),
        ),
      );

      // Wait for loading to complete
      await tester.pumpAndSettle();

      // Verify the guidance text is displayed
      expect(find.textContaining('AI suggestions are guidance-only'), findsOneWidget);
      
      // Verify the Save button is present
      expect(find.text('Save'), findsOneWidget);
    });
  });
}
