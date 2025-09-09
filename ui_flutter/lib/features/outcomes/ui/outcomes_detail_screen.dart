import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import '../../../core/http/api_client.dart';

import '../../../core/validators/field_validators.dart';
import '../../../core/util/error_mapper.dart';
import '../../../shared/widgets/field_error_text.dart';
import '../../../shared/widgets/app_scaffold.dart';
import '../../../shared/widgets/toasts.dart';
import '../../../shared/widgets/route_guard.dart';
import '../../../state/health_provider.dart';
import '../data/llm_api.dart';
import '../data/outcomes_api.dart';

class OutcomesDetailScreen extends ConsumerStatefulWidget {
  const OutcomesDetailScreen({super.key, required this.outcomeId, this.vm});
  final String outcomeId; // must be leaf id
  final String? vm; // optional VM label for prefill
  @override
  ConsumerState<OutcomesDetailScreen> createState() => _S();
}

class _S extends ConsumerState<OutcomesDetailScreen> {
  final _fKey = GlobalKey<FormState>();
  final _triage = TextEditingController();
  final _actions = TextEditingController();
  String? _errTriage, _errActions;
  bool _saving = false;
  bool _llmOn = false;
  String? _llmCheckedAt;
  bool _dirty = false;
  List<String> _breadcrumb = [];
  bool _loading = true;
  String? _vmLabel;

  int _wc(String s) =>
      s.trim().isEmpty ? 0 : s.trim().split(RegExp(r'\s+')).length;

  Future<void> _probeLlm() async {
    final res = await ref.read(llmApiProvider).health();
    setState(() {
      _llmOn = res.ready;
      _llmCheckedAt = res.checkedAt;
    });
  }

  Future<void> _loadBreadcrumb() async {
    try {
      final api = ref.read(outcomesApiProvider);
      final path = await api.getTreePath(widget.outcomeId);
      final labels = path['labels'] as List<dynamic>? ?? [];
      setState(() {
        _breadcrumb = labels.map((l) => l.toString()).toList();
        _vmLabel = _breadcrumb.isNotEmpty ? _breadcrumb.first : null;
      });
    } catch (e) {
      // Fallback breadcrumb if API fails
      setState(() => _breadcrumb = ['VM', 'N1', 'N2', 'N3', 'N4', 'N5']);
    }
  }

  Future<void> _loadInitialData() async {
    setState(() => _loading = true);
    await Future.wait([_probeLlm(), _loadBreadcrumb()]);

    if (widget.vm != null && widget.vm!.isNotEmpty) {
      // Prefill from last outcome under same VM
      try {
        final api = ref.read(outcomesApiProvider);
        final results = await api.search(vm: widget.vm);
        if (results['items'] != null && (results['items'] as List).isNotEmpty) {
          final latest =
              (results['items'] as List).first as Map<String, dynamic>;
          _triage.text = latest['diagnostic_triage'] ?? '';
          _actions.text = latest['actions'] ?? '';
          _dirty = true;
        }
      } catch (e) {
        // If VM copy fails, fall back to empty form
        _triage.text = '';
        _actions.text = '';
      }
    } else {
      // Load existing data for this specific outcome
      try {
        final api = ref.read(outcomesApiProvider);
        final data = await api.getDetail(widget.outcomeId);
        _triage.text = data['diagnostic_triage'] ?? '';
        _actions.text = data['actions'] ?? '';
      } catch (e) {
        // Data loading will fail gracefully, form will be empty
      }
    }
    setState(() => _loading = false);
  }

