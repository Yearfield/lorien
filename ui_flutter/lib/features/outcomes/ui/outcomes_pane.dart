import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../warhammer/state/warhammer_notifier.dart';
import '../../warhammer/state/warhammer_state.dart';
import '../../warhammer/data/warhammer_models.dart';
import '../../warhammer/ui/warhammer_import_screen.dart';
import '../../warhammer/ui/symptom_comparison_screen.dart';

class OutcomesPane extends ConsumerStatefulWidget {
  const OutcomesPane({super.key});

  @override
  ConsumerState<OutcomesPane> createState() => _OutcomesPaneState();
}

class _OutcomesPaneState extends ConsumerState<OutcomesPane> {
  String _selectedEngine = 'Warhammer';

  @override
  Widget build(BuildContext context) {
    final warhammerState = ref.watch(warhammerNotifierProvider);
    final isLoading = ref.watch(warhammerLoadingProvider);
    final isCalculating = ref.watch(warhammerCalculatingProvider);
    final error = ref.watch(warhammerErrorProvider);

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Engine selector
          Row(
            children: [
              const Text(
                'Engine:',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(width: 12),
              DropdownButton<String>(
                value: _selectedEngine,
                onChanged: (String? newValue) {
                  if (newValue != null) {
                    setState(() {
                      _selectedEngine = newValue;
                    });
                  }
                },
                items: const [
                  DropdownMenuItem<String>(
                    value: 'Warhammer',
                    child: Text('Warhammer'),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 24),

          // Main content based on selected engine
          Expanded(
            child: _selectedEngine == 'Warhammer'
                ? _buildWarhammerContent(warhammerState, isLoading, isCalculating, error)
                : const Center(
                    child: Text('Engine not implemented yet'),
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildWarhammerContent(
    WarhammerState state,
    bool isLoading,
    bool isCalculating,
    String? error,
  ) {
    if (isLoading) {
    return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red[300],
            ),
            const SizedBox(height: 16),
            Text(
              'Error: $error',
              style: TextStyle(color: Colors.red[700]),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                ref.read(warhammerNotifierProvider.notifier).clearError();
                ref.read(warhammerNotifierProvider.notifier).refresh();
              },
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    // Check if data is available
    if (state.symptoms.isEmpty && state.diseases.isEmpty) {
      return _buildEmptyState();
    }

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Stats card
          if (state.stats != null) _buildStatsCard(state.stats!),
          const SizedBox(height: 24),

          // Import Data button
          _buildImportDataButton(),
          const SizedBox(height: 16),

          // Compare Symptoms button
          _buildSymptomComparisonButton(),
          const SizedBox(height: 16),

          // Scan VM Builder button
          _buildScanVMBuilderButton(),
          const SizedBox(height: 24),

          // Symptom selection
          _buildSymptomSelection(state),
          const SizedBox(height: 24),

          // Calculate button
          _buildCalculateButton(isCalculating),
          const SizedBox(height: 24),

          // Results
          if (state.lastCalculation != null) _buildResults(state),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.upload_file,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          const Text(
            'No Warhammer data available',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            'Import disease, symptom, and conditional probability data to get started.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => const WarhammerImportScreen(),
                ),
              );
            },
            icon: const Icon(Icons.upload),
            label: const Text('Import Data'),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsCard(WarhammerStats stats) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Data Summary',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatItem('Diseases', stats.totalDiseases.toString()),
                _buildStatItem('Symptoms', stats.totalSymptoms.toString()),
                _buildStatItem('Conditionals', stats.totalConditionals.toString()),
                _buildStatItem('Calculations', stats.savedCalculations.toString()),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        Text(
          label,
          style: const TextStyle(fontSize: 12, color: Colors.grey),
        ),
      ],
    );
  }

  Widget _buildSymptomSelection(WarhammerState state) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Text(
                  'Select Symptoms (1-5 required)',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                if (state.selectedSymptoms.length == 5)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.green.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.green.withOpacity(0.3)),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.auto_awesome, color: Colors.green, size: 16),
                        const SizedBox(width: 4),
                        Text(
                          'Auto-calculating...',
                          style: TextStyle(
                            color: Colors.green,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 12),

            // Selected symptoms
            if (state.selectedSymptoms.isNotEmpty) ...[
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: state.selectedSymptoms.map((symptom) {
                  return Chip(
                    label: Text(symptom),
                    onDeleted: () {
                      ref.read(warhammerNotifierProvider.notifier).removeSymptom(symptom);
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: 12),
            ],

            // Decision tree navigation dropdown
            Consumer(
              builder: (context, ref, child) {
                final currentTreeOptions = ref.watch(currentTreeOptionsProvider);
                final availableOptions = currentTreeOptions
                    .where((option) => !state.selectedSymptoms.contains(option['label']))
                    .toList();

                return DropdownButtonFormField<Map<String, dynamic>>(
                  key: ValueKey('${state.currentParentId}_${availableOptions.length}'), // Force rebuild when options change
                  value: null, // Explicitly set to null to avoid value conflicts
                  decoration: InputDecoration(
                    labelText: state.currentParentId == 0 ? 'Select Root Condition' : 'Select Symptom',
                    border: const OutlineInputBorder(),
                  ),
                  items: availableOptions.map((option) {
                    return DropdownMenuItem<Map<String, dynamic>>(
                      value: option,
                      child: Text(option['label']),
                    );
                  }).toList(),
                  onChanged: (Map<String, dynamic>? selectedOption) {
                    if (selectedOption != null) {
                      final label = selectedOption['label'] as String;
                      final id = selectedOption['id'] as int;

                      // Add the selected option as a symptom
                      ref.read(warhammerNotifierProvider.notifier).addSymptom(label);

                      // Navigate to children of this node
                      ref.read(warhammerNotifierProvider.notifier).navigateToTreeNode(id);
                    }
                  },
                );
              },
            ),

            // Navigation controls
            if (state.currentParentId != 0) ...[
              const SizedBox(height: 12),
              Row(
                children: [
                  TextButton.icon(
                    onPressed: () {
                      ref.read(warhammerNotifierProvider.notifier).resetTreeNavigation();
                    },
                    icon: const Icon(Icons.home),
                    label: const Text('Back to Roots'),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'Current: ${state.currentParentId}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ],

            if (state.selectedSymptoms.isNotEmpty) ...[
              const SizedBox(height: 8),
              TextButton(
                onPressed: () {
                  ref.read(warhammerNotifierProvider.notifier).clearSelectedSymptoms();
                },
                child: const Text('Clear All'),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildCalculateButton(bool isCalculating) {
    final selectedSymptoms = ref.watch(selectedSymptomsProvider);
    final canCalculate = selectedSymptoms.isNotEmpty && selectedSymptoms.length <= 5;
    final hasFiveSymptoms = selectedSymptoms.length == 5;

    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: canCalculate && !isCalculating
            ? () {
                ref.read(warhammerNotifierProvider.notifier).calculate();
              }
            : null,
        style: ElevatedButton.styleFrom(
          backgroundColor: hasFiveSymptoms ? Colors.green : null,
          foregroundColor: hasFiveSymptoms ? Colors.white : null,
        ),
        child: isCalculating
            ? const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                  SizedBox(width: 8),
                  Text('Calculating...'),
                ],
              )
            : hasFiveSymptoms
                ? const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.auto_awesome, size: 20),
                      SizedBox(width: 8),
                      Text('Auto-calculated! Click to recalculate'),
                    ],
                  )
                : Text(
                    selectedSymptoms.isEmpty
                        ? 'Select symptoms to calculate'
                        : 'Calculate Disease Probabilities (${selectedSymptoms.length}/5)',
                  ),
      ),
    );
  }

  Widget _buildResults(WarhammerState state) {
    final last = state.lastCalculation;
    final warnings = last?.errors ?? const <String>[];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (warnings.isNotEmpty) _buildWarnings(warnings),
        ..._buildResultCards(last?.results ?? []),
      ],
    );
  }

  Widget _buildWarnings(List<String> errors) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.orange[100],
        borderRadius: BorderRadius.circular(4),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Warnings:',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          ...errors.map((error) => Text('• $error')),
        ],
      ),
    );
  }

