import 'package:flutter/material.dart';
import '../../data/api_client.dart';

class BugReportSheet extends StatefulWidget {
  const BugReportSheet({super.key});

  @override
  State<BugReportSheet> createState() => _BugReportSheetState();
}

class _BugReportSheetState extends State<BugReportSheet> {
  final _desc = TextEditingController();
  bool _busy = false, _done = false;

  Future<void> _submit() async {
    setState(() => _busy = true);
    try {
      await ApiClient.I().postJson('telemetry/bug', body: {
        'description': _desc.text,
        'base_url': ApiClient.I().baseUrl,
      });
      if (mounted) setState(() => _done = true);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text(
            'Report a Bug',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: _desc,
            minLines: 3,
            maxLines: 6,
            decoration: const InputDecoration(
              hintText: 'What happened?',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: FilledButton(
                  onPressed: _busy ? null : _submit,
                  child: Text(_done ? 'Sent' : 'Send'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
