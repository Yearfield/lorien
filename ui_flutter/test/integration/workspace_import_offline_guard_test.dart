import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lorien/features/workspace/ui/workspace_screen.dart';
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
  testWidgets('Workspace screen renders correctly with offline mock', (tester) async {
    // Create mock health state indicating API is offline
    final mockHealth = HealthStatus(
      ok: false, // API is offline
      version: '1.0.0',
      lastPing: DateTime.now(),
      db: const DbInfo(path: '/db', wal: true, foreignKeys: true),
      features: const Features(llm: true, csvExport: true),
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          healthControllerProvider.overrideWith(() => TestHealthController(mockHealth)),
        ],
        child: const MaterialApp(
          home: WorkspaceScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Basic smoke test - verify the screen renders
    expect(find.text('Workspace'), findsOneWidget);
    expect(find.text('Import Data'), findsOneWidget);
    expect(find.text('Export Data'), findsOneWidget);
    expect(find.text('Select Excel/CSV'), findsOneWidget);
    expect(find.text('Select CSV'), findsOneWidget);
  });

  testWidgets('Workspace screen renders correctly with online mock', (tester) async {
    // Create mock health state indicating API is online
    final mockHealth = HealthStatus(
      ok: true, // API is online
      version: '1.0.0',
      lastPing: DateTime.now(),
      db: const DbInfo(path: '/db', wal: true, foreignKeys: true),
      features: const Features(llm: true, csvExport: true),
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          healthControllerProvider.overrideWith(() => TestHealthController(mockHealth)),
        ],
        child: const MaterialApp(
          home: WorkspaceScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Verify screen renders correctly when API is online
    expect(find.text('Workspace'), findsOneWidget);
    expect(find.text('Import Data'), findsOneWidget);
    expect(find.text('Export Data'), findsOneWidget);
    expect(find.text('Select Excel/CSV'), findsOneWidget);
    expect(find.text('Select CSV'), findsOneWidget);

    // Verify no offline banner when API is online
    expect(find.text('API Offline'), findsNothing);
  });
}
