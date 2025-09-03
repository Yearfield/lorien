import 'package:flutter/material.dart';

typedef CalcNode = ({int rank, String symptomId, String symptomLabel, String? quality});

class CalcExportDialog extends StatefulWidget {
  const CalcExportDialog({super.key});

  static Future<({String diagnosis, List<CalcNode> nodes})?> open(BuildContext ctx) {
    return showDialog(
      context: ctx,
      builder: (_) => const Dialog(child: CalcExportDialog()),
    );
  }

  @override
  State<CalcExportDialog> createState() => _CalcExportDialogState();
}

class _CalcExportDialogState extends State<CalcExportDialog> {
  final _form = GlobalKey<FormState>();
  final _dxCtl = TextEditingController();
  final List<TextEditingController> _id = List.generate(5, (_) => TextEditingController());
  final List<TextEditingController> _label = List.generate(5, (_) => TextEditingController());
  final List<TextEditingController> _quality = List.generate(5, (_) => TextEditingController());

  @override
  void dispose() {
    _dxCtl.dispose();
    for (final c in [..._id, ..._label, ..._quality]) { c.dispose(); }
    super.dispose();
  }

  String? _req(String? v) => (v==null || v.trim().isEmpty) ? 'Required' : null;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Form(
        key: _form,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('CSV Export (V1)', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            TextFormField(controller: _dxCtl, decoration: const InputDecoration(labelText: 'Diagnosis'), validator: _req),
            const SizedBox(height: 12),
            const Align(alignment: Alignment.centerLeft, child: Text('Exactly 5 symptoms (rank 1–5)')),
            const SizedBox(height: 8),
            for (int i=0;i<5;i++) Row(children: [
              Expanded(child: TextFormField(controller: _id[i], decoration: InputDecoration(labelText: 'Symptom ID (rank ${i+1})'), validator: _req)),
              const SizedBox(width: 8),
              Expanded(child: TextFormField(controller: _label[i], decoration: const InputDecoration(labelText: 'Symptom Label'), validator: _req)),
              const SizedBox(width: 8),
              Expanded(child: TextFormField(controller: _quality[i], decoration: const InputDecoration(labelText: 'Quality (optional)'))),
            ]),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(onPressed: ()=> Navigator.of(context).pop(), child: const Text('Cancel')),
                const SizedBox(width: 8),
                FilledButton(
                  onPressed: () {
                    if (!_form.currentState!.validate()) return;
                    final nodes = List.generate(5, (i)=>(
                      rank: i+1,
                      symptomId: _id[i].text.trim(),
                      symptomLabel: _label[i].text.trim(),
                      quality: _quality[i].text.trim().isEmpty ? null : _quality[i].text.trim(),
                    ));
                    Navigator.of(context).pop((diagnosis: _dxCtl.text.trim(), nodes: nodes));
                  },
                  child: const Text('Export'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
