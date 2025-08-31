import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:flutter/material.dart';
import 'package:lorien/widgets/chained_calculator.dart';

// Generate mocks
@GenerateMocks([Dio])
import 'chained_calculator_test.mocks.dart';

void main() {
  group('ChainedCalculator Widget Tests', () {
    late MockDio mockDio;

    setUp(() {
      mockDio = MockDio();
    });

    testWidgets('can be instantiated without errors', (tester) async {
      // Mock the API call to avoid network errors
      when(mockDio.get('/api/v1/calc/options', queryParameters: {}))
          .thenAnswer((_) async => Response(
                data: {'roots': ['VM1', 'VM2'], 'remaining': 0},
                requestOptions: RequestOptions(path: '/api/v1/calc/options'),
              ));
      
      // Just verify the widget can be created without crashing
      expect(() => ChainedCalculator(baseUrl: '/api/v1', dio: mockDio), returnsNormally);
    });

    testWidgets('has required constructor parameters', (tester) async {
      final widget = ChainedCalculator(baseUrl: '/api/v1', dio: mockDio);
      expect(widget.baseUrl, equals('/api/v1'));
      expect(widget.dio, equals(mockDio));
    });
  });
}
