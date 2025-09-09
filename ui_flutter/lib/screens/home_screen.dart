import 'package:flutter/material.dart';
import '../core/api_config.dart';
import '../features/workspace/calculator_screen.dart';
import '../features/workspace/ui/workspace_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Home'),
        automaticallyImplyLeading: false,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Calculator',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    'Navigate through decision trees and find diagnostic outcomes.',
                    style: TextStyle(color: Colors.grey),
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton.icon(
                    onPressed: () => Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) =>
                            const CalculatorScreen(baseUrl: ApiConfig.baseUrl),
                      ),
                    ),
                    icon: const Icon(Icons.calculate_outlined),
                    label: const Text('Open Calculator'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          Card(
            child: ListTile(
              title: const Text('Workspace'),
              subtitle: const Text('Import, visualize, analyze, edit'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const WorkspaceScreen()),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
