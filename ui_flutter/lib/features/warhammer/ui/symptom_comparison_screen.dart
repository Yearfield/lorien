import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/warhammer_models.dart';
import '../state/warhammer_notifier.dart';
import 'unified_synonym_management_dialog.dart';

class SymptomComparisonScreen extends ConsumerStatefulWidget {
  const SymptomComparisonScreen({super.key});

  @override
  ConsumerState<SymptomComparisonScreen> createState() => _SymptomComparisonScreenState();
}

class _SymptomComparisonScreenState extends ConsumerState<SymptomComparisonScreen> {
  @override
  void initState() {
    super.initState();
    // Load comparison data and synonyms when screen opens
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(warhammerNotifierProvider.notifier).loadSymptomComparison();
      ref.read(warhammerNotifierProvider.notifier).loadSynonyms();
    });
  }

  @override
  Widget build(BuildContext context) {
    final comparison = ref.watch(symptomComparisonProvider);
    final isLoading = ref.watch(symptomComparisonLoadingProvider);
    final error = ref.watch(warhammerErrorProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Symptom Comparison'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: _buildBody(comparison, isLoading, error),
    );
  }

  Widget _buildBody(SymptomComparison? comparison, bool isLoading, String? error) {
    if (isLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Loading symptom comparison...'),
          ],
        ),
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
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              'Error loading comparison',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              error,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                ref.read(warhammerNotifierProvider.notifier).loadSymptomComparison();
              },
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (comparison == null) {
      return const Center(
        child: Text('No comparison data available'),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSummaryCard(comparison),
          const SizedBox(height: 24),
          _buildMatchingSymptoms(comparison),
          const SizedBox(height: 24),
          if (comparison.normalizedMatches.isNotEmpty) ...[
              _buildNormalizedMatches(comparison),
              const SizedBox(height: 24),
            ],
            _buildExistingSynonyms(),
            const SizedBox(height: 24),
            _buildMissingSymptoms(comparison),
            const SizedBox(height: 24),
            _buildExtraSymptoms(comparison),
        ],
      ),
    );
  }

  Widget _buildSummaryCard(SymptomComparison comparison) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Summary',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'Decision Tree Symptoms',
                    comparison.totalDecisionTree,
                    Icons.account_tree,
                    Colors.blue,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildStatItem(
                    'Warhammer Symptoms',
                    comparison.totalWarhammer,
                    Icons.medical_services,
                    Colors.green,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'Matching Symptoms',
                    comparison.matchCount,
                    Icons.check_circle,
                    Colors.orange,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildStatItem(
                    'Match Rate',
                    comparison.totalDecisionTree > 0
                        ? '${((comparison.matchCount / comparison.totalDecisionTree) * 100).toStringAsFixed(1)}%'
                        : '0.0%',
                    Icons.percent,
                    Colors.purple,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, dynamic value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value.toString(),
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
              color: color,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: Theme.of(context).textTheme.bodySmall,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildMatchingSymptoms(SymptomComparison comparison) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.check_circle, color: Colors.green),
                const SizedBox(width: 8),
                Text(
                  'Matching Symptoms (${comparison.matchingSymptoms.length})',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (comparison.matchingSymptoms.isEmpty)
              const Text('No matching symptoms found.')
            else
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: comparison.matchingSymptoms.map((symptom) {
                  return Chip(
                    label: Text(symptom),
                    backgroundColor: Colors.green.withOpacity(0.1),
                    side: BorderSide(color: Colors.green.withOpacity(0.3)),
                  );
                }).toList(),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildNormalizedMatches(SymptomComparison comparison) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.transform, color: Colors.teal),
                const SizedBox(width: 8),
                Text(
                  'Normalized Matches (${comparison.normalizedMatches.length})',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'These symptoms were matched through case-insensitive normalization:',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.teal.shade700,
              ),
            ),
            const SizedBox(height: 16),
            ...comparison.normalizedMatches.map((match) {
              return Container(
                margin: const EdgeInsets.only(bottom: 8),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.teal.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.teal.withOpacity(0.3)),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Decision Tree:',
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(match.decisionTree),
                        ],
                      ),
                    ),
                    const SizedBox(width: 16),
                    Icon(Icons.arrow_forward, color: Colors.teal),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Warhammer:',
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(match.warhammer),
                        ],
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildMissingSymptoms(SymptomComparison comparison) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.warning, color: Colors.orange),
                const SizedBox(width: 8),
                Text(
                  'Missing from Warhammer (${comparison.missingFromWarhammer.length})',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'These symptoms exist in your decision tree but are not in the Warhammer database.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.orange.shade700,
              ),
            ),
            const SizedBox(height: 16),
            if (comparison.missingFromWarhammer.isEmpty)
              const Text('All decision tree symptoms are in the Warhammer database!')
            else
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: comparison.missingFromWarhammer.map((symptom) {
                  return Chip(
                    label: Text(symptom),
                    backgroundColor: Colors.orange.withOpacity(0.1),
                    side: BorderSide(color: Colors.orange.withOpacity(0.3)),
                  );
                }).toList(),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildExtraSymptoms(SymptomComparison comparison) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.info, color: Colors.blue),
                const SizedBox(width: 8),
                Text(
                  'Extra in Warhammer (${comparison.extraInWarhammer.length})',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'These symptoms exist in the Warhammer database but are not in your decision tree.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.blue.shade700,
              ),
            ),
            const SizedBox(height: 16),
            if (comparison.extraInWarhammer.isEmpty)
              const Text('No extra symptoms in Warhammer database.')
            else
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: comparison.extraInWarhammer.map((symptom) {
                  return GestureDetector(
                    onTap: () => _showSynonymDialog(symptom, comparison.decisionTreeSymptoms),
                    child: Chip(
                      label: Text(symptom),
                      backgroundColor: Colors.blue.withOpacity(0.1),
                      side: BorderSide(color: Colors.blue.withOpacity(0.3)),
                      deleteIcon: const Icon(Icons.add, size: 18),
                      onDeleted: () => _showSynonymDialog(symptom, comparison.decisionTreeSymptoms),
                    ),
                  );
                }).toList(),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildExistingSynonyms() {
    final synonyms = ref.watch(synonymsProvider);

    if (synonyms.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.link, color: Colors.purple),
                const SizedBox(width: 8),
                Text(
                  'Existing Synonym Mappings (${synonyms.length})',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'These Warhammer symptoms are mapped to decision tree synonyms:',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.purple.shade700,
              ),
            ),
            const SizedBox(height: 16),
            ...synonyms.map((synonym) {
              return Container(
                margin: const EdgeInsets.only(bottom: 8),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.purple.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.purple.withOpacity(0.3)),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Warhammer:',
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(synonym.warhammerSymptom),
                        ],
                      ),
                    ),
                    const SizedBox(width: 16),
                    Icon(Icons.arrow_forward, color: Colors.purple),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Decision Tree:',
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(synonym.decisionTreeSymptom),
                        ],
                      ),
                    ),
                    const SizedBox(width: 16),
                    IconButton(
                      icon: const Icon(Icons.edit, size: 20),
                      onPressed: () => _showSynonymDialog(
                        synonym.warhammerSymptom,
                        [], // Empty list since we're editing existing
                      ),
                      tooltip: 'Edit synonyms',
                    ),
                    IconButton(
                      icon: const Icon(Icons.delete, size: 20, color: Colors.red),
                      onPressed: () => _deleteSynonym(synonym),
                      tooltip: 'Delete mapping',
                    ),
                  ],
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  void _deleteSynonym(SymptomSynonym synonym) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Synonym Mapping'),
        content: Text(
          'Are you sure you want to delete the mapping between '
          '"${synonym.warhammerSymptom}" and "${synonym.decisionTreeSymptom}"?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.of(context).pop();
              try {
                await ref.read(warhammerNotifierProvider.notifier).deleteSynonym(synonym.id);
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Synonym mapping deleted successfully'),
                      backgroundColor: Colors.green,
                    ),
                  );
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Failed to delete synonym: $e'),
                      backgroundColor: Colors.red,
                    ),
                  );
                }
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Delete', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  void _showSynonymDialog(String warhammerSymptom, List<String> decisionTreeSymptoms) {
    // Get current synonyms for this Warhammer symptom
    final synonyms = ref.read(synonymsProvider);
    final currentSynonyms = synonyms
        .where((s) => s.warhammerSymptom == warhammerSymptom)
        .map((s) => s.decisionTreeSymptom)
        .toList();

    showDialog(
      context: context,
      builder: (context) => UnifiedSynonymManagementDialog(
        type: SynonymType.warhammer,
        warhammerSymptom: warhammerSymptom,
        currentSynonyms: currentSynonyms,
      ),
    );
  }
}
