import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../state/app_settings_provider.dart';
import '../../state/repository_providers.dart';
import '../../core/crash_report_service.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  final _baseUrlController = TextEditingController();
  bool _isTestingConnection = false;
  bool _telemetryEnabled = false;

  @override
  void initState() {
    super.initState();
    _loadCurrentSettings();
  }

  @override
  void dispose() {
    _baseUrlController.dispose();
    super.dispose();
  }

  Future<void> _loadCurrentSettings() async {
    final baseUrl = ref.read(apiBaseUrlProvider);
    _baseUrlController.text = baseUrl;

    final prefs = await SharedPreferences.getInstance();
    _telemetryEnabled = prefs.getBool('telemetry_remote') ?? false;
    CrashReportService.enableRemote(_telemetryEnabled);

    if (mounted) setState(() {});
  }

  Future<void> _testConnection() async {
    setState(() {
      _isTestingConnection = true;
    });

    final connectionNotifier = ref.read(connectionStatusProvider.notifier);
    await connectionNotifier.testConnection(_baseUrlController.text);

    setState(() {
      _isTestingConnection = false;
    });

    if (mounted) {
      final status = ref.read(connectionStatusProvider);
      String message;
      Color color;

      switch (status) {
        case ConnectionStatus.connected:
          message = 'Connection successful!';
          color = Colors.green;
          break;
        case ConnectionStatus.disconnected:
          message = 'Unable to connect. Please check the URL and try again.';
          color = Colors.red;
          break;
        case ConnectionStatus.error:
          message = 'Connection error. Please check the URL and try again.';
          color = Colors.orange;
          break;
        case ConnectionStatus.unknown:
          message = 'Connection test failed.';
          color = Colors.grey;
          break;
      }

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: color,
        ),
      );
    }
  }

  Future<void> _saveSettings() async {
    final baseUrl = _baseUrlController.text.trim();
    if (baseUrl.isNotEmpty) {
      await ref.read(apiBaseUrlProvider.notifier).setBaseUrl(baseUrl);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Settings saved successfully!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    }
  }

  Future<void> _toggleTelemetry(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('telemetry_remote', value);
    setState(() => _telemetryEnabled = value);
    CrashReportService.enableRemote(value);
  }

  @override
  Widget build(BuildContext context) {
    final connectionStatus = ref.watch(connectionStatusProvider);
    final themeMode = ref.watch(themeModeProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/'),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // API Configuration Section
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'API Configuration',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 16),

                    TextField(
                      controller: _baseUrlController,
                      decoration: const InputDecoration(
                        labelText: 'API Base URL',
                        hintText: 'http://localhost:8000',
                        prefixIcon: Icon(Icons.link),
                      ),
                    ),
                    const SizedBox(height: 16),

                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed:
                                _isTestingConnection ? null : _testConnection,
                            icon: _isTestingConnection
                                ? const SizedBox(
                                    width: 16,
                                    height: 16,
                                    child: CircularProgressIndicator(
                                        strokeWidth: 2),
                                  )
                                : const Icon(Icons.wifi_tethering),
                            label: Text(_isTestingConnection
                                ? 'Testing...'
                                : 'Test Connection'),
                          ),
                        ),
                        const SizedBox(width: 12),
                        ElevatedButton.icon(
                          onPressed: _saveSettings,
                          icon: const Icon(Icons.save),
                          label: const Text('Save'),
                        ),
                      ],
                    ),

                    const SizedBox(height: 12),

                    // Connection Status Indicator
                    Row(
                      children: [
                        Icon(
                          _getStatusIcon(connectionStatus),
                          color: _getStatusColor(connectionStatus),
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          _getStatusText(connectionStatus),
                          style: TextStyle(
                            color: _getStatusColor(connectionStatus),
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 16),

                    // LAN Usage Tips
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.blue.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                            color: Colors.blue.withValues(alpha: 0.3)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Row(
                            children: [
                              Icon(Icons.info, color: Colors.blue, size: 20),
                              SizedBox(width: 8),
                              Text(
                                'LAN Usage Tips',
                                style: TextStyle(
                                  color: Colors.blue,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'For Android emulator use http://10.0.2.2:<port>, for device testing use http://<LAN-IP>:<port>',
                            style: TextStyle(
                              color: Colors.blue.shade700,
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Theme Configuration Section
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Appearance',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 16),
                    ListTile(
                      leading: const Icon(Icons.palette),
                      title: const Text('Theme Mode'),
                      subtitle: Text(_getThemeModeText(themeMode)),
                      trailing: DropdownButton<ThemeMode>(
                        value: themeMode,
                        onChanged: (ThemeMode? newValue) {
                          if (newValue != null) {
                            ref
                                .read(themeModeProvider.notifier)
                                .setThemeMode(newValue);
                          }
                        },
                        items: const [
                          DropdownMenuItem(
                            value: ThemeMode.system,
                            child: Text('System'),
                          ),
                          DropdownMenuItem(
                            value: ThemeMode.light,
                            child: Text('Light'),
                          ),
                          DropdownMenuItem(
                            value: ThemeMode.dark,
                            child: Text('Dark'),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Privacy & Telemetry Section
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Privacy & Telemetry',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 16),
                    SwitchListTile(
                      title: const Text('Send crash telemetry (opt-in)'),
                      subtitle: const Text(
                          'Includes error message and stack trace; no PII.'),
                      value: _telemetryEnabled,
                      onChanged: _toggleTelemetry,
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // About Section
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'About',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 16),
                    Consumer(
                      builder: (context, ref, child) {
                        final healthAsync = ref.watch(healthProvider);

                        return healthAsync.when(
                          data: (health) {
                            final version =
                                health['version'] as String? ?? 'Unknown';
                            return ListTile(
                              leading: const Icon(Icons.info),
                              title: const Text('API Version'),
                              subtitle: Text(version),
                            );
                          },
                          loading: () => const ListTile(
                            leading: Icon(Icons.info),
                            title: Text('API Version'),
                            subtitle: Text('Loading...'),
                          ),
                          error: (error, stack) => const ListTile(
                            leading: Icon(Icons.error),
                            title: Text('API Version'),
                            subtitle: Text('Unable to fetch'),
                          ),
                        );
                      },
                    ),
                    const ListTile(
                      leading: Icon(Icons.description),
                      title: Text('Description'),
                      subtitle: Text(
                          'Cross-platform decision tree management with offline-first storage'),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  IconData _getStatusIcon(ConnectionStatus status) {
    switch (status) {
      case ConnectionStatus.connected:
        return Icons.check_circle;
      case ConnectionStatus.disconnected:
        return Icons.error;
      case ConnectionStatus.error:
        return Icons.warning;
      case ConnectionStatus.unknown:
        return Icons.help;
    }
  }

  Color _getStatusColor(ConnectionStatus status) {
    switch (status) {
      case ConnectionStatus.connected:
        return Colors.green;
      case ConnectionStatus.disconnected:
        return Colors.red;
      case ConnectionStatus.error:
        return Colors.orange;
      case ConnectionStatus.unknown:
        return Colors.grey;
    }
  }

  String _getStatusText(ConnectionStatus status) {
    switch (status) {
      case ConnectionStatus.connected:
        return 'Connected';
      case ConnectionStatus.disconnected:
        return 'Disconnected';
      case ConnectionStatus.error:
        return 'Error';
      case ConnectionStatus.unknown:
        return 'Unknown';
    }
  }

  String _getThemeModeText(ThemeMode themeMode) {
    switch (themeMode) {
      case ThemeMode.system:
        return 'Follow system theme';
      case ThemeMode.light:
        return 'Light theme';
      case ThemeMode.dark:
        return 'Dark theme';
    }
  }
}
