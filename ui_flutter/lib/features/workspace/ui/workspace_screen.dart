import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:file_selector/file_selector.dart';
import 'package:path_provider/path_provider.dart';
import 'package:dio/dio.dart';
import 'dart:io';
import '../../../data/api_client.dart';
import '../../../widgets/layout/scroll_scaffold.dart';
import '../../../widgets/app_back_leading.dart';
import '../../../widgets/calc_export_dialog.dart';
import '../../../state/health_provider.dart';

class WorkspaceScreen extends ConsumerStatefulWidget {
  const WorkspaceScreen({super.key});

  @override
  ConsumerState<WorkspaceScreen> createState() => _WorkspaceScreenState();
}

class _WorkspaceScreenState extends ConsumerState<WorkspaceScreen> {
  String? _status;
  bool _busy = false;
  bool _csvSupported = true;
  bool _checkedFromFeatures = false;
  bool _apiAvailable = true;

  @override
  void initState() {
    super.initState();
    // Don't make network calls during widget tests
    if (!const bool.fromEnvironment('FLUTTER_TEST')) {
      _detectCsvSupported();
    }
  }

  Future<void> _importFile(String path, {required bool isExcel}) async {
    // Gate behind health check
    final health = await ref.read(healthControllerProvider.future)
        .timeout(const Duration(seconds: 2), onTimeout: () => null);
    _apiAvailable = health?.ok == true;
    if (!_apiAvailable) {
      setState(() {
        _status = '❌ API is offline at ${ApiClient.I().baseUrl}. Start the server or update Settings → API Base URL.';
      });
      return;
    }

    setState(() {
      _busy = true;
      _status = 'Uploading file...';
    });

    try {
      final fileName = path.split('/').last;
      setState(() => _status = 'Uploading $fileName...');

      final file = File(path);
      final bytes = await file.readAsBytes();

      // Create proper FormData with filename for server compatibility
      final formData = FormData.fromMap({
        'file': MultipartFile.fromBytes(bytes, filename: fileName),
        'source': 'workspace',
      });

      final data = await ApiClient.I().postMultipart(
        'import',
        formData: formData,
        onSendProgress: (sent, total) {
          if (!mounted) return;
          if (total > 0) {
            final percent = ((sent / total) * 100).toInt();
            setState(() => _status = 'Uploading $fileName... ${percent}%');
          }
        },
      );

      final summary = data['summary'] ?? 'Successfully imported';
      setState(() => _status = '✅ Import complete: $summary');

    } on ApiUnavailable catch (e) {
      setState(() {
        _status = '❌ Connection failed: Could not reach ${ApiClient.I().baseUrl}. Is the server running?';
        _apiAvailable = false;
      });
    } on ApiFailure catch (e) {
      if (e.statusCode == 422) {
        setState(() => _status = '⚠️ Validation error (422): ${e.message}');
      } else if (e.statusCode == 400) {
        setState(() => _status = '❌ Invalid file format or data structure');
      } else if (e.statusCode == 500) {
        setState(() => _status = '❌ Server error: Please try again later');
      } else {
        setState(() => _status = '❌ Import failed (${e.statusCode ?? 'error'}): ${e.message}');
      }
    } catch (e) {
      final errorMsg = e.toString();
      setState(() => _status = '❌ Import failed: $errorMsg');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _onPickExcelCsv() async {
    try {
      final typeGroup = XTypeGroup(
        label: 'Spreadsheets',
        extensions: ['xlsx', 'xls', 'csv'],
      );
      final XFile? x = await openFile(acceptedTypeGroups: [typeGroup]);
      if (x != null) {
        final isExcel = x.path.endsWith('.xlsx') || x.path.endsWith('.xls');
        await _importFile(x.path, isExcel: isExcel);
      }
    } catch (e) {
      setState(() => _status = 'File selection failed: $e');
    }
  }

  Future<void> _onPickCsv() async {
    try {
      final typeGroup = XTypeGroup(
        label: 'CSV Files',
        extensions: ['csv'],
      );
      final XFile? x = await openFile(acceptedTypeGroups: [typeGroup]);
      if (x != null) {
        await _importFile(x.path, isExcel: false);
      }
    } catch (e) {
      setState(() => _status = 'File selection failed: $e');
    }
  }

  // Helper to build calculator payload for CSV export
  Future<Map<String, dynamic>> _buildCalcPayloadOrPrompt(BuildContext context) async {
    // For now, return a minimal payload structure
    // In a real implementation, this would prompt the user for diagnosis and node values
    return {
      'diagnosis': 'Sample Diagnosis',
      'nodes': [
        {'id': 1, 'value': 'Node 1'},
        {'id': 2, 'value': 'Node 2'},
        {'id': 3, 'value': 'Node 3'},
        {'id': 4, 'value': 'Node 4'},
        {'id': 5, 'value': 'Node 5'},
      ],
    };
  }

  Future<void> _detectCsvSupported() async {
    try {
      final health = await ref.read(healthControllerProvider.future);
      if (health != null && health.features.csvExport != false) { // true or absent -> optimistic
        _csvSupported = health.features.csvExport == true;
        _checkedFromFeatures = true;
      }
    } catch (_) {/* ignore; fall through */}
    if (!_checkedFromFeatures) {
      // Fallback probe if features key absent
      try { await ApiClient.I().head('export/csv'); _csvSupported = true; }
      catch (_) { _csvSupported = false; }
    }
    if (mounted) setState((){});
  }

  Future<void> _exportCsv() async {
    setState(() => _status = 'Preparing CSV export...');
    try {
      // Always prompt for CSV V1 payload; dialog enforces exactly 5.
      final result = await CalcExportDialog.open(context);
      if (result == null) return;
      final payload = {
        'diagnosis': result.diagnosis,
        'nodes': result.nodes.map((n)=> {
          'rank': n.rank,
          'symptom_id': n.symptomId,
          'symptom_label': n.symptomLabel,
          'quality': n.quality,
        }).toList(),
      };
      final resp = await ApiClient.I().postBytes('export/csv', body: payload,
        headers: {'Accept':'text/csv'});
      setState(() => _status = 'Downloading CSV file...');

      final dir = await getDownloadsDirectory() ?? await getApplicationDocumentsDirectory();
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final file = File('${dir.path}/lorien_calc_export_$timestamp.csv');
      await file.writeAsBytes(resp.data ?? const <int>[]);

      setState(() => _status = '✅ CSV exported: ${file.path}');
    } on ApiFailure catch (e) {
      if (e.statusCode == 404) {
        setState(() => _status = '❌ CSV export endpoint not found on server. Check API version or use XLSX export.');
        setState(()=>_csvSupported=false);
      } else {
        setState(() => _status = '❌ Export failed: ${e.message}');
      }
    } catch (e) {
      setState(() => _status = '❌ Export failed: $e');
    }
  }

  Future<void> _exportXlsx() async {
    setState(() => _status = 'Preparing XLSX export...');
    try {
      final resp = await ApiClient.I().download('export/xlsx');
      setState(() => _status = 'Downloading XLSX file...');

      final dir = await getDownloadsDirectory() ?? await getApplicationDocumentsDirectory();
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final file = File('${dir.path}/lorien_tree_export_$timestamp.xlsx');
      await file.writeAsBytes(resp.data ?? const <int>[]);

      setState(() => _status = '✅ XLSX exported: ${file.path}');
    } catch (e) {
      final errorMsg = e.toString();
      if (errorMsg.contains('404')) {
        setState(() => _status = '❌ No data available for export');
      } else if (errorMsg.contains('500')) {
        setState(() => _status = '❌ Server error during export');
      } else {
        setState(() => _status = '❌ Export failed: $errorMsg');
      }
    }
  }



  @override
  Widget build(BuildContext context) {
    return ScrollScaffold(
      title: 'Workspace',
      leading: const AppBackLeading(),
      children: [
        _ImportPanel(
          busy: _busy,
          apiAvailable: _apiAvailable,
          onPickExcelCsv: _onPickExcelCsv,
          onPickCsv: _onPickCsv,
          status: _status,
          onRetry: () {
            ref.refresh(healthControllerProvider);
            setState(() {
              _apiAvailable = true;
              _status = null;
            });
          },
        ),
        const SizedBox(height: 24),
        _EditTreePanel(),
        const SizedBox(height: 24),
        _ExportPanel(onExportCsv: _exportCsv, onExportXlsx: _exportXlsx, csvSupported: _csvSupported),
      ],
    );
  }

}

class _ImportPanel extends StatelessWidget {
  const _ImportPanel({
    required this.busy,
    required this.apiAvailable,
    required this.onPickExcelCsv,
    required this.onPickCsv,
    required this.status,
    required this.onRetry,
  });
  final bool busy;
  final bool apiAvailable;
  final VoidCallback onPickExcelCsv;
  final VoidCallback onPickCsv;
  final String? status;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('Import Data', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
          const SizedBox(height: 12),
          Row(children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: (busy || !apiAvailable) ? null : onPickExcelCsv,
                icon: busy ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.upload),
                label: Text(busy ? 'Importing...' : 'Select Excel/CSV')
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: OutlinedButton.icon(
                onPressed: (busy || !apiAvailable) ? null : onPickCsv,
                icon: busy ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.upload),
                label: Text(busy ? 'Importing...' : 'Select CSV')
              ),
            ),
          ]),
          if (!apiAvailable) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.red[50],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.red[200]!),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.wifi_off, color: Colors.red),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'API Offline',
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            color: Colors.red,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Cannot import files while the API is offline. Start the server and try again.',
                          style: TextStyle(color: Colors.red[700]),
                        ),
                      ],
                    ),
                  ),
                  TextButton.icon(
                    onPressed: onRetry,
                    icon: const Icon(Icons.refresh),
                    label: const Text('Retry'),
                    style: TextButton.styleFrom(foregroundColor: Colors.red),
                  ),
                ],
              ),
            ),
          ] else if (status != null) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: status!.startsWith('✅')
                  ? Colors.green[50]
                  : status!.startsWith('❌') || status!.startsWith('⚠️')
                    ? Colors.red[50]
                    : Colors.blue[50],
                borderRadius: BorderRadius.circular(4),
                border: Border.all(
                  color: status!.startsWith('✅')
                    ? Colors.green[200]!
                    : status!.startsWith('❌') || status!.startsWith('⚠️')
                      ? Colors.red[200]!
                      : Colors.blue[200]!,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    status!.startsWith('✅')
                      ? Icons.check_circle
                      : status!.startsWith('❌') || status!.startsWith('⚠️')
                        ? Icons.error
                        : Icons.info,
                    size: 16,
                    color: status!.startsWith('✅')
                      ? Colors.green[700]
                      : status!.startsWith('❌') || status!.startsWith('⚠️')
                        ? Colors.red[700]
                        : Colors.blue[700],
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      status!,
                      style: TextStyle(
                        color: status!.startsWith('✅')
                          ? Colors.green[700]
                          : status!.startsWith('❌') || status!.startsWith('⚠️')
                            ? Colors.red[700]
                            : Colors.blue[700],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ]),
      ),
    );
  }
}

