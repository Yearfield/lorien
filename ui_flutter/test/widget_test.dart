// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lorien/widgets/connection_banner.dart';
import 'package:dio/dio.dart';

void main() {
  testWidgets('ConnectionBanner smoke test', (WidgetTester tester) async {
    // Create a simple mock health call
    Future<Response<dynamic>> mockHealthCall() async {
      return Response(
        data: {'status': 'ok'},
        requestOptions: RequestOptions(path: '/api/v1/health'),
      );
    }

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          home: Scaffold(
            body: ConnectionBanner(healthCall: mockHealthCall),
          ),
        ),
      ),
    );

    // Basic structure test - should show loading initially
    expect(find.byType(ConnectionBanner), findsOneWidget);
  });
}
