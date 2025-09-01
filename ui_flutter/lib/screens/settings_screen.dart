import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:dio/dio.dart';
import '../data/api_client.dart';
import '../utils/env.dart';
import '../widgets/layout/scroll_scaffold.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final TextEditingController _baseUrlController = TextEditingController();
  bool _testingConnection = false;
  String? _connectionStatus;

  @override
  void initState() {
    super.initState();
    _baseUrlController.text = ApiClient().baseUrl;
  }

  Future<void> _testConnection() async {
    if (_testingConnection) return;

    setState(() {
      _testingConnection = true;
      _connectionStatus = null;
    });

    try {
      final testedUrl = '${_baseUrlController.text}/health';
      final dio = Dio();
      final response = await dio.get(testedUrl);

      if (response.statusCode == 200) {
        setState(() {
          _connectionStatus = 'Connected: $testedUrl';
        });
        _showSnackBar('Connected: $testedUrl');
      } else {
        setState(() {
          _connectionStatus = 'HTTP ${response.statusCode} at $testedUrl';
        });
        _showSnackBar('HTTP ${response.statusCode} at $testedUrl');
      }
    } catch (e) {
      final res = (e is DioException) ? e.response : null;
      final status = res?.statusCode ?? 'n/a';
      final body =
          (res?.data is String ? res?.data : res?.toString() ?? e.toString())
              .toString();
      final truncatedBody =
          body.length > 100 ? '${body.substring(0, 100)}...' : body;

      setState(() {
        _connectionStatus =
            'Failed: $testedUrl · HTTP $status · $truncatedBody';
      });
      _showSnackBar('Failed: $testedUrl · HTTP $status · $truncatedBody');
    } finally {
      setState(() {
        _testingConnection = false;
      });
    }
  }

  void _showSnackBar(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
    }
  }

  List<Widget> _buildFields(BuildContext context) {
    return <Widget>[
      const Text(
        'API Configuration',
        style: TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.bold,
        ),
      ),
      const SizedBox(height: 16),

      // API Base URL
      TextFormField(
        controller: _baseUrlController,
        decoration: const InputDecoration(
          labelText: 'API Base URL',
          hintText: 'http://localhost:8000',
          border: OutlineInputBorder(),
        ),
        onChanged: (value) {
          // TODO: Save to preferences
        },
      ),

      const SizedBox(height: 16),

      // Test Connection Button
      Row(
        children: [
          Expanded(
            child: ElevatedButton.icon(
              onPressed: _testingConnection ? null : _testConnection,
              icon: _testingConnection
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.wifi_tethering),
              label:
                  Text(_testingConnection ? 'Testing...' : 'Test Connection'),
            ),
          ),
        ],
      ),

      if (_connectionStatus != null) ...[
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: _connectionStatus!.contains('Connected')
                ? Colors.green[50]
                : Colors.red[50],
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: _connectionStatus!.contains('Connected')
                  ? Colors.green[200]!
                  : Colors.red[200]!,
            ),
          ),
          child: Text(
            _connectionStatus!,
            style: TextStyle(
              color: _connectionStatus!.contains('Connected')
                  ? Colors.green[700]
                  : Colors.red[700],
            ),
          ),
        ),
      ],

      const SizedBox(height: 24),

      // LAN Connection Tips
      const Text(
        'LAN Connection Tips',
        style: TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.bold,
        ),
      ),
      const SizedBox(height: 16),

      Card(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Linux/Desktop:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const Text('http://127.0.0.1:8000/api/v1'),
              const SizedBox(height: 8),
              const Text(
                'Android Emulator:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const Text('http://10.0.2.2:8000/api/v1'),
              const SizedBox(height: 8),
              const Text(
                'Physical Device (same network):',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const Text('http://<LAN-IP>:8000/api/v1'),
              const SizedBox(height: 8),
              const Text(
                'iOS Simulator:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const Text('http://localhost:8000/api/v1'),
            ],
          ),
        ),
      ),

      const SizedBox(height: 16),

      // Copy LAN IP Button
      ElevatedButton.icon(
        onPressed: () => _copyLanIp(context),
        icon: const Icon(Icons.copy),
        label: const Text('Copy LAN IP to Clipboard'),
      ),

      const SizedBox(height: 24),

      // CSV Export Settings
      const Text(
        'CSV Export Settings',
        style: TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.bold,
        ),
      ),
      const SizedBox(height: 16),

      Card(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Default File Names:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text('• Calculator Export: lorien_calc_export.csv'),
              const Text('• Tree Export: lorien_tree_export.csv'),
              const SizedBox(height: 8),
              const Text(
                'Files are saved to temporary directory and can be shared or moved.',
                style: TextStyle(fontStyle: FontStyle.italic),
              ),
            ],
          ),
        ),
      ),

      // Add bottom padding to ensure content doesn't get hidden behind bottom bar
      const SizedBox(height: 80),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return ScrollScaffold(
      title: 'Settings',
      children: _buildFields(context),
      actions: <Widget>[
        ElevatedButton(
          onPressed: () {
            // TODO: Implement save functionality
          },
          child: const Text('Save'),
        ),
        OutlinedButton(
          onPressed: () {
            // TODO: Implement test connection
          },
          child: const Text('Test Connection'),
        ),
      ],
    );
  }

  void _copyLanIp(BuildContext context) async {
    // This is a placeholder - in a real app you'd get the actual LAN IP
    const lanIp = '192.168.1.100'; // Example IP

    await Clipboard.setData(ClipboardData(text: lanIp));

    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('LAN IP copied to clipboard: $lanIp'),
          duration: const Duration(seconds: 2),
        ),
      );
    }
  }
}
