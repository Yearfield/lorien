import 'package:flutter/material.dart';

class LabelChip extends StatelessWidget {
  final String label;
  final int slot;
  final int fromId;
  final bool isSelected;
  final bool isSynthetic;
  final VoidCallback onTap;

  const LabelChip({
    super.key,
    required this.label,
    required this.slot,
    required this.fromId,
    required this.isSelected,
    required this.isSynthetic,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final source = isSynthetic ? 'new' : 'from $fromId';
    
    return FilterChip(
      label: Text(
        'S${slot == -1 ? "-" : slot}: $label • $source',
        style: TextStyle(
          color: isSynthetic ? Colors.blue.shade700 : null,
        ),
      ),
      selected: isSelected,
      onSelected: (_) => onTap(),
      selectedColor: Theme.of(context).primaryColor.withOpacity(0.2),
      checkmarkColor: Theme.of(context).primaryColor,
    );
  }
}
