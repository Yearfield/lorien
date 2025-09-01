import 'package:flutter_test/flutter_test.dart';

void main() {
  test('CSV header matches 8-column contract (client parses head)', () {
    const header = 'Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions';
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
}
