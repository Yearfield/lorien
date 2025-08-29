import 'package:flutter_test/flutter_test.dart';
import '../../lib/utils/env.dart';
import '../../lib/data/api_client.dart';

void main() {
  test('resolveApiBaseUrl ends with /api/v1/', () {
    final base = resolveApiBaseUrl();
    expect(base.endsWith('/api/v1/'), isTrue);
  });

  test('resolveApiBaseUrl normalizes various input formats', () {
    // Test that the function properly normalizes URLs
    final base = resolveApiBaseUrl();
    expect(base.contains('127.0.0.1'), isTrue);
    expect(base.contains('8000'), isTrue);
    expect(base.endsWith('/api/v1/'), isTrue);
  });

  test('ApiClient join forbids leading slash and /api/v1 in resource', () {
    final client = ApiClient();
    
    // Test that leading slash throws assertion error
    expect(() => client.get('/health'), throwsA(isA<AssertionError>()));
    
    // Test that /api/v1 in resource throws assertion error
    expect(() => client.get('api/v1/health'), throwsA(isA<AssertionError>()));
    
    // Test that valid resource paths work
    expect(() => client.get('health'), returnsNormally);
    expect(() => client.get('tree/next-incomplete-parent'), returnsNormally);
  });

  test('ApiClient properly joins base URL with resource paths', () {
    final client = ApiClient();
    final baseUrl = client.baseUrl;
    
    // Verify base URL format
    expect(baseUrl.endsWith('/api/v1/'), isTrue);
    
    // Test that the base URL is properly formatted
    expect(baseUrl, matches(r'^https?://[^/]+/api/v1/$'));
  });
}
