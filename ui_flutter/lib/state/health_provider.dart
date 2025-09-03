import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import '../data/api_client.dart';

class DbInfo {
  const DbInfo({required this.path, required this.wal, required this.foreignKeys});
  final String path;
  final bool wal;
  final bool foreignKeys;
}

class Features {
  const Features({required this.llm, required this.csvExport});
  final bool llm;
  final bool csvExport;
}

class HealthStatus {
  const HealthStatus({
    required this.ok,
    required this.version,
    required this.lastPing,
    required this.db,
    required this.features,
  });
  final bool ok;
  final String version;
  final DateTime lastPing;
  final DbInfo db;
  final Features features;
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
      final response = await ApiClient.I().get('health');
      final data = response.data as Map<String, dynamic>?;
      final ok = data?['ok'] == true;
      final version = (data?['version'] ?? '?').toString();

      final dbData = data?['db'] as Map<String, dynamic>? ?? {};
      final db = DbInfo(
        path: (dbData['path'] ?? '?').toString(),
        wal: dbData['wal'] == true,
        foreignKeys: dbData['foreign_keys'] == true,
      );

      final featuresData = data?['features'] as Map<String, dynamic>? ?? {};
      final features = Features(
        llm: featuresData['llm'] == true,
        csvExport: featuresData['csv_export'] == true,
      );

      final st = HealthStatus(
        ok: ok,
        version: version,
        lastPing: DateTime.now(),
        db: db,
        features: features,
      );
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

final connectivityProvider = StreamProvider<ConnectivityResult>(
  (ref) => Connectivity().onConnectivityChanged.expand((results) => results),
);
