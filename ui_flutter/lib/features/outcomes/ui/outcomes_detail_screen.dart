import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import '../../../core/http/api_client.dart';

import '../../../core/validators/field_validators.dart';
import '../../../core/util/error_mapper.dart';
import '../../../shared/widgets/field_error_text.dart';

class OutcomesDetailScreen extends ConsumerStatefulWidget {
  const OutcomesDetailScreen({super.key, required this.outcomeId});
  final String outcomeId; // must be leaf id
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

  int _wc(String s) =>
      s.trim().isEmpty ? 0 : s.trim().split(RegExp(r'\s+')).length;

    Future<void> _probeLlm() async {
    try {
      final dio = ref.read(dioProvider);
      final res = await dio.get('/llm/health');
      setState(() => _llmOn = res.statusCode == 200);
    } catch (_) { 
      setState(() => _llmOn = false); 
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
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(const SnackBar(content: Text('Saved')));
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 422) {
        final mapped = mapPydanticFieldErrors(e.response?.data);
        setState(() {
          _errTriage = mapped['diagnostic_triage'];
          _errActions = mapped['actions'];
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error ${e.response?.statusCode ?? ''}')));
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  void initState() {
    super.initState();
    _probeLlm();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Outcomes Detail')),
      body: Form(
        key: _fKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            TextFormField(
              controller: _triage,
              validator: (v) =>
                  maxSevenWordsAndAllowed(v, field: 'Diagnostic Triage'),
              decoration: InputDecoration(
                  labelText: 'Diagnostic Triage',
                  helperText: 'Keep under 7 words, concise phrase only.',
                  suffixText: '${_wc(_triage.text)}/7'),
              onChanged: (_) => setState(() {}),
            ),
            FieldErrorText(_errTriage),
            const SizedBox(height: 16),
            TextFormField(
              controller: _actions,
              validator: (v) => maxSevenWordsAndAllowed(v, field: 'Actions'),
              decoration: InputDecoration(
                  labelText: 'Actions',
                  helperText: 'Keep under 7 words, concise phrase only.',
                  suffixText: '${_wc(_actions.text)}/7'),
              onChanged: (_) => setState(() {}),
            ),
            FieldErrorText(_errActions),
            const SizedBox(height: 24),
            Row(children: [
              if (_llmOn)
                OutlinedButton.icon(
                    onPressed: () {/* GET suggestions only */},
                    icon: const Icon(Icons.auto_awesome),
                    label: const Text('LLM Fill')),
              const Spacer(),
              FilledButton(
                  onPressed: _saving ? null : _save,
                  child: _saving
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2))
                      : const Text('Save')),
            ]),
          ],
        ),
      ),
    );
  }
}
