import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../widgets/layout/scroll_scaffold.dart';
import '../../../widgets/app_back_leading.dart';
import '../data/vm_builder_service.dart';
import '../data/vm_builder_models.dart';

class VmBuilderWizardScreen extends ConsumerStatefulWidget {
  const VmBuilderWizardScreen({super.key});

  @override
  ConsumerState<VmBuilderWizardScreen> createState() =>
      _VmBuilderWizardScreenState();
}

class _VmBuilderWizardScreenState extends ConsumerState<VmBuilderWizardScreen> {
  int _currentStep = 0;
  final _formKey = GlobalKey<FormState>();

  // Step 1: Sheet details
  final TextEditingController _sheetNameController = TextEditingController();
  bool _useTemplate = false;
  String? _selectedTemplate;

  // Step 2: Vital Measurements
  final List<VitalMeasurementDraft> _vitalMeasurements = [];
  final TextEditingController _vmController = TextEditingController();
  List<String> _existingVMs = [];
  List<Map<String, dynamic>> _availableTemplates = [];

  // Step 3: Node configuration
  VitalMeasurementDraft? _selectedVM;
  final List<TextEditingController> _nodeControllers =
      List.generate(5, (_) => TextEditingController());
  bool _autoGenerateNodes = true;

  // Step 4: Review and validation
  ValidationResult? _validationResult;
  DuplicateCheckResult? _duplicateResult;
  bool _isValidating = false;

  // Final step: Creation
  bool _isCreating = false;
  CreationResult? _creationResult;

  @override
  void initState() {
    super.initState();
    _loadExistingVMs();
    _loadTemplates();
  }

  @override
  void dispose() {
    _sheetNameController.dispose();
    _vmController.dispose();
    for (final controller in _nodeControllers) {
      controller.dispose();
    }
    super.dispose();
  }

