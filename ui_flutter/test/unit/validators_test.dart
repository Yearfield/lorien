import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/core/validators/field_validators.dart';

void main() {
  test('≤7 words passes; 8 fails', () {
    expect(maxSevenWordsAndAllowed('one two three four five six seven', field: 'T'), isNull);
    expect(maxSevenWordsAndAllowed('one two three four five six seven eight', field: 'T'), isNotNull);
  });
  
  test('Allowed regex', () {
    expect(maxSevenWordsAndAllowed('Shock index high', field: 'T'), isNull);
    expect(maxSevenWordsAndAllowed('Hello 👋', field: 'T'), isNotNull);
  });
  
  test('Empty string fails', () {
    expect(maxSevenWordsAndAllowed('', field: 'T'), isNotNull);
    expect(maxSevenWordsAndAllowed('   ', field: 'T'), isNotNull);
  });
  
  test('Special characters allowed', () {
    expect(maxSevenWordsAndAllowed('Blood pressure, high', field: 'T'), isNull);
    expect(maxSevenWordsAndAllowed('Heart rate - elevated', field: 'T'), isNull);
  });
}
