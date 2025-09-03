import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../widgets/layout/scroll_scaffold.dart';
import '../../../widgets/app_back_leading.dart';
import '../../../shared/widgets/scroll_to_top_fab.dart';

class OutcomesListScreen extends StatefulWidget {
  const OutcomesListScreen({super.key});

  @override
  State<OutcomesListScreen> createState() => _OutcomesListScreenState();
}

class _OutcomesListScreenState extends State<OutcomesListScreen> {
  final _searchController = TextEditingController();
  final _scrollController = ScrollController();
  String _selectedVitalMeasurement = 'All';
  final List<String> _vitalMeasurements = [
    'All',
    'Blood Pressure',
    'Heart Rate',
    'Temperature'
  ];

  @override
  Widget build(BuildContext context) {
    return ScrollScaffold(
      title: 'Outcomes',
      leading: const AppBackLeading(),
      children: [
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: _searchController,
                decoration: const InputDecoration(
                  labelText: 'Search outcomes',
                  prefixIcon: Icon(Icons.search),
                ),
                onChanged: (value) {
                  setState(() {
                    // TODO: Implement search filtering
                  });
                },
              ),
            ),
            const SizedBox(width: 16),
            DropdownButton<String>(
              value: _selectedVitalMeasurement,
              items: _vitalMeasurements.map((String value) {
                return DropdownMenuItem<String>(
                  value: value,
                  child: Text(value),
                );
              }).toList(),
              onChanged: (String? newValue) {
                setState(() {
                  _selectedVitalMeasurement = newValue!;
                  // TODO: Implement VM filtering
                });
              },
            ),
          ],
        ),
        const SizedBox(height: 16),
        ...List.generate(10, (index) => _OutcomeListItem(
          id: 'outcome_$index',
          title: 'Outcome ${index + 1}',
          vitalMeasurement: 'Blood Pressure',
          isLeaf: index % 3 == 0,
        )),
      ],
    );
  }
}

class _OutcomeListItem extends StatelessWidget {
  const _OutcomeListItem({
    required this.id,
    required this.title,
    required this.vitalMeasurement,
    required this.isLeaf,
  });

  final String id;
  final String title;
  final String vitalMeasurement;
  final bool isLeaf;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: ListTile(
        title: Text(title),
        subtitle: Text(vitalMeasurement),
        trailing: isLeaf
            ? const Chip(label: Text('Leaf'), backgroundColor: Colors.green)
            : null,
        onTap: () => context.go('/outcomes/$id'),
      ),
    );
  }
}
