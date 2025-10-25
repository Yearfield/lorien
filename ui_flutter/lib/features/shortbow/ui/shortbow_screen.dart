import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../state/shortbow_notifier.dart';
import 'shortbow_import_screen.dart';
import 'shortbow_navigator_widget.dart';

class ShortBowScreen extends ConsumerStatefulWidget {
  const ShortBowScreen({super.key});

  @override
  ConsumerState<ShortBowScreen> createState() => _ShortBowScreenState();
}

class _ShortBowScreenState extends ConsumerState<ShortBowScreen> {
  int _selectedTab = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('ShortBow Navigator'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.read(shortBowNotifierProvider.notifier).refresh();
            },
            tooltip: 'Refresh data',
          ),
        ],
      ),
      body: Column(
        children: [
          // Tab selector
          Container(
            decoration: BoxDecoration(
              border: Border(
                bottom: BorderSide(color: Colors.grey[300]!),
              ),
            ),
            child: Row(
              children: [
                Expanded(
                  child: InkWell(
                    onTap: () => setState(() => _selectedTab = 0),
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        border: Border(
                          bottom: BorderSide(
                            color: _selectedTab == 0 ? Colors.blue : Colors.transparent,
                            width: 2,
                          ),
                        ),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.upload_file,
                            color: _selectedTab == 0 ? Colors.blue : Colors.grey,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Import Data',
                            style: TextStyle(
                              color: _selectedTab == 0 ? Colors.blue : Colors.grey,
                              fontWeight: _selectedTab == 0 ? FontWeight.bold : FontWeight.normal,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                Expanded(
                  child: InkWell(
                    onTap: () => setState(() => _selectedTab = 1),
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        border: Border(
                          bottom: BorderSide(
                            color: _selectedTab == 1 ? Colors.blue : Colors.transparent,
                            width: 2,
                          ),
                        ),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.navigation,
                            color: _selectedTab == 1 ? Colors.blue : Colors.grey,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Navigate',
                            style: TextStyle(
                              color: _selectedTab == 1 ? Colors.blue : Colors.grey,
                              fontWeight: _selectedTab == 1 ? FontWeight.bold : FontWeight.normal,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Tab content
          Expanded(
            child: _selectedTab == 0
                ? const ShortBowImportScreen()
                : const ShortBowNavigatorWidget(),
          ),
        ],
      ),
    );
  }
}