  Future<void> _llmFill() async {
    if (!_llmOn) return;
    try {
      final api = ref.read(llmApiProvider);
      final suggestions = await api.fill(widget.outcomeId);
      // Update fields with LLM suggestions (≤7 words each)
      setState(() {
        if (suggestions['diagnostic_triage'] != null) {
          _triage.text = suggestions['diagnostic_triage'].toString();
        }
        if (suggestions['actions'] != null) {
          _actions.text = suggestions['actions'].toString();
        }
        _dirty = true;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('LLM fill failed: $e')),
        );
      }
    }
  }

  Future<void> _copyFromVm() async {
    if (_vmLabel == null) return;
    try {
      final api = ref.read(outcomesApiProvider);
      final results = await api.search(vm: _vmLabel);
      final items = results['items'] as List<dynamic>? ?? [];
      if (items.isNotEmpty) {
        final item = items.first as Map<String, dynamic>;
        setState(() {
          _triage.text = item['diagnostic_triage'] ?? '';
          _actions.text = item['actions'] ?? '';
          _dirty = true;
        });
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Copied from most recent VM outcome')),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
                content: Text('No previous outcomes found for this VM')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Copy failed: $e')),
        );
      }
    }
  }

  Future<void> _save() async {
    if (!_fKey.currentState!.validate()) return;
    setState(() {
      _saving = true;
      _errTriage = _errActions = null;
    });
    try {
      final dio = ref.read(dioProvider);
      await dio.put('/triage/${widget.outcomeId}', data: {
        'diagnostic_triage': _triage.text.trim(),
        'actions': _actions.text.trim(),
      });
      setState(() => _dirty = false);
      if (mounted) {
        showSuccess(context, 'Saved successfully');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 422) {
        final mapped = mapPydanticFieldErrors(e.response?.data);
        setState(() {
          _errTriage = mapped['diagnostic_triage'];
          _errActions = mapped['actions'];
        });
      } else {
        if (mounted) {
          showError(context, 'Error ${e.response?.statusCode ?? ''}');
        }
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  void initState() {
    super.initState();
    _loadInitialData();
  }

  @override
  Widget build(BuildContext context) {
    final health = ref.watch(healthControllerProvider).valueOrNull;
    final llmEnabled = (health?.features.llm ?? false);

    // Show disabled notice if LLM features are not available
    if (!llmEnabled) {
      return AppScaffold(
        title: 'Outcomes Detail',
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.auto_awesome,
                  size: 64,
                  color: Colors.grey[400],
                ),
                const SizedBox(height: 16),
                Text(
                  'LLM Features Disabled',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 8),
                Text(
                  'LLM suggestions are disabled by server configuration. '
                  'Contact your administrator to enable LLM features.',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.grey[600],
                      ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 24),
                OutlinedButton.icon(
                  onPressed: () =>
                      ref.read(healthControllerProvider.notifier).ping(),
                  icon: const Icon(Icons.refresh),
                  label: const Text('Check Status'),
                ),
              ],
            ),
          ),
        ),
      );
    }

    return RouteGuard(
      // busy guard during save
      isBusy: () => _saving,
      confirmMessage: 'A save is in progress. Leave and cancel?',
      child: PopScope(
        canPop: !_dirty,
        onPopInvoked: (didPop) async {
          if (didPop || !_dirty) return;
          final go = await showDialog<bool>(
            context: context,
            builder: (_) => AlertDialog(
              title: const Text('Discard changes?'),
              content: const Text(
                  'You have unsaved edits. Do you want to discard them?'),
              actions: [
                TextButton(
                    onPressed: () => Navigator.of(context).pop(false),
                    child: const Text('Stay')),
                FilledButton(
                    onPressed: () => Navigator.of(context).pop(true),
                    child: const Text('Discard')),
              ],
            ),
          );
          if (go == true && context.mounted) {
            Navigator.of(context).pop();
          }
        },
        child: AppScaffold(
          title: 'Outcomes Detail',
          body: _loading
              ? const Center(child: CircularProgressIndicator())
              : Form(
                  key: _fKey,
                  child: ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      // Breadcrumb
                      if (_breadcrumb.isNotEmpty) ...[
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: Theme.of(context).colorScheme.surfaceContainerHighest,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.location_on, size: 16),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  _breadcrumb.join(' > '),
                                  style: Theme.of(context).textTheme.bodySmall,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 16),
                      ],
                      TextFormField(
                        controller: _triage,
                        validator: (v) => maxSevenWordsAndAllowed(v,
                            field: 'Diagnostic Triage'),
                        decoration: InputDecoration(
                            labelText: 'Diagnostic Triage',
                            helperText:
                                'Keep under 7 words. Avoid dosing/route/time tokens (mg, ml, IV, q6h, etc.).',
                            suffixText: '${_wc(_triage.text)}/7'),
                        onChanged: (_) => setState(() {
                          _dirty = true;
                        }),
                      ),
                      FieldErrorText(_errTriage),
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: _actions,
                        validator: (v) =>
                            maxSevenWordsAndAllowed(v, field: 'Actions'),
                        decoration: InputDecoration(
                            labelText: 'Actions',
                            helperText:
                                'Keep under 7 words. Avoid dosing/route/time tokens (mg, ml, IV, q6h, etc.).',
                            suffixText: '${_wc(_actions.text)}/7'),
                        onChanged: (_) => setState(() {
                          _dirty = true;
                        }),
                      ),
                      FieldErrorText(_errActions),
                      const SizedBox(height: 24),
                      Row(children: [
                        if (_vmLabel != null)
                          OutlinedButton.icon(
                            onPressed: _copyFromVm,
                            icon: const Icon(Icons.content_copy),
                            label: const Text('Copy from VM'),
                          ),
                        if (_vmLabel != null) const SizedBox(width: 8),
                        if (_llmOn)
                          OutlinedButton.icon(
                            onPressed: _llmFill,
                            icon: const Icon(Icons.auto_awesome),
                            label: const Text('LLM Fill'),
                          ),
                        if (!_llmOn && llmEnabled)
                          OutlinedButton.icon(
                            onPressed: null,
                            icon: const Icon(Icons.auto_awesome),
                            label: const Text('LLM Unavailable'),
                          ),
                        const Spacer(),
                        FilledButton(
                            onPressed: _saving ? null : _save,
                            child: _saving
                                ? const SizedBox(
                                    width: 16,
                                    height: 16,
                                    child: CircularProgressIndicator(
                                        strokeWidth: 2))
                                : const Text('Save')),
                      ]),
                      // Show LLM status if enabled but not ready
                      if (!llmEnabled) ...[
                        const SizedBox(height: 8),
                        Text(
                          'LLM features disabled by server',
                          style:
                              Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: Theme.of(context).colorScheme.error,
                                  ),
                        ),
                      ] else if (!_llmOn && _llmCheckedAt != null) ...[
                        const SizedBox(height: 8),
                        Text(
                          'LLM unavailable (last checked: $_llmCheckedAt)',
                          style:
                              Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: Theme.of(context).colorScheme.error,
                                  ),
                        ),
                      ],
                    ],
                  ),
                ),
        ),
      ),
    );
  }
}
