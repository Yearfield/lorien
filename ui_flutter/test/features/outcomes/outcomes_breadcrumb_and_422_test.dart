import 'package:flutter_test/flutter_test.dart';
import '../../../lib/core/validators/field_validators.dart';

void main() {
  test('Field validators prohibit dosing tokens', () {
    expect(
      maxSevenWordsAndAllowed('Take 10 mg tablet', field: 'Test'),
      contains('prohibited tokens'),
    );
    expect(
      maxSevenWordsAndAllowed('Inject IV q6h', field: 'Test'),
      contains('prohibited tokens'),
    );
    expect(
      maxSevenWordsAndAllowed('Give 5 ml PO bid', field: 'Test'),
      contains('prohibited tokens'),
    );
  });

  test('Field validators allow valid content', () {
    expect(
      maxSevenWordsAndAllowed('Suspected pneumonia requires chest X-ray', field: 'Test'),
      isNull,
    );
    expect(
      maxSevenWordsAndAllowed('Administer oxygen and monitor vital signs', field: 'Test'),
      isNull,
    );
  });

  test('Field validators enforce 7 word limit', () {
    expect(
      maxSevenWordsAndAllowed('This is a very long sentence with more than seven words in it', field: 'Test'),
      contains('≤7 words'),
    );
  });

  test('Field validators enforce allowed characters', () {
    expect(
      maxSevenWordsAndAllowed('Invalid @#\$% characters', field: 'Test'),
      contains('disallowed characters'),
    );
  });
}
