import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/warhammer_models.dart';
import '../state/warhammer_notifier.dart';

class SynonymSelectionDialog extends ConsumerStatefulWidget {
  final String warhammerSymptom;
  final List<String> decisionTreeSymptoms;

  const SynonymSelectionDialog({
    super.key,
    required this.warhammerSymptom,
    required this.decisionTreeSymptoms,
  });

  @override
  ConsumerState<SynonymSelectionDialog> createState() => _SynonymSelectionDialogState();
}

class _SynonymSelectionDialogState extends ConsumerState<SynonymSelectionDialog> {
  String? selectedSymptom;
  bool isCreating = false;

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Create Synonym Mapping'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Map "${widget.warhammerSymptom}" to a decision tree symptom:',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.blue.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.blue.withOpacity(0.3)),
            ),
            child: Row(
              children: [
                Icon(Icons.medical_services, color: Colors.blue),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    widget.warhammerSymptom,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Select decision tree symptom:',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Container(
            constraints: const BoxConstraints(maxHeight: 300),
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: widget.decisionTreeSymptoms.length,
              itemBuilder: (context, index) {
                final symptom = widget.decisionTreeSymptoms[index];
                final isSelected = selectedSymptom == symptom;

                return ListTile(
                  title: Text(symptom),
                  leading: Radio<String>(
                    value: symptom,
                    groupValue: selectedSymptom,
                    onChanged: (value) {
                      setState(() {
                        selectedSymptom = value;
                      });
                    },
                  ),
                  selected: isSelected,
                  selectedTileColor: Colors.blue.withOpacity(0.1),
                );
              },
            ),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: isCreating ? null : () {
            Navigator.of(context).pop();
          },
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: (selectedSymptom != null && !isCreating) ? _createSynonym : null,
          child: isCreating
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Create Mapping'),
        ),
      ],
    );
  }

  Future<void> _createSynonym() async {
    if (selectedSymptom == null) return;

    setState(() {
      isCreating = true;
    });

    try {
      await ref.read(warhammerNotifierProvider.notifier).createSynonym(
        widget.warhammerSymptom,
        selectedSymptom!,
      );

      if (mounted) {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Synonym mapping created: "${widget.warhammerSymptom}" → "$selectedSymptom"',
            ),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to create synonym: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          isCreating = false;
        });
      }
    }
  }
}
