import 'package:flutter/material.dart';

class FlagAssignerSheet extends StatefulWidget {
  const FlagAssignerSheet({super.key});
  @override
  State<FlagAssignerSheet> createState() => _S();
}

class _S extends State<FlagAssignerSheet> {
  final _q = TextEditingController();
  final Set<String> _selected = {};
  bool _cascade = true;
  int _preview = 0;

  final List<String> _symptoms = [
    'Fever',
    'Cough',
    'Shortness of breath',
    'Chest pain',
    'Headache',
    'Nausea',
    'Vomiting',
    'Diarrhea',
    'Fatigue',
    'Loss of appetite',
  ];

  List<String> get _filteredSymptoms {
    if (_q.text.isEmpty) return _symptoms;
    return _symptoms
        .where(
            (symptom) => symptom.toLowerCase().contains(_q.text.toLowerCase()))
        .toList();
  }

  void _updatePreview() {
    setState(() {
      _preview =
          _selected.length * (_cascade ? 5 : 1); // Simplified calculation
    });
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
              controller: _q,
              decoration: const InputDecoration(labelText: 'Search symptom'),
              onChanged: (_) => setState(() {}),
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
            const Text('Select symptoms:',
                style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            ...(_filteredSymptoms.map((symptom) => CheckboxListTile(
                  title: Text(symptom),
                  value: _selected.contains(symptom),
                  onChanged: (bool? value) {
                    setState(() {
                      if (value == true) {
                        _selected.add(symptom);
                      } else {
                        _selected.remove(symptom);
                      }
                    });
                    _updatePreview();
                  },
                ))),
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
                      onPressed: _selected.isEmpty
                          ? null
                          : () {
                              // TODO: POST assign
                              Navigator.pop(context);
                            },
                      child: const Text('Confirm Assign')),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
