import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lorien/state/flags_search_provider.dart';

void main() {
  test('flags query provider updates state', () {
    final c = ProviderContainer();
    addTearDown(c.dispose);
    expect(c.read(flagsQueryProvider), '');
    c.read(flagsQueryProvider.notifier).state = 'abc';
    expect(c.read(flagsQueryProvider), 'abc');
  });
}
