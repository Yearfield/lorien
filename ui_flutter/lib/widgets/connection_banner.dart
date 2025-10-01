import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/health_state.dart';

class ConnectionBanner extends StatelessWidget {
  const ConnectionBanner({super.key});

  @override
  Widget build(BuildContext context) {
    final health = context.watch<HealthState>();
    if (health.online) return const SizedBox.shrink();
    return MaterialBanner(
      backgroundColor: Colors.red.shade50,
      content: const Text('Disconnected from API. Some actions are disabled.',
          style: TextStyle(color: Colors.red)),
      actions: [
        TextButton(
          onPressed: () => context.read<HealthState>().check(),
          child: const Text('Retry'),
        ),
      ],
    );
  }
}
