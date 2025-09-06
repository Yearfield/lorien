import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import '../../../core/services/health_service.dart';
import '../../../shared/widgets/connected_badge.dart';
import '../../../shared/widgets/app_scaffold.dart';
import '../../../widgets/layout/scroll_scaffold.dart';
import '../../../widgets/app_back_leading.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  final _baseCtrl = TextEditingController();
  String? _testedUrl, _snippet, _responseTime;
  int? _code;
  bool _busy = false;
  bool _autoTest = true;
  bool _showAdvanced = false;
  Timer? _healthCheckTimer;
  ConnectivityResult _connectivity = ConnectivityResult.none;
  StreamSubscription<List<ConnectivityResult>>? _connectivitySubscription;
  List<String> _connectionHistory = [];
  DateTime? _lastSuccessfulConnection;
  Map<String, dynamic>? _serverInfo;

  // Predefined URL templates
  final _urlTemplates = {
    'Local Development': 'http://127.0.0.1:8000/api/v1',
    'Android Emulator': 'http://10.0.2.2:8000/api/v1',
    'iOS Simulator': 'http://127.0.0.1:8000/api/v1',
    'LAN (Custom)': 'http://192.168.1.100:8000/api/v1',
    'Production': 'https://api.lorien.example.com/api/v1',
  };

  @override
  void initState() {
    super.initState();
    _baseCtrl.text = ref.read(baseUrlProvider);

    // Monitor connectivity changes
    _connectivitySubscription = Connectivity().onConnectivityChanged.listen(
      (results) => setState(() => _connectivity = results.isNotEmpty ? results.first : ConnectivityResult.none),
    );

    // Auto health check every 30 seconds
    _startHealthMonitoring();

    // Get initial connectivity
    Connectivity().checkConnectivity().then(
      (results) => setState(() => _connectivity = results.isNotEmpty ? results.first : ConnectivityResult.none),
    );
  }

  @override
  void dispose() {
    _healthCheckTimer?.cancel();
    _connectivitySubscription?.cancel();
    _baseCtrl.dispose();
    super.dispose();
  }

  void _startHealthMonitoring() {
    if (!_autoTest) return;

    _healthCheckTimer?.cancel();
    _healthCheckTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      if (mounted) {
        _performSilentHealthCheck();
      }
    });
  }

  Future<void> _performSilentHealthCheck() async {
    try {
      final res = await ref.read(healthServiceProvider).test();
      // Also check LLM health
      await ref.read(healthServiceProvider).testLlm();
      if (mounted) {
        setState(() {
          if (res.statusCode == 200) {
            _lastSuccessfulConnection = DateTime.now();
            _serverInfo = res.serverInfo;
          }
          _connectionHistory.add('${DateTime.now().toIso8601String()}: ${res.statusCode}');
          if (_connectionHistory.length > 10) {
            _connectionHistory.removeAt(0);
          }
        });
      }
    } catch (e) {
      // Silent failure for auto-check
    }
  }

  Future<void> _test() async {
    final stopwatch = Stopwatch()..start();
    setState(() => _busy = true);

    ref.read(baseUrlProvider.notifier).state = _baseCtrl.text.trim();

    try {
      final res = await ref.read(healthServiceProvider).test();
      // Also test LLM health
      await ref.read(healthServiceProvider).testLlm();
      stopwatch.stop();

      if (mounted) {
        setState(() {
          _testedUrl = res.testedUrl;
          _code = res.statusCode;
          _snippet = res.bodySnippet;
          _responseTime = '${stopwatch.elapsedMilliseconds}ms';
          _busy = false;

          if (res.statusCode == 200) {
            _lastSuccessfulConnection = DateTime.now();
            _serverInfo = res.serverInfo;
            _connectionHistory.add('${DateTime.now().toIso8601String()}: ${res.statusCode} (${_responseTime})');
            if (_connectionHistory.length > 10) {
              _connectionHistory.removeAt(0);
            }
          }
        });
      }
    } catch (e) {
      stopwatch.stop();
      if (mounted) {
        setState(() {
          _responseTime = '${stopwatch.elapsedMilliseconds}ms';
          _busy = false;
          _connectionHistory.add('${DateTime.now().toIso8601String()}: ERROR (${_responseTime})');
          if (_connectionHistory.length > 10) {
            _connectionHistory.removeAt(0);
          }
        });
      }
    }
  }

  void _applyUrlTemplate(String template) {
    setState(() => _baseCtrl.text = template);
  }

  Future<void> _resetToDefault() async {
    const defaultUrl = 'http://127.0.0.1:8000/api/v1';
    setState(() => _baseCtrl.text = defaultUrl);
    ref.read(baseUrlProvider.notifier).state = defaultUrl;

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Reset to default URL')),
    );
  }

  Future<void> _clearHistory() async {
    setState(() => _connectionHistory.clear());
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Connection history cleared')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return ScrollScaffold(
      title: 'Settings',
      leading: const AppBackLeading(),
      actions: [
        Padding(
          padding: const EdgeInsets.all(8),
          child: ConnectedBadge(),
        ),
      ],
      children: [
        // Connectivity Status
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Connectivity Status',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Icon(
                      _connectivity == ConnectivityResult.none
                          ? Icons.wifi_off
                          : Icons.wifi,
                      color: _connectivity == ConnectivityResult.none
                          ? Colors.red
                          : Colors.green,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      _connectivity == ConnectivityResult.none
                          ? 'No Network'
                          : 'Network Available',
                      style: TextStyle(
                        color: _connectivity == ConnectivityResult.none
                            ? Colors.red
                            : Colors.green,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                const Row(
                  children: [
                    LlmBadge(),
                  ],
                ),
                if (_lastSuccessfulConnection != null) ...[
                  const SizedBox(height: 8),
                  Text(
                    'Last successful connection: ${_lastSuccessfulConnection!.toString().split('.')[0]}',
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Base URL Configuration
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Server Configuration',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _baseCtrl,
                  decoration: InputDecoration(
                    labelText: 'Base URL',
                    hintText: 'https://api.example.com/api/v1',
                    border: const OutlineInputBorder(),
                    suffixIcon: IconButton(
                      icon: const Icon(Icons.clear),
                      onPressed: () => _baseCtrl.clear(),
                      tooltip: 'Clear URL',
                    ),
                  ),
                  keyboardType: TextInputType.url,
                ),
                const SizedBox(height: 12),

                // URL Templates
                const Text('Quick Setup:', style: TextStyle(fontWeight: FontWeight.w500)),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: _urlTemplates.entries.map((entry) {
                    return OutlinedButton(
                      onPressed: () => _applyUrlTemplate(entry.value),
                      child: Text(entry.key),
                    );
                  }).toList(),
                ),

                const SizedBox(height: 12),

                // Control buttons
                Row(
                  children: [
                    Expanded(
                      child: FilledButton.icon(
                        onPressed: _busy ? null : _test,
                        icon: _busy
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.network_check),
                        label: Text(_busy ? 'Testing...' : 'Test Connection'),
                      ),
                    ),
                    const SizedBox(width: 8),
                    OutlinedButton.icon(
                      onPressed: _resetToDefault,
                      icon: const Icon(Icons.refresh),
                      label: const Text('Reset'),
                    ),
                  ],
                ),

                // Connection status
                if (_code != null) ...[
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: _code == 200 ? Colors.green[50] : Colors.red[50],
                      borderRadius: BorderRadius.circular(8),
                      border: Border(
                        left: BorderSide(
                          color: _code == 200 ? Colors.green : Colors.red,
                          width: 4,
                        ),
                      ),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          _code == 200 ? Icons.check_circle : Icons.error,
                          color: _code == 200 ? Colors.green : Colors.red,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            _code == 200 ? 'Connected' : 'Connection Failed',
                            style: TextStyle(
                              color: _code == 200 ? Colors.green[800] : Colors.red[800],
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                        if (_responseTime != null)
                          Text(
                            _responseTime!,
                            style: const TextStyle(fontSize: 12, color: Colors.grey),
                          ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Connection Details
        if (_testedUrl != null) ...[
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Connection Details',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 12),
                  DefaultTextStyle.merge(
                    style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Text('URL: ', style: TextStyle(fontWeight: FontWeight.bold)),
                            Expanded(child: Text(_testedUrl!)),
                            IconButton(
                              icon: const Icon(Icons.copy, size: 16),
                              onPressed: () => Clipboard.setData(ClipboardData(text: _testedUrl!)),
                              tooltip: 'Copy URL',
                            ),
                          ],
                        ),
                        Row(
                          children: [
                            const Text('HTTP: ', style: TextStyle(fontWeight: FontWeight.bold)),
                            Text('${_code ?? 'N/A'}'),
                            if (_responseTime != null) ...[
                              const SizedBox(width: 16),
                              const Text('Response: ', style: TextStyle(fontWeight: FontWeight.bold)),
                              Text(_responseTime!),
                            ],
                          ],
                        ),
                        if (_snippet != null && _snippet!.isNotEmpty) ...[
                          const SizedBox(height: 8),
                          const Text('Response: ', style: TextStyle(fontWeight: FontWeight.bold)),
                          Container(
                            width: double.infinity,
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: Colors.grey[100],
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              _snippet!,
                              style: const TextStyle(fontSize: 11),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                  if (_serverInfo != null) ...[
                    const SizedBox(height: 16),
                    const Text('Server Info:', style: TextStyle(fontWeight: FontWeight.bold)),
                    ..._serverInfo!.entries.map((entry) {
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 2),
                        child: Text('${entry.key}: ${entry.value}'),
                      );
                    }),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
        ],

        // Monitoring Settings
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Connection Monitoring',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),
                SwitchListTile(
                  title: const Text('Auto Health Check'),
                  subtitle: const Text('Automatically test connection every 30 seconds'),
                  value: _autoTest,
                  onChanged: (value) {
                    setState(() => _autoTest = value);
                    if (value) {
                      _startHealthMonitoring();
                    } else {
                      _healthCheckTimer?.cancel();
                    }
                  },
                ),
                const SizedBox(height: 8),
                OutlinedButton.icon(
                  onPressed: () => setState(() => _showAdvanced = !_showAdvanced),
                  icon: Icon(_showAdvanced ? Icons.expand_less : Icons.expand_more),
                  label: Text(_showAdvanced ? 'Hide Advanced' : 'Show Advanced'),
                ),
                if (_showAdvanced) ...[
                  const SizedBox(height: 16),
                  const Text(
                    'Connection History',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    height: 150,
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey[300]!),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: _connectionHistory.isEmpty
                        ? const Center(
                            child: Text('No connection history'),
                          )
                        : ListView.builder(
                            itemCount: _connectionHistory.length,
                            itemBuilder: (context, index) {
                              final entry = _connectionHistory[_connectionHistory.length - 1 - index];
                              return Padding(
                                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                                child: Text(
                                  entry,
                                  style: const TextStyle(fontSize: 12, fontFamily: 'monospace'),
                                ),
                              );
                            },
                          ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      OutlinedButton.icon(
                        onPressed: _clearHistory,
                        icon: const Icon(Icons.clear),
                        label: const Text('Clear History'),
                      ),
                      const Spacer(),
                      Text(
                        '${_connectionHistory.length} entries',
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Help Section
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Connection Help',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 12),
                const Text(
                  'Common connection URLs:',
                  style: TextStyle(fontWeight: FontWeight.w500),
                ),
                const SizedBox(height: 8),
                _buildHelpItem('Local Development', 'http://127.0.0.1:8000/api/v1'),
                _buildHelpItem('Android Emulator', 'http://10.0.2.2:8000/api/v1'),
                _buildHelpItem('iOS Simulator', 'http://127.0.0.1:8000/api/v1'),
                _buildHelpItem('LAN/Network', 'http://192.168.1.xxx:8000/api/v1'),
                const SizedBox(height: 12),
                const Text(
                  'Note: Replace xxx with your server\'s IP address on the local network.',
                  style: TextStyle(fontSize: 12, color: Colors.grey),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildHelpItem(String label, String url) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
                Text(
                  url,
                  style: const TextStyle(fontSize: 12, fontFamily: 'monospace'),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.copy, size: 16),
            onPressed: () => Clipboard.setData(ClipboardData(text: url)),
            tooltip: 'Copy URL',
          ),
          IconButton(
            icon: const Icon(Icons.play_arrow, size: 16),
            onPressed: () => _applyUrlTemplate(url),
            tooltip: 'Use this URL',
          ),
        ],
      ),
    );
  }
}
