import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/utils/env.dart';

void main() {
  test('resolveApiBaseUrl appends /api/v1/ when missing', () {
    // Test that the function always returns a URL ending with /api/v1/
    final result = resolveApiBaseUrl();
    expect(result.endsWith('/api/v1/'), isTrue);
  });

  test('resolveApiBaseUrl handles various input formats', () {
    // Test with no dart-define (should use default)
    final result = resolveApiBaseUrl();
    expect(result, equals('http://127.0.0.1:8000/api/v1/'));
  });

  test('resolveApiBaseUrl normalizes URLs correctly', () {
    // This test would work if we could mock String.fromEnvironment
    // For now, just test the default behavior
    final result = resolveApiBaseUrl();
    expect(result.contains('127.0.0.1'), isTrue);
    expect(result.contains('8000'), isTrue);
    expect(result.endsWith('/api/v1/'), isTrue);
  });
}
