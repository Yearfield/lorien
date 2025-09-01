import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/api_client.dart';

class HealthStatus {
  const HealthStatus(
      {required this.ok, required this.version, required this.lastPing});
  final bool ok;
  final String version;
  final DateTime lastPing;
}

class HealthController extends AsyncNotifier<HealthStatus?> {
  static const _cooldown = Duration(seconds: 10);
  DateTime? _last;

  @override
  Future<HealthStatus?> build() async {
    return ping(); // initial ping on first watch
  }

  Future<HealthStatus?> ping() async {
    if (_last != null && DateTime.now().difference(_last!) < _cooldown) {
      return state.value; // within cooldown
    }
    state = const AsyncLoading();
    try {
      final response = await ApiClient().get('health');
      final data = response.data as Map<String, dynamic>?;
      final ok = data?['ok'] == true;
      final version = (data?['version'] ?? '?').toString();
      final st =
          HealthStatus(ok: ok, version: version, lastPing: DateTime.now());
      _last = st.lastPing;
      state = AsyncData(st);
      return st;
    } catch (e, st) {
      state = AsyncError(e, st);
      return null;
    }
  }
}

final healthControllerProvider =
    AsyncNotifierProvider<HealthController, HealthStatus?>(
        () => HealthController());
