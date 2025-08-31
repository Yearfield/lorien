import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../widgets/export_buttons.dart';
import '../state/app_settings_provider.dart';
import '../state/repository_providers.dart';

class WorkspaceScreen extends ConsumerWidget {
  const WorkspaceScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(appSettingsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Workspace'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/'),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Health Check Section
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.health_and_safety, color: Colors.green),
                          const SizedBox(width: 8),
                          Text(
                            'System Health',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      
                      Consumer(
                        builder: (context, ref, child) {
                          final healthAsync = ref.watch(healthProvider);
                          
                          return healthAsync.when(
                            data: (health) {
                              return Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  _buildHealthRow('Status', health['ok'] == true ? 'Healthy' : 'Unhealthy'),
                                  _buildHealthRow('Version', health['version'] ?? 'Unknown'),
                                  _buildHealthRow('Database', health['db']?['path'] ?? 'Unknown'),
                                  _buildHealthRow('WAL Mode', health['db']?['wal'] == true ? 'Enabled' : 'Disabled'),
                                  _buildHealthRow('Foreign Keys', health['db']?['foreign_keys'] == true ? 'Enabled' : 'Disabled'),
                                  _buildHealthRow('LLM Feature', health['features']?['llm'] == true ? 'Enabled' : 'Disabled'),
                                ],
                              );
                            },
                            loading: () => const Center(
                              child: Padding(
                                padding: EdgeInsets.all(16),
                                child: CircularProgressIndicator(),
                              ),
                            ),
                            error: (error, stack) => Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.red[50],
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.red[200]!),
                              ),
                              child: Row(
                                children: [
                                  Icon(Icons.error, color: Colors.red[600]),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      'Health check failed: $error',
                                      style: TextStyle(color: Colors.red[800]),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 24),
              
              // Export Section
              if (settings.apiBaseUrl.isNotEmpty) ...[
                ExportButtons(baseUrl: settings.apiBaseUrl),
              ] else ...[
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.warning, color: Colors.orange[600]),
                            const SizedBox(width: 8),
                            Text(
                              'Export Unavailable',
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                color: Colors.orange[800],
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Please set the API base URL in Settings to enable export functionality.',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: Colors.orange[700],
                          ),
                        ),
                        const SizedBox(height: 12),
                        ElevatedButton.icon(
                          onPressed: () => context.go('/settings'),
                          icon: const Icon(Icons.settings),
                          label: const Text('Go to Settings'),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
              
              const SizedBox(height: 24),
              
              // Quick Actions Section
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.flash_on, color: Colors.blue),
                          const SizedBox(width: 8),
                          Text(
                            'Quick Actions',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: () => context.go('/calculator'),
                              icon: const Icon(Icons.calculate),
                              label: const Text('Calculator'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.blue,
                                foregroundColor: Colors.white,
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: () => context.go('/editor'),
                              icon: const Icon(Icons.edit),
                              label: const Text('Editor'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.green,
                                foregroundColor: Colors.white,
                              ),
                            ),
                          ),
                        ],
                      ),
                      
                      const SizedBox(height: 12),
                      
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: () => context.go('/flags'),
                              icon: const Icon(Icons.flag),
                              label: const Text('Flags'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.orange,
                                foregroundColor: Colors.white,
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: () => context.go('/settings'),
                              icon: const Icon(Icons.settings),
                              label: const Text('Settings'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.purple,
                                foregroundColor: Colors.white,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHealthRow(String label, String value) {
    final isHealthy = value == 'Healthy' || value == 'Enabled';
    
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Text(
            '$label:',
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
          const SizedBox(width: 8),
          Icon(
            isHealthy ? Icons.check_circle : Icons.error,
            color: isHealthy ? Colors.green : Colors.red,
            size: 16,
          ),
          const SizedBox(width: 4),
          Text(value),
        ],
      ),
    );
  }
}
