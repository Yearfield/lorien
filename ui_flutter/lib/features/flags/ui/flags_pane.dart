import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../state/health_provider.dart';
import '../../../data/dto/health_dto.dart';

class FlagsPane extends ConsumerWidget {
  const FlagsPane({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final healthState = ref.watch(healthStateProvider);
    final healthNotifier = ref.read(healthStateProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('System Status & Flags'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: healthState.isRefreshing ? null : () {
              healthNotifier.refreshHealthStatus();
            },
            tooltip: 'Refresh Status',
          ),
        ],
      ),
      body: healthState.isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: () => healthNotifier.refreshHealthStatus(),
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildSystemStatusCard(context, healthState),
                    const SizedBox(height: 16),
                    _buildDatabaseInfoCard(context, healthState),
                    const SizedBox(height: 16),
                    _buildFeatureFlagsCard(context, healthState),
                    const SizedBox(height: 16),
                    _buildConnectionTestCard(context, healthState, healthNotifier),
                    if (healthState.hasError) ...[
                      const SizedBox(height: 16),
                      _buildErrorCard(context, healthState),
                    ],
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildSystemStatusCard(BuildContext context, HealthState healthState) {
    final healthResponse = healthState.healthResponse;
    final statusColor = _getStatusColor(healthResponse?.status);
    final statusIcon = _getStatusIcon(healthResponse?.status);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(statusIcon, color: statusColor, size: 24),
                const SizedBox(width: 8),
                Text(
                  'System Status',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),
            const SizedBox(height: 12),
            _buildInfoRow('Overall Status', healthResponse?.status ?? 'Unknown', statusColor),
            _buildInfoRow('API Version', healthResponse?.version ?? 'Unknown'),
            if (healthState.lastChecked != null)
              _buildInfoRow('Last Checked', _formatDateTime(healthState.lastChecked!)),
          ],
        ),
      ),
    );
  }

  Widget _buildDatabaseInfoCard(BuildContext context, HealthState healthState) {
    final dbInfo = healthState.healthResponse?.db;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  dbInfo?.isHealthy == true ? Icons.storage : Icons.error,
                  color: dbInfo?.isHealthy == true ? Colors.green : Colors.red,
                  size: 24,
                ),
                const SizedBox(width: 8),
                Text(
                  'Database Information',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (dbInfo?.path != null)
              _buildInfoRow('Database Path', dbInfo!.path!),
            _buildInfoRow('Journal Mode', dbInfo?.journalMode ?? 'Unknown'),
            _buildInfoRow('Tables', dbInfo?.tables.toString() ?? '0'),
            _buildInfoRow('Nodes', dbInfo?.nodes.toString() ?? '0'),
            _buildInfoRow('Objects', dbInfo?.objects.toString() ?? '0'),
            _buildInfoRow(
              'Integrity',
              dbInfo?.integrity ?? 'Unknown',
              dbInfo?.isHealthy == true ? Colors.green : Colors.red,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureFlagsCard(BuildContext context, HealthState healthState) {
    final features = healthState.healthResponse?.features ?? {};

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.flag, color: Colors.blue, size: 24),
                const SizedBox(width: 8),
                Text(
                  'Feature Flags',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),
            const SizedBox(height: 12),
            _buildFeatureFlagRow('LLM Integration', features['llm'] ?? false),
            _buildFeatureFlagRow('Analytics', features['analytics'] ?? false),
            if (features.isEmpty)
              const Text(
                'No feature flags available',
                style: TextStyle(color: Colors.grey),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildConnectionTestCard(
    BuildContext context,
    HealthState healthState,
    HealthStateNotifier healthNotifier,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  healthState.isOnline ? Icons.wifi : Icons.wifi_off,
                  color: healthState.isOnline ? Colors.green : Colors.red,
                  size: 24,
                ),
                const SizedBox(width: 8),
                Text(
                  'Connection Status',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),
            const SizedBox(height: 12),
            _buildInfoRow(
              'API Connection',
              healthState.isOnline ? 'Connected' : 'Disconnected',
              healthState.isOnline ? Colors.green : Colors.red,
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: healthState.isRefreshing
                    ? null
                    : () => healthNotifier.refreshHealthStatus(),
                icon: healthState.isRefreshing
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.network_check),
                label: Text(healthState.isRefreshing ? 'Testing...' : 'Test Connection'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorCard(BuildContext context, HealthState healthState) {
    return Card(
      color: Colors.red.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.error, color: Colors.red, size: 24),
                const SizedBox(width: 8),
                Text(
                  'Error',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: Colors.red,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              healthState.error ?? 'Unknown error occurred',
              style: const TextStyle(color: Colors.red),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value, [Color? valueColor]) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(
                color: valueColor,
                fontWeight: valueColor != null ? FontWeight.w600 : null,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeatureFlagRow(String label, bool enabled) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        children: [
          SizedBox(
            width: 120,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: enabled ? Colors.green.shade100 : Colors.red.shade100,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              enabled ? 'Enabled' : 'Disabled',
              style: TextStyle(
                color: enabled ? Colors.green.shade800 : Colors.red.shade800,
                fontWeight: FontWeight.w600,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _getStatusColor(String? status) {
    switch (status?.toLowerCase()) {
      case 'ok':
        return Colors.green;
      case 'degraded':
        return Colors.orange;
      case 'error':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _getStatusIcon(String? status) {
    switch (status?.toLowerCase()) {
      case 'ok':
        return Icons.check_circle;
      case 'degraded':
        return Icons.warning;
      case 'error':
        return Icons.error;
      default:
        return Icons.help;
    }
  }

  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.hour.toString().padLeft(2, '0')}:'
        '${dateTime.minute.toString().padLeft(2, '0')}:'
        '${dateTime.second.toString().padLeft(2, '0')}';
  }
}
