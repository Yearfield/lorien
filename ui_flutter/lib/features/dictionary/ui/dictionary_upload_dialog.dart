import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import '../state/dictionary_provider.dart';

class DictionaryUploadDialog extends ConsumerStatefulWidget {
  const DictionaryUploadDialog({super.key});

  @override
  ConsumerState<DictionaryUploadDialog> createState() => _DictionaryUploadDialogState();
}

class _DictionaryUploadDialogState extends ConsumerState<DictionaryUploadDialog> {
  File? _selectedFile;
  bool _updateExisting = true;
  bool _createNewTerms = true;
  double _minSimilarity = 0.8;

  @override
  Widget build(BuildContext context) {
    final uploadState = ref.watch(dictionaryUploadProvider);
    final uploadNotifier = ref.read(dictionaryUploadProvider.notifier);

    return AlertDialog(
      title: const Text('Upload Medical Dictionary'),
      content: SizedBox(
        width: 500,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // File selection
            _buildFileSelection(),

            if (_selectedFile != null) ...[
              const SizedBox(height: 16),
              _buildUploadOptions(),
              const SizedBox(height: 16),
              _buildValidationResults(uploadState),
              const SizedBox(height: 16),
              _buildUploadResults(uploadState),
            ],

            if (uploadState.error != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  border: Border.all(color: Colors.red.shade200),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(Icons.error, color: Colors.red.shade600),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        uploadState.error!,
                        style: TextStyle(color: Colors.red.shade700),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () {
            uploadNotifier.clearResults();
            Navigator.of(context).pop();
          },
          child: const Text('Cancel'),
        ),
        if (_selectedFile != null) ...[
          TextButton(
            onPressed: uploadState.isValidating ? null : () async {
              await uploadNotifier.validateFile(_selectedFile!);
            },
            child: uploadState.isValidating
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('Validate'),
          ),
          ElevatedButton(
            onPressed: (uploadState.isUploading || uploadState.validationResult == null)
                ? null
                : () async {
                    await uploadNotifier.uploadFile(
                      _selectedFile!,
                      updateExisting: _updateExisting,
                      createNewTerms: _createNewTerms,
                      minSimilarity: _minSimilarity,
                    );
                  },
            child: uploadState.isUploading
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('Upload'),
          ),
        ],
      ],
    );
  }

