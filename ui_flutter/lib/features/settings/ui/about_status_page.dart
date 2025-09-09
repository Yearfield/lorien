import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/services/health_service.dart';
import '../../../shared/widgets/app_scaffold.dart';

class AboutStatusPage extends ConsumerWidget {
  const AboutStatusPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final base = ref.watch(baseUrlProvider);
    final last = ref.watch(lastPingProvider);
    final connected = ref.watch(connectedProvider);

    // Trigger health check to get version/db/features info
    ref.watch(healthServiceProvider);

    return AppScaffold(
      title: 'About / Status',
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Base URL: $base'),
            Text('Last ping: ${last ?? '-'}'),
            Text('Connected: $connected'),
            const SizedBox(height: 12),
            const Text('Contracts:',
                style: TextStyle(fontWeight: FontWeight.bold)),
            const Text('• 5 children exactly'),
            const Text('• 8-column export header'),
            const Text('• /health is SoT'),
            const Text('• Outcomes ≤7 words, regex allowed'),
            const Text('• LLM OFF by default'),
            const SizedBox(height: 12),
            // TODO: Display version, WAL, FK, LLM enabled from health result
            const Text('Backend Info:',
                style: TextStyle(fontWeight: FontWeight.bold)),
            const Text('• Version: (from /health)'),
            const Text('• WAL: (from /health)'),
            const Text('• Foreign Keys: (from /health)'),
            const Text('• LLM Enabled: (from /health)'),
          ],
        ),
      ),
    );
  }
}
