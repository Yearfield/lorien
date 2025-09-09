import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/data/api_client.dart';

void main() {
  test('ApiClient singleton returns same instance', () {
    final client1 = ApiClient.I();
    final client2 = ApiClient.I();
    expect(client1, same(client2));
  });

  test('ApiClient setBaseUrl updates base URL', () {
    final client = ApiClient.I();
    final originalBase = client.baseUrl;

    ApiClient.setBaseUrl('http://test.example.com');
    expect(client.baseUrl, 'http://test.example.com/');

    // Restore original
    ApiClient.setBaseUrl(originalBase);
  });

  test('ApiClient join method validates paths', () {
    final client = ApiClient.I();

    // Test that leading slash throws
    expect(() => client.get('/health'), throwsA(isA<AssertionError>()));

    // Test that /api/v1 in path throws
    expect(() => client.get('api/v1/health'), throwsA(isA<AssertionError>()));

    // Test valid paths don't throw
    expect(() => client.get('health'), returnsNormally);
  });
}
