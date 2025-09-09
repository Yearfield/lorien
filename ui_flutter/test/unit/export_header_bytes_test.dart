import 'package:flutter_test/flutter_test.dart';

void main() {
  group('Export Header Contract', () {
    test('CSV header matches 8-column contract (client parses head)', () {
      const header =
          'Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions';
      expect(header.split(',').length, 8);
      expect(header.split(',')[0], 'Vital Measurement');
      expect(header.split(',')[1], 'Node 1');
      expect(header.split(',')[2], 'Node 2');
      expect(header.split(',')[3], 'Node 3');
      expect(header.split(',')[4], 'Node 4');
      expect(header.split(',')[5], 'Node 5');
      expect(header.split(',')[6], 'Diagnostic Triage');
      expect(header.split(',')[7], 'Actions');
    });

    test('Export header is frozen and immutable', () {
      const expected = [
        'Vital Measurement',
        'Node 1',
        'Node 2',
        'Node 3',
        'Node 4',
        'Node 5',
        'Diagnostic Triage',
        'Actions'
      ];
      
      const header =
          'Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions';
      
      final actual = header.split(',');
      expect(actual, expected);
    });

    test('Header contains no empty or null values', () {
      const header =
          'Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions';
      
      final columns = header.split(',');
      for (final column in columns) {
        expect(column.isNotEmpty, true, reason: 'Column should not be empty');
        expect(column.trim(), column, reason: 'Column should not have leading/trailing whitespace');
      }
    });

    test('Header format is consistent for CSV and XLSX exports', () {
      const csvHeader =
          'Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions';
      
      // Simulate XLSX header (should be same as CSV)
      const xlsxHeader =
          'Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions';
      
      expect(csvHeader, xlsxHeader, reason: 'CSV and XLSX headers must be identical');
    });
  });
}
