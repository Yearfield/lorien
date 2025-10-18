import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import 'package:lorien/features/pathogens/models/pathogen_models.dart';
import 'package:lorien/features/pathogens/providers/pathogen_providers.dart';
import 'package:lorien/features/pathogens/services/pathogen_service.dart';

class PathogenImportDialog extends ConsumerStatefulWidget {
  const PathogenImportDialog({super.key});

  @override
  ConsumerState<PathogenImportDialog> createState() => _PathogenImportDialogState();
}

class _PathogenImportDialogState extends ConsumerState<PathogenImportDialog> {
  File? _selectedFile;
  bool _isImporting = false;
  PathogenImportResult? _importResult;

  Future<void> _pickFile() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['csv', 'xlsx'],
        allowMultiple: false,
      );

      if (result != null && result.files.single.path != null) {
        setState(() {
          _selectedFile = File(result.files.single.path!);
          _importResult = null;
        });
      }
    } catch (e) {
      _showErrorSnackBar('Failed to pick file: $e');
    }
  }

  Future<void> _importFile() async {
    if (_selectedFile == null) return;

    setState(() {
      _isImporting = true;
    });

    try {
      final service = PathogenService();
      final result = await service.importPathogens(_selectedFile!);

      setState(() {
        _importResult = result;
        _isImporting = false;
      });

      // Refresh the pathogen list
      ref.read(pathogenListProvider.notifier).loadPathogens();
      ref.read(pathogenStatsProvider.notifier).loadStats();

      _showSuccessSnackBar('Import completed successfully!');
    } catch (e) {
      setState(() {
        _isImporting = false;
      });
      _showErrorSnackBar('Import failed: $e');
    }
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }

  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Row(
        children: [
          Icon(Icons.upload_file, color: Colors.blue),
          SizedBox(width: 8),
          Text('Import Pathogen Data'),
        ],
      ),
      content: SizedBox(
        width: 500,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Select a CSV or XLSX file containing pathogen data:',
              style: TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 16),

            // File picker
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                children: [
                  Icon(
                    _selectedFile != null ? Icons.check_circle : Icons.cloud_upload,
                    size: 48,
                    color: _selectedFile != null ? Colors.green : Colors.grey,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _selectedFile?.path.split('/').last ?? 'No file selected',
                    style: TextStyle(
                      fontSize: 16,
                      color: _selectedFile != null ? Colors.green : Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 8),
                  ElevatedButton.icon(
                    onPressed: _pickFile,
                    icon: const Icon(Icons.folder_open),
                    label: const Text('Choose File'),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Import result
            if (_importResult != null) ...[
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  border: Border.all(color: Colors.green.shade200),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Import Results:',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text('Pathogens processed: ${_importResult!.pathogensProcessed}'),
                    Text('Pathogens created: ${_importResult!.pathogensCreated}'),
                    Text('Pathogens updated: ${_importResult!.pathogensUpdated}'),
                    Text('Associations processed: ${_importResult!.associationsProcessed}'),
                    Text('Associations created: ${_importResult!.associationsCreated}'),
                    if (_importResult!.errors.isNotEmpty) ...[
                      const SizedBox(height: 8),
                      const Text(
                        'Errors:',
                        style: TextStyle(fontWeight: FontWeight.bold, color: Colors.red),
                      ),
                      ..._importResult!.errors.map((error) => Text('• $error', style: const TextStyle(color: Colors.red))),
                    ],
                    if (_importResult!.warnings.isNotEmpty) ...[
                      const SizedBox(height: 8),
                      const Text(
                        'Warnings:',
                        style: TextStyle(fontWeight: FontWeight.bold, color: Colors.orange),
                      ),
                      ..._importResult!.warnings.map((warning) => Text('• $warning', style: const TextStyle(color: Colors.orange))),
                    ],
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],

            // Supported formats info
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                border: Border.all(color: Colors.blue.shade200),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Supported Formats:',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 4),
                  Text('• CSV files (.csv)'),
                  Text('• Excel files (.xlsx)'),
                  SizedBox(height: 8),
                  Text(
                    'Expected format: Properties in columns A-AJ, binary associations (0/1) in columns AK+',
                    style: TextStyle(fontSize: 12, fontStyle: FontStyle.italic),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: _isImporting ? null : () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _selectedFile != null && !_isImporting ? _importFile : null,
          child: _isImporting
              ? const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                    SizedBox(width: 8),
                    Text('Importing...'),
                  ],
                )
              : const Text('Import'),
        ),
      ],
    );
  }
}
