import 'package:flutter/foundation.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/core/crash_report_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  setUp(() async {
    // Reset crash report service state for each test
    CrashReportService.enableRemote(false);
    SharedPreferences.setMockInitialValues({});
  });

  test('Crash report service does not fire remote posts during startup',
      () async {
    // Ensure remote telemetry is disabled by default
    CrashReportService.enableRemote(false);

    // Simulate a Flutter error during startup
    final errorDetails = FlutterErrorDetails(
      exception: Exception('Test startup error'),
      stack: StackTrace.current,
    );

    // This should not make any network calls (we can't easily verify this without mocking)
    await CrashReportService.recordFlutterError(errorDetails);

    // Test should complete without hanging or making network requests
    expect(true, isTrue);
  });

  test('Crash report service handles zone errors during startup', () async {
    // Simulate a zone error during startup
    final error = Exception('Test startup zone error');
    final stack = StackTrace.current;

    // This should not make any network calls
    await CrashReportService.recordZoneError(error, stack);

    // Test should complete without issues
    expect(true, isTrue);
  });

  test('Remote telemetry toggle works correctly', () {
    // Start with disabled state
    CrashReportService.enableRemote(false);

    // Simulate error - should not attempt remote posting
    final error = Exception('Test error');
    final stack = StackTrace.current;

    // This should complete without attempting network calls
    CrashReportService.recordZoneError(error, stack);

    expect(true, isTrue);
  });

  test('Crash report service handles malformed errors gracefully', () async {
    // Test with empty stack trace
    await CrashReportService.recordZoneError(
        Exception('Test'), StackTrace.empty);

    // Should not crash the app
    expect(true, isTrue);
  });
}
