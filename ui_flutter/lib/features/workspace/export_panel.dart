import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:file_selector/file_selector.dart';
import 'package:cross_file/cross_file.dart';

class ExportPanel extends StatefulWidget {
  final String baseUrl;
  const ExportPanel({super.key, required this.baseUrl});

  @override
  State<ExportPanel> createState() => _ExportPanelState();
}

class _ExportPanelState extends State<ExportPanel> {
  bool _busy = false;

  Future<void> _download(String fmt) async {
    if (_busy) return;
    setState(() => _busy = true);
    try {
      final isCsv = fmt == 'csv';
      final url = isCsv
          ? '${widget.baseUrl}/api/v1/tree/export'
          : '${widget.baseUrl}/api/v1/tree/export.xlsx';

      // 1) Fetch bytes
      final r = await http.get(Uri.parse(url));
      if (r.statusCode != 200) {
        if (!mounted) return;
        final why = r.statusCode == 404
            ? 'Endpoint not found. Check that /api/v1/tree/export(.xlsx) is mounted.'
            : 'HTTP ${r.statusCode}';
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('Export failed ($why)')));
        return;
      }

      // 2) Ask user where to save (new API)
      final suggestedName = isCsv ? 'tree_export.csv' : 'tree_export.xlsx';
      final location = await getSaveLocation(
        suggestedName: suggestedName,
        acceptedTypeGroups: [
          XTypeGroup(
            label: isCsv ? 'CSV' : 'Excel',
            extensions: isCsv ? ['csv'] : ['xlsx'],
          ),
        ],
      );
      if (location == null) return; // user canceled

      // 3) Package bytes as an XFile and save
      final xfile = XFile.fromData(
        r.bodyBytes,
        name: suggestedName,
        mimeType: isCsv
            ? 'text/csv'
            : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      );
      final file = File(location.path);
      await file.writeAsBytes(await xfile.readAsBytes());

      if (!mounted) return;
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Exported $suggestedName')));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Export error: $e')));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      children: [
        ElevatedButton.icon(
          key: const Key('btn_export_csv'),
          onPressed: _busy ? null : () => _download('csv'),
          icon: const Icon(Icons.download),
          label: const Text('Export CSV'),
        ),
        OutlinedButton.icon(
          key: const Key('btn_export_xlsx'),
          onPressed: _busy ? null : () => _download('xlsx'),
          icon: const Icon(Icons.grid_on),
          label: const Text('Export XLSX'),
        ),
      ],
    );
  }
}
