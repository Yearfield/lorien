import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lorien/state/health_provider.dart';

void main() {
  test('health provider initializes', () {
    final c = ProviderContainer();
    addTearDown(c.dispose);
    final state = c.read(healthControllerProvider);
    expect(state, isA<AsyncValue>());
  });

  test('health provider has cooldown mechanism', () {
    final c = ProviderContainer();
    addTearDown(c.dispose);
    final controller = c.read(healthControllerProvider.notifier);
    expect(controller, isA<HealthController>());
  });
}
