import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/api_client.dart';

final flagsQueryProvider = StateProvider<String>((ref) => '');

final flagsResultsProvider =
    AsyncNotifierProvider<FlagsSearchController, List<Map<String, dynamic>>>(
        () {
  return FlagsSearchController();
});

class FlagsSearchController extends AsyncNotifier<List<Map<String, dynamic>>> {
  Timer? _debounce;
  KeepAliveLink? _keepAlive;
  static const _debounceMs = 250;

  @override
  Future<List<Map<String, dynamic>>> build() async {
    _keepAlive ??= ref.keepAlive();
    ref.onDispose(() {
      _debounce?.cancel();
      _keepAlive?.close();
    });
    final q = ref.watch(flagsQueryProvider);
    final c = Completer<List<Map<String, dynamic>>>();
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: _debounceMs), () async {
      try {
        final data =
            await ApiClient.I().getJson('flags/search', query: {'q': q});
        final items = (data['items'] as List?)?.cast<Map<String, dynamic>>() ??
            const <Map<String, dynamic>>[];
        c.complete(items);
      } catch (e, st) {
        c.completeError(e, st);
      }
    });
    return c.future;
  }
}
