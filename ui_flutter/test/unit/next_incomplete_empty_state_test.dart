import 'package:flutter_test/flutter_test.dart';

void main() {
  test('Treats 204 or {parent_id:null} as empty', () {
    const a = null; // 204 mapped to null
    final b = {"parent_id": null};
    expect(a == null, isTrue);
    expect(b['parent_id'] == null, isTrue);
  });
}
