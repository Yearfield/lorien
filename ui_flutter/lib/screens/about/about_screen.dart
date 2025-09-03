import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/api_client.dart';
import '../../state/health_provider.dart';
import '../../widgets/layout/scroll_scaffold.dart';
import '../../widgets/app_back_leading.dart';

class AboutScreen extends ConsumerWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final baseUrl = ApiClient.I().baseUrl;
    final health = ref.watch(healthControllerProvider).valueOrNull;
    final last = health?.lastPing;

    return ScrollScaffold(
      title: 'About / Status',
      leading: const AppBackLeading(),
      children: [
        ListTile(
          title: const Text('API Base URL'),
          subtitle: Text(baseUrl),
          leading: const Icon(Icons.link),
        ),
        if (last != null)
          ListTile(
            title: const Text('Last Ping'),
            subtitle: Text(last.toLocal().toString()),
            leading: const Icon(Icons.access_time),
          ),
        if (health != null) ...[
          ListTile(
            title: const Text('API Status'),
            subtitle: Text('OK: ${health.ok} • Version: ${health.version}'),
            leading: Icon(
              health.ok ? Icons.check_circle : Icons.error,
              color: health.ok ? Colors.green : Colors.red,
            ),
          ),
          ListTile(
            title: const Text('Database'),
            subtitle: Text('${health.db.path} • WAL: ${health.db.wal ? 'ON' : 'OFF'} • FK: ${health.db.foreignKeys ? 'ON' : 'OFF'}'),
            leading: const Icon(Icons.storage),
          ),
          ListTile(
            title: const Text('Features'),
            subtitle: Text('LLM: ${health.features.llm ? 'ENABLED' : 'DISABLED'}'),
            leading: const Icon(Icons.settings),
          ),
        ],
        const SizedBox(height: 24),
        const Text(
          'App Information',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        const ListTile(
          title: Text('Decision Tree Manager'),
          subtitle: Text('Cross-platform decision tree tooling platform'),
          leading: Icon(Icons.account_tree),
        ),
        const ListTile(
          title: Text('Flutter Version'),
          subtitle: Text('3.35.2'),
          leading: Icon(Icons.flutter_dash),
        ),
      ],
      actions: [
        OutlinedButton(
          onPressed: () => ref.read(healthControllerProvider.notifier).ping(),
          child: const Text('Ping API'),
        ),
      ],
    );
  }
}
