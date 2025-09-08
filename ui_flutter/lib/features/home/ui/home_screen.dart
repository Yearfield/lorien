import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../features/tree/data/tree_api.dart';
import '../../../core/api_config.dart';
import '../../../features/workspace/calculator_screen.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Lorien - Decision Tree Platform'),
        actions: [
          IconButton(
            tooltip: 'Next incomplete parent',
            icon: const Icon(Icons.skip_next),
            onPressed: () async {
              final data = await ref.read(treeApiProvider).nextIncompleteParent();
              if (data == null) {
                ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('All parents complete.')));
                return;
              }
              // Deterministic display for now (we don't have a full tree editor screen here)
              showDialog(context: context, builder: (_) => AlertDialog(
                title: const Text('Next incomplete parent'),
                content: Text('ID: ${data['parent_id']}\nLabel: ${data['label']}\nMissing slots: ${data['missing_slots']}\nDepth: ${data['depth']}'),
                actions: [TextButton(onPressed: ()=>Navigator.pop(context), child: const Text('OK'))],
              ));
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: GridView.count(
          crossAxisCount: _getCrossAxisCount(context),
          crossAxisSpacing: 16,
          mainAxisSpacing: 16,
          children: [
            _NavigationTile(
              title: 'Calculator',
              icon: Icons.calculate,
              onTap: () => Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => CalculatorScreen(baseUrl: ApiConfig.baseUrl),
                ),
              ),
            ),
            _NavigationTile(
              title: 'Outcomes',
              icon: Icons.list_alt,
              onTap: () => context.go('/outcomes'),
            ),
            _NavigationTile(
              title: 'Flags',
              icon: Icons.flag,
              onTap: () => context.go('/flags'),
            ),
            _NavigationTile(
              title: 'Dictionary',
              icon: Icons.book,
              onTap: () => context.go('/dictionary'),
            ),
            _NavigationTile(
              title: 'Settings',
              icon: Icons.settings,
              onTap: () => context.go('/settings'),
            ),
            _NavigationTile(
              title: 'Workspace',
              icon: Icons.work,
              onTap: () => context.go('/workspace'),
            ),
            _NavigationTile(
              title: 'About',
              icon: Icons.info,
              onTap: () => context.go('/about'),
            ),
          ],
        ),
      ),
    );
  }

  int _getCrossAxisCount(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    if (width > 1200) return 3;
    if (width > 600) return 2;
    return 1;
  }
}

class _NavigationTile extends StatelessWidget {
  const _NavigationTile({
    required this.title,
    required this.icon,
    required this.onTap,
  });

  final String title;
  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon,
                  size: 48, color: Theme.of(context).colorScheme.primary),
              const SizedBox(height: 8),
              Text(
                title,
                style: Theme.of(context).textTheme.titleMedium,
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
