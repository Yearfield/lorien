import 'dart:io';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/warhammer_models.dart';
import '../state/warhammer_notifier.dart';

class WarhammerImportScreen extends ConsumerStatefulWidget {
  const WarhammerImportScreen({super.key});

  @override
  ConsumerState<WarhammerImportScreen> createState() => _WarhammerImportScreenState();
}

class _WarhammerImportScreenState extends ConsumerState<WarhammerImportScreen> {
  File? _diseasesFile;
  File? _symptomsFile;
  File? _conditionalsFile;

  ImportResultResponse? _lastImportResult;
  String? _importError;

  @override
  Widget build(BuildContext context) {
    final isImporting = ref.watch(warhammerImportingProvider);
    final error = ref.watch(warhammerErrorProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Import Warhammer Data'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              const Text(
                'Import Data Files',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                'Upload CSV or Excel files containing disease, symptom, and conditional probability data.',
                style: TextStyle(color: Colors.grey),
              ),
              const SizedBox(height: 24),

              // Error display
              if (error != null) ...[
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red[50],
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.red[200]!),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.error_outline, color: Colors.red[700]),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          error,
                          style: TextStyle(color: Colors.red[700]),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // Import result display
              if (_lastImportResult != null) ...[
                _buildImportResult(_lastImportResult!),
                const SizedBox(height: 16),
              ],

              // Diseases file upload
              _buildFileUploadSection(
                title: 'Diseases Data (P(Disease).csv/.xlsx)',
                description: 'Upload CSV or Excel file containing disease names and estimated lifetime risks',
                file: _diseasesFile,
                onFileSelected: (file) {
                  setState(() {
                    _diseasesFile = file;
                    _lastImportResult = null;
                    _importError = null;
                  });
                },
                onImport: () => _importDiseases(),
                isImporting: isImporting,
              ),
              const SizedBox(height: 24),

              // Symptoms file upload
              _buildFileUploadSection(
                title: 'Symptoms Data (P(Symptom).csv/.xlsx)',
                description: 'Upload CSV or Excel file containing symptom names and base probabilities',
                file: _symptomsFile,
                onFileSelected: (file) {
                  setState(() {
                    _symptomsFile = file;
                    _lastImportResult = null;
                    _importError = null;
                  });
                },
                onImport: () => _importSymptoms(),
                isImporting: isImporting,
              ),
              const SizedBox(height: 24),

              // Conditionals file upload
              _buildFileUploadSection(
                title: 'Conditional Probabilities (P(Symptom|Disease).csv/.xlsx)',
                description: 'Upload CSV or Excel file containing conditional probabilities for symptoms given diseases',
                file: _conditionalsFile,
                onFileSelected: (file) {
                  setState(() {
                    _conditionalsFile = file;
                    _lastImportResult = null;
                    _importError = null;
                  });
                },
                onImport: () => _importConditionals(),
                isImporting: isImporting,
              ),
              const SizedBox(height: 32),

