import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/services/health_service.dart';
import '../../../core/http/api_client.dart';

class CalculatorScreen extends ConsumerStatefulWidget {
  const CalculatorScreen({super.key});

  @override
  ConsumerState<CalculatorScreen> createState() => _CalculatorScreenState();
}

class _CalculatorScreenState extends ConsumerState<CalculatorScreen> {
  String? _selectedVM;
  String? _selectedNode1;
  String? _selectedNode2;
  String? _selectedNode3;
  String? _selectedNode4;
  String? _selectedNode5;
  int _remainingLeaves = 0;

  final List<String> _vitalMeasurements = ['Blood Pressure', 'Heart Rate', 'Temperature'];
  final List<String> _nodeOptions = ['Option 1', 'Option 2', 'Option 3', 'Option 4', 'Option 5'];

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    // TODO: Load actual data from API
    setState(() {
      _remainingLeaves = 25; // Placeholder
    });
  }

  void _onVMChanged(String? value) {
    setState(() {
      _selectedVM = value;
      // Reset downstream selections
      _selectedNode1 = null;
      _selectedNode2 = null;
      _selectedNode3 = null;
      _selectedNode4 = null;
      _selectedNode5 = null;
    });
    _updateRemainingLeaves();
  }

  void _onNodeChanged(int nodeIndex, String? value) {
    setState(() {
      switch (nodeIndex) {
        case 1:
          _selectedNode1 = value;
          // Reset downstream
          _selectedNode2 = null;
          _selectedNode3 = null;
          _selectedNode4 = null;
          _selectedNode5 = null;
          break;
        case 2:
          _selectedNode2 = value;
          _selectedNode3 = null;
          _selectedNode4 = null;
          _selectedNode5 = null;
          break;
        case 3:
          _selectedNode3 = value;
          _selectedNode4 = null;
          _selectedNode5 = null;
          break;
        case 4:
          _selectedNode4 = value;
          _selectedNode5 = null;
          break;
        case 5:
          _selectedNode5 = value;
          break;
      }
    });
    _updateRemainingLeaves();
  }

  void _updateRemainingLeaves() {
    // TODO: Calculate actual remaining leaves based on selections
    setState(() {
      _remainingLeaves = 25 - (_selectedNode1 != null ? 5 : 0) - 
                        (_selectedNode2 != null ? 5 : 0) - 
                        (_selectedNode3 != null ? 5 : 0) - 
                        (_selectedNode4 != null ? 5 : 0) - 
                        (_selectedNode5 != null ? 5 : 0);
    });
  }

  Future<void> _exportCSV() async {
    try {
      final base = ref.read(baseUrlProvider);
      await dio.get('$base/export/csv');
      // TODO: Handle file download
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('CSV exported successfully'))
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Export failed: $e'))
        );
      }
    }
  }

  Future<void> _exportXLSX() async {
    try {
      final base = ref.read(baseUrlProvider);
      await dio.get('$base/export/xlsx');
      // TODO: Handle file download
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('XLSX exported successfully'))
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Export failed: $e'))
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Calculator'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          DropdownButtonFormField<String>(
            value: _selectedVM,
            decoration: const InputDecoration(labelText: 'Vital Measurement'),
            items: _vitalMeasurements.map((String value) {
              return DropdownMenuItem<String>(
                value: value,
                child: Text(value),
              );
            }).toList(),
            onChanged: _onVMChanged,
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            value: _selectedNode1,
            decoration: const InputDecoration(labelText: 'Node 1'),
            items: _nodeOptions.map((String value) {
              return DropdownMenuItem<String>(
                value: value,
                child: Text(value),
              );
            }).toList(),
            onChanged: (value) => _onNodeChanged(1, value),
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            value: _selectedNode2,
            decoration: const InputDecoration(labelText: 'Node 2'),
            items: _nodeOptions.map((String value) {
              return DropdownMenuItem<String>(
                value: value,
                child: Text(value),
              );
            }).toList(),
            onChanged: (value) => _onNodeChanged(2, value),
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            value: _selectedNode3,
            decoration: const InputDecoration(labelText: 'Node 3'),
            items: _nodeOptions.map((String value) {
              return DropdownMenuItem<String>(
                value: value,
                child: Text(value),
              );
            }).toList(),
            onChanged: (value) => _onNodeChanged(3, value),
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            value: _selectedNode4,
            decoration: const InputDecoration(labelText: 'Node 4'),
            items: _nodeOptions.map((String value) {
              return DropdownMenuItem<String>(
                value: value,
                child: Text(value),
              );
            }).toList(),
            onChanged: (value) => _onNodeChanged(4, value),
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            value: _selectedNode5,
            decoration: const InputDecoration(labelText: 'Node 5'),
            items: _nodeOptions.map((String value) {
              return DropdownMenuItem<String>(
                value: value,
                child: Text(value),
              );
            }).toList(),
            onChanged: (value) => _onNodeChanged(5, value),
          ),
          const SizedBox(height: 24),
          Text(
            'Remaining leaves: $_remainingLeaves',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 24),
          Row(
            children: [
              Expanded(
                child: FilledButton.icon(
                  onPressed: _exportCSV,
                  icon: const Icon(Icons.file_download),
                  label: const Text('Export CSV'),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: FilledButton.icon(
                  onPressed: _exportXLSX,
                  icon: const Icon(Icons.file_download),
                  label: const Text('Export XLSX'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
