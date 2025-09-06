import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_selector/file_selector.dart';
import '../../../widgets/layout/scroll_scaffold.dart';
import '../../../widgets/app_back_leading.dart';
import '../data/session_service.dart';
import '../data/session_models.dart';

class SessionSourceScreen extends ConsumerStatefulWidget {
  const SessionSourceScreen({super.key});

  @override
  ConsumerState<SessionSourceScreen> createState() => _SessionSourceScreenState();
}

class _SessionSourceScreenState extends ConsumerState<SessionSourceScreen>
    with TickerProviderStateMixin {
  late TabController _tabController;

  // Session state
  SessionExport? _currentSession;
  bool _isExporting = false;
  bool _isImporting = false;

  // Source state
  String? _selectedFilePath;
  CsvPreview? _csvPreview;
  bool _isPreviewing = false;
  Map<String, String> _headerMapping = {};
  bool _hasHeaders = true;

  // Push log state
  PushLogSummary? _pushLog;
  bool _isLoadingLog = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadPushLog();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _exportSession() async {
    setState(() => _isExporting = true);

    try {
      final service = ref.read(sessionServiceProvider);
      final sessionData = await service.exportSession();
      final jsonString = await service.exportToJsonFile(sessionData);

      // Save to file
      final fileName = 'lorien_session_${DateTime.now().toIso8601String().split('T')[0]}.json';
      final filePath = await _saveJsonToFile(jsonString, fileName);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Session exported to: $filePath')),
        );
        setState(() => _currentSession = sessionData);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Export failed: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isExporting = false);
      }
    }
  }

  Future<void> _importSession() async {
    try {
      final jsonString = await _loadJsonFromFile();
      if (jsonString == null) return;

      final service = ref.read(sessionServiceProvider);
      final sessionData = await service.importFromJsonFile(jsonString);

      // Validate import
      final validationErrors = await service.validateSessionImport(sessionData);
      if (validationErrors.isNotEmpty) {
        if (mounted) {
          _showValidationDialog(validationErrors, sessionData);
        }
        return;
      }

      // Proceed with import
      setState(() => _isImporting = true);
      final result = await service.importSession(sessionData);

      if (mounted) {
        setState(() => _isImporting = false);
        _showImportResult(result);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Import failed: $e')),
        );
      }
    }
  }

  void _showValidationDialog(List<String> errors, SessionExport data) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Import Validation'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('The following issues were found:'),
              const SizedBox(height: 8),
              ...errors.map((error) => Text('• $error')),
              const SizedBox(height: 16),
              const Text('Do you want to proceed anyway?'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.of(context).pop();
              setState(() => _isImporting = true);
              final service = ref.read(sessionServiceProvider);
              final result = await service.importSession(data);
              if (mounted) {
                setState(() => _isImporting = false);
                _showImportResult(result);
              }
            },
            child: const Text('Proceed'),
          ),
        ],
      ),
    );
  }

  void _showImportResult(SessionImportResult result) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(result.success ? 'Import Successful' : 'Import Failed'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (result.importedSheets.isNotEmpty) ...[
                const Text('Imported sheets:', style: TextStyle(fontWeight: FontWeight.bold)),
                ...result.importedSheets.map((sheet) => Text('• $sheet')),
                const SizedBox(height: 8),
              ],
              if (result.errors.isNotEmpty) ...[
                const Text('Errors:', style: TextStyle(fontWeight: FontWeight.bold)),
                ...result.errors.map((error) => Text('• $error')),
                const SizedBox(height: 8),
              ],
              if (result.warnings.isNotEmpty) ...[
                const Text('Warnings:', style: TextStyle(fontWeight: FontWeight.bold)),
                ...result.warnings.map((warning) => Text('• $warning')),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  Future<String?> _saveJsonToFile(String jsonString, String fileName) async {
    // In a real implementation, this would use file_selector to save the file
    // For now, return a placeholder path
    return '/downloads/$fileName';
  }

  Future<String?> _loadJsonFromFile() async {
    // In a real implementation, this would use file_selector to load the file
    // For now, return null to indicate no file selected
    return null;
  }

  Future<void> _pickCsvFile() async {
    try {
      final typeGroup = XTypeGroup(
        label: 'CSV Files',
        extensions: ['csv'],
      );
      final XFile? file = await openFile(acceptedTypeGroups: [typeGroup]);

      if (file != null && mounted) {
        setState(() => _selectedFilePath = file.path);
        await _previewCsv();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('File selection failed: $e')),
        );
      }
    }
  }

  Future<void> _previewCsv() async {
    if (_selectedFilePath == null) return;

    setState(() => _isPreviewing = true);

    try {
      final service = ref.read(sessionServiceProvider);
      final preview = await service.previewCsv(_selectedFilePath!, hasHeaders: _hasHeaders);

      // Auto-suggest header mapping
      final suggestions = await service.suggestHeaderMapping(preview.headers);
      setState(() {
        _csvPreview = preview;
        _headerMapping = suggestions;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Preview failed: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isPreviewing = false);
      }
    }
  }

  Future<void> _importCsv() async {
    if (_selectedFilePath == null || _csvPreview == null) return;

    try {
      final service = ref.read(sessionServiceProvider);
      final result = await service.importCsv(
        _selectedFilePath!,
        _headerMapping,
        hasHeaders: _hasHeaders,
      );

      if (mounted) {
        _showCsvImportResult(result);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Import failed: $e')),
        );
      }
    }
  }

  void _showCsvImportResult(CsvImportResult result) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(result.success ? 'Import Successful' : 'Import Failed'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Rows processed: ${result.rowsProcessed}'),
              Text('Rows imported: ${result.rowsImported}'),
              if (result.errors.isNotEmpty) ...[
                const SizedBox(height: 8),
                const Text('Errors:', style: TextStyle(fontWeight: FontWeight.bold)),
                ...result.errors.map((error) => Text('• $error')),
              ],
              if (result.warnings.isNotEmpty) ...[
                const SizedBox(height: 8),
                const Text('Warnings:', style: TextStyle(fontWeight: FontWeight.bold)),
                ...result.warnings.map((warning) => Text('• $warning')),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  Future<void> _loadPushLog() async {
    setState(() => _isLoadingLog = true);

    try {
      final service = ref.read(sessionServiceProvider);
      final log = await service.getPushLog();
      if (mounted) {
        setState(() => _pushLog = log);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load push log: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoadingLog = false);
      }
    }
  }

  Widget _buildSessionTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Session Management',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Export Current Session',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Export your current workbook, sheets, and UI state to a JSON file for backup or sharing.',
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    onPressed: _isExporting ? null : _exportSession,
                    icon: _isExporting
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.download),
                    label: Text(_isExporting ? 'Exporting...' : 'Export Session'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Import Session',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Import a previously exported session from a JSON file.',
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    onPressed: _isImporting ? null : _importSession,
                    icon: _isImporting
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.upload),
                    label: Text(_isImporting ? 'Importing...' : 'Import Session'),
                  ),
                ],
              ),
            ),
          ),
          if (_currentSession != null) ...[
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Last Exported Session',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    Text('Exported: ${_currentSession!.exportedAt.toString().split('.')[0]}'),
                    Text('Version: ${_currentSession!.version}'),
                    Text('Sheets: ${_currentSession!.workbook.sheets.length}'),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSourceTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Source Data Import',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'CSV File Import',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          _selectedFilePath ?? 'No file selected',
                          style: TextStyle(
                            color: _selectedFilePath != null ? Colors.black : Colors.grey,
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      ElevatedButton.icon(
                        onPressed: _pickCsvFile,
                        icon: const Icon(Icons.file_upload),
                        label: const Text('Select CSV'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  SwitchListTile(
                    title: const Text('First row contains headers'),
                    value: _hasHeaders,
                    onChanged: (value) {
                      setState(() => _hasHeaders = value);
                      if (_selectedFilePath != null) {
                        _previewCsv();
                      }
                    },
                  ),
                  if (_selectedFilePath != null) ...[
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: _isPreviewing ? null : _previewCsv,
                      icon: _isPreviewing
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.preview),
                      label: Text(_isPreviewing ? 'Loading...' : 'Preview'),
                    ),
                  ],
                ],
              ),
            ),
          ),
          if (_csvPreview != null) ...[
            const SizedBox(height: 16),
            _buildCsvPreview(),
          ],
        ],
      ),
    );
  }

  Widget _buildCsvPreview() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'CSV Preview',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            // Header mapping
            const Text('Header Mapping:', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            ..._csvPreview!.normalizedHeaders.entries.map((entry) {
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  children: [
                    Expanded(
                      flex: 2,
                      child: Text('${entry.key}:'),
                    ),
                    Expanded(
                      flex: 3,
                      child: DropdownButton<String>(
                        value: _headerMapping[entry.key],
                        isExpanded: true,
                        items: _csvPreview!.headers.map((header) {
                          return DropdownMenuItem(
                            value: header,
                            child: Text(header),
                          );
                        }).toList(),
                        onChanged: (value) {
                          if (value != null) {
                            setState(() => _headerMapping[entry.key] = value);
                          }
                        },
                      ),
                    ),
                  ],
                ),
              );
            }),
            const SizedBox(height: 16),
            // Data preview
            const Text('Data Preview:', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Container(
              height: 200,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey[300]!),
                borderRadius: BorderRadius.circular(8),
              ),
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: DataTable(
                  columns: _csvPreview!.normalizedHeaders.values.map((header) {
                    return DataColumn(label: Text(header));
                  }).toList(),
                  rows: _csvPreview!.rows.take(5).map((row) {
                    return DataRow(
                      cells: _csvPreview!.normalizedHeaders.values.map((header) {
                        return DataCell(Text(row[header] ?? ''));
                      }).toList(),
                    );
                  }).toList(),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Text('${_csvPreview!.totalRows ?? _csvPreview!.rows.length} total rows'),
                const Spacer(),
                ElevatedButton.icon(
                  onPressed: _importCsv,
                  icon: const Icon(Icons.import_export),
                  label: const Text('Import CSV'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPushLogTab() {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              const Text(
                'Push Log',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const Spacer(),
              IconButton(
                onPressed: _loadPushLog,
                icon: const Icon(Icons.refresh),
                tooltip: 'Refresh',
              ),
              IconButton(
                onPressed: () async {
                  final confirmed = await showDialog<bool>(
                    context: context,
                    builder: (context) => AlertDialog(
                      title: const Text('Clear Push Log'),
                      content: const Text('This will clear all push log entries. Continue?'),
                      actions: [
                        TextButton(
                          onPressed: () => Navigator.of(context).pop(false),
                          child: const Text('Cancel'),
                        ),
                        TextButton(
                          onPressed: () => Navigator.of(context).pop(true),
                          child: const Text('Clear'),
                        ),
                      ],
                    ),
                  );

                  if (confirmed == true) {
                    final service = ref.read(sessionServiceProvider);
                    await service.clearPushLog();
                    _loadPushLog();
                  }
                },
                icon: const Icon(Icons.clear_all),
                tooltip: 'Clear Log',
              ),
            ],
          ),
        ),
        Expanded(
          child: _isLoadingLog
              ? const Center(child: CircularProgressIndicator())
              : _pushLog == null || _pushLog!.entries.isEmpty
                  ? const Center(child: Text('No push log entries'))
                  : ListView.builder(
                      itemCount: _pushLog!.entries.length,
                      itemBuilder: (context, index) {
                        final entry = _pushLog!.entries[index];
                        return Card(
                          child: ListTile(
                            leading: Icon(
                              entry.success == true
                                  ? Icons.check_circle
                                  : entry.success == false
                                      ? Icons.error
                                      : Icons.info,
                              color: entry.success == true
                                  ? Colors.green
                                  : entry.success == false
                                      ? Colors.red
                                      : Colors.blue,
                            ),
                            title: Text(entry.operation),
                            subtitle: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(entry.description),
                                Text(
                                  entry.timestamp.toString().split('.')[0],
                                  style: const TextStyle(fontSize: 12),
                                ),
                              ],
                            ),
                            trailing: entry.user != null ? Text(entry.user!) : null,
                          ),
                        );
                      },
                    ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return ScrollScaffold(
      title: 'Session & Source',
      leading: const AppBackLeading(),
      children: [
        Card(
          child: Column(
            children: [
              TabBar(
                controller: _tabController,
                tabs: const [
                  Tab(text: 'Session', icon: Icon(Icons.save)),
                  Tab(text: 'Source', icon: Icon(Icons.upload_file)),
                  Tab(text: 'Push Log', icon: Icon(Icons.history)),
                ],
              ),
              SizedBox(
                height: 600,
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildSessionTab(),
                    _buildSourceTab(),
                    _buildPushLogTab(),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
