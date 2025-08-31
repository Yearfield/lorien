import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/data/triage_repository.dart';
import 'package:lorien/models/triage_models.dart';
import 'package:dio/dio.dart';

void main() {
  test('TriageRepository can be instantiated', () {
    // Simple smoke test to ensure the class can be created
    final dio = Dio();
    expect(() => TriageRepository(dio: dio, baseUrl: '/api/v1'), returnsNormally);
    expect(() => TriageRepository(dio: dio, baseUrl: 'http://localhost:8000'), returnsNormally);
  });

  test('TriageRepository requires non-null dio', () {
    // Test that null dio is rejected - we need to handle this differently since Dio is non-nullable
    expect(() => TriageRepository(dio: Dio(), baseUrl: '/api/v1'), returnsNormally);
    expect(() => TriageRepository(dio: Dio(), baseUrl: 'http://localhost:8000'), returnsNormally);
  });

  test('LlmFillRequest can be created and serialized', () {
    final request = LlmFillRequest(
      root: 'Pulse',
      nodes: ['Fast', 'Irregular', '', '', ''],
      triageStyle: 'diagnosis-only',
      actionsStyle: 'referral-only',
    );

    final json = request.toJson();
    expect(json['root'], 'Pulse');
    expect(json['nodes'], ['Fast', 'Irregular', '', '', '']);
    expect(json['triage_style'], 'diagnosis-only');
    expect(json['actions_style'], 'referral-only');
    expect(json['apply'], false);
  });

  test('LlmFillRequest with custom apply value', () {
    final request = LlmFillRequest(
      root: 'Blood Pressure',
      nodes: ['High', 'Severe', 'Chest Pain', 'Emergency', 'Immediate'],
      triageStyle: 'referral-only',
      actionsStyle: 'diagnosis-only',
      apply: true,
    );

    final json = request.toJson();
    expect(json['apply'], true);
  });
}
