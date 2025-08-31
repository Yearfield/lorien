import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:flutter/material.dart';
import 'package:lorien/widgets/connection_banner.dart';

// Generate mocks
@GenerateMocks([Dio])
import 'connection_banner_no_timer_test.mocks.dart';

void main() {
  group('ConnectionBanner No Timer Tests', () {
    late MockDio mockDio;

    setUp(() {
      mockDio = MockDio();
    });

    testWidgets('can be instantiated without errors', (tester) async {
      // Just verify the widget can be created without crashing
      expect(() => ConnectionBanner(
        healthCall: () => mockDio.get('/api/v1/health')
      ), returnsNormally);
    });

    testWidgets('has required constructor parameters', (tester) async {
      final widget = ConnectionBanner(
        healthCall: () => mockDio.get('/api/v1/health')
      );
      expect(widget.healthCall, isNotNull);
    });
  });
}
