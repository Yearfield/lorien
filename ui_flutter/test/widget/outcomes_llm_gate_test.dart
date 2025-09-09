import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lorien/features/outcomes/ui/outcomes_detail_screen.dart';
import 'package:lorien/state/health_provider.dart';

class TestHealthController extends HealthController {
  TestHealthController(this._mockHealth);

  final HealthStatus _mockHealth;

  @override
  Future<HealthStatus?> build() async => _mockHealth;

  @override
  Future<HealthStatus?> ping() async => _mockHealth;
}

void main() {
  testWidgets('shows LLM disabled notice when llm=false', (tester) async {
    // Create a mock health state with LLM disabled
    final mockHealth = HealthStatus(
      ok: true,
      version: '1.0.0',
      lastPing: DateTime.now(),
      db: const DbInfo(path: '/db', wal: true, foreignKeys: true),
      features: const Features(llm: false),
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          healthControllerProvider
              .overrideWith(() => TestHealthController(mockHealth)),
        ],
        child: const MaterialApp(
          home: OutcomesDetailScreen(outcomeId: 'test'),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Verify disabled message is shown
    expect(find.text('LLM Features Disabled'), findsOneWidget);
    expect(find.textContaining('disabled by server configuration'),
        findsOneWidget);
    expect(find.byIcon(Icons.auto_awesome), findsOneWidget);
  });

  testWidgets('shows normal UI when llm=true', (tester) async {
    // Create a mock health state with LLM enabled
    final mockHealth = HealthStatus(
      ok: true,
      version: '1.0.0',
      lastPing: DateTime.now(),
      db: const DbInfo(path: '/db', wal: true, foreignKeys: true),
      features: const Features(llm: true),
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          healthControllerProvider
              .overrideWith(() => TestHealthController(mockHealth)),
        ],
        child: const MaterialApp(
          home: OutcomesDetailScreen(outcomeId: 'test'),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Verify normal UI is shown (no disabled message)
    expect(find.text('LLM Features Disabled'), findsNothing);
    expect(find.text('Diagnostic Triage'), findsOneWidget);
    expect(find.text('Actions'), findsOneWidget);
  });
}
