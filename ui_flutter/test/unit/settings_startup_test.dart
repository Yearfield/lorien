import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:lorien/features/settings/logic/settings_controller.dart';
import 'package:lorien/core/services/health_service.dart';

void main() {
  late ProviderContainer container;

  setUp(() async {
    container = ProviderContainer();
    // Set up mock SharedPreferences
    SharedPreferences.setMockInitialValues({});
  });

  tearDown(() {
    container.dispose();
  });

  test('Settings controller loads asynchronously without blocking', () async {
    // Create settings controller
    final settingsController = container.read(settingsControllerProvider);

    // This should not block or make synchronous network calls
    await settingsController.load();

    // Verify that base URL provider was updated
    final baseUrl = container.read(baseUrlProvider);
    expect(baseUrl, isNotNull);
    expect(baseUrl, isNotEmpty);
  });

  test('Settings controller handles missing preferences gracefully', () async {
    // Ensure SharedPreferences is completely empty
    SharedPreferences.setMockInitialValues({});

    final settingsController = container.read(settingsControllerProvider);

    // Should not crash even with empty prefs
    await settingsController.load();

    // Should have fallback values
    final baseUrl = container.read(baseUrlProvider);
    expect(baseUrl, equals('http://127.0.0.1:8000/api/v1'));
  });

  test('Settings controller handles corrupted preferences', () async {
    // Set corrupted data
    SharedPreferences.setMockInitialValues({
      'api_base_url': null,  // Invalid null value
      'theme_mode': 'invalid_mode',
    });

    final settingsController = container.read(settingsControllerProvider);

    // Should handle corruption gracefully
    await settingsController.load();

    // Should fall back to default
    final baseUrl = container.read(baseUrlProvider);
    expect(baseUrl, equals('http://127.0.0.1:8000/api/v1'));
  });

  test('Settings controller saves preferences correctly', () async {
    final settingsController = container.read(settingsControllerProvider);

    // Save a custom URL
    await settingsController.save('http://custom.api.com');

    // Verify it was saved
    final savedUrl = container.read(baseUrlProvider);
    expect(savedUrl, equals('http://custom.api.com'));
  });

  test('Multiple settings controller instances work correctly', () async {
    final controller1 = container.read(settingsControllerProvider);
    final controller2 = container.read(settingsControllerProvider);

    // Both should work independently
    await controller1.load();
    await controller2.save('http://test.com');

    final baseUrl = container.read(baseUrlProvider);
    expect(baseUrl, equals('http://test.com'));
  });
}
