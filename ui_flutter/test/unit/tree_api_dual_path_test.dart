import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:http_mock_adapter/http_mock_adapter.dart';
import 'package:lorien/features/tree/data/tree_api.dart';

void main() {
  group('TreeApi dual path fallback', () {
    late Dio dio;
    late DioAdapter adapter;
    late TreeApi treeApi;

    setUp(() {
      dio = Dio(BaseOptions(baseUrl: 'http://test/api/v1'));
      adapter = DioAdapter(dio: dio);
      treeApi = TreeApi(dio);
    });

    test('readChildren falls back to legacy endpoint on 404', () async {
      // Mock 404 for canonical endpoint
      adapter.onGet(
        '/tree/123/children',
        (server) => server.reply(404, {'detail': 'not found'}),
      );

      // Mock 200 for legacy endpoint
      adapter.onGet(
        '/tree/parent/123/children',
        (server) => server.reply(200, {
          'parent_id': 123,
          'version': 7,
          'missing_slots': [2, 5],
          'children': [
            {'slot': 1, 'node_id': 101, 'label': 'A', 'updated_at': '2025-08-31T00:00:00Z'},
            {'slot': 2, 'node_id': 102, 'label': '', 'updated_at': '2025-08-31T00:00:00Z'},
            {'slot': 3, 'node_id': 103, 'label': 'B', 'updated_at': '2025-08-31T00:00:00Z'},
            {'slot': 4, 'node_id': 104, 'label': '', 'updated_at': '2025-08-31T00:00:00Z'},
            {'slot': 5, 'node_id': 105, 'label': 'C', 'updated_at': '2025-08-31T00:00:00Z'},
          ],
          'path': {
            'node_id': 123, 'is_leaf': false, 'depth': 1, 'vital_measurement': 'VM',
            'nodes': ['', '', '', '', '']
          }
        }),
      );

      final result = await treeApi.readChildren(123);

      expect(result['parent_id'], 123);
      expect(result['version'], 7);
      expect(result['missing_slots'], [2, 5]);
      expect(result['children'], isA<List>());
      expect((result['children'] as List).length, 5);
    });

    test('readChildren throws on non-404 error', () async {
      // Mock 500 for canonical endpoint
      adapter.onGet(
        '/tree/123/children',
        (server) => server.reply(500, {'error': 'Internal server error'}),
      );

      expect(
        () => treeApi.readChildren(123),
        throwsA(isA<DioException>()),
      );
    });
  });
}
