import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/services/health_service.dart';
import '../../../shared/widgets/connected_badge.dart';
import '../../../shared/widgets/app_scaffold.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});
  @override
  ConsumerState<SettingsScreen> createState() => _S();
}

class _S extends ConsumerState<SettingsScreen> {
  final _baseCtrl = TextEditingController();
  String? _testedUrl, _snippet;
  int? _code;
  bool _busy = false;

  @override
  void initState() {
    super.initState();
    _baseCtrl.text = ref.read(baseUrlProvider);
  }

  Future<void> _test() async {
    setState(() => _busy = true);
    ref.read(baseUrlProvider.notifier).state = _baseCtrl.text.trim();
    final res = await ref.read(healthServiceProvider).test();
    setState(() {
      _testedUrl = res.testedUrl;
      _code = res.statusCode;
      _snippet = res.bodySnippet;
      _busy = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'Settings',
      actions: const [
        Padding(padding: EdgeInsets.all(8), child: ConnectedBadge())
      ],
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextFormField(
              controller: _baseCtrl,
              decoration: const InputDecoration(labelText: 'Base URL')),
          const SizedBox(height: 8),
          Row(children: [
            FilledButton(
                onPressed: _busy ? null : _test,
                child: const Text('Test Connection')),
            const SizedBox(width: 12),
            if (_code != null)
              Chip(label: Text(_code == 200 ? 'Connected' : 'Disconnected')),
          ]),
          if (_testedUrl != null) ...[
            const SizedBox(height: 12),
            Card(
                child: Padding(
              padding: const EdgeInsets.all(12),
              child: DefaultTextStyle.merge(
                style: const TextStyle(fontFamily: 'monospace'),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('URL: $_testedUrl'),
                    Text('HTTP: ${_code ?? ''}'),
                    Text('Body: ${_snippet ?? ''}'),
                  ],
                ),
              ),
            )),
          ],
          const SizedBox(height: 16),
          const Text(
              'Tips:\n• Linux: http://127.0.0.1:8000/api/v1\n• Android emu: http://10.0.2.2:8000/api/v1\n• Device: http://<LAN-IP>:8000/api/v1'),
        ],
      ),
    );
  }
}
