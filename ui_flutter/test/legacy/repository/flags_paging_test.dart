import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:mockito/mockito.dart';
import 'package:lorien/data/repos/flags_repository.dart';

// Mock ApiClient for testing
class MockApiClient extends Mock implements ApiClient {}

void main() {
  late MockApiClient mockApiClient;
  late FlagsRepository repo;

  setUp(() {
    mockApiClient = MockApiClient();
    repo = FlagsRepository(mockApiClient);
  });

  group('Flags Repository Paging', () {
    test('listFlags calls correct endpoint with paging parameters', () async {
      // Arrange
      final mockResponse = Response(
        data: {
          'items': [
            {'id': 1, 'label': 'Test Flag'}
          ],
          'total': 1,
          'limit': 10,
          'offset': 0,
        },
        statusCode: 200,
        requestOptions: RequestOptions(path: '/flags'),
      );

      when(mockApiClient.get('/flags', queryParameters: {
        'query': '',
        'limit': 10,
        'offset': 0,
      })).thenAnswer((_) async => mockResponse);

      // Act
      final result = await repo.listFlags(limit: 10, offset: 0);

      // Assert
      expect(result.items.length, 1);
      expect(result.items[0].id, 1);
      expect(result.items[0].label, 'Test Flag');
      expect(result.total, 1);
      expect(result.limit, 10);
      expect(result.offset, 0);

      verify(mockApiClient.get('/flags', queryParameters: {
        'query': '',
        'limit': 10,
        'offset': 0,
      })).called(1);
    });

    test('listFlags with query parameter', () async {
      // Arrange
      final mockResponse = Response(
        data: {
          'items': [],
          'total': 0,
          'limit': 20,
          'offset': 0,
        },
        statusCode: 200,
        requestOptions: RequestOptions(path: '/flags'),
      );

      when(mockApiClient.get('/flags', queryParameters: {
        'query': 'test',
        'limit': 20,
        'offset': 0,
      })).thenAnswer((_) async => mockResponse);

      // Act
      final result = await repo.listFlags(query: 'test', limit: 20, offset: 0);

      // Assert
      expect(result.items.length, 0);
      expect(result.total, 0);
      expect(result.limit, 20);
      expect(result.offset, 0);
    });
  });
}
