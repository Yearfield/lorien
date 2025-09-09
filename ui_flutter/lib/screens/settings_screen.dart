import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../data/api_client.dart';
import '../widgets/layout/scroll_scaffold.dart';
import '../widgets/app_back_leading.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final TextEditingController _baseUrlController = TextEditingController();
  bool _testingConnection = false;
  bool _saving = false;
  String? _connectionStatus;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    final override = prefs.getString('api_base_override');
    _baseUrlController.text = override ?? ApiClient.I().baseUrl;
    setState(() {});
  }

  Future<void> _onSave() async {
    setState(() => _saving = true);
    try {
      final prefs = await SharedPreferences.getInstance();
      final val = _baseUrlController.text.trim();
      await prefs.setString('api_base_override', val);
      ApiClient.setBaseUrl(val);
      if (mounted) {
        setState(() => _saving = false);
        _showSnackBar('Settings saved successfully');
      }
    } catch (e) {
      if (mounted) {
        setState(() => _saving = false);
        _showSnackBar('Failed to save settings: $e');
      }
    }
  }

  Future<void> _testConnection() async {
    if (_testingConnection) return;

    setState(() {
      _testingConnection = true;
      _connectionStatus = null;
    });

    try {
      // Use the shared ApiClient for testing
      final response = await ApiClient.I().get('health');
      final data = response.data as Map<String, dynamic>?;

      if (response.statusCode == 200 && data?['ok'] == true) {
        setState(() {
          _connectionStatus = 'Connected: ${ApiClient.I().baseUrl}';
        });
        _showSnackBar('Connected successfully');
      } else {
        setState(() {
          _connectionStatus = 'HTTP ${response.statusCode} - API not healthy';
        });
        _showSnackBar('HTTP ${response.statusCode} - API not healthy');
      }
    } on ApiUnavailable catch (e) {
      setState(() {
        _connectionStatus = 'Connection failed: ${e.message}';
      });
      _showSnackBar('Connection failed: ${e.message}');
    } catch (e) {
      setState(() {
        _connectionStatus = 'Connection failed: $e';
      });
      _showSnackBar('Connection failed: $e');
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

      const Card(
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Linux/Desktop:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              Text('http://127.0.0.1:8000/api/v1'),
              SizedBox(height: 8),
              Text(
                'Android Emulator:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              Text('http://10.0.2.2:8000/api/v1'),
              SizedBox(height: 8),
              Text(
                'Physical Device (same network):',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              Text('http://<LAN-IP>:8000/api/v1'),
              SizedBox(height: 8),
              Text(
                'iOS Simulator:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              Text('http://localhost:8000/api/v1'),
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

      const Card(
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Default File Names:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 8),
              Text('• Calculator Export: lorien_calc_export.csv'),
              Text('• Tree Export: lorien_tree_export.csv'),
              SizedBox(height: 8),
              Text(
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
      leading: const AppBackLeading(),
      actions: <Widget>[
        ElevatedButton(
          onPressed: _saving ? null : _onSave,
          child: _saving
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2))
              : const Text('Save'),
        ),
        OutlinedButton(
          onPressed: _testConnection,
          child: const Text('Test Connection'),
        ),
      ],
      children: _buildFields(context),
    );
  }

  void _copyLanIp(BuildContext context) async {
    // This is a placeholder - in a real app you'd get the actual LAN IP
    const lanIp = '192.168.1.100'; // Example IP

    await Clipboard.setData(const ClipboardData(text: lanIp));

    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('LAN IP copied to clipboard: $lanIp'),
          duration: Duration(seconds: 2),
        ),
      );
    }
  }
}
