import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/data/dto/incomplete_parent_dto.dart';

void main() {
  test('decodes snake_case json from API', () {
    final json = {
      'parent_id': 2,
      'missing_slots': [1, 2, 3, 4, 5],
    };
    final dto = IncompleteParentDTO.fromJson(json);
    expect(dto.parentId, 2);
    expect(dto.missingSlots, [1, 2, 3, 4, 5]);
  });

  test('handles null missing_slots gracefully', () {
    final json = {
      'parent_id': 3,
      'missing_slots': null,
    };
    final dto = IncompleteParentDTO.fromJson(json);
    expect(dto.parentId, 3);
    expect(dto.missingSlots, isEmpty);
  });

  test('handles empty missing_slots array', () {
    final json = {
      'parent_id': 4,
      'missing_slots': [],
    };
    final dto = IncompleteParentDTO.fromJson(json);
    expect(dto.parentId, 4);
    expect(dto.missingSlots, isEmpty);
  });

  test('handles string missing_slots (comma-separated)', () {
    final json = {
      'parent_id': 5,
      'missing_slots': '1,2,3',
    };
    final dto = IncompleteParentDTO.fromJson(json);
    expect(dto.parentId, 5);
    expect(dto.missingSlots, [1, 2, 3]);
  });

  test('handles mixed data types in missing_slots', () {
    final json = {
      'parent_id': 6,
      'missing_slots': [1, '2', 3.0, '4', 5],
    };
    final dto = IncompleteParentDTO.fromJson(json);
    expect(dto.parentId, 6);
    expect(dto.missingSlots, [1, 2, 3, 4, 5]);
  });
}
