import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import '../../../lib/features/outcomes/data/llm_api.dart';

class MockDio implements Dio {
  dynamic mockResponse;

  @override
  Future<Response<T>> get<T>(String path, {Map<String, dynamic>? queryParameters, Options? options, CancelToken? cancelToken, ProgressCallback? onReceiveProgress}) async {
    return Response<T>(
      data: mockResponse as T,
      statusCode: 200,
      requestOptions: RequestOptions(path: path),
    );
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

void main() {
  late MockDio mockDio;
  late LlmApi llmApi;

  setUp(() {
    mockDio = MockDio();
    llmApi = LlmApi(mockDio);
  });

  test('LLM health returns ready=true when status=200 and ready=true', () async {
    mockDio.mockResponse = {
      'ready': true,
      'checked_at': '2024-01-01T12:00:00Z'
    };

    final result = await llmApi.health();
    expect(result.ready, isTrue);
    expect(result.checkedAt, '2024-01-01T12:00:00Z');
  });

  test('LLM health returns ready=false when status=503', () async {
    mockDio.mockResponse = {
      'ready': false,
      'checked_at': '2024-01-01T12:00:00Z'
    };

    final result = await llmApi.health();
    expect(result.ready, isFalse);
    expect(result.checkedAt, '2024-01-01T12:00:00Z');
  });

  test('LLM health handles missing checked_at gracefully', () async {
    mockDio.mockResponse = {'ready': true};

    final result = await llmApi.health();
    expect(result.ready, isTrue);
    expect(result.checkedAt, isNull);
  });

  test('LLM health handles missing ready field as true by default', () async {
    mockDio.mockResponse = {'checked_at': '2024-01-01T12:00:00Z'};

    final result = await llmApi.health();
    expect(result.ready, isTrue);
    expect(result.checkedAt, '2024-01-01T12:00:00Z');
  });
}
