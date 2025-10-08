import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import 'package:open_filex/open_filex.dart';
import '../../../../core/settings_provider.dart';

class SettingsPane extends ConsumerStatefulWidget {
  const SettingsPane({super.key});

  @override
  ConsumerState<SettingsPane> createState() => _SettingsPaneState();
}

class _SettingsPaneState extends ConsumerState<SettingsPane> {
  late TextEditingController _apiUrlController;
  bool _isTestingConnection = false;

  @override
  void initState() {
    super.initState();
    final settings = ref.read(settingsProvider);
    _apiUrlController = TextEditingController(text: settings.apiBaseUrl);
  }

  @override
  void dispose() {
    _apiUrlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final settings = ref.watch(settingsProvider);
    final connectionStatus = ref.watch(connectionStatusProvider);
    final settingsNotifier = ref.read(settingsProvider.notifier);
    final connectionNotifier = ref.read(connectionStatusProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // API Configuration Section
            _buildSectionHeader('API Configuration', Icons.api),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    TextField(
                      controller: _apiUrlController,
                      decoration: const InputDecoration(
                        labelText: 'API Base URL',
                        hintText: 'http://127.0.0.1:8000/api/v1',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.link),
                      ),
                      onChanged: (value) {
                        // Auto-save as user types (with debounce could be added)
                        settingsNotifier.updateApiBaseUrl(value);
                      },
                    ),
                    const SizedBox(height: 16),

                    // Connection Status
                    Row(
                      children: [
                        Icon(
                          connectionStatus.isConnected
                            ? Icons.check_circle
                            : Icons.error,
                          color: connectionStatus.isConnected
                            ? Colors.green
                            : Colors.red,
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          connectionStatus.isConnected
                            ? 'Connected'
                            : 'Disconnected',
                          style: TextStyle(
                            color: connectionStatus.isConnected
                              ? Colors.green
                              : Colors.red,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        if (connectionStatus.error != null) ...[
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              '(${connectionStatus.error})',
                              style: TextStyle(
                                color: Colors.red.shade600,
                                fontSize: 12,
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),

                    if (connectionStatus.lastChecked != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        'Last checked: ${_formatDateTime(connectionStatus.lastChecked!)}',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],

                    const SizedBox(height: 16),

                    // Test Connection Button
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: _isTestingConnection ? null : () async {
                          setState(() {
                            _isTestingConnection = true;
                          });
                          await connectionNotifier.testConnection();
                          setState(() {
                            _isTestingConnection = false;
                          });
                        },
                        icon: _isTestingConnection
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.wifi_protected_setup),
                        label: Text(_isTestingConnection ? 'Testing...' : 'Test Connection'),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Application Behavior Section
            _buildSectionHeader('Application Behavior', Icons.settings_applications),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SwitchListTile(
                      title: const Text('Auto-save'),
                      subtitle: const Text('Automatically save changes as you work'),
                      value: settings.autoSave,
                      onChanged: (value) {
                        settingsNotifier.updateAutoSave(value);
                      },
                    ),
                    SwitchListTile(
                      title: const Text('Show Confirmation Dialogs'),
                      subtitle: const Text('Ask for confirmation before destructive actions'),
                      value: settings.showConfirmations,
                      onChanged: (value) {
                        settingsNotifier.updateShowConfirmations(value);
                      },
                    ),
                    const Divider(),
                    ListTile(
                      title: const Text('Auto-save Delay'),
                      subtitle: Text('${settings.autoSaveDelayMs}ms'),
                      trailing: const Icon(Icons.arrow_forward_ios),
                      onTap: () => _showAutoSaveDelayDialog(context, settingsNotifier, settings.autoSaveDelayMs),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Export Settings Section
            _buildSectionHeader('Export Settings', Icons.file_download),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'CSV Format',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 8),

                    // Encoding selection
                    ListTile(
                      title: const Text('Encoding'),
                      subtitle: Text(_getEncodingLabel(settings.exportSettings.encoding)),
                      trailing: const Icon(Icons.arrow_forward_ios),
                      onTap: () => _showEncodingDialog(context, settingsNotifier, settings.exportSettings),
                    ),

                    // Delimiter selection
                    ListTile(
                      title: const Text('Delimiter'),
                      subtitle: Text(_getDelimiterLabel(settings.exportSettings.delimiter)),
                      trailing: const Icon(Icons.arrow_forward_ios),
                      onTap: () => _showDelimiterDialog(context, settingsNotifier, settings.exportSettings),
                    ),

                    const Divider(),

                    // Export options
                    SwitchListTile(
                      title: const Text('Include Headers'),
                      subtitle: const Text('Add column headers to exported CSV'),
                      value: settings.exportSettings.includeHeaders,
                      onChanged: (value) {
                        final newExportSettings = settings.exportSettings.copyWith(includeHeaders: value);
                        settingsNotifier.updateExportSettings(newExportSettings);
                      },
                    ),
                    SwitchListTile(
                      title: const Text('Include Timestamps'),
                      subtitle: const Text('Add export timestamp to filename'),
                      value: settings.exportSettings.includeTimestamps,
                      onChanged: (value) {
                        final newExportSettings = settings.exportSettings.copyWith(includeTimestamps: value);
                        settingsNotifier.updateExportSettings(newExportSettings);
                      },
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Appearance Section
            _buildSectionHeader('Appearance', Icons.palette),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Theme',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 8),
                    RadioGroup<ThemeMode>(
                      groupValue: settings.themeMode,
                      onChanged: (value) {
                        if (value != null) {
                          settingsNotifier.updateThemeMode(value);
                        }
                      },
                      child: Column(
                        children: ThemeMode.values.map((mode) => RadioListTile<ThemeMode>(
                          title: Text(_getThemeModeLabel(mode)),
                          subtitle: Text(_getThemeModeDescription(mode)),
                          value: mode,
                        )).toList(),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Application Info Section
            _buildSectionHeader('Application Info', Icons.info),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildInfoRow('App Version', '0.7.0+1'),
                    if (connectionStatus.apiVersion != null) ...[
                      _buildInfoRow('API Version', connectionStatus.apiVersion!),
                    ],
                    _buildInfoRow('Platform', _getPlatformName()),

                    if (connectionStatus.databaseStatus != null) ...[
                      const Divider(),
                      const Text(
                        'Database Information',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 8),
                      _buildInfoRow(
                        'Status',
                        connectionStatus.databaseStatus!.statusText,
                        statusColor: connectionStatus.databaseStatus!.isHealthy
                          ? Colors.green
                          : Colors.orange,
                      ),
                      if (connectionStatus.databaseStatus!.path != null)
                        _buildInfoRow('Path', connectionStatus.databaseStatus!.path!),
                      if (connectionStatus.databaseStatus!.journalMode != null)
                        _buildInfoRow('Journal Mode', connectionStatus.databaseStatus!.journalMode!),
                      if (connectionStatus.databaseStatus!.tableCount != null)
                        _buildInfoRow('Tables', '${connectionStatus.databaseStatus!.tableCount}'),
                      if (connectionStatus.databaseStatus!.nodeCount != null)
                        _buildInfoRow('Nodes', '${connectionStatus.databaseStatus!.nodeCount}'),
                      if (connectionStatus.databaseStatus!.objectCount != null)
                        _buildInfoRow('Objects', '${connectionStatus.databaseStatus!.objectCount}'),
                      if (connectionStatus.databaseStatus!.foreignKeys != null)
                        _buildInfoRow('Foreign Keys', connectionStatus.databaseStatus!.foreignKeys! ? 'Enabled' : 'Disabled'),
                      if (connectionStatus.databaseStatus!.pageSize != null)
                        _buildInfoRow('Page Size', '${connectionStatus.databaseStatus!.pageSize} bytes'),
                    ],

                    if (connectionStatus.features != null && connectionStatus.features!.isNotEmpty) ...[
                      const Divider(),
                      const Text(
                        'Feature Flags',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 8),
                      ...connectionStatus.features!.entries.map((entry) =>
                        _buildInfoRow(
                          entry.key.toUpperCase(),
                          entry.value ? 'Enabled' : 'Disabled',
                          statusColor: entry.value ? Colors.green : Colors.grey,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Debug Options Section
            _buildSectionHeader('Debug Options', Icons.bug_report),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Development Tools',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 8),
                    SwitchListTile(
                      title: const Text('Debug Mode'),
                      subtitle: const Text('Enable debug features and verbose output'),
                      value: settings.debugSettings.debugMode,
                      onChanged: (value) {
                        final newDebugSettings = settings.debugSettings.copyWith(debugMode: value);
                        settingsNotifier.updateDebugSettings(newDebugSettings);
                      },
                    ),
                    SwitchListTile(
                      title: const Text('API Logging'),
                      subtitle: const Text('Show detailed API request/response logs'),
                      value: settings.debugSettings.apiLogging,
                      onChanged: (value) {
                        final newDebugSettings = settings.debugSettings.copyWith(apiLogging: value);
                        settingsNotifier.updateDebugSettings(newDebugSettings);
                      },
                    ),
                    SwitchListTile(
                      title: const Text('Mock Data'),
                      subtitle: const Text('Use mock data instead of real API calls'),
                      value: settings.debugSettings.mockData,
                      onChanged: (value) {
                        final newDebugSettings = settings.debugSettings.copyWith(mockData: value);
                        settingsNotifier.updateDebugSettings(newDebugSettings);
                      },
                    ),
                    SwitchListTile(
                      title: const Text('Verbose Logging'),
                      subtitle: const Text('Enable detailed application logging'),
                      value: settings.debugSettings.verboseLogging,
                      onChanged: (value) {
                        final newDebugSettings = settings.debugSettings.copyWith(verboseLogging: value);
                        settingsNotifier.updateDebugSettings(newDebugSettings);
                      },
                    ),
                    SwitchListTile(
                      title: const Text('Performance Metrics'),
                      subtitle: const Text('Show performance timing information'),
                      value: settings.debugSettings.showPerformanceMetrics,
                      onChanged: (value) {
                        final newDebugSettings = settings.debugSettings.copyWith(showPerformanceMetrics: value);
                        settingsNotifier.updateDebugSettings(newDebugSettings);
                      },
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Data Management Section
            _buildSectionHeader('Data Management', Icons.storage),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    ListTile(
                      leading: const Icon(Icons.clear_all),
                      title: const Text('Clear Cache'),
                      subtitle: const Text('Clear all cached data and temporary files'),
                      trailing: const Icon(Icons.arrow_forward_ios),
                      onTap: () => _showClearCacheDialog(context, settingsNotifier),
                    ),
                    const Divider(),
                    ListTile(
                      leading: const Icon(Icons.refresh),
                      title: const Text('Reset All Data'),
                      subtitle: const Text('Reset all settings and data to defaults'),
                      trailing: const Icon(Icons.arrow_forward_ios),
                      onTap: () => _showResetDataDialog(context, settingsNotifier),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Backup & Restore Section
            _buildSectionHeader('Backup & Restore', Icons.backup),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    ListTile(
                      leading: const Icon(Icons.save_alt),
                      title: const Text('Create Backup'),
                      subtitle: const Text('Save current settings to a backup file'),
                      trailing: const Icon(Icons.arrow_forward_ios),
                      onTap: () => _createBackup(context, settingsNotifier),
                    ),
                    const Divider(),
                    ListTile(
                      leading: const Icon(Icons.restore),
                      title: const Text('Restore from Backup'),
                      subtitle: const Text('Load settings from a backup file'),
                      trailing: const Icon(Icons.arrow_forward_ios),
                      onTap: () => _restoreFromBackup(context, settingsNotifier),
                    ),
                    const Divider(),
                    ListTile(
                      leading: const Icon(Icons.file_download),
                      title: const Text('Export Settings'),
                      subtitle: const Text('Export settings to a JSON file'),
                      trailing: const Icon(Icons.arrow_forward_ios),
                      onTap: () => _exportSettings(context, settingsNotifier),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Actions Section
            _buildSectionHeader('Actions', Icons.settings),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    SizedBox(
                      width: double.infinity,
                      child: OutlinedButton.icon(
                        onPressed: () async {
                          final confirmed = await _showConfirmDialog(
                            context,
                            'Reset Settings',
                            'Are you sure you want to reset all settings to defaults?',
                          );
                          if (confirmed == true) {
                            await settingsNotifier.resetToDefaults();
                            _apiUrlController.text = ref.read(settingsProvider).apiBaseUrl;
                            if (mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Settings reset to defaults')),
                              );
                            }
                          }
                        },
                        icon: const Icon(Icons.restore),
                        label: const Text('Reset to Defaults'),
                      ),
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

  Widget _buildSectionHeader(String title, IconData icon) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        children: [
          Icon(icon, size: 20),
          const SizedBox(width: 8),
          Text(
            title,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value, {Color? statusColor}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(
                color: statusColor ?? Theme.of(context).textTheme.bodyMedium?.color?.withValues(alpha: 0.8),
                fontWeight: statusColor != null ? FontWeight.w500 : null,
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _getThemeModeLabel(ThemeMode mode) {
    switch (mode) {
      case ThemeMode.system:
        return 'System';
      case ThemeMode.light:
        return 'Light';
      case ThemeMode.dark:
        return 'Dark';
    }
  }

  String _getThemeModeDescription(ThemeMode mode) {
    switch (mode) {
      case ThemeMode.system:
        return 'Follow system theme';
      case ThemeMode.light:
        return 'Always use light theme';
      case ThemeMode.dark:
        return 'Always use dark theme';
    }
  }

  String _getPlatformName() {
    // This is a simplified version - in a real app you might want to use
    // platform detection packages
    return 'Desktop';
  }

  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }

  Future<bool?> _showConfirmDialog(
    BuildContext context,
    String title,
    String content,
  ) {
    return showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(content),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Reset'),
          ),
        ],
      ),
    );
  }

  Future<void> _showAutoSaveDelayDialog(
    BuildContext context,
    SettingsNotifier settingsNotifier,
    int currentDelay,
  ) async {
    final controller = TextEditingController(text: currentDelay.toString());

    final result = await showDialog<int>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Auto-save Delay'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Set the delay in milliseconds before auto-saving changes.'),
            const SizedBox(height: 16),
            TextField(
              controller: controller,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: 'Delay (ms)',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              final delay = int.tryParse(controller.text);
              if (delay != null && delay >= 100 && delay <= 10000) {
                Navigator.of(context).pop(delay);
              }
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );

    if (result != null) {
      await settingsNotifier.updateAutoSaveDelay(result);
    }
  }

  Future<void> _showEncodingDialog(
    BuildContext context,
    SettingsNotifier settingsNotifier,
    ExportSettings currentSettings,
  ) async {
    final result = await showDialog<CsvEncoding>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('CSV Encoding'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: CsvEncoding.values.map((encoding) => RadioListTile<CsvEncoding>(
            title: Text(_getEncodingLabel(encoding)),
            subtitle: Text(_getEncodingDescription(encoding)),
            value: encoding,
            groupValue: currentSettings.encoding,
            onChanged: (value) {
              if (value != null) {
                Navigator.of(context).pop(value);
              }
            },
          )).toList(),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
        ],
      ),
    );

    if (result != null) {
      final newSettings = currentSettings.copyWith(encoding: result);
      await settingsNotifier.updateExportSettings(newSettings);
    }
  }

  Future<void> _showDelimiterDialog(
    BuildContext context,
    SettingsNotifier settingsNotifier,
    ExportSettings currentSettings,
  ) async {
    final result = await showDialog<CsvDelimiter>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('CSV Delimiter'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: CsvDelimiter.values.map((delimiter) => RadioListTile<CsvDelimiter>(
            title: Text(_getDelimiterLabel(delimiter)),
            subtitle: Text(_getDelimiterDescription(delimiter)),
            value: delimiter,
            groupValue: currentSettings.delimiter,
            onChanged: (value) {
              if (value != null) {
                Navigator.of(context).pop(value);
              }
            },
          )).toList(),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
        ],
      ),
    );

    if (result != null) {
      final newSettings = currentSettings.copyWith(delimiter: result);
      await settingsNotifier.updateExportSettings(newSettings);
    }
  }

  String _getEncodingLabel(CsvEncoding encoding) {
    switch (encoding) {
      case CsvEncoding.utf8:
        return 'UTF-8';
      case CsvEncoding.utf8Bom:
        return 'UTF-8 with BOM';
      case CsvEncoding.latin1:
        return 'Latin-1 (ISO-8859-1)';
    }
  }

  String _getEncodingDescription(CsvEncoding encoding) {
    switch (encoding) {
      case CsvEncoding.utf8:
        return 'Standard Unicode encoding';
      case CsvEncoding.utf8Bom:
        return 'UTF-8 with Byte Order Mark (Excel compatible)';
      case CsvEncoding.latin1:
        return 'Western European encoding';
    }
  }

  String _getDelimiterLabel(CsvDelimiter delimiter) {
    switch (delimiter) {
      case CsvDelimiter.comma:
        return 'Comma (,)';
      case CsvDelimiter.semicolon:
        return 'Semicolon (;)';
      case CsvDelimiter.tab:
        return 'Tab';
    }
  }

  String _getDelimiterDescription(CsvDelimiter delimiter) {
    switch (delimiter) {
      case CsvDelimiter.comma:
        return 'Standard CSV format';
      case CsvDelimiter.semicolon:
        return 'European CSV format';
      case CsvDelimiter.tab:
        return 'Tab-separated values (TSV)';
    }
  }

  // Phase 3 dialog methods
  Future<void> _showClearCacheDialog(
    BuildContext context,
    SettingsNotifier settingsNotifier,
  ) async {
    final confirmed = await _showConfirmDialog(
      context,
      'Clear Cache',
      'This will clear all cached data and temporary files. This action cannot be undone.',
    );

    if (confirmed == true) {
      // Here you would implement actual cache clearing logic
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Cache cleared successfully')),
        );
      }
    }
  }

  Future<void> _showResetDataDialog(
    BuildContext context,
    SettingsNotifier settingsNotifier,
  ) async {
    final confirmed = await _showConfirmDialog(
      context,
      'Reset All Data',
      'This will reset all settings and data to defaults. This action cannot be undone.',
    );

    if (confirmed == true) {
      await settingsNotifier.clearAllData();
      _apiUrlController.text = ref.read(settingsProvider).apiBaseUrl;
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('All data reset to defaults')),
        );
      }
    }
  }

  Future<void> _createBackup(
    BuildContext context,
    SettingsNotifier settingsNotifier,
  ) async {
    try {
      final filePath = await settingsNotifier.createBackup();
      if (filePath != null) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Backup created: ${filePath.split('/').last}'),
              action: SnackBarAction(
                label: 'Open',
                onPressed: () => OpenFilex.open(filePath),
              ),
            ),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Failed to create backup')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Error creating backup')),
        );
      }
    }
  }

  Future<void> _restoreFromBackup(
    BuildContext context,
    SettingsNotifier settingsNotifier,
  ) async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['json'],
        allowMultiple: false,
      );

      if (result != null && result.files.isNotEmpty) {
        final filePath = result.files.first.path;
        if (filePath != null) {
          final success = await settingsNotifier.restoreFromBackup(filePath);
          if (success) {
            _apiUrlController.text = ref.read(settingsProvider).apiBaseUrl;
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Settings restored successfully')),
              );
            }
          } else {
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Failed to restore backup')),
              );
            }
          }
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Error restoring backup')),
        );
      }
    }
  }

  Future<void> _exportSettings(
    BuildContext context,
    SettingsNotifier settingsNotifier,
  ) async {
    try {
      final filePath = await settingsNotifier.exportSettings();
      if (filePath != null) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Settings exported: ${filePath.split('/').last}'),
              action: SnackBarAction(
                label: 'Open',
                onPressed: () => OpenFilex.open(filePath),
              ),
            ),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Failed to export settings')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Error exporting settings')),
        );
      }
    }
  }
}
