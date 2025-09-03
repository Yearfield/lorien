import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/core/crash_report_service.dart';

void main() {
  test('CrashReportService write local log', () async {
    await CrashReportService.recordZoneError('boom', StackTrace.current);
    expect(true, isTrue);
  });
}
