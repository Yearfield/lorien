import 'dart:io';
import 'package:flutter/foundation.dart';
import '../data/api_client.dart';

class CrashReportService {
  static bool _remoteEnabled = false;
  static void enableRemote(bool v) => _remoteEnabled = v;

  static Future<void> recordFlutterError(FlutterErrorDetails d) async {
    await _writeLocal('flutter', d.exceptionAsString(), d.stack?.toString());
    if (_remoteEnabled) {
      await _postRemote('flutter', d.exceptionAsString(), d.stack?.toString());
    }
  }

  static Future<void> recordZoneError(Object e, StackTrace st) async {
    await _writeLocal('zone', e.toString(), st.toString());
    if (_remoteEnabled) {
      await _postRemote('zone', e.toString(), st.toString());
    }
  }

  static Future<void> _writeLocal(String kind, String msg, String? st) async {
    final f = await _logFile();
    final line = '${DateTime.now().toIso8601String()} [$kind] $msg\n$st\n';
    await f.writeAsString(line, mode: FileMode.append, flush: true);
  }

  static Future<void> _postRemote(String kind, String msg, String? st) async {
    try {
      await ApiClient.I().postJson('telemetry/crash', body: {
        'kind': kind,
        'msg': msg,
        'stack': st
      });
    } catch (_) {
      // swallow 404/ network errors silently
    }
  }

  static Future<File> _logFile() async {
    final dir = Directory.systemTemp.createTempSync('lorien-logs');
    return File('${dir.path}/app.log');
  }
}
