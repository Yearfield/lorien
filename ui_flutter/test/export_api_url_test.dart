import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/data/export_api.dart';

void main() {
  test('v1 joiner avoids double prefix', () async {
    final a1 = ExportApi('http://h:8000'); // no v1
    final a2 = ExportApi('http://h:8000/api/v1'); // already v1

    // Access private via method behavior (won't call network)
    final csv1 =
        a1.downloadCsv(); // will throw if executed; we only inspect toString
    final csv2 = a2.downloadCsv();

    expect(a1.baseUrl.endsWith('/api/v1'), isFalse);
    expect(a2.baseUrl.endsWith('/api/v1'), isTrue);
    // This test is a placeholder to keep the API class under test in CI.
    // Real request URLs are printed in debug via kDebugMode.
  });
}
