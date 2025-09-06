import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/services/health_service.dart';

class ConnectedBadge extends ConsumerWidget {
  const ConnectedBadge({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ok = ref.watch(connectedProvider);
    return Chip(
      label: Text(ok ? 'Connected' : 'Disconnected'),
      backgroundColor: ok
          ? Theme.of(context).colorScheme.secondaryContainer
          : Theme.of(context).colorScheme.errorContainer,
    );
  }
}

class LlmBadge extends ConsumerWidget {
  const LlmBadge({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final llmHealth = ref.watch(llmHealthProvider);

    if (llmHealth == null) {
      return Chip(
        label: const Text('LLM: Unknown'),
        backgroundColor: Theme.of(context).colorScheme.surfaceVariant,
      );
    }

    final ready = llmHealth['ready'] as bool? ?? false;
    final llmEnabled = llmHealth['llm_enabled'] as bool? ?? false;

    String label;
    Color backgroundColor;

    if (!llmEnabled) {
      label = 'LLM: Disabled';
      backgroundColor = Theme.of(context).colorScheme.surfaceVariant;
    } else if (ready) {
      label = 'LLM: Ready';
      backgroundColor = Theme.of(context).colorScheme.secondaryContainer;
    } else {
      label = 'LLM: Unavailable';
      backgroundColor = Theme.of(context).colorScheme.errorContainer;
    }

    return Chip(
      label: Text(label),
      backgroundColor: backgroundColor,
    );
  }
}
