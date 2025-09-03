import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:mockito/mockito.dart';
import 'package:lorien/features/tree/data/tree_api.dart';

// Mock Dio for testing
class MockDio extends Mock implements Dio {}

void main() {
  late MockDio mockDio;
  late TreeApi treeApi;

  setUp(() {
    mockDio = MockDio();
    treeApi = TreeApi(mockDio);
  });

  group('Next Incomplete Empty State', () {
    test('nextIncompleteParent returns null on 204', () async {
      // Arrange
      final response = Response(
        statusCode: 204,
        requestOptions: RequestOptions(path: '/tree/next-incomplete-parent'),
      );

      when(mockDio.get(
        '/tree/next-incomplete-parent',
        validateStatus: anyNamed('validateStatus'),
      )).thenAnswer((_) async => response);

      // Act
      final result = await treeApi.nextIncompleteParent();

      // Assert
      expect(result, null);
    });

    test('nextIncompleteParent returns null when parent_id is null', () async {
      // Arrange
      final response = Response(
        data: {'parent_id': null, 'missing_slots': '1,2'},
        statusCode: 200,
        requestOptions: RequestOptions(path: '/tree/next-incomplete-parent'),
      );

      when(mockDio.get(
        '/tree/next-incomplete-parent',
        validateStatus: anyNamed('validateStatus'),
      )).thenAnswer((_) async => response);

      // Act
      final result = await treeApi.nextIncompleteParent();

      // Assert
      expect(result, null);
    });

    test('nextIncompleteParent returns data when available', () async {
      // Arrange
      final response = Response(
        data: {
          'parent_id': 123,
          'label': 'Test Parent',
          'depth': 1,
          'missing_slots': '2,4'
        },
        statusCode: 200,
        requestOptions: RequestOptions(path: '/tree/next-incomplete-parent'),
      );

      when(mockDio.get(
        '/tree/next-incomplete-parent',
        validateStatus: anyNamed('validateStatus'),
      )).thenAnswer((_) async => response);

      // Act
      final result = await treeApi.nextIncompleteParent();

      // Assert
      expect(result, isNotNull);
      expect(result!['parent_id'], 123);
      expect(result['label'], 'Test Parent');
      expect(result['depth'], 1);
      expect(result['missing_slots'], '2,4');
    });
  });
}
