import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:file_selector/file_selector.dart';
import '../../data/export_api.dart';

class ExportPanel extends StatefulWidget {
  final String baseUrl;
  const ExportPanel({super.key, required this.baseUrl});
  @override
  State<ExportPanel> createState() => _ExportPanelState();
}

class _ExportPanelState extends State<ExportPanel> {
  bool _busy = false;

  Future<void> _saveBytes(Uint8List bytes, {required bool csv}) async {
    final suggested = csv ? 'tree_export.csv' : 'tree_export.xlsx';
    final loc = await getSaveLocation(
      suggestedName: suggested,
      acceptedTypeGroups: [
        XTypeGroup(extensions: [csv ? 'csv' : 'xlsx'])
      ],
    );
    if (loc == null) return; // canceled
    final file = XFile.fromData(
      bytes,
      name: suggested,
      mimeType: csv
          ? 'text/csv'
          : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    );
    await file.saveTo(loc.path);
    if (!mounted) return;
    ScaffoldMessenger.of(context)
        .showSnackBar(SnackBar(content: Text('Saved $suggested')));
  }

  Future<void> _doExport(bool csv) async {
    if (_busy) return;
    setState(() => _busy = true);
    try {
      final api = ExportApi(widget.baseUrl);
      final bytes = csv ? await api.downloadCsv() : await api.downloadXlsx();
      await _saveBytes(bytes, csv: csv);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Export failed: $e')),
      );
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Wrap(spacing: 8, children: [
      ElevatedButton.icon(
          key: const Key('btn_export_csv'),
          onPressed: _busy ? null : () => _doExport(true),
          icon: const Icon(Icons.download),
          label: const Text('Export CSV')),
      OutlinedButton.icon(
          key: const Key('btn_export_xlsx'),
          onPressed: _busy ? null : () => _doExport(false),
          icon: const Icon(Icons.grid_on),
          label: const Text('Export XLSX')),
    ]);
  }
}
