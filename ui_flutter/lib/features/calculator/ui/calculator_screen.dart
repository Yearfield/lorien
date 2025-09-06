import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../shared/widgets/app_scaffold.dart';
import '../../../api/lorien_api.dart';
import '../../../providers/lorien_api_provider.dart';

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

  List<String> _vitalMeasurements = [];
  Map<int, List<String>> _nodeOptions = {};
  Map<String, dynamic>? _currentPath;
  bool _loading = false;

  late final LorienApi _api;

  @override
  void initState() {
    super.initState();
    _api = ref.read(lorienApiProvider);
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _loading = true);

    try {
      // Load VM data from roots endpoint
      final rootsResponse = await _api._client.getJson('tree/roots');
      final roots = rootsResponse['roots'] as List<dynamic>? ?? [];
      _vitalMeasurements = roots.map((r) => r as String).toList();

      if (_vitalMeasurements.isNotEmpty && _selectedVM == null) {
        _selectedVM = _vitalMeasurements.first;
        await _loadVMChildren();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load data: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  Future<void> _loadVMChildren() async {
    if (_selectedVM == null) return;

    try {
      // For now, we'll simulate loading children based on VM selection
      // In a real implementation, you'd have a way to get children for a specific VM
      setState(() {
        _nodeOptions = {
          1: ['Fever', 'Pain', 'Cough', 'Fatigue', 'Nausea'],
          2: ['High', 'Normal', 'Low', 'Irregular'],
          3: ['Severe', 'Moderate', 'Mild'],
          4: ['Acute', 'Chronic', 'Recurring'],
          5: ['Primary', 'Secondary', 'Complication']
        };
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load VM children: $e')),
        );
      }
    }
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
    _loadVMChildren();
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
    // Calculate remaining leaves based on selections
    // This is a simplified calculation - in practice you'd use API data
    setState(() {
      _remainingLeaves = 25 -
          (_selectedNode1 != null ? 5 : 0) -
          (_selectedNode2 != null ? 5 : 0) -
          (_selectedNode3 != null ? 5 : 0) -
          (_selectedNode4 != null ? 5 : 0) -
          (_selectedNode5 != null ? 5 : 0);
    });
  }

  Future<void> _exportCSV() async {
    try {
      final response = await _api._client.postBytes('calc/export');
      // TODO: Handle file download/save
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('CSV exported successfully')));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('Export failed: $e')));
      }
    }
  }

  Future<void> _exportXLSX() async {
    try {
      final response = await _api._client.postBytes('calc/export.xlsx');
      // TODO: Handle file download/save
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('XLSX exported successfully')));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('Export failed: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return AppScaffold(
        title: 'Calculator',
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    return AppScaffold(
      title: 'Calculator',
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Vital Measurement dropdown
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

          // Dynamic node dropdowns based on loaded data
          ...List.generate(5, (i) {
            final nodeIndex = i + 1;
            final options = _nodeOptions[nodeIndex] ?? [];
            String? selectedValue;

            switch (nodeIndex) {
              case 1: selectedValue = _selectedNode1; break;
              case 2: selectedValue = _selectedNode2; break;
              case 3: selectedValue = _selectedNode3; break;
              case 4: selectedValue = _selectedNode4; break;
              case 5: selectedValue = _selectedNode5; break;
            }

            return Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: DropdownButtonFormField<String>(
                value: selectedValue,
                decoration: InputDecoration(labelText: 'Node $nodeIndex'),
                items: options.map((String value) {
                  return DropdownMenuItem<String>(
                    value: value,
                    child: Text(value),
                  );
                }).toList(),
                onChanged: (value) => _onNodeChanged(nodeIndex, value),
              ),
            );
          }),

          const SizedBox(height: 24),

          // Path display (breadcrumb)
          if (_currentPath != null) ...[
            Text(
              'Path: ${_currentPath!['vital_measurement']} → ${(_currentPath!['nodes'] as List).join(" → ")}',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
          ],

          // Remaining leaves counter
          Text(
            'Remaining leaves: $_remainingLeaves',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 24),

          // Export buttons
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
