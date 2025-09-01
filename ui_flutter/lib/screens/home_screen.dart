import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../state/app_settings_provider.dart';
import '../widgets/connection_banner.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectionStatus = ref.watch(connectionStatusProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Decision Tree Manager'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => context.go('/settings'),
          ),
        ],
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const ConnectionBanner(),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Connection Status Card
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Row(
                        children: [
                          _buildStatusIcon(connectionStatus),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Connection Status',
                                  style:
                                      Theme.of(context).textTheme.titleMedium,
                                ),
                                Text(
                                  _getStatusText(connectionStatus),
                                  style: Theme.of(context)
                                      .textTheme
                                      .bodyMedium
                                      ?.copyWith(
                                        color:
                                            _getStatusColor(connectionStatus),
                                      ),
                                ),
                              ],
                            ),
                          ),
                          if (connectionStatus == ConnectionStatus.disconnected)
                            ElevatedButton(
                              onPressed: () => context.go('/settings'),
                              child: const Text('Configure'),
                            ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Quick Actions
                  Text(
                    'Quick Actions',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 16),

                  Expanded(
                    child: GridView.count(
                      crossAxisCount: 2,
                      crossAxisSpacing: 16,
                      mainAxisSpacing: 16,
                      children: [
                        _buildActionCard(
                          context,
                          'Editor',
                          Icons.edit,
                          Colors.blue,
                          () => context.go('/editor'),
                          'Manage decision tree structure',
                        ),
                        _buildActionCard(
                          context,
                          'Red Flags',
                          Icons.flag,
                          Colors.red,
                          () => context.go('/flags'),
                          'Search and assign red flags',
                        ),
                        _buildActionCard(
                          context,
                          'Calculator',
                          Icons.calculate,
                          Colors.green,
                          () => context.go('/calculator'),
                          'Export CSV data',
                        ),
                        _buildActionCard(
                          context,
                          'Settings',
                          Icons.settings,
                          Colors.grey,
                          () => context.go('/settings'),
                          'Configure API and preferences',
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusIcon(ConnectionStatus status) {
    IconData icon;
    Color color;

    switch (status) {
      case ConnectionStatus.connected:
        icon = Icons.check_circle;
        color = Colors.green;
        break;
      case ConnectionStatus.disconnected:
        icon = Icons.error;
        color = Colors.red;
        break;
      case ConnectionStatus.error:
        icon = Icons.warning;
        color = Colors.orange;
        break;
      case ConnectionStatus.unknown:
        icon = Icons.help;
        color = Colors.grey;
        break;
    }

    return Icon(icon, color: color, size: 32);
  }

  String _getStatusText(ConnectionStatus status) {
    switch (status) {
      case ConnectionStatus.connected:
        return 'Connected to API';
      case ConnectionStatus.disconnected:
        return 'Unable to connect';
      case ConnectionStatus.error:
        return 'Connection error';
      case ConnectionStatus.unknown:
        return 'Checking connection...';
    }
  }

  Color _getStatusColor(ConnectionStatus status) {
    switch (status) {
      case ConnectionStatus.connected:
        return Colors.green;
      case ConnectionStatus.disconnected:
        return Colors.red;
      case ConnectionStatus.error:
        return Colors.orange;
      case ConnectionStatus.unknown:
        return Colors.grey;
    }
  }

  Widget _buildActionCard(
    BuildContext context,
    String title,
    IconData icon,
    Color color,
    VoidCallback onTap,
    String description,
  ) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 48,
                color: color,
              ),
              const SizedBox(height: 12),
              Text(
                title,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                description,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.grey[600],
                    ),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
