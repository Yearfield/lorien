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
  bool _replace = false;

  http.Client get _http => widget.client ?? http.Client();

  Future<void> _previewImport() async {
    if (_filePath == null) return;
    
    setState(() { _status = 'previewing'; _error = null; });
    
    try {
      final uri = Uri.parse('${widget.baseUrl}/api/v1/import/preview');
      final request = http.MultipartRequest('POST', uri);
      
      final file = File(_filePath!);
      final bytes = await file.readAsBytes();
      final mime = _fileName!.toLowerCase().endsWith('.csv') ? 'text/csv' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      
      request.files.add(http.MultipartFile.fromBytes(
        'file', bytes,
        filename: _fileName,
        contentType: MediaType.parse(mime),
      ));
      
      final response = await _http.send(request);
      final body = await response.stream.bytesToString();
      
      if (response.statusCode == 200) {
        final data = jsonDecode(body);
        _showPreviewDialog(data);
      } else {
        setState(() { _error = 'Preview failed: ${response.statusCode}'; });
      }
    } catch (e) {
      setState(() { _error = 'Preview error: $e'; });
    } finally {
      setState(() { _status = 'idle'; });
    }
  }

  Future<void> _performImport() async {
    if (_filePath == null) return;
    
    setState(() { _status = 'processing'; _error = null; });
    
    try {
      final uri = Uri.parse('${widget.baseUrl}/api/v1/import?mode=${_replace ? 'replace' : 'append'}');
      final request = http.MultipartRequest('POST', uri);
      
      final file = File(_filePath!);
      final bytes = await file.readAsBytes();
      final mime = _fileName!.toLowerCase().endsWith('.csv') ? 'text/csv' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      
      request.files.add(http.MultipartFile.fromBytes(
        'file', bytes,
        filename: _fileName,
        contentType: MediaType.parse(mime),
      ));
      
      final response = await _http.send(request);
      final body = await response.stream.bytesToString();
      
      if (response.statusCode == 200) {
        setState(() { _status = 'done'; _error = null; });
        try {
          final sp = await SharedPreferences.getInstance();
          await sp.setString('workspace_last_uploaded_file', _fileName ?? '');
        } catch (_) {}
      } else if (response.statusCode == 422) {
        try {
          final data = jsonDecode(body);
          final first = (data['detail'] as List).isNotEmpty ? data['detail'][0] : null;
          setState(() {
            _error = first?['msg'] ?? 'Validation error';
            _ctx = first?['ctx'];
          });
        } catch (_) {
          setState(() { _error = 'Validation error'; });
        }
      } else {
        setState(() { _error = 'Upload failed: ${response.statusCode}'; });
      }
    } catch (e) {
      setState(() { _error = 'Upload error: $e'; });
    } finally {
      setState(() { _status = 'idle'; });
    }
  }

  void _showPreviewDialog(Map<String, dynamic> data) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Import Preview'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Rows: ${data['rows']}'),
            Text('Roots detected: ${data['roots_count']}'),
            const SizedBox(height: 8),
            const Text('Root labels:', style: TextStyle(fontWeight: FontWeight.bold)),
            ...(data['roots_detected'] as List).map((root) => Text('• $root')),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              _performImport();
            },
            child: const Text('Import'),
          ),
        ],
      ),
    );
  }

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

    final uri = Uri.parse('${widget.baseUrl}/api/v1/import?mode=${_replace ? 'replace' : 'append'}');
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
            SwitchListTile(
              title: const Text('Replace existing data (atomic)'),
              subtitle: const Text('Clears current nodes/outcomes first'),
              value: _replace,
              onChanged: (v) => setState(() => _replace = v),
            ),
            const SizedBox(height: 12),
            if (_fileName != null) ...[
              Text('File: $_fileName'),
              const SizedBox(height: 8),
              Row(
                children: [
                  ElevatedButton.icon(
                    onPressed: _previewImport,
                    icon: const Icon(Icons.preview),
                    label: const Text('Preview Import'),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton.icon(
                    onPressed: _performImport,
                    icon: const Icon(Icons.upload),
                    label: const Text('Import Now'),
                  ),
                ],
              ),
            ],
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
