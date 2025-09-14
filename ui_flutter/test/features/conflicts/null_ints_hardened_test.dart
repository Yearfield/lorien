import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mockito/mockito.dart';
import 'package:dio/dio.dart';

import 'package:lorien/features/conflicts/data/conflicts_repository.dart';

class MockConflictsRepository extends Mock implements ConflictsRepository {}

void main() {
  group('Null Ints Hardened Tests', () {
    testWidgets('handles null integer fields gracefully in ConflictsPage', (WidgetTester tester) async {
      // Mock API response with null/missing integer fields
      final mockResponse = {
        'items': [
          {
            'parent_id': null,  // null integer
            'label': 'Test Parent',
            'depth': 'invalid',  // non-integer string
            'child_count': null,  // null integer
            'slot_dup_count': 'not_a_number',  // non-parseable string
            'null_slot_count': null,  // null integer
            'overfilled': false,
            'underfilled': false,
            'duplicate_parents': null,  // null integer
            'variant_sets': null,  // null integer
          }
        ],
        'total': null,  // null integer
        'limit': 'invalid',  // non-integer string
        'offset': null,  // null integer
      };

      // Test that the repository can parse the response without crashing
      final result = ConflictsPage.fromJson(mockResponse);
      
      // Verify that null values are handled gracefully (converted to 0)
      expect(result.total, equals(0));
      expect(result.limit, equals(0));
      expect(result.offset, equals(0));
      expect(result.items.length, equals(1));
      
      final item = result.items.first;
      expect(item.parentId, equals(0));
      expect(item.depth, equals(0));
      expect(item.childCount, equals(0));
      expect(item.slotDupCount, equals(0));
      expect(item.nullSlotCount, equals(0));
      expect(item.duplicateParents, equals(0));
      expect(item.variantSets, equals(0));
      expect(item.label, equals('Test Parent'));
    });

    testWidgets('handles group endpoint with null integers', (WidgetTester tester) async {
      // Mock group response with null integers
      final mockGroupResponse = {
        'group': [
          {
            'id': 1,
            'label': 'Test Parent',
            'depth': null,  // null integer
          }
        ],
        'children': [
          {
            'child_id': null,  // null integer
            'from_id': 'invalid',  // non-integer string
            'slot': null,  // null integer
            'label': 'Test Child',
          }
        ],
        'summary': {
          'unique_children': null,  // null integer
          'total_children': 'not_a_number',  // non-parseable string
        }
      };

      // Test that the repository can parse the response without crashing
      final result = GroupPayload.fromJson(mockGroupResponse);
      
      // Verify that null values are handled gracefully (converted to 0)
      expect(result.summary.uniqueChildren, equals(0));
      expect(result.summary.totalChildren, equals(0));
    });

    testWidgets('progress HUD handles zero total gracefully', (WidgetTester tester) async {
      // Mock empty response
      final mockResponse = {
        'items': [],
        'total': 0,
        'limit': 5,
        'offset': 0,
      };

      final result = ConflictsPage.fromJson(mockResponse);
      
      // Verify the response is parsed correctly
      expect(result.items, isEmpty);
      expect(result.total, equals(0));
      expect(result.limit, equals(5));
      expect(result.offset, equals(0));
    });
  });
}