  List<Widget> _buildResultCards(List<DiseaseResult> results) {
    return results.asMap().entries.map((entry) {
      final index = entry.key;
      final result = entry.value;
      return Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: index == 0 ? Colors.blue[50] : Colors.grey[50],
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: index == 0 ? Colors.blue[200]! : Colors.grey[300]!,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    result.disease,
                    style: TextStyle(
                      fontWeight: index == 0 ? FontWeight.bold : FontWeight.normal,
                      fontSize: index == 0 ? 16 : 14,
                    ),
                  ),
                ),
                Text(
                  '${(result.probability * 100).toStringAsFixed(2)}%',
                  style: TextStyle(
                    fontWeight: index == 0 ? FontWeight.bold : FontWeight.normal,
                    fontSize: index == 0 ? 16 : 14,
                    color: index == 0 ? Colors.blue[700] : Colors.grey[700],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            // Confidence meter
            ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: result.probability.clamp(0.0, 1.0),
                minHeight: 6,
                backgroundColor: Colors.grey[300],
                valueColor: AlwaysStoppedAnimation<Color>(
                  index == 0 ? Colors.blue : Colors.grey.shade600,
                ),
              ),
            ),
          ],
        ),
      );
    }).toList();
  }

  // Removed the explanations section for now; warnings and results remain.

  Widget _buildImportDataButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: () {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (context) => const WarhammerImportScreen(),
            ),
          );
        },
        icon: const Icon(Icons.upload),
        label: const Text('Import Data'),
        style: ElevatedButton.styleFrom(
          padding: const EdgeInsets.symmetric(vertical: 16),
        ),
      ),
    );
  }

  Widget _buildSymptomComparisonButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: () {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (context) => const SymptomComparisonScreen(),
            ),
          );
        },
        icon: const Icon(Icons.compare_arrows),
        label: const Text('Compare Symptoms'),
        style: ElevatedButton.styleFrom(
          padding: const EdgeInsets.symmetric(vertical: 16),
          backgroundColor: Colors.blue,
          foregroundColor: Colors.white,
        ),
      ),
    );
  }

  Widget _buildScanVMBuilderButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: () {
          ref.read(warhammerNotifierProvider.notifier).refreshDecisionTreeData();
        },
        icon: const Icon(Icons.refresh),
        label: const Text('Scan VM Builder'),
        style: ElevatedButton.styleFrom(
          padding: const EdgeInsets.symmetric(vertical: 16),
          backgroundColor: Colors.green,
          foregroundColor: Colors.white,
        ),
      ),
    );
  }
}
