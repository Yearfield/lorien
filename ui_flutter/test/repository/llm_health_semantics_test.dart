import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:mockito/mockito.dart';
import 'package:lorien/features/outcomes/data/llm_api.dart';

// Mock Dio for testing
class MockDio extends Mock implements Dio {}

void main() {
  late MockDio mockDio;
  late LlmApi llmApi;

  setUp(() {
    mockDio = MockDio();
    llmApi = LlmApi(mockDio);
  });

  group('LLM Health Semantics', () {
    test('health returns ready=true and checkedAt on 200', () async {
      // Arrange
      final response = Response(
        data: {'ready': true, 'checked_at': '2024-01-01T12:00:00Z'},
        statusCode: 200,
        requestOptions: RequestOptions(path: '/llm/health'),
      );

      when(mockDio.get('/llm/health')).thenAnswer((_) async => response);

      // Act
      final result = await llmApi.health();

      // Assert
      expect(result.ready, true);
      expect(result.checkedAt, '2024-01-01T12:00:00Z');
    });

    test('health returns ready=false and checkedAt on 503', () async {
      // Arrange
      final response = Response(
        data: {'ready': false, 'checked_at': '2024-01-01T12:00:00Z'},
        statusCode: 503,
        requestOptions: RequestOptions(path: '/llm/health'),
      );

      when(mockDio.get('/llm/health')).thenAnswer((_) async => response);

      // Act
      final result = await llmApi.health();

      // Assert
      expect(result.ready, false);
      expect(result.checkedAt, '2024-01-01T12:00:00Z');
    });

    test('health returns ready=false on error', () async {
      // Arrange
      when(mockDio.get('/llm/health')).thenThrow(DioException(
        requestOptions: RequestOptions(path: '/llm/health'),
        error: 'Network error',
      ));

      // Act
      final result = await llmApi.health();

      // Assert
      expect(result.ready, false);
      expect(result.checkedAt, null);
    });
  });
}
