import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
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
              decoration: const InputDecoration(
                labelText: 'API Base URL',
                hintText: 'http://localhost:8000',
                border: OutlineInputBorder(),
              ),
              initialValue: 'http://localhost:8000',
              onChanged: (value) {
                // TODO: Save to preferences
              },
            ),
            
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
                      'Android Emulator:',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const Text('http://10.0.2.2:8000'),
                    const SizedBox(height: 8),
                    
                    const Text(
                      'Physical Device (same network):',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const Text('http://<LAN-IP>:8000'),
                    const SizedBox(height: 8),
                    
                    const Text(
                      'iOS Simulator:',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const Text('http://localhost:8000'),
                    const SizedBox(height: 8),
                    
                    const Text(
                      'Physical iOS Device (same network):',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const Text('http://<LAN-IP>:8000'),
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
          ],
        ),
      ),
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
