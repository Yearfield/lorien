import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../widgets/layout/scroll_scaffold.dart';
import '../../../widgets/app_back_leading.dart';
import '../data/symptoms_repository.dart';

class SymptomsScreen extends ConsumerStatefulWidget {
  const SymptomsScreen({super.key});

  @override
  ConsumerState<SymptomsScreen> createState() => _SymptomsScreenState();
}

class _SymptomsScreenState extends ConsumerState<SymptomsScreen> {
  String? root, n1, n2, n3, n4, n5;
  List<String> optsRoot = [], opts1 = [], opts2 = [], opts3 = [], opts4 = [], opts5 = [];
  int remainingLeaves = 0;
  Map<String, dynamic>? leafPreview;
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _loadRoots();
  }

  Future<void> _loadRoots() async {
    final repo = ref.read(symptomsRepositoryProvider);
    try {
      setState(() => _loading = true);
      final roots = await repo.getRoots();
      if (mounted) {
        setState(() {
          optsRoot = roots;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _loading = false);
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed to load roots: $e')));
      }
    }
  }

  Future<void> _loadNext() async {
    final repo = ref.read(symptomsRepositoryProvider);
    try {
      setState(() => _loading = true);
      final options = await repo.getOptions(
        root: root, n1: n1, n2: n2, n3: n3, n4: n4
      );
      if (mounted) {
        setState(() {
          opts1 = List<String>.from(options["n1"] ?? opts1);
          opts2 = List<String>.from(options["n2"] ?? opts2);
          opts3 = List<String>.from(options["n3"] ?? opts3);
          opts4 = List<String>.from(options["n4"] ?? opts4);
          opts5 = List<String>.from(options["n5"] ?? opts5);
          remainingLeaves = options["remaining"] ?? 0;
          _loading = false;
        });
      }

      // Leaf preview
      if (n5 != null) {
        final leafId = options["leaf_id"];
        if (leafId != null) {
          final preview = await repo.getLeafPreview(leafId.toString());
          if (mounted) {
            setState(() => leafPreview = preview);
          }
        }
      } else {
        setState(() => leafPreview = null);
      }
    } catch (e) {
      if (mounted) {
        setState(() => _loading = false);
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed to load options: $e')));
      }
    }
  }

  void _resetFrom(int depth) {
    if (depth <= 1) { n1 = null; opts1 = []; }
    if (depth <= 2) { n2 = null; opts2 = []; }
    if (depth <= 3) { n3 = null; opts3 = []; }
    if (depth <= 4) { n4 = null; opts4 = []; }
    if (depth <= 5) { n5 = null; opts5 = []; }
    remainingLeaves = 0;
    leafPreview = null;
  }

  Future<void> _nextIncomplete() async {
    final repo = ref.read(symptomsRepositoryProvider);
    try {
      final data = await repo.nextIncompleteParent();
      if (data == null) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('All parents complete.')));
        }
        return;
      }
      final pid = data['parent_id'];
      // Deep-link to Editor route - for now show a dialog with details
      if (mounted) {
        showDialog(
          context: context,
          builder: (_) => AlertDialog(
            title: const Text('Next incomplete parent'),
            content: Text(
                'ID: $pid\nLabel: ${data['label']}\nMissing slots: ${data['missing_slots']}\nDepth: ${data['depth']}'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('OK'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed to find next incomplete: $e')));
      }
    }
  }

  Widget _dd(String label, String? v, List<String> opts, void Function(String?) onChanged) {
    return DropdownButtonFormField<String>(
      initialValue: v,
      decoration: InputDecoration(labelText: label),
      items: opts.map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(),
      onChanged: (val) {
        onChanged(val);
        _loadNext();
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return ScrollScaffold(
      title: 'Symptoms',
      leading: const AppBackLeading(),
      children: [
        if (_loading)
          const Center(child: CircularProgressIndicator())
        else ...[
          _dd('Vital Measurement', root, optsRoot, (v) {
            setState(() => root = v);
            _resetFrom(1);
          }),
          _dd('Node 1', n1, opts1, (v) {
            setState(() => n1 = v);
            _resetFrom(2);
          }),
          _dd('Node 2', n2, opts2, (v) {
            setState(() => n2 = v);
            _resetFrom(3);
          }),
          _dd('Node 3', n3, opts3, (v) {
            setState(() => n3 = v);
            _resetFrom(4);
          }),
          _dd('Node 4', n4, opts4, (v) {
            setState(() => n4 = v);
            _resetFrom(5);
          }),
          _dd('Node 5', n5, opts5, (v) {
            setState(() => n5 = v);
          }),
          const SizedBox(height: 8),
          Text('Remaining leaf options: $remainingLeaves'),
          if (leafPreview != null) ...[
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Outcomes (preview)',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    Text('Triage: ${leafPreview!["diagnostic_triage"] ?? ""}'),
                    Text('Actions: ${leafPreview!["actions"] ?? ""}'),
                  ],
                ),
              ),
            ),
          ],
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: _nextIncomplete,
            icon: const Icon(Icons.skip_next),
            label: const Text('Next Incomplete Parent'),
          ),
        ],
      ],
    );
  }
}
