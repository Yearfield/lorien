import 'package:flutter_test/flutter_test.dart';
import 'package:http_mock_adapter/http_mock_adapter.dart';
import 'package:lorien/api/lorien_api.dart';
import 'package:lorien/data/api_client.dart';

void main() {
  late DioAdapter dioAdapter;
  late LorienApi api;

  setUp(() {
    dioAdapter = DioAdapter();
    final client = ApiClient.I();
    client.dio.httpClientAdapter = dioAdapter;
    api = LorienApi(client);
  });

  group('Edit Tree API Integration', () {
    test('getParentChildren returns correct data structure', () async {
      // Mock the API response
      dioAdapter.onGet('/tree/parent/123/children').reply(200, {
        'parent_id': 123,
        'version': 7,
        'missing_slots': [2, 4],
        'children': [
          {
            'slot': 1,
            'node_id': 456,
            'label': 'Fever',
            'updated_at': '2025-01-01T12:00:00Z'
          },
          {
            'slot': 2,
            'node_id': 0,
            'label': '',
            'updated_at': '2025-01-01T12:00:00Z'
          },
          {
            'slot': 3,
            'node_id': 789,
            'label': 'High',
            'updated_at': '2025-01-01T12:00:00Z'
          },
        ],
        'path': {
          'node_id': 123,
          'is_leaf': false,
          'depth': 1,
          'vital_measurement': 'Temperature',
          'nodes': ['', '', '', '', '']
        },
        'etag': 'W/"parent-123:v7"'
      });

      final result = await api.getParentChildren(123);

      expect(result.parentId, 123);
      expect(result.version, 7);
      expect(result.missingSlots, [2, 4]);
      expect(result.children.length, 3);
      expect(result.children[0].label, 'Fever');
      expect(result.path['vital_measurement'], 'Temperature');
      expect(result.etag, 'W/"parent-123:v7"');
    });

    test('updateParentChildren handles successful save', () async {
      dioAdapter.onPut('/tree/parent/123/children').reply(200, {
        'parent_id': 123,
        'version': 8,
        'missing_slots': [],
        'updated': [1, 2, 3]
      });

      final body = {
        'children': [
          {'slot': 1, 'label': 'Fever'},
          {'slot': 2, 'label': 'High'},
          {'slot': 3, 'label': 'Severe'}
        ]
      };

      final result = await api.updateParentChildren(123, body);

      expect(result['parent_id'], 123);
      expect(result['version'], 8);
      expect(result['missing_slots'], []);
      expect(result['updated'], [1, 2, 3]);
    });

    test('updateParentChildren handles 409 conflict', () async {
      dioAdapter.onPut('/tree/parent/123/children').reply(409, {
        'detail': [
          {
            'type': 'conflict.slot',
            'msg': 'Concurrent changes detected',
            'ctx': {'slot': 2, 'server_label': 'Different', 'server_version': 8}
          }
        ]
      });

      final body = {
        'children': [
          {'slot': 2, 'label': 'New Label'}
        ]
      };

      expect(
        () => api.updateParentChildren(123, body),
        throwsA(isA<Exception>()),
      );
    });

    test('updateParentChildren handles 422 validation errors', () async {
      dioAdapter.onPut('/tree/parent/123/children').reply(422, {
        'detail': [
          {
            'type': 'value_error.word_count',
            'msg': 'Label too long',
            'ctx': {'slot': 1}
          }
        ]
      });

      final body = {
        'children': [
          {'slot': 1, 'label': 'Very long label that exceeds word limit'}
        ]
      };

      expect(
        () => api.updateParentChildren(123, body),
        throwsA(isA<Exception>()),
      );
    });
  });
}
