import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lorien/features/pathogens/models/pathogen_models.dart';
import 'package:lorien/features/pathogens/providers/pathogen_providers.dart';

class PathogenCreateDialog extends ConsumerStatefulWidget {
  const PathogenCreateDialog({super.key});

  @override
  ConsumerState<PathogenCreateDialog> createState() => _PathogenCreateDialogState();
}

class _PathogenCreateDialogState extends ConsumerState<PathogenCreateDialog> {
  final _formKey = GlobalKey<FormState>();
  final _pathogenNameController = TextEditingController();
  final _classificationController = TextEditingController();
  final _ntController = TextEditingController();
  final _pathogenIdController = TextEditingController();
  final _vaccineController = TextEditingController();
  final _toxinController = TextEditingController();
  final _transmissionController = TextEditingController();
  final _abResistanceController = TextEditingController();
  final _hostController = TextEditingController();
  final _commensalController = TextEditingController();
  final _diseaseController = TextEditingController();
  final _incubationController = TextEditingController();
  final _diagnosisController = TextEditingController();
  final _treatmentController = TextEditingController();
  final _preventionController = TextEditingController();
  final _notesController = TextEditingController();

  bool _isLoading = false;

  @override
  void dispose() {
    _pathogenNameController.dispose();
    _classificationController.dispose();
    _ntController.dispose();
    _pathogenIdController.dispose();
    _vaccineController.dispose();
    _toxinController.dispose();
    _transmissionController.dispose();
    _abResistanceController.dispose();
    _hostController.dispose();
    _commensalController.dispose();
    _diseaseController.dispose();
    _incubationController.dispose();
    _diagnosisController.dispose();
    _treatmentController.dispose();
    _preventionController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Row(
        children: [
          Icon(Icons.add_circle, color: Colors.green),
          SizedBox(width: 8),
          Text('Create New Pathogen'),
        ],
      ),
      content: SizedBox(
        width: 600,
        height: 500,
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Basic Information
                _buildSection(
                  'Basic Information',
                  Icons.info,
                  [
                    _buildTextField('Pathogen Name *', _pathogenNameController, required: true),
                    _buildTextField('Classification', _classificationController),
                    _buildTextField('NT', _ntController),
                    _buildTextField('Pathogen ID', _pathogenIdController),
                    _buildTextField('Vaccine', _vaccineController),
                    _buildTextField('Toxin', _toxinController),
                  ],
                ),
                const SizedBox(height: 16),
                // Transmission & Resistance
                _buildSection(
                  'Transmission & Resistance',
                  Icons.warning,
                  [
                    _buildTextField('Transmission', _transmissionController, maxLines: 3),
                    _buildTextField('Antibiotic Resistance', _abResistanceController),
                    _buildTextField('Host', _hostController),
                    _buildTextField('Commensal', _commensalController),
                  ],
                ),
                const SizedBox(height: 16),
                // Clinical Information
                _buildSection(
                  'Clinical Information',
                  Icons.medical_services,
                  [
                    _buildTextField('Disease', _diseaseController, maxLines: 3),
                    _buildTextField('Incubation', _incubationController),
                    _buildTextField('Diagnosis', _diagnosisController, maxLines: 3),
                    _buildTextField('Treatment', _treatmentController, maxLines: 3),
                    _buildTextField('Prevention', _preventionController),
                  ],
                ),
                const SizedBox(height: 16),
                // Notes
                _buildSection(
                  'Notes',
                  Icons.note,
                  [
                    _buildTextField('Notes', _notesController, maxLines: 3),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: _isLoading ? null : () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _isLoading ? null : _handleCreate,
          child: _isLoading
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Create'),
        ),
      ],
    );
  }

  Widget _buildSection(String title, IconData icon, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 20, color: Colors.blue),
            const SizedBox(width: 8),
            Text(
              title,
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ...children,
      ],
    );
  }

  Widget _buildTextField(String label, TextEditingController controller, {bool required = false, int maxLines = 1}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: TextFormField(
        controller: controller,
        maxLines: maxLines,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
          isDense: true,
        ),
        validator: required
            ? (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'This field is required';
                }
                return null;
              }
            : null,
      ),
    );
  }

  Future<void> _handleCreate() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final properties = PathogenProperties(
        classification: _classificationController.text.trim().isEmpty ? null : _classificationController.text.trim(),
        nt: _ntController.text.trim().isEmpty ? null : _ntController.text.trim(),
        pathogenId: _pathogenIdController.text.trim().isEmpty ? null : _pathogenIdController.text.trim(),
        pathogenName: _pathogenNameController.text.trim(),
        vaccine: _vaccineController.text.trim().isEmpty ? null : _vaccineController.text.trim(),
        toxin: _toxinController.text.trim().isEmpty ? null : _toxinController.text.trim(),
        transmission: _transmissionController.text.trim().isEmpty ? null : _transmissionController.text.trim(),
        abResistance: _abResistanceController.text.trim().isEmpty ? null : _abResistanceController.text.trim(),
        host: _hostController.text.trim().isEmpty ? null : _hostController.text.trim(),
        commensal: _commensalController.text.trim().isEmpty ? null : _commensalController.text.trim(),
        disease: _diseaseController.text.trim().isEmpty ? null : _diseaseController.text.trim(),
        incubation: _incubationController.text.trim().isEmpty ? null : _incubationController.text.trim(),
        diagnosis: _diagnosisController.text.trim().isEmpty ? null : _diagnosisController.text.trim(),
        treatment: _treatmentController.text.trim().isEmpty ? null : _treatmentController.text.trim(),
        prevention: _preventionController.text.trim().isEmpty ? null : _preventionController.text.trim(),
        notes: _notesController.text.trim().isEmpty ? null : _notesController.text.trim(),
      );

      // TODO: Implement create pathogen API call
      // await ref.read(pathogenListProvider.notifier).createPathogen(properties);

      if (mounted) {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Pathogen created successfully')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error creating pathogen: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }
}
