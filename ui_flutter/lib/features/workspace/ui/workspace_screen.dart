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
import '../data/workspace_models.dart';
import '../export_panel.dart';
import '../stats_details_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';

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
  String? _lastUploadedFileName;

  // Enhanced status tracking
  ImportJob? _currentImportJob;
  final List<ImportJob> _importHistory = [];
  BackupRestoreStatus? _backupStatus;

  @override
  void initState() {
    super.initState();
    // Don't make network calls during widget tests
    if (!const bool.fromEnvironment('FLUTTER_TEST')) {
      _detectCsvSupported();
    }
    // Load persisted last uploaded file name
    _loadLastUploaded();
  }

  Future<void> _loadLastUploaded() async {
    try {
      final sp = await SharedPreferences.getInstance();
      if (mounted) {
        setState(() {
          _lastUploadedFileName = sp.getString('workspace_last_uploaded_file');
        });
      }
    } catch (_) {}
  }

  Future<void> _importFile(String path, {required bool isExcel}) async {
    // Gate behind health check
    final health = await ref
        .read(healthControllerProvider.future)
        .timeout(const Duration(seconds: 2), onTimeout: () => null);
    _apiAvailable = health?.ok == true;
    if (!_apiAvailable) {
      setState(() {
        _status =
            '❌ API is offline at ${ApiClient.I().baseUrl}. Start the server or update Settings → API Base URL.';
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
            setState(() => _status = 'Uploading $fileName... $percent%');
          }
        },
      );

      final summary = data['summary'] ?? 'Successfully imported';
      setState(() => _status = '✅ Import complete: $summary');

      // Persist and reflect last uploaded file name
      try {
        final sp = await SharedPreferences.getInstance();
        final fileName = path.split('/').last;
        await sp.setString('workspace_last_uploaded_file', fileName);
        if (mounted) {
          setState(() {
            _lastUploadedFileName = fileName;
          });
        }
      } catch (_) {}
    } on ApiUnavailable {
      setState(() {
        _status =
            '❌ Connection failed: Could not reach ${ApiClient.I().baseUrl}. Is the server running?';
        _apiAvailable = false;
      });
    } on ApiFailure catch (e) {
      if (e.statusCode == 422) {
        // Enhanced 422 error handling with header context
        final enhancedMessage = _enhance422ErrorMessage(e.message, null);
        setState(() => _status = '⚠️ Validation error (422): $enhancedMessage');
      } else if (e.statusCode == 400) {
        setState(() => _status = '❌ Invalid file format or data structure');
      } else if (e.statusCode == 500) {
        setState(() => _status = '❌ Server error: Please try again later');
      } else {
        setState(() => _status =
            '❌ Import failed (${e.statusCode ?? 'error'}): ${e.message}');
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
      const typeGroup = XTypeGroup(
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
      const typeGroup = XTypeGroup(
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
  Future<Map<String, dynamic>> _buildCalcPayloadOrPrompt(
      BuildContext context) async {
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
      if (health != null && health.features.csvExport != false) {
        // true or absent -> optimistic
        _csvSupported = health.features.csvExport == true;
        _checkedFromFeatures = true;
      }
    } catch (_) {/* ignore; fall through */}
    if (!_checkedFromFeatures) {
      // Fallback probe if features key absent
      try {
        await ApiClient.I().head('export/csv');
        _csvSupported = true;
      } catch (_) {
        _csvSupported = false;
      }
    }
    if (mounted) setState(() {});
  }

  String _enhance422ErrorMessage(String originalMessage, dynamic errorData) {
    if (errorData == null) return originalMessage;

    try {
      // Parse header validation errors
      if (errorData is Map<String, dynamic> &&
          errorData.containsKey('header_errors')) {
        final headerErrors = errorData['header_errors'] as List<dynamic>;
        if (headerErrors.isNotEmpty) {
          final error = headerErrors.first as Map<String, dynamic>;
          final row = error['row'] ?? '?';
          final col = error['col_index'] ?? '?';
          final expected = error['expected'] ?? [];
          final received = error['received'] ?? '';

          return 'Header mismatch at row $row, column $col. '
              'Expected: ${expected.join(', ')}, Received: $received. '
              '$originalMessage';
        }
      }
    } catch (e) {
      // If parsing fails, return original message
    }

    return originalMessage;
  }

  Future<void> _performIntegrityCheck() async {
    setState(() => _busy = true);
    setState(() => _status = '🔍 Performing integrity check...');

    try {
      // Call integrity check endpoint
      final response = await ApiClient.I().get('/workspace/integrity-check');

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        final passed = data['passed'] as bool;
        final issues = data['issues'] as List<dynamic>? ?? [];

        if (passed) {
          setState(() => _status = '✅ Integrity check passed');
        } else {
          setState(() =>
              _status = '⚠️ Integrity issues found: ${issues.length} issues');
          // Show detailed issues dialog
          _showIntegrityIssuesDialog(issues);
        }
      }
    } catch (e) {
      setState(() => _status = '❌ Integrity check failed: $e');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  void _showIntegrityIssuesDialog(List<dynamic> issues) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Integrity Issues Found'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('The following integrity issues were detected:'),
              const SizedBox(height: 8),
              ...issues.map((issue) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 2),
                    child: Text('• ${issue.toString()}'),
                  )),
              const SizedBox(height: 16),
              const Text(
                'Consider creating a backup before proceeding with any repairs.',
                style: TextStyle(fontStyle: FontStyle.italic),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              _createBackup();
            },
            child: const Text('Create Backup'),
          ),
        ],
      ),
    );
  }

  Future<void> _createBackup() async {
    setState(() => _busy = true);
    setState(() => _status = '💾 Creating backup...');

    try {
      final response = await ApiClient.I().post('/workspace/backup');

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        final backupPath = data['backup_path'] as String;
        setState(() => _status = '✅ Backup created: $backupPath');
      }
    } catch (e) {
      setState(() => _status = '❌ Backup failed: $e');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _viewStats() async {
    try {
      final res = await ApiClient.I().getJson('tree/stats');
      final progress = await ApiClient.I().getJson('tree/progress');
      if (!mounted) return;
      showDialog(
        context: context,
        builder: (context) {
          return AlertDialog(
            title: const Text('Database Statistics'),
            content: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Wrap(spacing: 8, runSpacing: 8, children: [
                    _buildClickableChip(
                        'Nodes: ${res['nodes']}', () => _openDetails('nodes')),
                    _buildClickableChip(
                        'Roots: ${res['roots']}', () => _openDetails('roots')),
                    _buildClickableChip('Leaves: ${res['leaves']}',
                        () => _openDetails('leaves')),
                    _buildClickableChip(
                        'Complete paths: ${res['complete_paths']}',
                        () => _openDetails('complete_paths')),
                    _buildClickableChip(
                        'Complete parents: ${progress['complete_parents'] ?? 0}',
                        () => _openDetails('complete5')),
                    _buildClickableChip(
                        'Incomplete parents (<4): ${progress['incomplete_lt4'] ?? 0}',
                        () => _openDetails('incomplete_lt4')),
                    _buildClickableChip(
                        'Saturated: ${progress['saturated_parents'] ?? 0}',
                        () => _openDetails('saturated')),
                  ]),
                  const SizedBox(height: 16),
                  _buildProgressBars(progress),
                ],
              ),
            ),
            actions: [
              TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('Close')),
            ],
          );
        },
      );
    } catch (e) {
      if (!mounted) return;
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Database Statistics'),
          content: Text('Failed to load stats: $e'),
          actions: [
            TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Close'))
          ],
        ),
      );
    }
  }

  Widget _buildClickableChip(String label, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      child: Chip(
        label: Text(label),
        backgroundColor: Theme.of(context).colorScheme.primaryContainer,
      ),
    );
  }

  Widget _buildProgressBars(Map<String, dynamic> progress) {
    final totalParents = (progress['parents_total'] ?? 0) as int;
    int v(String k) => (progress[k] ?? 0) as int;

    List<Widget> bars = [
      _buildProgressBar(
          'Complete parents (same)', v('complete_parents_same'), totalParents,
          color: Colors.green),
      _buildProgressBar('Complete parents (different)',
          v('complete_parents_diff'), totalParents,
          color: Colors.teal),
      _buildProgressBar(
          'Incomplete parents (<4)', v('incomplete_lt4'), totalParents,
          color: Colors.orange),
      _buildProgressBar(
          'Saturated parents (>5)', v('saturated_parents'), totalParents,
          color: Colors.red),
      _buildProgressBar(
          'Complete branches', v('complete_branches'), v('leaves'),
          color: Colors.blue),
      _buildProgressBar(
          'Triage filled', v('triage_filled'), v('complete_branches'),
          color: Colors.indigo),
      _buildProgressBar(
          'Actions filled', v('actions_filled'), v('complete_branches'),
          color: Colors.purple),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Progress Analytics',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        ...bars,
      ],
    );
  }

  Widget _buildProgressBar(String label, int n, int d, {Color? color}) {
    final pct = d > 0 ? n / d : 0.0;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('$label: $n / $d'),
          LinearProgressIndicator(
            value: pct.clamp(0, 1),
            minHeight: 8,
            backgroundColor: Colors.grey[300],
            valueColor: AlwaysStoppedAnimation<Color>(color ?? Colors.blue),
          ),
        ],
      ),
    );
  }

  void _openDetails(String kind) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => StatsDetailsScreen(
          baseUrl: ApiClient.I().baseUrl,
          kind: kind,
        ),
      ),
    );
  }

  Future<void> _restoreFromBackup() async {
    try {
      const typeGroup = XTypeGroup(
        label: 'Backup Files',
        extensions: ['db', 'sqlite', 'bak'],
      );
      final XFile? file = await openFile(acceptedTypeGroups: [typeGroup]);

      if (file != null) {
        final confirmed = await showDialog<bool>(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Restore from Backup'),
            content: Text(
              'This will replace the current database with the backup file: ${file.name}. '
              'This action cannot be undone. Continue?',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(false),
                child: const Text('Cancel'),
              ),
              TextButton(
                onPressed: () => Navigator.of(context).pop(true),
                style: TextButton.styleFrom(
                  foregroundColor: Theme.of(context).colorScheme.error,
                ),
                child: const Text('Restore'),
              ),
            ],
          ),
        );

        if (confirmed == true) {
          setState(() => _busy = true);
          setState(() => _status = '🔄 Restoring from backup...');

          try {
            final fileBytes = await file.readAsBytes();

            final formData = FormData.fromMap({
              'backup_file': MultipartFile.fromBytes(
                fileBytes,
                filename: file.name,
              ),
            });

            final response = await ApiClient.I()
                .postMultipart('/workspace/restore', formData: formData);

            // postMultipart returns data, success indicated by no exception
            setState(() => _status = '✅ Database restored successfully');
          } catch (e) {
            setState(() => _status = '❌ Restore failed: $e');
          } finally {
            if (mounted) setState(() => _busy = false);
          }
        }
      }
    } catch (e) {
      setState(() => _status = '❌ File selection failed: $e');
    }
  }

  Future<void> _exportCsv() async {
    setState(() => _status = 'Preparing CSV export...');
    try {
      // Always prompt for CSV V1 payload; dialog enforces exactly 5.
      final result = await CalcExportDialog.open(context);
      if (result == null) return;
      final payload = {
        'diagnosis': result.diagnosis,
        'nodes': result.nodes
            .map((n) => {
                  'rank': n.rank,
                  'symptom_id': n.symptomId,
                  'symptom_label': n.symptomLabel,
                  'quality': n.quality,
                })
            .toList(),
      };
      final resp = await ApiClient.I().postBytes('export/csv',
          body: payload, headers: {'Accept': 'text/csv'});
      setState(() => _status = 'Downloading CSV file...');

      final dir = await getDownloadsDirectory() ??
          await getApplicationDocumentsDirectory();
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final file = File('${dir.path}/lorien_calc_export_$timestamp.csv');
      await file.writeAsBytes(resp.data ?? const <int>[]);

      setState(() => _status = '✅ CSV exported: ${file.path}');
    } on ApiFailure catch (e) {
      if (e.statusCode == 404) {
        setState(() => _status =
            '❌ CSV export endpoint not found on server. Check API version or use XLSX export.');
        setState(() => _csvSupported = false);
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

      final dir = await getDownloadsDirectory() ??
          await getApplicationDocumentsDirectory();
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
          lastUploadedFileName: _lastUploadedFileName,
        ),
        const SizedBox(height: 24),
        const _EditTreePanel(),
        const SizedBox(height: 24),
        const _VMBuilderPanel(),
        const SizedBox(height: 24),
        _MaintenancePanel(
          onIntegrityCheck: _performIntegrityCheck,
          onCreateBackup: _createBackup,
          onRestoreBackup: _restoreFromBackup,
          onViewStats: _viewStats,
        ),
        const SizedBox(height: 24),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Export Data',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 12),
                ExportPanel(baseUrl: ApiClient.I().baseUrl),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _ImportPanel extends StatefulWidget {
  const _ImportPanel({
    required this.busy,
    required this.apiAvailable,
    required this.onPickExcelCsv,
    required this.onPickCsv,
    required this.status,
    required this.onRetry,
    this.lastUploadedFileName,
  });
  final bool busy;
  final bool apiAvailable;
  final VoidCallback onPickExcelCsv;
  final VoidCallback onPickCsv;
  final String? status;
  final VoidCallback onRetry;
  final String? lastUploadedFileName;

  @override
  State<_ImportPanel> createState() => _ImportPanelState();
}

class _ImportPanelState extends State<_ImportPanel> {
  bool _replace = false;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('Import Data',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
          const SizedBox(height: 12),
          SwitchListTile(
            title: const Text('Replace existing data (atomic)'),
            subtitle:
                const Text('Clears current nodes & outcomes before importing'),
            value: _replace,
            onChanged: (v) => setState(() => _replace = v),
          ),
          const SizedBox(height: 12),
          Row(children: [
            Expanded(
              child: OutlinedButton.icon(
                  onPressed: (widget.busy || !widget.apiAvailable)
                      ? null
                      : widget.onPickExcelCsv,
                  icon: widget.busy
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.upload),
                  label:
                      Text(widget.busy ? 'Importing...' : 'Select Excel/CSV')),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: OutlinedButton.icon(
                  onPressed: (widget.busy || !widget.apiAvailable)
                      ? null
                      : widget.onPickCsv,
                  icon: widget.busy
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.upload),
                  label: Text(widget.busy ? 'Importing...' : 'Select CSV')),
            ),
          ]),
          if (widget.lastUploadedFileName != null) ...[
            const SizedBox(height: 12),
            Text('Last uploaded: ${widget.lastUploadedFileName}',
                style: const TextStyle(color: Colors.grey)),
          ],
          if (!widget.apiAvailable) ...[
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
                    onPressed: widget.onRetry,
                    icon: const Icon(Icons.refresh),
                    label: const Text('Retry'),
                    style: TextButton.styleFrom(foregroundColor: Colors.red),
                  ),
                ],
              ),
            ),
          ] else if (widget.status != null) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: widget.status!.startsWith('✅')
                    ? Colors.green[50]
                    : widget.status!.startsWith('❌') ||
                            widget.status!.startsWith('⚠️')
                        ? Colors.red[50]
                        : Colors.blue[50],
                borderRadius: BorderRadius.circular(4),
                border: Border.all(
                  color: widget.status!.startsWith('✅')
                      ? Colors.green[200]!
                      : widget.status!.startsWith('❌') ||
                              widget.status!.startsWith('⚠️')
                          ? Colors.red[200]!
                          : Colors.blue[200]!,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    widget.status!.startsWith('✅')
                        ? Icons.check_circle
                        : widget.status!.startsWith('❌') ||
                                widget.status!.startsWith('⚠️')
                            ? Icons.error
                            : Icons.info,
                    size: 16,
                    color: widget.status!.startsWith('✅')
                        ? Colors.green[700]
                        : widget.status!.startsWith('❌') ||
                                widget.status!.startsWith('⚠️')
                            ? Colors.red[700]
                            : Colors.blue[700],
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      widget.status!,
                      style: TextStyle(
                        color: widget.status!.startsWith('✅')
                            ? Colors.green[700]
                            : widget.status!.startsWith('❌') ||
                                    widget.status!.startsWith('⚠️')
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
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    key: const Key('btn_fix_incomplete'),
                    onPressed: () => context.go('/edit-tree'),
                    icon: const Icon(Icons.edit),
                    label: const Text('Fix Incomplete Parents'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    key: const Key('btn_conflicts'),
                    onPressed: () => context.go('/conflicts'),
                    icon: const Icon(Icons.warning),
                    label: const Text('Fix Same parent BUT different children'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _VMBuilderPanel extends StatelessWidget {
  const _VMBuilderPanel();

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'VM Builder (Vital Measurement Builder)',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            const Text(
              'Create a new Vital Measurement and build its decision tree using existing labels.',
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                ElevatedButton.icon(
                  key: const Key('btn_open_vm_builder'),
                  onPressed: () => context.go('/vm-builder'),
                  icon: const Icon(Icons.account_tree_outlined),
                  label: const Text('Open VM Builder'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _MaintenancePanel extends StatelessWidget {
  const _MaintenancePanel({
    required this.onIntegrityCheck,
    required this.onCreateBackup,
    required this.onRestoreBackup,
    required this.onViewStats,
  });

  final VoidCallback onIntegrityCheck;
  final VoidCallback onCreateBackup;
  final VoidCallback onRestoreBackup;
  final VoidCallback onViewStats;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Database Maintenance',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 12),
            const Text(
              'Perform integrity checks and manage database backups.',
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    key: const Key('btn_integrity_check'),
                    onPressed: onIntegrityCheck,
                    icon: const Icon(Icons.check_circle_outline),
                    label: const Text('Integrity Check'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton.icon(
                    key: const Key('btn_create_backup'),
                    onPressed: onCreateBackup,
                    icon: const Icon(Icons.backup),
                    label: const Text('Create Backup'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    key: const Key('btn_restore_backup'),
                    onPressed: onRestoreBackup,
                    icon: const Icon(Icons.restore),
                    label: const Text('Restore Backup'),
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: Colors.orange),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: OutlinedButton.icon(
                    key: const Key('btn_view_stats'),
                    onPressed: onViewStats,
                    icon: const Icon(Icons.analytics),
                    label: const Text('View Stats'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    key: const Key('btn_clear_workspace'),
                    onPressed: () async {
                      final confirmed = await showDialog<bool>(
                        context: context,
                        builder: (ctx) => AlertDialog(
                          title: const Text('Clear Workspace'),
                          content: const Text(
                              'This will remove all nodes and outcomes but keep the dictionary intact. Continue?'),
                          actions: [
                            TextButton(
                              onPressed: () => Navigator.of(ctx).pop(false),
                              child: const Text('Cancel'),
                            ),
                            ElevatedButton(
                              onPressed: () => Navigator.of(ctx).pop(true),
                              child: const Text('Clear'),
                            ),
                          ],
                        ),
                      );

                      if (confirmed == true) {
                        try {
                          final response =
                              await ApiClient.I().post('/admin/clear-nodes');
                          if (response.statusCode == 200) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                  content: Text(
                                      'Workspace cleared (nodes/outcomes only)')),
                            );
                          }
                        } catch (e) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Clear failed: $e')),
                          );
                        }
                      }
                    },
                    icon: const Icon(Icons.cleaning_services),
                    label: const Text('Clear workspace (keep dictionary)'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.orange,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
