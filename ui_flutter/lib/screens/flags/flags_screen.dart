import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../state/flags_search_provider.dart';
import '../../widgets/layout/scroll_scaffold.dart';
import '../../widgets/app_back_leading.dart';

class FlagsScreen extends ConsumerWidget {
  const FlagsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final results = ref.watch(flagsResultsProvider);
    return ScrollScaffold(
      title: 'Flags',
      leading: const AppBackLeading(),
      children: [
        TextField(
          decoration: const InputDecoration(prefixIcon: Icon(Icons.search), hintText: 'Search flags'),
          onChanged: (q) => ref.read(flagsQueryProvider.notifier).state = q,
        ),
        const SizedBox(height: 16),
        results.when(
          data: (items) => items.isEmpty
              ? const Center(child: Padding(padding: EdgeInsets.all(24), child: Text('No flags found')))
              : Column(
                  children: [
                    for (final m in items)
                      ListTile(
                        title: Text('${m['code'] ?? m['id'] ?? 'flag'}'),
                        subtitle: Text('${m['label'] ?? ''}'),
                        trailing: IconButton(icon: const Icon(Icons.flag), onPressed: () {/* assign */}),
                      ),
                  ],
                ),
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, _) => Text('Failed to load flags: $e'),
        ),
      ],
      actions: [
        ElevatedButton.icon(onPressed: () {/* bulk assign flow */}, icon: const Icon(Icons.outbond), label: const Text('Assign Flags')),
      ],
    );
  }
}
