import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:lorien/data/api_client.dart';
import 'package:lorien/data/repos/outcomes_repository.dart';

// Generate mocks
@GenerateMocks([Dio, ApiClient])
import 'outcomes_put_fallback_test.mocks.dart';

void main() {
  late MockApiClient mockApiClient;
  late OutcomesRepository repo;

  setUp(() {
    mockApiClient = MockApiClient();
    repo = OutcomesRepository(mockApiClient);
  });

  group('OutcomesRepository fallback tests', () {
    test('getOutcomes uses /outcomes first', () async {
      // Arrange
      final mockResponse = Response(
        data: {'diagnostic_triage': 'Test', 'actions': 'Actions'},
        statusCode: 200,
        requestOptions: RequestOptions(path: '/outcomes/1'),
      );

      when(mockApiClient.get('/outcomes/1')).thenAnswer((_) async => mockResponse);

      // Act
      final result = await repo.getOutcomes(1);

      // Assert
      expect(result?.diagnosticTriage, 'Test');
      expect(result?.actions, 'Actions');
      verify(mockApiClient.get('/outcomes/1')).called(1);
      verifyNever(mockApiClient.get('/triage/1'));
    });

    test('getOutcomes falls back to /triage on 404', () async {
      // Arrange
      final notFoundResponse = Response(
        statusCode: 404,
        requestOptions: RequestOptions(path: '/outcomes/1'),
      );

      final triageResponse = Response(
        data: {'diagnostic_triage': 'Fallback', 'actions': 'Fallback Actions'},
        statusCode: 200,
        requestOptions: RequestOptions(path: '/triage/1'),
      );

      when(mockApiClient.get('/outcomes/1')).thenAnswer((_) async => notFoundResponse);
      when(mockApiClient.get('/triage/1')).thenAnswer((_) async => triageResponse);

      // Act
      final result = await repo.getOutcomes(1);

      // Assert
      expect(result?.diagnosticTriage, 'Fallback');
      expect(result?.actions, 'Fallback Actions');
      verify(mockApiClient.get('/outcomes/1')).called(1);
      verify(mockApiClient.get('/triage/1')).called(1);
    });

    test('updateOutcomes uses /outcomes first', () async {
      // Arrange
      final mockResponse = Response(
        statusCode: 200,
        requestOptions: RequestOptions(path: '/outcomes/1'),
      );

      when(mockApiClient.put('/outcomes/1', data: anyNamed('data')))
          .thenAnswer((_) async => mockResponse);

      // Act
      await repo.updateOutcomes(1, const TriageDTO(diagnosticTriage: 'Test', actions: 'Actions'));

      // Assert
      verify(mockApiClient.put('/outcomes/1', data: anyNamed('data'))).called(1);
      verifyNever(mockApiClient.put('/triage/1', data: anyNamed('data')));
    });

    test('updateOutcomes falls back to /triage on 405', () async {
      // Arrange
      final methodNotAllowedResponse = Response(
        statusCode: 405,
        requestOptions: RequestOptions(path: '/outcomes/1'),
      );

      final triageResponse = Response(
        statusCode: 200,
        requestOptions: RequestOptions(path: '/triage/1'),
      );

      when(mockApiClient.put('/outcomes/1', data: anyNamed('data')))
          .thenAnswer((_) async => methodNotAllowedResponse);
      when(mockApiClient.put('/triage/1', data: anyNamed('data')))
          .thenAnswer((_) async => triageResponse);

      // Act
      await repo.updateOutcomes(1, const TriageDTO(diagnosticTriage: 'Test', actions: 'Actions'));

      // Assert
      verify(mockApiClient.put('/outcomes/1', data: anyNamed('data'))).called(1);
      verify(mockApiClient.put('/triage/1', data: anyNamed('data'))).called(1);
    });
  });
}
