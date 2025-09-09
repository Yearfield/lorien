import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class ExportApi {
  final String baseUrl; // may or may not already include /api/v1
  final http.Client _client;
  ExportApi(this.baseUrl, {http.Client? client}) : _client = client ?? http.Client();

  String _v1(String path) {
    // normalize base (strip trailing '/')
    var b = baseUrl;
    while (b.endsWith('/')) b = b.substring(0, b.length - 1);
    final hasV1 = b.endsWith('/api/v1');
    // normalize path (no leading /api/v1, ensure leading '/')
    var p = path;
    if (p.startsWith('/api/v1')) {
      p = p.substring('/api/v1'.length);
    }
    if (!p.startsWith('/')) p = '/$p';
    final url = '${hasV1 ? b : '$b/api/v1'}$p';
    if (kDebugMode) print('[ExportApi] GET $url');
    return url;
  }

  Future<Uint8List> downloadCsv() async {
    final r = await _client.get(Uri.parse(_v1('/tree/export')));
    if (r.statusCode != 200) {
      throw Exception('CSV export failed: HTTP ${r.statusCode}');
    }
    return r.bodyBytes;
  }

  Future<Uint8List> downloadXlsx() async {
    final r = await _client.get(Uri.parse(_v1('/tree/export.xlsx')));
    if (r.statusCode != 200) {
      throw Exception('XLSX export failed: HTTP ${r.statusCode}');
    }
    return r.bodyBytes;
  }
}
