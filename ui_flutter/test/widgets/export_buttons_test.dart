import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:flutter/material.dart';
import 'package:lorien/widgets/export_buttons.dart';

// Generate mocks
@GenerateMocks([Dio])
import 'export_buttons_test.mocks.dart';

void main() {
  group('ExportButtons Widget Tests', () {
    late MockDio mockDio;

    setUp(() {
      mockDio = MockDio();
    });

    testWidgets('can be instantiated without errors', (tester) async {
      // Just verify the widget can be created without crashing
      expect(() => ExportButtons(baseUrl: '/api/v1', dio: mockDio), returnsNormally);
    });

    testWidgets('has required constructor parameters', (tester) async {
      final widget = ExportButtons(baseUrl: '/api/v1', dio: mockDio);
      expect(widget.baseUrl, equals('/api/v1'));
      expect(widget.dio, equals(mockDio));
    });
  });
}
