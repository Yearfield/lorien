import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http_mock_adapter/http_mock_adapter.dart';
import 'package:lorien/api/lorien_api.dart';
import 'package:lorien/data/api_client.dart';
import 'package:lorien/providers/lorien_api_provider.dart';

void main() {
  late DioAdapter dioAdapter;
  late ProviderContainer container;
  late LorienApi api;

  setUp(() {
    dioAdapter = DioAdapter();
    final client = ApiClient.I();
    client.dio.httpClientAdapter = dioAdapter;
    api = LorienApi(client);

    container = ProviderContainer(
      overrides: [
        lorienApiProvider.overrideWithValue(api),
      ],
    );
  });

  tearDown(() {
    container.dispose();
  });

  group('UI Backend Integration', () {
    test('Health endpoint integration', () async {
      dioAdapter.onGet('/health').reply(200, {
        'ok': true,
        'version': '6.8.0-beta.1',
        'db': {'path': '/tmp/lorien.db', 'wal': true, 'foreign_keys': true},
        'features': {'llm': false}
      });

      final health = await api.health();

      expect(health['ok'], true);
      expect(health['version'], '6.8.0-beta.1');
      expect(health['db']['wal'], true);
      expect(health['features']['llm'], false);
    });

    test('LLM health endpoint integration', () async {
      dioAdapter.onGet('/llm/health').reply(503,
          {'ok': false, 'ready': false, 'checked_at': '2025-01-01T12:00:00Z'});

      final llmHealth = await api.llmHealth();

      expect(llmHealth['ok'], false);
      expect(llmHealth['ready'], false);
      expect(llmHealth['checked_at'], '2025-01-01T12:00:00Z');
    });

    test('Edit Tree parent children integration', () async {
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

      final data = await api.getParentChildren(123);

      expect(data.parentId, 123);
      expect(data.version, 7);
      expect(data.missingSlots, [2, 4]);
      expect(data.children.length, 2);
      expect(data.children[0].label, 'Fever');
      expect(data.path['vital_measurement'], 'Temperature');
      expect(data.etag, 'W/"parent-123:v7"');
    });

    test('Dictionary suggestions integration', () async {
      dioAdapter.onGet('/dictionary', queryParameters: {
        'type': 'node_label',
        'query': 'fe',
        'limit': 10
      }).reply(200, [
        {'id': 1, 'term': 'Fever'},
        {'id': 2, 'term': 'Feverish'},
      ]);

      final suggestions = await api.dictionarySuggest('fe', limit: 10);

      expect(suggestions.length, 2);
      expect(suggestions[0]['term'], 'Fever');
      expect(suggestions[1]['term'], 'Feverish');
    });

    test('Tree path integration', () async {
      dioAdapter
          .onGet('/tree/path', queryParameters: {'node_id': 456}).reply(200, {
        'node_id': 456,
        'is_leaf': true,
        'depth': 5,
        'vital_measurement': 'Temperature',
        'nodes': ['Fever', 'High', 'Severe', 'Acute', 'Primary']
      });

      final path = await api.getPath(456);

      expect(path['node_id'], 456);
      expect(path['is_leaf'], true);
      expect(path['depth'], 5);
      expect(path['vital_measurement'], 'Temperature');
      expect(path['nodes'], ['Fever', 'High', 'Severe', 'Acute', 'Primary']);
    });

    test('Next incomplete parent integration', () async {
      dioAdapter.onGet('/tree/next-incomplete-parent').reply(200, {
        'parent_id': 789,
        'label': 'Blood Pressure',
        'depth': 0,
        'missing_slots': [3, 5]
      });

      final next = await api.nextIncompleteParent();

      expect(next, isNotNull);
      expect(next!['parent_id'], 789);
      expect(next['label'], 'Blood Pressure');
      expect(next['missing_slots'], [3, 5]);
    });

    test('Next incomplete parent 204 integration', () async {
      dioAdapter.onGet('/tree/next-incomplete-parent').reply(204);

      final next = await api.nextIncompleteParent();

      expect(next, isNull);
    });

    test('Outcomes PUT integration', () async {
      dioAdapter.onPut('/outcomes/456').reply(200, {
        'diagnostic_triage': 'Acute infection',
        'actions': 'Administer antibiotics'
      });

      final response = await api.putOutcome(456, {
        'diagnostic_triage': 'Acute infection',
        'actions': 'Administer antibiotics'
      });

      expect(response.statusCode, 200);
    });
  });
}