class _ExportPanel extends StatelessWidget {
  const _ExportPanel({super.key, required this.onExportCsv, required this.onExportXlsx, required this.csvSupported});
  final VoidCallback onExportCsv;
  final VoidCallback onExportXlsx;
  final bool csvSupported;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('Export Data', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
          const SizedBox(height: 12),
          Row(children: [
            Expanded(child: Tooltip(
              message: csvSupported ? 'Export to CSV' : 'CSV not supported by server',
              child: ElevatedButton.icon(
                onPressed: (csvSupported) ? onExportCsv : null,
                icon: const Icon(Icons.download),
                label: const Text('Export CSV'),
              ),
            )),
            const SizedBox(width: 16),
            Expanded(child: ElevatedButton.icon(onPressed: onExportXlsx, icon: const Icon(Icons.download), label: const Text('Export XLSX'))),
          ]),
        ]),
      ),
    );
  }
}

class _EditTreePanel extends StatelessWidget {
  const _EditTreePanel();

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Edit Tree',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            const Text(
              'Browse and edit incomplete parent nodes in the decision tree.',
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 12),
            ElevatedButton.icon(
              onPressed: () => context.go('/edit-tree'),
              icon: const Icon(Icons.edit),
              label: const Text('Open Edit Tree'),
            ),
          ],
        ),
      ),
    );
  }
}
