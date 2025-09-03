import 'package:flutter/material.dart';

class FormBanner extends StatelessWidget {
  const FormBanner(this.message, {super.key, this.type = BannerType.error});

  final String? message;
  final BannerType type;

  @override
  Widget build(BuildContext context) {
    if (message == null || message!.isEmpty) return const SizedBox.shrink();

    final color = type == BannerType.error
        ? Theme.of(context).colorScheme.errorContainer
        : Theme.of(context).colorScheme.secondaryContainer;

    final textColor = type == BannerType.error
        ? Theme.of(context).colorScheme.onErrorContainer
        : Theme.of(context).colorScheme.onSecondaryContainer;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          Icon(
            type == BannerType.error ? Icons.error_outline : Icons.info_outline,
            color: textColor,
            size: 20,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              message!,
              style: TextStyle(color: textColor),
            ),
          ),
        ],
      ),
    );
  }
}

enum BannerType { error, info }