  Widget _buildFileSelection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Select Dictionary File',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              'Upload a CSV or XLSX file containing medical terms with definitions, synonyms, and red flag status.',
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 12),
            ElevatedButton.icon(
              onPressed: _pickFile,
              icon: const Icon(Icons.upload_file),
              label: const Text('Choose File'),
            ),
            if (_selectedFile != null) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  border: Border.all(color: Colors.green.shade200),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Row(
                  children: [
                    Icon(Icons.check_circle, color: Colors.green.shade600, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _selectedFile!.path.split('/').last,
                        style: TextStyle(color: Colors.green.shade700),
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

  Widget _buildUploadOptions() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Upload Options',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),

            // Update existing terms
            CheckboxListTile(
              title: const Text('Update existing terms'),
              subtitle: const Text('Update definitions, synonyms, and red flag status for existing terms'),
              value: _updateExisting,
              onChanged: (value) => setState(() => _updateExisting = value ?? true),
              controlAffinity: ListTileControlAffinity.leading,
              contentPadding: EdgeInsets.zero,
            ),

            // Create new terms
            CheckboxListTile(
              title: const Text('Create new terms'),
              subtitle: const Text('Add terms that are not currently in the dictionary'),
              value: _createNewTerms,
              onChanged: (value) => setState(() => _createNewTerms = value ?? true),
              controlAffinity: ListTileControlAffinity.leading,
              contentPadding: EdgeInsets.zero,
            ),

            // Similarity threshold
            const SizedBox(height: 8),
            Text('Similarity threshold: ${(_minSimilarity * 100).round()}%'),
            Slider(
              value: _minSimilarity,
              min: 0.5,
              max: 1.0,
              divisions: 10,
              onChanged: (value) => setState(() => _minSimilarity = value),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildValidationResults(DictionaryUploadState state) {
    if (state.validationResult == null) return const SizedBox.shrink();

    final validation = state.validationResult!;
    final isValid = validation['valid'] as bool? ?? false;
    final errors = (validation['errors'] as List?)?.cast<String>() ?? [];
    final warnings = (validation['warnings'] as List?)?.cast<String>() ?? [];
    final analysis = validation['analysis'] as Map<String, dynamic>? ?? {};

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  isValid ? Icons.check_circle : Icons.error,
                  color: isValid ? Colors.green : Colors.red,
                ),
                const SizedBox(width: 8),
                Text(
                  'File Validation ${isValid ? 'Passed' : 'Failed'}',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: isValid ? Colors.green : Colors.red,
                  ),
                ),
              ],
            ),

            if (analysis['total_rows'] != null) ...[
              const SizedBox(height: 8),
              Text('Rows: ${analysis['total_rows']}'),
            ],

            if (errors.isNotEmpty) ...[
              const SizedBox(height: 8),
              ...errors.map((error) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.error, color: Colors.red, size: 16),
                    const SizedBox(width: 8),
                    Expanded(child: Text(error, style: const TextStyle(color: Colors.red))),
                  ],
                ),
              )),
            ],

            if (warnings.isNotEmpty) ...[
              const SizedBox(height: 8),
              ...warnings.map((warning) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.warning, color: Colors.orange, size: 16),
                    const SizedBox(width: 8),
                    Expanded(child: Text(warning, style: const TextStyle(color: Colors.orange))),
                  ],
                ),
              )),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildUploadResults(DictionaryUploadState state) {
    if (state.uploadResult == null) return const SizedBox.shrink();

    final result = state.uploadResult!;
    final summary = result['summary'] as Map<String, dynamic>? ?? {};
    final processingResults = result['processing_results'] as Map<String, dynamic>? ?? {};
    final spellingSuggestions = (processingResults['spelling_suggestions'] as List?) ?? [];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.green),
                const SizedBox(width: 8),
                const Text(
                  'Upload Complete',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.green),
                ),
              ],
            ),

            const SizedBox(height: 12),

            // Summary
            _buildSummaryCard(summary),

            // Spelling suggestions
            if (spellingSuggestions.isNotEmpty) ...[
              const SizedBox(height: 12),
              _buildSpellingSuggestions(spellingSuggestions),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryCard(Map<String, dynamic> summary) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        border: Border.all(color: Colors.blue.shade200),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Processing Summary',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          _buildSummaryRow('Terms Processed', summary['total_terms_processed']?.toString() ?? '0'),
          _buildSummaryRow('Exact Matches', summary['exact_matches_found']?.toString() ?? '0'),
          _buildSummaryRow('Updates Applied', summary['updates_applied']?.toString() ?? '0'),
          _buildSummaryRow('New Terms Created', summary['new_terms_created']?.toString() ?? '0'),
          _buildSummaryRow('Spelling Suggestions', summary['spelling_suggestions_found']?.toString() ?? '0'),
          _buildSummaryRow('Success Rate', '${summary['success_rate']?.toString() ?? '0'}%'),
        ],
      ),
    );
  }

  Widget _buildSummaryRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  Widget _buildSpellingSuggestions(List spellingSuggestions) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Spelling Suggestions',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        ...spellingSuggestions.take(5).map((suggestion) {
          final term = suggestion['term'] as String? ?? '';
          final suggestions = (suggestion['spelling_suggestions'] as List?) ?? [];

          return Card(
            margin: const EdgeInsets.symmetric(vertical: 2),
            child: Padding(
              padding: const EdgeInsets.all(8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    term,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Suggested: ${suggestions.map((s) => s['suggested_term']).join(', ')}',
                    style: const TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ],
              ),
            ),
          );
        }).toList(),
      ],
    );
  }

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['csv', 'xlsx'],
    );

    if (result != null && result.files.single.path != null) {
      setState(() {
        _selectedFile = File(result.files.single.path!);
      });
    }
  }
}
