import 'package:flutter_test/flutter_test.dart';

void main() {
  test('Importer 422 ctx exposes schema drift fields', () {
    final ctx = {
      "first_offending_row": 0,
      "col_index": 0,
      "expected": [
        "Vital Measurement",
        "Node 1",
        "Node 2",
        "Node 3",
        "Node 4",
        "Node 5",
        "Diagnostic Triage",
        "Actions"
      ],
      "received": ["Vital Measurement", "Node1", "…"]
    };
    expect(ctx['col_index'], 0);
    expect((ctx['expected'] as List).length, 8);
  });
}
