import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/core/util/error_mapper.dart';

void main() {
  test('Pydantic detail[] maps to fields', () {
    final resp = {
      "detail":[
        {"loc":["body","diagnostic_triage"],"msg":"Diagnostic Triage must be ≤7 words"},
        {"loc":["body","actions"],"msg":"Actions has disallowed characters"}
      ]
    };
    final m = mapPydanticFieldErrors(resp);
    expect(m['diagnostic_triage'], contains('≤7 words'));
    expect(m['actions'], contains('disallowed'));
  });
  
  test('Empty detail list returns empty map', () {
    final resp = {"detail": []};
    final m = mapPydanticFieldErrors(resp);
    expect(m, isEmpty);
  });
  
  test('Null response returns empty map', () {
    final m = mapPydanticFieldErrors(null);
    expect(m, isEmpty);
  });
  
  test('Missing detail key returns empty map', () {
    final resp = {"other": "data"};
    final m = mapPydanticFieldErrors(resp);
    expect(m, isEmpty);
  });
  
  test('Complex location paths are handled', () {
    final resp = {
      "detail":[
        {"loc":["body","diagnostic_triage","nested"],"msg":"Nested error"},
        {"loc":["body","actions"],"msg":"Simple error"}
      ]
    };
    final m = mapPydanticFieldErrors(resp);
    expect(m['diagnostic_triage'], contains('Nested error'));
    expect(m['actions'], contains('Simple error'));
  });
}
