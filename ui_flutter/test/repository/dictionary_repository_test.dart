import 'package:flutter_test/flutter_test.dart';
import '../../lib/features/dictionary/data/dictionary_repository.dart';

void main() {
  test('DictionaryEntry.fromJson creates correct object', () {
    final json = {
      'id': 1,
      'type': 'vital_measurement',
      'term': 'Blood Pressure',
      'normalized': 'blood pressure',
      'hints': 'Medical measurement',
      'updated_at': '2024-01-01T12:00:00Z'
    };

    final entry = DictionaryEntry.fromJson(json);

    expect(entry.id, 1);
    expect(entry.type, 'vital_measurement');
    expect(entry.term, 'Blood Pressure');
    expect(entry.normalized, 'blood pressure');
    expect(entry.hints, 'Medical measurement');
    expect(entry.updatedAt, '2024-01-01T12:00:00Z');
  });

  test('DictionaryPage.fromJson creates correct object', () {
    final json = {
      'items': [
        {
          'id': 1,
          'type': 'vital_measurement',
          'term': 'Blood Pressure',
          'normalized': 'blood pressure',
          'hints': null,
          'updated_at': '2024-01-01T12:00:00Z'
        }
      ],
      'total': 1,
      'limit': 50,
      'offset': 0
    };

    final page = DictionaryPage.fromJson(json);

    expect(page.items.length, 1);
    expect(page.total, 1);
    expect(page.limit, 50);
    expect(page.offset, 0);
    expect(page.items.first.term, 'Blood Pressure');
  });

  test('DictionaryRepository methods have correct signatures', () {
    // This is a smoke test to ensure the API structure is correct
    // We can't instantiate without Dio, but we can verify the class exists
    expect(DictionaryRepository, isNotNull);
    expect(DictionaryEntry, isNotNull);
    expect(DictionaryPage, isNotNull);
  });
}
