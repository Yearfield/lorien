import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/services/health_service.dart';
import '../../../core/http/api_client.dart';
import '../../../shared/widgets/app_scaffold.dart';
import '../../../shared/widgets/route_guard.dart';

class WorkspaceScreen extends ConsumerStatefulWidget {
  const WorkspaceScreen({super.key});

  @override
  ConsumerState<WorkspaceScreen> createState() => _WorkspaceScreenState();
}

class _WorkspaceScreenState extends ConsumerState<WorkspaceScreen> {
  String _importStatus = 'idle'; // idle, queued, processing, done
  List<HeaderMismatch> _headerMismatches = [];
  
  bool get _importInProgress => _importStatus == 'queued' || _importStatus == 'processing';
  bool get _exportInProgress => false; // TODO: implement export progress tracking

  @override
  Widget build(BuildContext context) {
    return RouteGuard(
      isBusy: () => _importInProgress || _exportInProgress,
      confirmMessage: 'Import/Export is running. Leave and cancel?',
      child: AppScaffold(
        title: 'Workspace',
        body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Import Data',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed:
                              _importStatus == 'idle' ? _pickExcelFile : null,
                          icon: const Icon(Icons.file_upload),
                          label: const Text('Select Excel/CSV'),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed:
                              _importStatus == 'idle' ? _pickCSVFile : null,
                          icon: const Icon(Icons.file_upload),
                          label: const Text('Select CSV'),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  _buildImportProgress(),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          if (_headerMismatches.isNotEmpty) ...[
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Header Mismatches',
                      style:
                          TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 16),
                    _buildHeaderMismatchTable(),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Export Data',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: FilledButton.icon(
                          onPressed: _exportCSV,
                          icon: const Icon(Icons.file_download),
                          label: const Text('Export CSV'),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: FilledButton.icon(
                          onPressed: _exportXLSX,
                          icon: const Icon(Icons.file_download),
                          label: const Text('Export XLSX'),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
        ),
  }

  Widget _buildImportProgress() {
    if (_importStatus == 'idle') {
      return const Text('No import in progress');
    }

    String statusText;
    IconData statusIcon;

    switch (_importStatus) {
      case 'queued':
        statusText = 'Queued for processing...';
        statusIcon = Icons.schedule;
        break;
      case 'processing':
        statusText = 'Processing import...';
        statusIcon = Icons.hourglass_empty;
        break;
      case 'done':
        statusText = 'Import completed';
        statusIcon = Icons.check_circle;
        break;
      default:
        statusText = 'Unknown status';
        statusIcon = Icons.help;
    }

    return Row(
      children: [
        Icon(statusIcon),
        const SizedBox(width: 8),
        Text(statusText),
      ],
    );
  }

  Widget _buildHeaderMismatchTable() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        columns: const [
          DataColumn(label: Text('Position')),
          DataColumn(label: Text('Expected')),
          DataColumn(label: Text('Got')),
        ],
        rows: _headerMismatches
            .map((mismatch) => DataRow(
                  cells: [
                    DataCell(Text('${mismatch.position}')),
                    DataCell(Text(mismatch.expected)),
                    DataCell(Text(mismatch.got)),
                  ],
                ))
            .toList(),
      ),
    );
  }

  Future<void> _pickExcelFile() async {
    // TODO: Implement file picker
    setState(() => _importStatus = 'queued');
    await _simulateImport();
  }

  Future<void> _pickCSVFile() async {
    // TODO: Implement file picker
    setState(() => _importStatus = 'queued');
    await _simulateImport();
  }

  Future<void> _simulateImport() async {
    await Future.delayed(const Duration(seconds: 1));
    setState(() => _importStatus = 'processing');

    await Future.delayed(const Duration(seconds: 2));

    setState(() {
      _importStatus = 'done';
      _headerMismatches = [
        HeaderMismatch(1, 'Vital Measurement', 'VitalMeasurement'),
        HeaderMismatch(3, 'Node 3', 'Node3'),
      ];
    });
  }

  Future<void> _exportCSV() async {
    try {
      final dio = ref.read(dioProvider);
      await dio.get('/export/csv');
      // TODO: Handle file download
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('CSV exported successfully')));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('Export failed: $e')));
      }
    }
  }

  Future<void> _exportXLSX() async {
    try {
      final dio = ref.read(dioProvider);
      await dio.get('/export/xlsx');
      // TODO: Handle file download
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('XLSX exported successfully')));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('Export failed: $e')));
      }
    }
  }
}

class HeaderMismatch {
  final int position;
  final String expected;
  final String got;

  HeaderMismatch(this.position, this.expected, this.got);
}
