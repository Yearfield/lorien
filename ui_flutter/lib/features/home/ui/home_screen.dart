import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Lorien - Decision Tree Platform'),
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
              onTap: () => context.go('/calculator'),
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
