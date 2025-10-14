import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../state/dictionary_provider.dart';
import '../data/dictionary_dto.dart';

class TermDetailsDialog extends ConsumerStatefulWidget {
  final int termId;

  const TermDetailsDialog({
    super.key,
    required this.termId,
  });

  @override
  ConsumerState<TermDetailsDialog> createState() => _TermDetailsDialogState();
}

class _TermDetailsDialogState extends ConsumerState<TermDetailsDialog> {
  late TextEditingController _definitionController;
  late TextEditingController _synonymsController;
  late TextEditingController _termNameController;
  bool _isRedFlag = false;
  bool _hasChanges = false;
  List<String> _currentSynonyms = [];

  @override
  void initState() {
    super.initState();
    _definitionController = TextEditingController();
    _synonymsController = TextEditingController();
    _termNameController = TextEditingController();

    // Load the term details
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(termDetailsProvider.notifier).loadTerm(widget.termId);
    });
  }

  @override
  void dispose() {
    _definitionController.dispose();
    _synonymsController.dispose();
    _termNameController.dispose();
    super.dispose();
  }

  void _onFieldChanged() {
    setState(() {
      _hasChanges = true;
    });
  }

  void _updateControllersFromTerm(DictionaryTerm term) {
    setState(() {
      // Only update if the text is different to avoid interfering with user input
      if (_definitionController.text != (term.definition ?? '')) {
        _definitionController.text = term.definition ?? '';
      }
      if (_termNameController.text != term.term) {
        _termNameController.text = term.term;
      }
      _isRedFlag = term.isRedFlag;
      _currentSynonyms = List.from(term.synonyms);
    });
  }

  Future<void> _saveChanges() async {
    final definition = _definitionController.text.trim().isEmpty
        ? null
        : _definitionController.text.trim();

    // Use current synonyms list, plus any new ones from the text field
    final newSynonyms = _synonymsController.text.trim().isEmpty
        ? <String>[]
        : _synonymsController.text
            .split(',')
            .map((s) => s.trim())
            .where((s) => s.isNotEmpty)
            .toList();

    final synonyms = {..._currentSynonyms, ...newSynonyms}.toList();

    await ref.read(termDetailsProvider.notifier).updateTerm(
      definition: definition,
      synonyms: synonyms,
      isRedFlag: _isRedFlag,
    );

    setState(() {
      _hasChanges = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final termState = ref.watch(termDetailsProvider);

    // Update controllers when term data is loaded
    ref.listen<TermDetailsState>(termDetailsProvider, (previous, next) {
      if (next.term != null && (previous?.term == null || previous?.term?.id != next.term?.id)) {
        _updateControllersFromTerm(next.term!);
      }
    });

    return Dialog(
      child: Container(
        width: MediaQuery.of(context).size.width * 0.8,
        height: MediaQuery.of(context).size.height * 0.8,
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Term Details',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ],
            ),
            const SizedBox(height: 24),

            if (termState.isLoading)
              const Expanded(
                child: Center(
                  child: CircularProgressIndicator(),
                ),
              )
            else if (termState.error != null)
              Expanded(
                child: Center(
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
                        'Error loading term',
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        termState.error!,
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              )
            else if (termState.term != null)
              Expanded(
                child: SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildTermInfo(termState.term!),
                      const SizedBox(height: 24),
                      _buildEditableFields(),
                      const SizedBox(height: 24),
                      _buildTreeRelationships(termState.relationships),
                    ],
                  ),
                ),
              ),

            // Footer with save button
            if (termState.term != null) ...[
              const Divider(),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton(
                    onPressed: () => Navigator.of(context).pop(),
                    child: const Text('Close'),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton(
                    onPressed: _hasChanges && !termState.isUpdating
                        ? _saveChanges
                        : null,
                    child: termState.isUpdating
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
          ],
        ),
      ),
    );
  }

  Widget _buildTermInfo(DictionaryTerm term) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Editable term name
            TextField(
              controller: _termNameController,
              style: Theme.of(context).textTheme.headlineMedium,
              decoration: const InputDecoration(
                labelText: 'Term Name',
                border: OutlineInputBorder(),
                hintText: 'Enter term name...',
              ),
              onChanged: (_) => _onFieldChanged(),
              enabled: true,
              readOnly: false,
              autofocus: false,
            ),
            const SizedBox(height: 16),

            // Action buttons for rename and merge
            Row(
              children: [
                OutlinedButton.icon(
                  icon: const Icon(Icons.edit),
                  label: const Text('Rename'),
                  onPressed: () => _handleRename(term),
                ),
                const SizedBox(width: 8),
                OutlinedButton.icon(
                  icon: const Icon(Icons.merge_type),
                  label: const Text('Merge'),
                  onPressed: () => _handleMerge(term),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Statistics chips
            Row(
              children: [
                _buildInfoChip(
                  'Avg Children',
                  term.avgChildrenCount.toString(),
                  Icons.account_tree,
                ),
                const SizedBox(width: 8),
                _buildInfoChip(
                  'Conflicts',
                  term.conflictsCount.toString(),
                  Icons.warning,
                  term.conflictsCount > 0 ? Colors.orange : null,
                ),
                const SizedBox(width: 8),
                if (term.isRedFlag)
                  _buildInfoChip(
                    'Red Flag',
                    'Yes',
                    Icons.flag,
                    Colors.red,
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoChip(String label, String value, IconData icon, [Color? color]) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: (color ?? Theme.of(context).colorScheme.surfaceVariant).withOpacity(0.3),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: color),
          const SizedBox(width: 4),
          Text(
            '$label: $value',
            style: TextStyle(
              fontSize: 12,
              color: color ?? Theme.of(context).colorScheme.onSurface,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEditableFields() {
    final term = ref.watch(termDetailsProvider).term;
    if (term == null) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Editable Fields',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 16),

        // Definition
        TextField(
          controller: _definitionController,
          decoration: const InputDecoration(
            labelText: 'Definition',
            hintText: 'Enter medical definition...',
            border: OutlineInputBorder(),
          ),
          maxLines: 3,
          onChanged: (_) => _onFieldChanged(),
        ),
        const SizedBox(height: 16),

        // Synonyms
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Synonyms',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
            ),
            const SizedBox(height: 8),

            // Display current synonyms as chips
            if (_getCurrentSynonyms().isNotEmpty) ...[
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: _getCurrentSynonyms().map((synonym) {
                  return Chip(
                    label: Text(synonym),
                    deleteIcon: const Icon(Icons.close, size: 18),
                    onDeleted: () => _removeSynonym(synonym),
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  );
                }).toList(),
              ),
              const SizedBox(height: 8),
            ],

            // Input field for adding new synonyms
            TextField(
              controller: _synonymsController,
              decoration: const InputDecoration(
                hintText: 'Enter synonyms separated by commas...',
                border: OutlineInputBorder(),
                helperText: 'Separate multiple synonyms with commas, or press Enter to add individually',
              ),
              onChanged: (_) => _onFieldChanged(),
              onSubmitted: (value) {
                if (value.trim().isNotEmpty) {
                  _addSynonym(value.trim());
                }
              },
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Red Flag toggle
        Card(
          child: CheckboxListTile(
            title: const Text('Red Flag Term'),
            subtitle: const Text('Mark this term as a red flag'),
            value: _isRedFlag,
            onChanged: (value) {
              setState(() {
                _isRedFlag = value ?? false;
                _hasChanges = true;
              });
            },
          ),
        ),
      ],
    );
  }

  Widget _buildTreeRelationships(DictionaryTreeRelationships? relationships) {
    if (relationships == null) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Tree Relationships',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 16),

        // Summary cards
        Row(
          children: [
            Expanded(
              child: _buildRelationshipCard(
                'Nodes',
                relationships.nodes.length.toString(),
                Icons.circle,
                Colors.blue,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildRelationshipCard(
                'Parents',
                relationships.parents.length.toString(),
                Icons.arrow_upward,
                Colors.green,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _buildRelationshipCard(
                'Children',
                relationships.children.length.toString(),
                Icons.arrow_downward,
                Colors.orange,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Parents list
        if (relationships.parents.isNotEmpty) ...[
          Text(
            'Parent Terms',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          ...relationships.parents.map((parent) => ListTile(
            leading: CircleAvatar(
              backgroundColor: Colors.green.shade100,
              child: Text('${parent.depth}'),
            ),
            title: Text(parent.label ?? 'Unknown'),
            subtitle: Text('Depth ${parent.depth}'),
            dense: true,
          )),
          const SizedBox(height: 16),
        ],

        // Children list
        if (relationships.children.isNotEmpty) ...[
          Text(
            'Child Terms',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          ...relationships.children.map((child) => ListTile(
            leading: CircleAvatar(
              backgroundColor: Colors.orange.shade100,
              child: Text('${child.depth}'),
            ),
            title: Text(child.label ?? 'Unknown'),
            subtitle: Text('Depth ${child.depth}'),
            dense: true,
          )),
        ],
      ],
    );
  }

  Widget _buildRelationshipCard(String label, String count, IconData icon, Color color) {
    return Card(
      color: color.withOpacity(0.1),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(
              count,
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                color: color,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }

  List<String> _getCurrentSynonyms() {
    return _currentSynonyms;
  }

  void _addSynonym(String synonym) {
    if (synonym.isNotEmpty && !_currentSynonyms.contains(synonym)) {
      setState(() {
        _currentSynonyms.add(synonym);
        _synonymsController.clear();
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

  Future<void> _handleRename(DictionaryTerm term) async {
    final newTerm = _termNameController.text.trim();

    if (newTerm.isEmpty) {
      _showErrorDialog('Term name cannot be empty');
      return;
    }

    if (newTerm == term.term) {
      _showErrorDialog('New term name is the same as current name');
      return;
    }

    try {
      // Check for conflicts first
      final conflicts = await ref.read(dictionaryRepoProvider).getRenameConflicts(term.id, newTerm);

      if (conflicts['has_conflicts'] == true) {
        _showErrorDialog('Cannot rename: ${conflicts['conflict_details']}');
        return;
      }

      // Show confirmation dialog
      final confirmed = await _showConfirmationDialog(
        'Rename Term',
        'Are you sure you want to rename "${term.term}" to "$newTerm"?\n\n'
        'This will update ${conflicts['affected_nodes']} nodes in the tree.',
      );

      if (confirmed == true) {
        // Perform the rename
        await ref.read(dictionaryRepoProvider).renameTerm(term.id, newTerm);

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Term renamed successfully')),
          );

          // Refresh the term details
          await ref.read(termDetailsProvider.notifier).loadTerm(term.id);
        }
      }
    } catch (e) {
      _showErrorDialog('Failed to rename term: $e');
    }
  }

  Future<void> _handleMerge(DictionaryTerm term) async {
    // Show dialog to select target term for merge
    final targetTerm = await _showTargetTermSelectionDialog();
    if (targetTerm == null) return;

    try {
      // Get merge conflicts
      final conflicts = await ref.read(dictionaryRepoProvider).getMergeConflicts(term.id, targetTerm.id);

      if (conflicts['has_conflicts'] == true && conflicts['max_children_exceeded'] == true) {
        // Show conflict resolution dialog
        final resolved = await _showConflictResolutionDialog(conflicts);
        if (resolved == null) return;

        // Perform merge with selected children
        await ref.read(dictionaryRepoProvider).mergeTerms(
          term.id,
          targetTerm.id,
          selectedChildren: resolved,
        );
      } else {
        // No conflicts, show confirmation and merge
        final confirmed = await _showConfirmationDialog(
          'Merge Terms',
          'Are you sure you want to merge "${term.term}" into "${targetTerm.term}"?\n\n'
          'This will combine their children and delete the source term.',
        );

        if (confirmed == true) {
          await ref.read(dictionaryRepoProvider).mergeTerms(term.id, targetTerm.id);
        }
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Terms merged successfully')),
        );

        // Close the dialog since the source term no longer exists
        Navigator.of(context).pop();
      }
    } catch (e) {
      _showErrorDialog('Failed to merge terms: $e');
    }
  }

  Future<DictionaryTerm?> _showTargetTermSelectionDialog() async {
    // For now, show a simple text input dialog
    // In a real implementation, this would be a searchable list
    final controller = TextEditingController();

    final result = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Select Target Term'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            labelText: 'Target term name',
            hintText: 'Enter the name of the term to merge into...',
          ),
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(controller.text.trim()),
            child: const Text('Select'),
          ),
        ],
      ),
    );

    if (result == null || result.isEmpty) return null;

    // Search for the target term
    try {
      final searchResults = await ref.read(dictionaryRepoProvider).searchTerms(query: result);
      if (searchResults.items.isNotEmpty) {
        return searchResults.items.first;
      }
    } catch (e) {
      _showErrorDialog('Failed to find target term: $e');
    }

    return null;
  }

  Future<List<String>?> _showConflictResolutionDialog(Map<String, dynamic> conflicts) async {
    final unionChildren = List<String>.from(conflicts['union_children'] ?? []);

    return showDialog<List<String>>(
      context: context,
      builder: (context) => _ConflictResolutionDialog(unionChildren: unionChildren),
    );
  }

  Future<bool?> _showConfirmationDialog(String title, String message) async {
    return showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Confirm'),
          ),
        ],
      ),
    );
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Error'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
}

class _ConflictResolutionDialog extends StatefulWidget {
  final List<String> unionChildren;

  const _ConflictResolutionDialog({required this.unionChildren});

  @override
  State<_ConflictResolutionDialog> createState() => _ConflictResolutionDialogState();
}

class _ConflictResolutionDialogState extends State<_ConflictResolutionDialog> {
  final Set<String> _selectedChildren = {};

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Resolve Merge Conflicts'),
      content: SizedBox(
        width: double.maxFinite,
        height: 400,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Combining children from both terms (${widget.unionChildren.length} total):',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            const SizedBox(height: 16),
            Text(
              'Select up to 5 children to keep:',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 8),
            Expanded(
              child: ListView.builder(
                itemCount: widget.unionChildren.length,
                itemBuilder: (context, index) {
                  final child = widget.unionChildren[index];
                  final isSelected = _selectedChildren.contains(child);

                  return CheckboxListTile(
                    title: Text(child),
                    value: isSelected,
                    onChanged: (value) {
                      setState(() {
                        if (value == true) {
                          if (_selectedChildren.length < 5) {
                            _selectedChildren.add(child);
                          }
                        } else {
                          _selectedChildren.remove(child);
                        }
                      });
                    },
                  );
                },
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Selected: ${_selectedChildren.length}/5',
              style: TextStyle(
                color: _selectedChildren.length > 5 ? Colors.red : null,
              ),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        FilledButton(
          onPressed: _selectedChildren.isNotEmpty && _selectedChildren.length <= 5
              ? () => Navigator.of(context).pop(_selectedChildren.toList())
              : null,
          child: const Text('Apply'),
        ),
      ],
    );
  }
}
