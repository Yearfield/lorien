import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../state/health_provider.dart';

class ConnectionBanner extends ConsumerWidget {
  const ConnectionBanner({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final health = ref.watch(healthControllerProvider);
    final busy = health.isLoading;
    final data = health.valueOrNull;
    final ok = data?.ok;
    final version = data?.version ?? '?';
    final color = ok == true ? Colors.green : (ok == false ? Colors.red : Colors.orange);
    final label = ok == true ? 'API OK' : (ok == false ? 'API DOWN' : 'CHECKING…');
    
    return Material(
      color: color.withOpacity(0.12),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        child: Row(
          children: [
            Icon(ok == true ? Icons.check_circle : Icons.warning, color: color),
            const SizedBox(width: 8),
            Text('$label · v$version', style: TextStyle(color: color, fontWeight: FontWeight.w600)),
            const Spacer(),
            TextButton(
              onPressed: busy ? null : () => ref.read(healthControllerProvider.notifier).ping(),
              child: busy
                  ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }
}
