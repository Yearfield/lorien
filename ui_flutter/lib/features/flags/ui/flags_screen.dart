import 'package:flutter/material.dart';
import 'flag_assigner_sheet.dart';
import '../../../shared/widgets/app_scaffold.dart';

class FlagsScreen extends StatefulWidget {
  const FlagsScreen({super.key});

  @override
  State<FlagsScreen> createState() => _FlagsScreenState();
}

class _FlagsScreenState extends State<FlagsScreen> {
  final _searchController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'Flags',
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              controller: _searchController,
              decoration: const InputDecoration(
                labelText: 'Search symptoms',
                prefixIcon: Icon(Icons.search),
              ),
              onChanged: (value) {
                setState(() {
                  // TODO: Implement search filtering
                });
              },
            ),
          ),
          Expanded(
            child: ListView.builder(
              itemCount: 10, // TODO: Replace with actual data
              itemBuilder: (context, index) {
                return _RecentBranchAuditItem(
                  title: 'Branch Audit ${index + 1}',
                  date: DateTime.now().subtract(Duration(days: index)),
                  flagCount: (index + 1) % 3,
                );
              },
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          showModalBottomSheet(
            context: context,
            isScrollControlled: true,
            builder: (context) => const FlagAssignerSheet(),
          );
        },
        icon: const Icon(Icons.flag),
        label: const Text('Assign Flags'),
      ),
    );
  }
}

class _RecentBranchAuditItem extends StatelessWidget {
  const _RecentBranchAuditItem({
    required this.title,
    required this.date,
    required this.flagCount,
  });

  final String title;
  final DateTime date;
  final int flagCount;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: ListTile(
        title: Text(title),
        subtitle: Text('Last updated: ${_formatDate(date)}'),
        trailing: flagCount > 0
            ? Chip(
                label: Text('$flagCount flags'),
                backgroundColor:
                    Theme.of(context).colorScheme.secondaryContainer,
              )
            : null,
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.month}/${date.day}/${date.year}';
  }
}
