import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:http_mock_adapter/http_mock_adapter.dart';
import 'package:lorien/core/util/error_mapper.dart';

void main() {
  group('duplicate_child_label error mapping', () {
    test('maps duplicate_child_label to slot error', () {
      final responseData = {
        'detail': [
          {
            'type': 'value_error.duplicate_child_label',
            'msg': 'Child label "Test" already exists for this parent',
            'ctx': {'slot': 2}
          }
        ]
      };

      final result = mapPydanticFieldErrors(responseData);

      expect(result['duplicate_child_label'], 'Child label "Test" already exists for this parent');
    });

    test('maps multiple error types including duplicate_child_label', () {
      final responseData = {
        'detail': [
          {
            'type': 'value_error.word_count',
            'msg': 'Too many words',
            'loc': ['diagnostic_triage']
          },
          {
            'type': 'value_error.duplicate_child_label',
            'msg': 'Duplicate label found',
            'ctx': {'slot': 3}
          },
          {
            'type': 'value_error.children_count',
            'msg': 'Must have exactly 5 children'
          }
        ]
      };

      final result = mapPydanticFieldErrors(responseData);

      expect(result['diagnostic_triage'], 'Too many words');
      expect(result['duplicate_child_label'], 'Duplicate label found');
      expect(result['children_count'], 'Must have exactly 5 children');
    });

    test('ignores non-duplicate_child_label errors', () {
      final responseData = {
        'detail': [
          {
            'type': 'value_error.word_count',
            'msg': 'Too many words',
            'loc': ['actions']
          }
        ]
      };

      final result = mapPydanticFieldErrors(responseData);

      expect(result['actions'], 'Too many words');
      expect(result.containsKey('duplicate_child_label'), false);
    });

    test('handles 422 response with duplicate_child_label in Edit Tree context', () {
      // Simulate a 422 response from the server
      final responseData = {
        'detail': [
          {
            'loc': ['body', 'children', 1, 'label'],
            'msg': 'duplicate label under same parent',
            'type': 'value_error.duplicate_child_label',
            'ctx': {'slot': 2}
          }
        ]
      };

      // Test error mapping
      final mapped = mapPydanticFieldErrors(responseData);
      expect(mapped['duplicate_child_label'], 'duplicate label under same parent');
    });
  });
}
