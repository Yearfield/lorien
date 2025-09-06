import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../http/api_client.dart';

final baseUrlProvider =
    StateProvider<String>((_) => 'http://127.0.0.1:8000/api/v1');
final lastPingProvider = StateProvider<DateTime?>((_) => null);
final connectedProvider = StateProvider<bool>((_) => false);

class HealthResult {
  final bool ok;
  final int statusCode;
  final String testedUrl;
  final String bodySnippet; // ≤100 chars (for Settings)
  final String? version;
  final bool? wal;
  final bool? foreignKeys;
  final bool? llmEnabled;
  HealthResult(this.ok, this.statusCode, this.testedUrl, this.bodySnippet,
      {this.version, this.wal, this.foreignKeys, this.llmEnabled});

  Map<String, dynamic> get serverInfo {
    return {
      'version': version,
      'wal_enabled': wal,
      'foreign_keys_enabled': foreignKeys,
      'llm_enabled': llmEnabled,
    };
  }
}

final healthServiceProvider = Provider((ref) => HealthService(ref));

class HealthService {
  final Ref _ref;
  HealthService(this._ref);

  Future<HealthResult> test() async {
    final base = _ref.read(baseUrlProvider);
    final url = '$base/health';
    try {
      final dio = _ref.read(dioProvider);
      final res = await dio.get('/health');
      final data = res.data as Map? ?? {};
      final raw = data.toString();
      final body = raw.length <= 100 ? raw : raw.substring(0, 100);
      final ok = res.statusCode == 200;
      _ref.read(connectedProvider.notifier).state = ok;
      _ref.read(lastPingProvider.notifier).state = DateTime.now();
      return HealthResult(
        ok, res.statusCode ?? 0, url, body,
        version: data['version']?.toString(),
        wal: data['db']?['wal'] as bool?,
        foreignKeys: data['db']?['foreign_keys'] as bool?,
        llmEnabled: data['features']?['llm'] as bool?,
      );
    } on DioException catch (e) {
      final code = e.response?.statusCode ?? 0;
      final data = e.response?.data?.toString() ?? e.message ?? 'error';
      final body = data.length <= 100 ? data : data.substring(0, 100);
      _ref.read(connectedProvider.notifier).state = false;
      _ref.read(lastPingProvider.notifier).state = DateTime.now();
      return HealthResult(false, code, url, body);
    }
  }
}
