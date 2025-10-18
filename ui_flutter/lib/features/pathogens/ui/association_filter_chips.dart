import 'package:flutter/material.dart';
import 'package:lorien/features/pathogens/models/pathogen_models.dart';

class AssociationFilterChips extends StatelessWidget {
  final List<AssociationType> associationTypes;
  final String? selectedFilter;
  final ValueChanged<String?> onFilterChanged;
  final bool showOnlyWithAssociations;
  final ValueChanged<bool> onShowOnlyWithAssociationsChanged;

  const AssociationFilterChips({
    super.key,
    required this.associationTypes,
    required this.selectedFilter,
    required this.onFilterChanged,
    required this.showOnlyWithAssociations,
    required this.onShowOnlyWithAssociationsChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Show only with associations toggle
        Row(
          children: [
            Checkbox(
              value: showOnlyWithAssociations,
              onChanged: (value) => onShowOnlyWithAssociationsChanged(value ?? false),
            ),
            const Text('Show only pathogens with associations'),
          ],
        ),

        const SizedBox(height: 8),

        // Association type filters
        if (associationTypes.isNotEmpty) ...[
          const Text(
            'Filter by Association:',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 4,
            children: [
              // Clear filter chip
              FilterChip(
                label: const Text('All'),
                selected: selectedFilter == null,
                onSelected: (selected) {
                  if (selected) {
                    onFilterChanged(null);
                  }
                },
              ),
              // Association type chips
              ...associationTypes.take(10).map((type) => FilterChip(
                label: Text(type.name),
                selected: selectedFilter == type.name,
                onSelected: (selected) {
                  if (selected) {
                    onFilterChanged(type.name);
                  } else {
                    onFilterChanged(null);
                  }
                },
              )),
              // Show more indicator if there are many types
              if (associationTypes.length > 10)
                Chip(
                  label: Text('+${associationTypes.length - 10} more'),
                  backgroundColor: Colors.grey.shade200,
                ),
            ],
          ),
        ] else ...[
          const Text(
            'No association types available',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey,
              fontStyle: FontStyle.italic,
            ),
          ),
        ],
      ],
    );
  }
}
