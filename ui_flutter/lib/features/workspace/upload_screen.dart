import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http_parser/http_parser.dart';

class UploadScreen extends StatefulWidget {
  final String baseUrl;
  final http.Client? client;
  const UploadScreen({super.key, this.baseUrl = const String.fromEnvironment('API_BASE_URL', defaultValue: 'http://127.0.0.1:8000'), this.client});

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  String? _filePath;
  String? _fileName;
  String _status = 'idle';
  String? _error;
  Map<String, dynamic>? _ctx;

  http.Client get _http => widget.client ?? http.Client();

  Future<void> _pickAndUpload() async {
    setState(() { _status = 'queued'; _error = null; _ctx = null; });

    final res = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['xlsx', 'xls', 'csv'],
      withData: true,
    );
    if (res == null || res.files.isEmpty) {
      setState(() { _status = 'idle'; });
      return;
    }
    final f = res.files.single;
    _fileName = f.name;
    _filePath = f.path ?? f.name;

    setState(() { _status = 'processing'; });

    final uri = Uri.parse('${widget.baseUrl}/api/v1/import');
    final request = http.MultipartRequest('POST', uri);

    final bytes = f.bytes ?? await File(f.path!).readAsBytes();
    final mime = f.extension == 'csv'
        ? 'text/csv'
        : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';

    request.files.add(http.MultipartFile.fromBytes('file', bytes, filename: _fileName, contentType: MediaType('application', 'octet-stream')));
    // Workaround: some servers inspect the actual filename to infer type; we also set contentType above.

    try {
      final streamed = await _http.send(request);
      final resp = await http.Response.fromStream(streamed);

      if (resp.statusCode == 200) {
        setState(() { _status = 'done'; _error = null; _ctx = null; });
        try {
          final sp = await SharedPreferences.getInstance();
          await sp.setString('workspace_last_uploaded_file', _fileName ?? '');
        } catch (_) {}
      } else if (resp.statusCode == 422) {
        try {
          final body = jsonDecode(resp.body);
          final first = (body['detail'] as List).isNotEmpty ? body['detail'][0] : null;
          setState(() {
            _status = 'error';
            _error = first?['msg'] ?? 'Unprocessable Entity';
            _ctx = (first?['ctx'] as Map?)?.map((k, v) => MapEntry(k.toString(), v));
          });
        } catch (_) {
          setState(() { _status = 'error'; _error = '422 (invalid header)'; });
        }
      } else {
        setState(() { _status = 'error'; _error = 'HTTP ${resp.statusCode}'; });
      }
    } catch (e) {
      setState(() { _status = 'error'; _error = 'Upload failed: $e'; });
    }
  }

  @override
  Widget build(BuildContext context) {
    final statusChip = Chip(label: Text('Status: $_status'));
    return Scaffold(
      appBar: AppBar(title: const Text('Workspace → Upload')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ElevatedButton.icon(
              onPressed: _pickAndUpload,
              icon: const Icon(Icons.upload_file),
              label: const Text('Select & Upload (.xlsx/.csv)'),
            ),
            const SizedBox(height: 12),
            if (_fileName != null) Text('File: $_fileName'),
            const SizedBox(height: 8),
            statusChip,
            if (_error != null) ...[
              const SizedBox(height: 8),
              Text(_error!, style: const TextStyle(color: Colors.red)),
            ],
            if (_ctx != null) ...[
              const SizedBox(height: 8),
              Text('Header diff:', style: const TextStyle(fontWeight: FontWeight.bold)),
              Text('row=${_ctx!['row']} col_index=${_ctx!['col_index']}'),
              const SizedBox(height: 4),
              const Text('expected:'),
              Text((_ctx!['expected'] as List).join(' | ')),
              const SizedBox(height: 4),
              const Text('received:'),
              Text((_ctx!['received'] as List).join(' | ')),
            ],
          ],
        ),
      ),
    );
  }
}
