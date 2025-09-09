import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../widgets/layout/scroll_scaffold.dart';
import '../../../widgets/app_back_leading.dart';
import '../data/materialization_service.dart';
import '../data/symptoms_models.dart';

class MaterializationScreen extends ConsumerStatefulWidget {
  const MaterializationScreen({super.key});

  @override
  ConsumerState<MaterializationScreen> createState() =>
      _MaterializationScreenState();
}

class _MaterializationScreenState extends ConsumerState<MaterializationScreen> {
  MaterializationStats? _stats;
  List<MaterializationHistoryItem> _history = [];
  bool _loading = false;
  bool _enforceFive = true;
  bool _safePrune = true;
  bool _showPreview = true;

  @override
  void initState() {
    super.initState();
    _loadStats();
    _loadHistory();
  }

  Future<void> _loadStats() async {
    try {
      final service = ref.read(materializationServiceProvider);
      final stats = await service.getMaterializationStats();
      if (mounted) {
        setState(() => _stats = stats);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load stats: $e')),
        );
      }
    }
  }

  Future<void> _loadHistory() async {
    try {
      final service = ref.read(materializationServiceProvider);
      final history = await service.getMaterializationHistory();
      if (mounted) {
        setState(() => _history = history);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load history: $e')),
        );
      }
    }
  }

  Future<void> _materializeAllIncomplete() async {
    setState(() => _loading = true);

    try {
      final service = ref.read(materializationServiceProvider);
      final result = await service.materializeAllIncomplete(
        enforceFive: _enforceFive,
        safePrune: _safePrune,
      );

      if (mounted) {
        _showResultDialog('Materialize All Incomplete', result);
        _loadStats();
        _loadHistory();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to materialize: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  Future<void> _undoLastMaterialization() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Undo Last Materialization'),
        content: const Text(
          'This will undo the last materialization operation. This action cannot be undone. Continue?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: TextButton.styleFrom(
              foregroundColor: Theme.of(context).colorScheme.error,
            ),
            child: const Text('Undo'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    try {
      final service = ref.read(materializationServiceProvider);
      await service.undoLastMaterialization();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Last materialization undone')),
        );
        _loadStats();
        _loadHistory();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to undo: $e')),
        );
      }
    }
  }

  void _showResultDialog(String title, MaterializationResult result) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildResultRow('Added', result.added, Colors.green),
              _buildResultRow('Filled', result.filled, Colors.blue),
              _buildResultRow('Pruned', result.pruned, Colors.orange),
              _buildResultRow('Kept', result.kept, Colors.grey),
              if (result.timestamp != null) ...[
                const SizedBox(height: 16),
                Text(
                  'Completed: ${result.timestamp!.toString().split('.')[0]}',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
              if (result.log != null && result.log!.isNotEmpty) ...[
                const SizedBox(height: 16),
                const Text('Log:',
                    style: TextStyle(fontWeight: FontWeight.bold)),
                Text(result.log!, style: const TextStyle(fontSize: 12)),
              ],
              if (result.details != null && result.details!.isNotEmpty) ...[
                const SizedBox(height: 16),
                const Text('Details:',
                    style: TextStyle(fontWeight: FontWeight.bold)),
                ...result.details!.map((detail) => Text(
                      '• $detail',
                      style: const TextStyle(fontSize: 12),
                    )),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  Widget _buildResultRow(String label, int value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(
            width: 60,
            child: Text(label,
                style: const TextStyle(fontWeight: FontWeight.bold)),
          ),
          Container(
            width: 24,
            height: 24,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Center(
              child: Text(
                value.toString(),
                style: TextStyle(
                  color: color,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsCard() {
    if (_stats == null) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Center(child: CircularProgressIndicator()),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Materialization Statistics',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'Total Operations',
                    _stats!.totalMaterializations.toString(),
                    Icons.build,
                    Colors.blue,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Total Added',
                    _stats!.totalAdded.toString(),
                    Icons.add_circle,
                    Colors.green,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'Total Filled',
                    _stats!.totalFilled.toString(),
                    Icons.edit,
                    Colors.blue,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Total Pruned',
                    _stats!.totalPruned.toString(),
                    Icons.remove_circle,
                    Colors.orange,
                  ),
                ),
              ],
            ),
            if (_stats!.lastMaterialization != null) ...[
              const SizedBox(height: 16),
              Text(
                'Last operation: ${_stats!.lastMaterialization!.toString().split('.')[0]}',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(
      String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Icon(icon, color: color),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            label,
            style: TextStyle(fontSize: 12, color: color),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryList() {
    if (_history.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Center(child: Text('No materialization history')),
        ),
      );
    }

    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              'Recent Operations',
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ),
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: _history.length,
            separatorBuilder: (_, __) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final item = _history[index];
              return ListTile(
                leading: const Icon(Icons.build),
                title: Text(item.operation),
                subtitle: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(item.timestamp.toString().split('.')[0]),
                    if (item.description != null)
                      Text(item.description!,
                          style: const TextStyle(fontSize: 12)),
                    Text(
                      'Added: ${item.result.added}, Filled: ${item.result.filled}, Pruned: ${item.result.pruned}',
                      style: const TextStyle(fontSize: 12),
                    ),
                  ],
                ),
                trailing: IconButton(
                  icon: const Icon(Icons.info_outline),
                  onPressed: () =>
                      _showResultDialog('Operation Details', item.result),
                  tooltip: 'View details',
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return ScrollScaffold(
      title: 'Materialization',
      leading: const AppBackLeading(),
      children: [
        // Statistics
        _buildStatsCard(),
        const SizedBox(height: 24),

        // Options
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Materialization Options',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 16),
                SwitchListTile(
                  title: const Text('Enforce 5 Children'),
                  subtitle:
                      const Text('Always ensure exactly 5 children per parent'),
                  value: _enforceFive,
                  onChanged: (value) => setState(() => _enforceFive = value),
                ),
                SwitchListTile(
                  title: const Text('Safe Prune'),
                  subtitle:
                      const Text('Only prune when deeper nodes are blank'),
                  value: _safePrune,
                  onChanged: (value) => setState(() => _safePrune = value),
                ),
                SwitchListTile(
                  title: const Text('Show Preview'),
                  subtitle: const Text('Preview changes before applying'),
                  value: _showPreview,
                  onChanged: (value) => setState(() => _showPreview = value),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 24),

        // Actions
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Actions',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: _loading ? null : _materializeAllIncomplete,
                        icon: _loading
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child:
                                    CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.build),
                        label: Text(_loading
                            ? 'Processing...'
                            : 'Materialize All Incomplete'),
                      ),
                    ),
                    const SizedBox(width: 16),
                    ElevatedButton.icon(
                      onPressed: _undoLastMaterialization,
                      icon: const Icon(Icons.undo),
                      label: const Text('Undo Last'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor:
                            Theme.of(context).colorScheme.secondary,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 24),

        // History
        _buildHistoryList(),
      ],
    );
  }
}
