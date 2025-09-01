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
