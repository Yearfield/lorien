import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import '../../../lib/core/services/health_service.dart';
import '../../../lib/shared/widgets/connected_badge.dart';

void main() {
  group('LlmBadge', () {
    testWidgets('shows Unknown when no LLM health data', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: LlmBadge(),
            ),
          ),
        ),
      );

      expect(find.text('LLM: Unknown'), findsOneWidget);
    });

    testWidgets('shows Disabled when LLM is disabled', (tester) async {
      final container = ProviderContainer(
        overrides: [
          llmHealthProvider.overrideWithValue({
            'ok': false,
            'llm_enabled': false,
            'ready': false,
          }),
        ],
      );

      await tester.pumpWidget(
        UncontrolledProviderScope(
          container: container,
          child: const MaterialApp(
            home: Scaffold(
              body: LlmBadge(),
            ),
          ),
        ),
      );

      expect(find.text('LLM: Disabled'), findsOneWidget);
    });

    testWidgets('shows Ready when LLM is enabled and ready', (tester) async {
      final container = ProviderContainer(
        overrides: [
          llmHealthProvider.overrideWithValue({
            'ok': true,
            'llm_enabled': true,
            'ready': true,
          }),
        ],
      );

      await tester.pumpWidget(
        UncontrolledProviderScope(
          container: container,
          child: const MaterialApp(
            home: Scaffold(
              body: LlmBadge(),
            ),
          ),
        ),
      );

      expect(find.text('LLM: Ready'), findsOneWidget);
    });

    testWidgets('shows Unavailable when LLM is enabled but not ready', (tester) async {
      final container = ProviderContainer(
        overrides: [
          llmHealthProvider.overrideWithValue({
            'ok': false,
            'llm_enabled': true,
            'ready': false,
          }),
        ],
      );

      await tester.pumpWidget(
        UncontrolledProviderScope(
          container: container,
          child: const MaterialApp(
            home: Scaffold(
              body: LlmBadge(),
            ),
          ),
        ),
      );

      expect(find.text('LLM: Unavailable'), findsOneWidget);
    });
  });
}
