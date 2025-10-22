import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../dictionary/data/dictionary_dto.dart';
import '../../dictionary/data/dictionary_repo.dart';
import '../../dictionary/state/dictionary_provider.dart';
import '../data/warhammer_models.dart';
import '../state/warhammer_notifier.dart';

enum SynonymType { dictionary, warhammer }

class UnifiedSynonymManagementDialog extends ConsumerStatefulWidget {
  final SynonymType type;
  final int? termId; // For dictionary terms
  final String? warhammerSymptom; // For Warhammer symptoms
  final List<String> currentSynonyms;

  const UnifiedSynonymManagementDialog({
    super.key,
    required this.type,
    this.termId,
    this.warhammerSymptom,
    required this.currentSynonyms,
  });

  @override
  ConsumerState<UnifiedSynonymManagementDialog> createState() => _UnifiedSynonymManagementDialogState();
}

class _UnifiedSynonymManagementDialogState extends ConsumerState<UnifiedSynonymManagementDialog> {
  late TextEditingController _synonymsController;
  List<String> _currentSynonyms = [];
  bool _hasChanges = false;
  bool _isSaving = false;
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _synonymsController = TextEditingController();
    _currentSynonyms = List.from(widget.currentSynonyms);
  }

  @override
  void dispose() {
    _synonymsController.dispose();
    super.dispose();
  }

  void _onFieldChanged() {
    setState(() {
      _hasChanges = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: Container(
        width: MediaQuery.of(context).size.width * 0.6,
        height: MediaQuery.of(context).size.height * 0.7,
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Icon(
                  widget.type == SynonymType.dictionary ? Icons.book : Icons.medical_services,
                  color: widget.type == SynonymType.dictionary ? Colors.blue : Colors.green,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '${widget.type == SynonymType.dictionary ? 'Dictionary' : 'Warhammer'} Synonym Management',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Term/Symptom info
            _buildTermInfo(),
            const SizedBox(height: 24),

            // Synonyms section
            Expanded(
              child: _buildSynonymsSection(),
            ),

            // Footer with save button
            const Divider(),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: _isSaving ? null : () => Navigator.of(context).pop(),
                  child: const Text('Close'),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: (_hasChanges && !_isSaving) ? _saveChanges : null,
                  child: _isSaving
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Save Changes'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTermInfo() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(
              widget.type == SynonymType.dictionary ? Icons.book : Icons.medical_services,
              color: widget.type == SynonymType.dictionary ? Colors.blue : Colors.green,
              size: 32,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.type == SynonymType.dictionary
                        ? 'Dictionary Term'
                        : 'Warhammer Symptom',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    widget.type == SynonymType.dictionary
                        ? 'ID: ${widget.termId}'
                        : widget.warhammerSymptom ?? 'Unknown',
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: (widget.type == SynonymType.dictionary ? Colors.blue : Colors.green).withOpacity(0.1),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: (widget.type == SynonymType.dictionary ? Colors.blue : Colors.green).withOpacity(0.3),
                ),
              ),
              child: Text(
                widget.type == SynonymType.dictionary ? 'Dictionary' : 'Warhammer',
                style: TextStyle(
                  color: widget.type == SynonymType.dictionary ? Colors.blue : Colors.green,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSynonymsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Synonyms',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 8),
        Text(
          'Manage synonyms for this ${widget.type == SynonymType.dictionary ? 'term' : 'symptom'}. '
          'Synonyms help connect related terms across different systems.',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: Colors.grey[600],
          ),
        ),
        const SizedBox(height: 16),

        // Current synonyms
        if (_currentSynonyms.isNotEmpty) ...[
          Text(
            'Current Synonyms (${_currentSynonyms.length})',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          Container(
            constraints: const BoxConstraints(maxHeight: 200),
            child: SingleChildScrollView(
              child: Wrap(
                spacing: 8,
                runSpacing: 8,
                children: _currentSynonyms.map((synonym) {
                  return Chip(
                    label: Text(synonym),
                    deleteIcon: const Icon(Icons.close, size: 18),
                    onDeleted: () => _removeSynonym(synonym),
                    backgroundColor: (widget.type == SynonymType.dictionary ? Colors.blue : Colors.green).withOpacity(0.1),
                    side: BorderSide(
                      color: (widget.type == SynonymType.dictionary ? Colors.blue : Colors.green).withOpacity(0.3),
                    ),
                  );
                }).toList(),
              ),
            ),
          ),
          const SizedBox(height: 16),
        ],

        // Add new synonyms
        Text(
          'Add New Synonyms',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        TextField(
          controller: _synonymsController,
          decoration: InputDecoration(
            hintText: 'Enter synonyms separated by commas...',
            border: const OutlineInputBorder(),
            helperText: 'Separate multiple synonyms with commas, or press Enter to add individually',
            suffixIcon: IconButton(
              icon: const Icon(Icons.add),
              onPressed: _addSynonymsFromText,
            ),
          ),
          onChanged: (_) => _onFieldChanged(),
          onSubmitted: (value) {
            if (value.trim().isNotEmpty) {
              _addSynonym(value.trim());
            }
          },
        ),
        const SizedBox(height: 16),

        // Quick add from decision tree (for Warhammer symptoms)
        if (widget.type == SynonymType.warhammer) ...[
          Text(
            'Quick Add from Decision Tree',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          _buildDecisionTreeQuickAdd(),
        ],
      ],
    );
  }

  Widget _buildDecisionTreeQuickAdd() {
    return Consumer(
      builder: (context, ref, child) {
        final decisionTreeRoots = ref.watch(decisionTreeRootsProvider);

        if (decisionTreeRoots.isEmpty) {
          return const Text('No decision tree data available');
        }

        final filteredSymptoms = _getFilteredDecisionTreeSymptoms(decisionTreeRoots);

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Search field
            TextField(
              decoration: InputDecoration(
                hintText: 'Search decision tree symptoms...',
                prefixIcon: const Icon(Icons.search),
                border: const OutlineInputBorder(),
                isDense: true,
              ),
              onChanged: (value) {
                setState(() {
                  _searchQuery = value.toLowerCase();
                });
              },
            ),
            const SizedBox(height: 8),

            // Show results only when searching
            if (_searchQuery.isNotEmpty) ...[
              Text(
                'Found ${filteredSymptoms.length} symptoms:',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey[600],
                ),
              ),
              const SizedBox(height: 8),

              // Filtered symptoms
              Container(
                constraints: const BoxConstraints(maxHeight: 200),
                child: SingleChildScrollView(
                  child: Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: filteredSymptoms.map((symptom) {
                      final isAlreadyAdded = _currentSynonyms.contains(symptom);

                      return FilterChip(
                        label: Text(symptom),
                        selected: isAlreadyAdded,
                        onSelected: isAlreadyAdded ? null : (selected) {
                          if (selected) {
                            _addSynonym(symptom);
                          }
                        },
                        selectedColor: Colors.green.withOpacity(0.2),
                        checkmarkColor: Colors.green,
                      );
                    }).toList(),
                  ),
                ),
              ),
            ] else ...[
              // Show instruction when not searching
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey[300]!),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info_outline, color: Colors.grey[600], size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Type in the search field above to find decision tree symptoms to add as synonyms.',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.grey[600],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        );
      },
    );
  }

  void _addSynonym(String synonym) {
    if (synonym.isNotEmpty && !_currentSynonyms.contains(synonym)) {
      setState(() {
        _currentSynonyms.add(synonym);
        _onFieldChanged();
      });
    }
  }

  void _removeSynonym(String synonym) {
    setState(() {
      _currentSynonyms.remove(synonym);
      _onFieldChanged();
    });
  }

  void _addSynonymsFromText() {
    final text = _synonymsController.text.trim();
    if (text.isEmpty) return;

    final synonyms = text
        .split(',')
        .map((s) => s.trim())
        .where((s) => s.isNotEmpty)
        .toList();

    for (final synonym in synonyms) {
      _addSynonym(synonym);
    }

    _synonymsController.clear();
  }

  List<String> _getFilteredDecisionTreeSymptoms(List<Map<String, dynamic>> decisionTreeRoots) {
    // Get all symptoms from decision tree (roots and their children)
    final allSymptoms = <String>{};

    for (final root in decisionTreeRoots) {
      final label = root['label'] as String;
      allSymptoms.add(label);

      // Add children if they exist
      final children = root['children'] as List<dynamic>?;
      if (children != null) {
        for (final child in children) {
          if (child is Map<String, dynamic> && child['label'] != null) {
            allSymptoms.add(child['label'] as String);
          }
        }
      }
    }

    // If we don't have many symptoms, try to get more from the symptom comparison
    if (allSymptoms.length < 10) {
      final comparison = ref.read(symptomComparisonProvider);
      if (comparison != null) {
        allSymptoms.addAll(comparison.decisionTreeSymptoms);
      }
    }

    // Filter based on search query
    final filteredSymptoms = allSymptoms.where((symptom) {
      if (_searchQuery.isEmpty) return true;
      return symptom.toLowerCase().contains(_searchQuery);
    }).toList();

    // Sort alphabetically
    filteredSymptoms.sort();

    return filteredSymptoms;
  }

  Future<void> _saveChanges() async {
    setState(() {
      _isSaving = true;
    });

    try {
      if (widget.type == SynonymType.dictionary) {
        // Update dictionary term synonyms
        await ref.read(dictionaryRepoProvider).updateTerm(
          termId: widget.termId!,
          synonyms: _currentSynonyms,
        );
      } else {
        // For Warhammer symptoms, we need to create individual synonym mappings
        // This is more complex as we need to map each synonym to the Warhammer symptom
        for (final synonym in _currentSynonyms) {
          if (!widget.currentSynonyms.contains(synonym)) {
            // Only create new mappings
            await ref.read(warhammerNotifierProvider.notifier).createSynonym(
              widget.warhammerSymptom!,
              synonym,
            );
          }
        }

        // Remove synonyms that are no longer in the list
        for (final oldSynonym in widget.currentSynonyms) {
          if (!_currentSynonyms.contains(oldSynonym)) {
            // Find and delete the synonym mapping
            final synonyms = ref.read(synonymsProvider);
            final synonymToDelete = synonyms.firstWhere(
              (s) => s.warhammerSymptom == widget.warhammerSymptom && s.decisionTreeSymptom == oldSynonym,
              orElse: () => throw Exception('Synonym not found'),
            );
            await ref.read(warhammerNotifierProvider.notifier).deleteSynonym(synonymToDelete.id);
          }
        }
      }

      if (mounted) {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Synonyms updated successfully for ${widget.type == SynonymType.dictionary ? 'dictionary term' : 'Warhammer symptom'}',
            ),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to update synonyms: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSaving = false;
        });
      }
    }
  }
}
