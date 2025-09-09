import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'flag_assigner_sheet.dart';
import '../../../widgets/layout/scroll_scaffold.dart';
import '../../../widgets/app_back_leading.dart';
import '../../../data/api_client.dart';
import '../data/flags_api.dart';

class FlagsScreen extends ConsumerStatefulWidget {
  const FlagsScreen({super.key});

  @override
  ConsumerState<FlagsScreen> createState() => _FlagsScreenState();
}

class _FlagsScreenState extends ConsumerState<FlagsScreen> {
  final _searchController = TextEditingController();
  List<dynamic> _flags = [];
  bool _loading = false;
  String _query = '';
  final int _limit = 20;
  int _offset = 0;
  int _total = 0;
  String? _lastAffected;
  bool _bulkMode = false;
  final Set<String> _selectedSymptoms = {};

  @override
  void initState() {
    super.initState();
    _loadFlags();
  }

  Future<void> _loadFlags() async {
    setState(() => _loading = true);
    try {
      final api = ref.read(flagsApiProvider);
      final flags =
          await api.list(query: _query, limit: _limit, offset: _offset);
      setState(() {
        _flags = flags;
        _loading = false;
        // Assume total count from response if available, otherwise estimate
        _total = flags.length >= _limit
            ? (_offset + _limit + 1).toInt()
            : (_offset + flags.length).toInt();
      });
    } catch (e) {
      setState(() => _loading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load flags: $e')),
        );
      }
    }
  }

  void _search(String value) {
    setState(() {
      _query = value;
      _offset = 0; // Reset to first page
    });
    _loadFlags();
  }

  void _toggleBulkMode() {
    setState(() {
      _bulkMode = !_bulkMode;
      if (!_bulkMode) {
        _selectedSymptoms.clear();
      }
    });
  }

  void _showBulkAssignDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Assign Flag to Selected Symptoms'),
        content:
            const Text('Choose a flag to assign to all selected symptoms.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              // For demo purposes, use a hardcoded flag code
              // In a real app, this would show a flag picker
              _bulkAssign(_selectedSymptoms, 'red_flag');
            },
            child: const Text('Assign Flag'),
          ),
        ],
      ),
    );
  }

  void _nextPage() {
    if (_offset + _limit < _total) {
      setState(() => _offset += _limit);
      _loadFlags();
    }
  }

  void _prevPage() {
    if (_offset > 0) {
      setState(
          () => _offset = (_offset - _limit).clamp(0, double.infinity).toInt());
      _loadFlags();
    }
  }

  @override
  Widget build(BuildContext context) {
    final start = _offset + 1;
    final end = (_offset + _flags.length).clamp(0, _total);
    final showingText =
        _total > 0 ? 'Showing $start–$end of $_total' : 'No flags found';

    return ScrollScaffold(
      title: 'Flags',
      leading: const AppBackLeading(),
      actions: [
        if (_bulkMode && _selectedSymptoms.isNotEmpty) ...[
          ElevatedButton.icon(
            onPressed: () => _showBulkAssignDialog(),
            icon: const Icon(Icons.flag),
            label: Text('Assign to ${_selectedSymptoms.length} Selected'),
          ),
          const SizedBox(width: 8),
        ],
        OutlinedButton.icon(
          onPressed: _toggleBulkMode,
          icon:
              Icon(_bulkMode ? Icons.check_box_outline_blank : Icons.check_box),
          label: Text(_bulkMode ? 'Cancel Bulk' : 'Bulk Select'),
        ),
        if (!_bulkMode) ...[
          const SizedBox(width: 8),
          ElevatedButton.icon(
            onPressed: () {
              showModalBottomSheet(
                context: context,
                isScrollControlled: true,
                builder: (context) => FlagAssignerSheet(
                  onAssign: (flagId, nodeId, cascade) =>
                      _assignFlag(flagId, nodeId, cascade),
                ),
              );
            },
            icon: const Icon(Icons.flag),
            label: const Text('Assign Single'),
          ),
        ],
      ],
      children: [
        TextField(
          controller: _searchController,
          decoration: const InputDecoration(
            labelText: 'Search flags',
            prefixIcon: Icon(Icons.search),
          ),
          onChanged: _search,
        ),
        if (_lastAffected != null) ...[
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(8),
            color: Theme.of(context).colorScheme.primaryContainer,
            child: Row(
              children: [
                Icon(Icons.info, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: 8),
                Text(_lastAffected!,
                    style: const TextStyle(fontWeight: FontWeight.bold)),
              ],
            ),
          ),
        ],
        const SizedBox(height: 16),
        Row(
          children: [
            Text(showingText, style: Theme.of(context).textTheme.bodySmall),
            const Spacer(),
            if (_flags.isNotEmpty) ...[
              IconButton(
                onPressed: _offset > 0 ? _prevPage : null,
                icon: const Icon(Icons.chevron_left),
                tooltip: 'Previous page',
              ),
              IconButton(
                onPressed: _offset + _limit < _total ? _nextPage : null,
                icon: const Icon(Icons.chevron_right),
                tooltip: 'Next page',
              ),
            ],
          ],
        ),
        const SizedBox(height: 16),
        if (_loading)
          const Center(child: CircularProgressIndicator())
        else if (_flags.isEmpty && !_loading)
          const Center(child: Text('No flags found'))
        else
          ..._flags.map((flag) {
            final flagMap = flag as Map<String, dynamic>;
            final symptomId =
                (flagMap['id'] ?? _flags.indexOf(flag)).toString();
            return _FlagListItem(
              id: flagMap['id'] ?? _flags.indexOf(flag),
              label: flagMap['label'] ?? 'Unknown Flag',
              onAudit: _bulkMode
                  ? null
                  : () => _showAudit(flagMap['id'] ?? _flags.indexOf(flag)),
              bulkMode: _bulkMode,
              isSelected: _selectedSymptoms.contains(symptomId),
              onSelectionChanged: _bulkMode
                  ? (selected) {
                      setState(() {
                        if (selected) {
                          _selectedSymptoms.add(symptomId);
                        } else {
                          _selectedSymptoms.remove(symptomId);
                        }
                      });
                    }
                  : null,
            );
          }),
      ],
    );
  }

  Future<void> _assignFlag(int flagId, int nodeId, bool cascade) async {
    try {
      final api = ref.read(flagsApiProvider);
      final result =
          await api.assign(nodeId: nodeId, flagId: flagId, cascade: cascade);
      final affected = result['affected'] ?? 0;
      setState(() => _lastAffected = 'Assigned flag to $affected nodes');

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Affected: $affected')),
        );
      }

      _loadFlags(); // Refresh the list
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to assign flag: $e')),
        );
      }
    }
  }

  Future<void> _bulkAssign(Set<String> symptomIds, String flagCode) async {
    if (symptomIds.isEmpty) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Please select at least one symptom')),
        );
      }
      return;
    }

    try {
      setState(() => _loading = true);

      // Use the ApiClient singleton for bulk assignment
      await ApiClient.I().postJson('flags/assign/bulk', body: {
        'symptom_ids': symptomIds.toList(),
        'flag_code': flagCode,
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
              content: Text(
                  'Successfully assigned flag to ${symptomIds.length} symptoms')),
        );
      }

      // Refresh the list
      await _loadFlags();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to assign flags: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  Future<void> _showAudit(int flagId) async {
    try {
      final api = ref.read(flagsApiProvider);
      final auditData = await api.audit(nodeId: flagId);

      if (mounted) {
        showDialog(
          context: context,
          builder: (_) => AlertDialog(
            title: const Text('Flag Audit'),
            content: SizedBox(
              width: double.maxFinite,
              child: auditData.isEmpty
                  ? const Text('No audit data available')
                  : ListView.builder(
                      shrinkWrap: true,
                      itemCount: auditData.length,
                      itemBuilder: (context, index) {
                        final item = auditData[index] as Map<String, dynamic>;
                        return ListTile(
                          title: Text(item['action'] ?? 'Unknown action'),
                          subtitle: Text(
                              'At: ${item['timestamp'] ?? 'Unknown time'}'),
                          trailing: Text(item['details'] ?? ''),
                        );
                      },
                    ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Close'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load audit: $e')),
        );
      }
    }
  }
}

class _FlagListItem extends StatelessWidget {
  const _FlagListItem({
    required this.id,
    required this.label,
    this.onAudit,
    this.bulkMode = false,
    this.isSelected = false,
    this.onSelectionChanged,
  });

  final int id;
  final String label;
  final VoidCallback? onAudit;
  final bool bulkMode;
  final bool isSelected;
  final ValueChanged<bool>? onSelectionChanged;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: ListTile(
        leading: bulkMode
            ? Checkbox(
                value: isSelected,
                onChanged: (value) => onSelectionChanged?.call(value ?? false),
              )
            : null,
        title: Text(label),
        subtitle: Text('ID: $id'),
        trailing: !bulkMode && onAudit != null
            ? IconButton(
                icon: const Icon(Icons.history),
                tooltip: 'View audit',
                onPressed: onAudit,
              )
            : null,
        onTap: bulkMode ? () => onSelectionChanged?.call(!isSelected) : null,
      ),
    );
  }
}
