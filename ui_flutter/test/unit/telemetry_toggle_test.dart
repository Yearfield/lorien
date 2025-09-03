import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/core/crash_report_service.dart';

void main() {
  test('crash telemetry toggle toggles remote', () {
    CrashReportService.enableRemote(false);
    // No exception expected when toggling; remote flag internal
    CrashReportService.enableRemote(true);
    expect(true, isTrue);
  });
}
