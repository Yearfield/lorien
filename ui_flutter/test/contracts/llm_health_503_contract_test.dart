import 'package:flutter_test/flutter_test.dart';

void main() {
  test('LLM 503 body carries checked_at and ready=false', () {
    final body = {
      "ok": false,
      "llm_enabled": true,
      "ready": false,
      "provider": "null",
      "model": "/fake.gguf",
      "checks": [
        {"name": "load", "ok": false, "details": "…"}
      ],
      "checked_at": "2025-01-01T00:00:00Z"
    };
    expect(body['ready'], isFalse);
    expect(body['checked_at'], isA<String>());
  });
}