              // Import all button
              if (_diseasesFile != null && _symptomsFile != null && _conditionalsFile != null)
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: isImporting ? null : _importAll,
                    icon: const Icon(Icons.upload),
                    label: const Text('Import All Files'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFileUploadSection({
    required String title,
    required String description,
    required File? file,
    required Function(File) onFileSelected,
    required VoidCallback onImport,
    required bool isImporting,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(
              description,
              style: const TextStyle(color: Colors.grey, fontSize: 14),
            ),
            const SizedBox(height: 16),

            // File selection
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: isImporting ? null : () => _selectFile(onFileSelected),
                    icon: const Icon(Icons.folder_open),
                    label: Text(
                      file?.path.split('/').last ?? 'Select File',
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                ElevatedButton(
                  onPressed: file != null && !isImporting ? onImport : null,
                  child: isImporting
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Import'),
                ),
              ],
            ),

            // File info
            if (file != null) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.green[50],
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Row(
                  children: [
                    Icon(Icons.check_circle, color: Colors.green[700], size: 16),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Selected: ${file.path.split('/').last}',
                        style: TextStyle(color: Colors.green[700], fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildImportResult(ImportResultResponse result) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: result.success ? Colors.green[50] : Colors.orange[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: result.success ? Colors.green[200]! : Colors.orange[200]!,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                result.success ? Icons.check_circle : Icons.warning,
                color: result.success ? Colors.green[700] : Colors.orange[700],
              ),
              const SizedBox(width: 8),
              Text(
                result.success ? 'Import Successful' : 'Import Completed with Issues',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: result.success ? Colors.green[700] : Colors.orange[700],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Statistics
          if (result.diseasesProcessed > 0) ...[
            _buildStatRow('Diseases', result.diseasesProcessed, result.diseasesCreated),
          ],
          if (result.symptomsProcessed > 0) ...[
            _buildStatRow('Symptoms', result.symptomsProcessed, result.symptomsCreated),
          ],
          if (result.conditionalsProcessed > 0) ...[
            _buildStatRow('Conditionals', result.conditionalsProcessed, result.conditionalsCreated),
          ],

          // Errors
          if (result.errors.isNotEmpty) ...[
            const SizedBox(height: 12),
            const Text(
              'Errors:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            ...result.errors.map((error) => Text('• $error')),
          ],

          // Warnings
          if (result.warnings.isNotEmpty) ...[
            const SizedBox(height: 12),
            const Text(
              'Warnings:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            ...result.warnings.map((warning) => Text('• $warning')),
          ],
        ],
      ),
    );
  }

  Widget _buildStatRow(String label, int processed, int created) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text('$label:'),
          Text('$processed processed, $created created'),
        ],
      ),
    );
  }

  Future<void> _selectFile(Function(File) onFileSelected) async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['csv', 'xlsx', 'xls'],
      );

      if (result != null && result.files.single.path != null) {
        final file = File(result.files.single.path!);
        onFileSelected(file);
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error selecting file: $e')),
      );
    }
  }


  Future<void> _importDiseases() async {
    if (_diseasesFile == null) return;

    try {
      await ref.read(warhammerNotifierProvider.notifier).importDiseases(_diseasesFile!);
      setState(() {
        _lastImportResult = null; // Will be updated by the notifier
      });
    } catch (e) {
      setState(() {
        _importError = e.toString();
      });
    }
  }

  Future<void> _importSymptoms() async {
    if (_symptomsFile == null) return;

    try {
      await ref.read(warhammerNotifierProvider.notifier).importSymptoms(_symptomsFile!);
      setState(() {
        _lastImportResult = null; // Will be updated by the notifier
      });
    } catch (e) {
      setState(() {
        _importError = e.toString();
      });
    }
  }

  Future<void> _importConditionals() async {
    if (_conditionalsFile == null) return;

    try {
      await ref.read(warhammerNotifierProvider.notifier).importConditionals(_conditionalsFile!);
      setState(() {
        _lastImportResult = null; // Will be updated by the notifier
      });
    } catch (e) {
      setState(() {
        _importError = e.toString();
      });
    }
  }

  Future<void> _importAll() async {
    if (_diseasesFile == null || _symptomsFile == null || _conditionalsFile == null) {
      return;
    }

    try {
      // Import in order: diseases, symptoms, conditionals
      await ref.read(warhammerNotifierProvider.notifier).importDiseases(_diseasesFile!);
      await ref.read(warhammerNotifierProvider.notifier).importSymptoms(_symptomsFile!);
      await ref.read(warhammerNotifierProvider.notifier).importConditionals(_conditionalsFile!);

      // Show success message
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('All files imported successfully!'),
          backgroundColor: Colors.green,
        ),
      );

      // Navigate back
      Navigator.of(context).pop();
    } catch (e) {
      setState(() {
        _importError = e.toString();
      });
    }
  }
}
