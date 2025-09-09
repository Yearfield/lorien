import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:dio/dio.dart';
import '../../providers/settings_provider.dart';
import '../../data/triage_repository.dart';
import '../../models/triage_models.dart';
import '../../services/telemetry_client.dart';

class OutcomesDetailScreen extends StatefulWidget {
  final int nodeId;
  final bool llmEnabled;
  const OutcomesDetailScreen(
      {super.key, required this.nodeId, required this.llmEnabled});
  @override
  State<OutcomesDetailScreen> createState() => _OutcomesDetailScreenState();
}

class _OutcomesDetailScreenState extends State<OutcomesDetailScreen> {
  late TriageRepository _repo;
  late TelemetryClient _telemetry;
  final _triageCtrl = TextEditingController();
  final _actionsCtrl = TextEditingController();
  bool _loading = true, _saving = false, _isLeaf = true;
  static const int triageMax = 7; // word limit
  static const int actionsMax = 7; // word limit

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final base = context.read<SettingsProvider>().baseUrl;
    final dio = Dio();
    _repo = TriageRepository(dio: dio, baseUrl: base);
    _telemetry = TelemetryClient(
        dio: dio,
        baseUrl: base,
        enabled: const String.fromEnvironment('ANALYTICS_ENABLED',
                defaultValue: 'false') ==
            'true');
    _load();
  }

  Future<void> _load() async {
    try {
      final d = await _repo.getLeaf(widget.nodeId);
      setState(() {
        _triageCtrl.text = d.diagnosticTriage;
        _actionsCtrl.text = d.actions;
        _isLeaf = d.isLeaf;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _loading = false);
      _showError('Load failed', e);
    }
  }

  void _showError(String title, Object e) {
    ScaffoldMessenger.of(context)
        .showSnackBar(SnackBar(content: Text('$title: $e')));
  }

  bool _validateLocal() {
    final t = _triageCtrl.text.trim(), a = _actionsCtrl.text.trim();
    final tWords =
        t.split(RegExp(r'\s+')).where((word) => word.isNotEmpty).length;
    final aWords =
        a.split(RegExp(r'\s+')).where((word) => word.isNotEmpty).length;

    if (tWords > triageMax || aWords > actionsMax) {
      _showError('Text too long',
          'Please keep under $triageMax words for triage and $actionsMax for actions');
      return false;
    }
    // Basic prohibited terms sample; mirror server where possible
    const bad = ['dose', 'dosage', 'mg/', 'tablet'];
    if (bad.any(
        (w) => t.toLowerCase().contains(w) || a.toLowerCase().contains(w))) {
      _showError('Prohibited content', 'No dosing/diagnosis content allowed');
      return false;
    }
    return true;
  }

  Future<void> _save() async {
    if (!_isLeaf) {
      _showError('Not a leaf', 'This node is not a leaf');
      return;
    }
    if (!_validateLocal()) return;
    final prevT = _triageCtrl.text, prevA = _actionsCtrl.text;
    setState(() => _saving = true);
    try {
      await _repo.saveLeaf(widget.nodeId, prevT, prevA);
      _telemetry.event('outcomes_save_success');
      if (!mounted) return;
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Saved ✓')));
    } catch (e) {
      _telemetry.event('outcomes_save_error');
      if (e is DioException && e.response?.statusCode == 422) {
        final data = e.response?.data;
        // Case 1: Pydantic detail array for body validation
        if (data is Map && data['detail'] is List) {
          final List det = data['detail'];
          String? triageMsg, actionsMsg;
          for (final d in det) {
            final loc = (d['loc'] ?? []) as List;
            if (loc.isNotEmpty && loc.last == 'diagnostic_triage') {
              triageMsg = d['msg']?.toString();
            }
            if (loc.isNotEmpty && loc.last == 'actions') {
              actionsMsg = d['msg']?.toString();
            }
          }
          if (triageMsg != null) {
            ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Diagnostic Triage: $triageMsg')));
          }
          if (actionsMsg != null) {
            ScaffoldMessenger.of(context)
                .showSnackBar(SnackBar(content: Text('Actions: $actionsMsg')));
          }
        } else if (data is Map &&
            data.containsKey('diagnostic_triage') &&
            data.containsKey('actions')) {
          // Case 2: LLM apply=true non-leaf 422 with suggestions at TOP-LEVEL
          setState(() {
            _triageCtrl.text = data['diagnostic_triage'] ?? '';
            _actionsCtrl.text = data['actions'] ?? '';
          });
          final err = data['error']?.toString() ??
              'Cannot apply triage/actions to non-leaf node';
          ScaffoldMessenger.of(context)
              .showSnackBar(SnackBar(content: Text('Non-leaf: $err')));
        } else {
          _showError('Save failed', e);
        }
      } else {
        _showError('Save failed', e);
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _copyFromVm() async {
    // We need the VM label; fetch via helper search using current record's VM by reading it again
    try {
      final d = await _repo.getLeaf(widget.nodeId);
      final vm = d.isLeaf
          ? null
          : null; // VM not in detail? We'll fallback to list path; better approach:
      // For simplicity, ask user for VM (or you can pass it via route arguments from list)
      final vmLabel = await _askVm();
      if (vmLabel == null || vmLabel.isEmpty) return;
      final res = await _repo.copyFromLastVm(vmLabel);
      if (res == null) {
        _showError('No prior outcome', 'No records under this VM');
        return;
      }
      final (t, a) = res;
      setState(() {
        _triageCtrl.text = t;
        _actionsCtrl.text = a;
      });
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Copied from last VM')));
    } catch (e) {
      _showError('Copy failed', e);
    }
  }

  Future<String?> _askVm() async {
    String tmp = '';
    return showDialog<String>(
        context: context,
        builder: (c) {
          return AlertDialog(
            title: const Text('Vital Measurement'),
            content: TextField(
                onChanged: (v) => tmp = v,
                decoration: const InputDecoration(hintText: 'Enter VM label')),
            actions: [
              TextButton(
                  onPressed: () => Navigator.pop(c),
                  child: const Text('Cancel')),
              TextButton(
                  onPressed: () => Navigator.pop(c, tmp),
                  child: const Text('Use'))
            ],
          );
        });
  }

  Future<void> _llmFill() async {
    try {
      // In a real flow, pass the current root/nodes context; here placeholder empty nodes
      final req = LlmFillRequest(
          root: 'Root',
          nodes: List.filled(5, ''),
          triageStyle: 'diagnosis-only',
          actionsStyle: 'referral-only');
      final (t, a) = await _repo.llmFill(req);
      setState(() {
        _triageCtrl.text = t;
        _actionsCtrl.text = a;
      });
      _telemetry.event('outcomes_llm_fill_used');
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text('AI suggestions populated (review before saving)')));
    } catch (e) {
      _showError('AI Fill failed', e);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Node ${widget.nodeId} Outcomes')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(12),
              child: Column(children: [
                if (!_isLeaf)
                  Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Text('Leaf-only: this node cannot be edited.',
                          style: TextStyle(
                              color: Theme.of(context).colorScheme.error))),
                _LabeledArea(
                    label: 'Diagnostic Triage',
                    controller: _triageCtrl,
                    max: triageMax),
                const SizedBox(height: 8),
                _LabeledArea(
                    label: 'Actions',
                    controller: _actionsCtrl,
                    max: actionsMax,
                    minLines: 4),
                const SizedBox(height: 8),
                Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                        'AI suggestions are guidance-only; no dosing/diagnosis.',
                        style: Theme.of(context).textTheme.bodySmall)),
                const SizedBox(height: 8),
                Row(children: [
                  ElevatedButton.icon(
                      onPressed: _saving ? null : _save,
                      icon: const Icon(Icons.save),
                      label: const Text('Save')),
                  const SizedBox(width: 12),
                  OutlinedButton.icon(
                      onPressed: _saving ? null : _copyFromVm,
                      icon: const Icon(Icons.copy),
                      label: const Text('Copy from last VM')),
                  const SizedBox(width: 12),
                  if (widget.llmEnabled)
                    OutlinedButton.icon(
                        onPressed: _saving ? null : _llmFill,
                        icon: const Icon(Icons.auto_awesome),
                        label: const Text('Fill with AI')),
                ]),
              ]),
            ),
    );
  }
}

class _LabeledArea extends StatelessWidget {
  final String label;
  final TextEditingController controller;
  final int max;
  final int minLines;
  const _LabeledArea(
      {required this.label,
      required this.controller,
      required this.max,
      this.minLines = 3});
  @override
  Widget build(BuildContext context) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(label, style: Theme.of(context).textTheme.labelLarge),
      TextField(
        controller: controller,
        minLines: minLines,
        maxLines: 10,
        maxLength: max, // soft clamp
        buildCounter: (ctx,
                {required currentLength, required isFocused, maxLength}) =>
            Text('$currentLength/$max'),
      ),
    ]);
  }
}
