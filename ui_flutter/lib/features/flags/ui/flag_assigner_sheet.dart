import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/flags_api.dart';

class FlagAssignerSheet extends ConsumerStatefulWidget {
  const FlagAssignerSheet({super.key, this.onAssign});
  final void Function(int flagId, int nodeId, bool cascade)? onAssign;

  @override
  ConsumerState<FlagAssignerSheet> createState() => _S();
}

class _S extends ConsumerState<FlagAssignerSheet> {
  final _q = TextEditingController();
  final _nodeIdController = TextEditingController();
  final Set<int> _selectedFlagIds = {};
  bool _cascade = true;
  int _preview = 0;
  List<dynamic> _flags = [];
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _loadFlags();
  }

  Future<void> _loadFlags() async {
    setState(() => _loading = true);
    try {
      final api = ref.read(flagsApiProvider);
      final flags = await api.list(query: _q.text, limit: 50, offset: 0);
      setState(() {
        _flags = flags;
        _loading = false;
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

  List<dynamic> get _filteredFlags {
    if (_q.text.isEmpty) return _flags;
    return _flags.where((flag) {
      final label = (flag as Map<String, dynamic>)['label']?.toString() ?? '';
      return label.toLowerCase().contains(_q.text.toLowerCase());
    }).toList();
  }

  Future<void> _updatePreview() async {
    if (_selectedFlagIds.isEmpty || _nodeIdController.text.isEmpty) {
      setState(() => _preview = 0);
      return;
    }

    try {
      final api = ref.read(flagsApiProvider);
      final nodeId = int.tryParse(_nodeIdController.text);
      if (nodeId != null) {
        // For now, just estimate based on cascade
        setState(() => _preview = _selectedFlagIds.length * (_cascade ? 5 : 1));
      }
    } catch (e) {
      setState(() => _preview = 0);
    }
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      expand: false,
      builder: (_, ctrl) => Padding(
        padding: const EdgeInsets.all(16),
        child: ListView(
          controller: ctrl,
          children: [
            TextField(
              controller: _nodeIdController,
              decoration: const InputDecoration(labelText: 'Node ID'),
              keyboardType: TextInputType.number,
              onChanged: (_) => _updatePreview(),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _q,
              decoration: const InputDecoration(labelText: 'Search flags'),
              onChanged: (_) {
                setState(() {});
                _loadFlags();
              },
            ),
            const SizedBox(height: 16),
            SwitchListTile(
                value: _cascade,
                onChanged: (v) {
                  setState(() => _cascade = v);
                  _updatePreview();
                },
                title: Text('Cascade to branch (preview: $_preview)')),
            const SizedBox(height: 16),
            const Text('Select flags:',
                style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            if (_loading)
              const Center(child: CircularProgressIndicator())
            else if (_filteredFlags.isEmpty)
              const Text('No flags found')
            else
              ...(_filteredFlags.map((flag) {
                final flagMap = flag as Map<String, dynamic>;
                final flagId = flagMap['id'] as int? ?? 0;
                final label = flagMap['label']?.toString() ?? 'Unknown Flag';
                return CheckboxListTile(
                  title: Text(label),
                  value: _selectedFlagIds.contains(flagId),
                  onChanged: (bool? value) {
                    setState(() {
                      if (value == true) {
                        _selectedFlagIds.add(flagId);
                      } else {
                        _selectedFlagIds.remove(flagId);
                      }
                    });
                    _updatePreview();
                  },
                );
              })),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => Navigator.pop(context),
                    child: const Text('Cancel'),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: FilledButton(
                      onPressed: (_selectedFlagIds.isNotEmpty &&
                              _nodeIdController.text.isNotEmpty)
                          ? () {
                              final nodeId =
                                  int.tryParse(_nodeIdController.text);
                              if (nodeId != null &&
                                  _selectedFlagIds.isNotEmpty) {
                                widget.onAssign?.call(
                                    _selectedFlagIds.first, nodeId, _cascade);
                              }
                              Navigator.pop(context);
                            }
                          : null,
                      child: const Text('Assign')),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
