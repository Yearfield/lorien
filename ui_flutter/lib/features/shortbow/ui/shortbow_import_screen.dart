import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';

import '../state/shortbow_notifier.dart';

class ShortBowImportScreen extends ConsumerStatefulWidget {
  const ShortBowImportScreen({super.key});

  @override
  ConsumerState<ShortBowImportScreen> createState() => _ShortBowImportScreenState();
}

class _ShortBowImportScreenState extends ConsumerState<ShortBowImportScreen> {
  bool _isImporting = false;

  @override
  Widget build(BuildContext context) {
    final shortBowState = ref.watch(shortBowNotifierProvider);
    final isLoading = ref.watch(shortBowLoadingProvider);
    final error = ref.watch(shortBowErrorProvider);

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Icon(Icons.upload_file, size: 24, color: Colors.blue[700]),
              const SizedBox(width: 8),
              const Text(
                'Import Symptom Matrix',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Import section
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Upload Excel File',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Upload an Excel file containing a symptom probability matrix. Rows and columns should be symptom names, with cell values representing probabilities (0-1) of symptom co-occurrence.',
                    style: TextStyle(color: Colors.grey),
                  ),
                  const SizedBox(height: 16),

                  // Import button
                  ElevatedButton.icon(
                    onPressed: _isImporting ? null : _importFile,
                    icon: _isImporting
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.upload),
                    label: Text(_isImporting ? 'Importing...' : 'Choose Excel File'),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16),

          // Statistics section
          if (shortBowState.stats != null) ...[
            const Text(
              'Data Statistics',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    _buildStatRow('Total Symptoms', shortBowState.stats!.totalSymptoms.toString()),
                    _buildStatRow('Total Links', shortBowState.stats!.totalLinks.toString()),
                    _buildStatRow('Calculations', shortBowState.stats!.totalCalculations.toString()),
                    _buildStatRow('Saved Calculations', shortBowState.stats!.savedCalculations.toString()),
                  ],
                ),
              ),
            ),
          ],

          // Error display
          if (error != null) ...[
            const SizedBox(height: 16),
            Card(
              color: Colors.red[50],
              child: Padding(
                padding: const EdgeInsets.all(16.0),
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
            ),
          ],

          // Loading indicator
          if (isLoading) ...[
            const SizedBox(height: 16),
            const Center(
              child: CircularProgressIndicator(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildStatRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }

  Future<void> _importFile() async {
    try {
      setState(() {
        _isImporting = true;
      });

      // Pick file
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['xlsx', 'xls'],
      );

      if (result == null || result.files.isEmpty) {
        setState(() {
          _isImporting = false;
        });
        return;
      }

      final file = File(result.files.first.path!);

      // Import via notifier
      final notifier = ref.read(shortBowNotifierProvider.notifier);
      await notifier.importMatrix(file);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Symptom matrix imported successfully!'),
            backgroundColor: Colors.green,
          ),
        );
      }

    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Import failed: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isImporting = false;
        });
      }
    }
  }
}