  Future<void> _loadExistingVMs() async {
    try {
      final service = ref.read(vmBuilderServiceProvider);
      final vms = await service.getExistingVitalMeasurements();
      if (mounted) {
        setState(() => _existingVMs = vms);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load existing VMs: $e')),
        );
      }
    }
  }

  Future<void> _loadTemplates() async {
    try {
      final service = ref.read(vmBuilderServiceProvider);
      final templates = await service.getAvailableTemplates();
      if (mounted) {
        setState(() => _availableTemplates = templates);
      }
    } catch (e) {
      // Templates are optional
    }
  }

  Future<void> _validateDraft() async {
    if (_vitalMeasurements.isEmpty) return;

    setState(() => _isValidating = true);

    try {
      final draft = SheetDraft(
        name: _sheetNameController.text,
        vitalMeasurements: _vitalMeasurements,
      );

      final service = ref.read(vmBuilderServiceProvider);

      final validation = await service.validateDraft(draft);
      final duplicates = await service.checkForDuplicates(draft);

      if (mounted) {
        setState(() {
          _validationResult = validation;
          _duplicateResult = duplicates;
          _isValidating = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isValidating = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Validation failed: $e')),
        );
      }
    }
  }

  Future<void> _createSheet() async {
    setState(() => _isCreating = true);

    try {
      final draft = SheetDraft(
        name: _sheetNameController.text,
        vitalMeasurements: _vitalMeasurements,
      );

      final service = ref.read(vmBuilderServiceProvider);
      final result = await service.createSheet(draft, autoMaterialize: true);

      if (mounted) {
        setState(() {
          _creationResult = result;
          _isCreating = false;
        });

        if (result.success) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Sheet created successfully!')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isCreating = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Creation failed: $e')),
        );
      }
    }
  }

  void _addVitalMeasurement() {
    final label = _vmController.text.trim();
    if (label.isEmpty) return;

    // Check for duplicates
    final exists = _existingVMs.contains(label) ||
        _vitalMeasurements.any((vm) => vm.label == label);

    if (exists) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('"$label" already exists')),
      );
      return;
    }

    setState(() {
      _vitalMeasurements.add(VitalMeasurementDraft(label: label));
      _vmController.clear();
    });
  }

  void _removeVitalMeasurement(int index) {
    setState(() => _vitalMeasurements.removeAt(index));
  }

  void _nextStep() {
    if (_currentStep < 4) {
      setState(() => _currentStep++);
      if (_currentStep == 3) {
        _validateDraft();
      }
    }
  }

  void _previousStep() {
    if (_currentStep > 0) {
      setState(() => _currentStep--);
    }
  }

  bool _canProceedToNextStep() {
    switch (_currentStep) {
      case 0:
        return _sheetNameController.text.trim().isNotEmpty;
      case 1:
        return _vitalMeasurements.isNotEmpty;
      case 2:
        return true; // Node configuration is optional
      case 3:
        return _validationResult?.isValid == true &&
            _duplicateResult?.hasDuplicates == false;
      default:
        return false;
    }
  }

  Widget _buildStepIndicator() {
    return Row(
      children: List.generate(5, (index) {
        final isActive = index == _currentStep;
        final isCompleted = index < _currentStep;
        final isPending = index > _currentStep;

        return Expanded(
          child: Container(
            height: 4,
            margin: const EdgeInsets.symmetric(horizontal: 2),
            decoration: BoxDecoration(
              color: isCompleted
                  ? Colors.green
                  : isActive
                      ? Colors.blue
                      : Colors.grey[300],
              borderRadius: BorderRadius.circular(2),
            ),
          ),
        );
      }),
    );
  }

  Widget _buildStep1SheetDetails() {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Step 1: Sheet Details',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _sheetNameController,
            decoration: const InputDecoration(
              labelText: 'Sheet Name',
              hintText: 'Enter a name for your new sheet',
              border: OutlineInputBorder(),
            ),
            validator: (value) {
              if (value?.trim().isEmpty ?? true) {
                return 'Sheet name is required';
              }
              return null;
            },
          ),
          const SizedBox(height: 16),
          SwitchListTile(
            title: const Text('Use Template'),
            subtitle: const Text('Start with a predefined template'),
            value: _useTemplate,
            onChanged: (value) => setState(() => _useTemplate = value),
          ),
          if (_useTemplate && _availableTemplates.isNotEmpty) ...[
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              decoration: const InputDecoration(
                labelText: 'Select Template',
                border: OutlineInputBorder(),
              ),
              initialValue: _selectedTemplate,
              items: _availableTemplates.map((template) {
                return DropdownMenuItem(
                  value: template['id'] as String,
                  child: Text(template['name'] as String),
                );
              }).toList(),
              onChanged: (value) => setState(() => _selectedTemplate = value),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildStep2VitalMeasurements() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Step 2: Vital Measurements',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: _vmController,
                decoration: const InputDecoration(
                  labelText: 'Vital Measurement',
                  hintText: 'Enter VM name',
                  border: OutlineInputBorder(),
                ),
                onSubmitted: (_) => _addVitalMeasurement(),
              ),
            ),
            const SizedBox(width: 16),
            ElevatedButton.icon(
              onPressed: _addVitalMeasurement,
              icon: const Icon(Icons.add),
              label: const Text('Add'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        if (_vitalMeasurements.isNotEmpty) ...[
          const Text('Added Vital Measurements:',
              style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Container(
            constraints: const BoxConstraints(maxHeight: 200),
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey[300]!),
              borderRadius: BorderRadius.circular(8),
            ),
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: _vitalMeasurements.length,
              itemBuilder: (context, index) {
                final vm = _vitalMeasurements[index];
                return ListTile(
                  title: Text(vm.label),
                  trailing: IconButton(
                    icon: const Icon(Icons.delete),
                    onPressed: () => _removeVitalMeasurement(index),
                  ),
                );
              },
            ),
          ),
        ],
        if (_existingVMs.isNotEmpty) ...[
          const SizedBox(height: 16),
          const Text('Existing Vital Measurements:',
              style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 4,
            children: _existingVMs.take(10).map((vm) {
              return Chip(
                label: Text(vm),
                backgroundColor: Colors.grey[200],
              );
            }).toList(),
          ),
        ],
      ],
    );
  }

  Widget _buildStep3NodeConfiguration() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Step 3: Node Configuration (Optional)',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        SwitchListTile(
          title: const Text('Auto-generate Node 1'),
          subtitle: const Text('Automatically create basic Node 1 entries'),
          value: _autoGenerateNodes,
          onChanged: (value) => setState(() => _autoGenerateNodes = value),
        ),
        if (!_autoGenerateNodes) ...[
          const SizedBox(height: 16),
          const Text('Configure Node 1 for each Vital Measurement:',
              style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          ...List.generate(_vitalMeasurements.length, (index) {
            final vm = _vitalMeasurements[index];
            return Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(vm.label,
                        style: const TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    ...List.generate(5, (nodeIndex) {
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: TextField(
                          decoration: InputDecoration(
                            labelText: 'Node 1 - Slot ${nodeIndex + 1}',
                            border: const OutlineInputBorder(),
                          ),
                          onChanged: (value) {
                            // Update VM with node data
                            final nodes = List<NodeDraft>.from(vm.nodes ?? []);
                            if (nodes.length <= nodeIndex) {
                              nodes.addAll(List.generate(
                                nodeIndex - nodes.length + 1,
                                (i) => NodeDraft(
                                  depth: 1,
                                  slot: i + nodes.length + 1,
                                  label: '',
                                ),
                              ));
                            }
                            nodes[nodeIndex] =
                                nodes[nodeIndex].copyWith(label: value);
                            _vitalMeasurements[index] =
                                vm.copyWith(nodes: nodes);
                          },
                        ),
                      );
                    }),
                  ],
                ),
              ),
            );
          }),
        ],
      ],
    );
  }

  Widget _buildStep4Review() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Step 4: Review & Validation',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        if (_isValidating)
          const Center(child: CircularProgressIndicator())
        else ...[
          _buildValidationSummary(),
          const SizedBox(height: 16),
          _buildDraftSummary(),
        ],
      ],
    );
  }

  Widget _buildValidationSummary() {
    if (_validationResult == null) return const SizedBox.shrink();

    return Card(
      color: _validationResult!.isValid ? Colors.green[50] : Colors.red[50],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  _validationResult!.isValid ? Icons.check_circle : Icons.error,
                  color: _validationResult!.isValid ? Colors.green : Colors.red,
                ),
                const SizedBox(width: 8),
                Text(
                  _validationResult!.isValid
                      ? 'Validation Passed'
                      : 'Validation Failed',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
            if (_validationResult!.errors != null &&
                _validationResult!.errors!.isNotEmpty) ...[
              const SizedBox(height: 8),
              const Text('Errors:',
                  style: TextStyle(fontWeight: FontWeight.bold)),
              ..._validationResult!.errors!.map((error) => Text('• $error')),
            ],
            if (_duplicateResult != null &&
                _duplicateResult!.hasDuplicates) ...[
              const SizedBox(height: 8),
              const Text('Duplicates:',
                  style: TextStyle(fontWeight: FontWeight.bold)),
              ..._duplicateResult!.duplicateLabels!
                  .map((label) => Text('• $label')),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDraftSummary() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Draft Summary',
                style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text('Sheet Name: ${_sheetNameController.text}'),
            Text('Vital Measurements: ${_vitalMeasurements.length}'),
            ..._vitalMeasurements.map((vm) => Text('• ${vm.label}')),
          ],
        ),
      ),
    );
  }

  Widget _buildStep5Creation() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Step 5: Create Sheet',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        if (_isCreating)
          const Center(child: CircularProgressIndicator())
        else if (_creationResult != null)
          _buildCreationResult()
        else
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  const Text('Ready to create your new sheet!'),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    onPressed: _createSheet,
                    icon: const Icon(Icons.build),
                    label: const Text('Create Sheet'),
                  ),
                ],
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildCreationResult() {
    final result = _creationResult!;
    return Card(
      color: result.success ? Colors.green[50] : Colors.red[50],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  result.success ? Icons.check_circle : Icons.error,
                  color: result.success ? Colors.green : Colors.red,
                ),
                const SizedBox(width: 8),
                Text(
                  result.success
                      ? 'Sheet Created Successfully!'
                      : 'Creation Failed',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
            if (result.materializationResult != null) ...[
              const SizedBox(height: 16),
              const Text('Materialization Results:',
                  style: TextStyle(fontWeight: FontWeight.bold)),
              Text('Added: ${result.materializationResult!.added}'),
              Text('Filled: ${result.materializationResult!.filled}'),
              Text('Pruned: ${result.materializationResult!.pruned}'),
              Text('Kept: ${result.materializationResult!.kept}'),
            ],
            if (result.errors != null && result.errors!.isNotEmpty) ...[
              const SizedBox(height: 16),
              const Text('Errors:',
                  style: TextStyle(fontWeight: FontWeight.bold)),
              ...result.errors!.map((error) => Text('• $error')),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStepContent() {
    switch (_currentStep) {
      case 0:
        return _buildStep1SheetDetails();
      case 1:
        return _buildStep2VitalMeasurements();
      case 2:
        return _buildStep3NodeConfiguration();
      case 3:
        return _buildStep4Review();
      case 4:
        return _buildStep5Creation();
      default:
        return const SizedBox.shrink();
    }
  }

  @override
  Widget build(BuildContext context) {
    return ScrollScaffold(
      title: 'VM Builder Wizard',
      leading: const AppBackLeading(),
      children: [
        // Progress indicator
        _buildStepIndicator(),
        const SizedBox(height: 24),

        // Step content
        Expanded(child: _buildStepContent()),

        // Navigation buttons
        const SizedBox(height: 24),
        Row(
          children: [
            if (_currentStep > 0)
              ElevatedButton.icon(
                onPressed: _previousStep,
                icon: const Icon(Icons.arrow_back),
                label: const Text('Previous'),
              ),
            const Spacer(),
            if (_currentStep < 4)
              ElevatedButton.icon(
                onPressed: _canProceedToNextStep() ? _nextStep : null,
                icon: const Icon(Icons.arrow_forward),
                label: const Text('Next'),
              ),
            if (_currentStep == 4 && _creationResult?.success == true)
              ElevatedButton.icon(
                onPressed: () => Navigator.of(context).pop(),
                icon: const Icon(Icons.done),
                label: const Text('Finish'),
              ),
          ],
        ),
      ],
    );
  }
}
