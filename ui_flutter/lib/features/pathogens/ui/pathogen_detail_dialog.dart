import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lorien/features/pathogens/models/pathogen_models.dart';
import 'package:lorien/features/pathogens/providers/pathogen_providers.dart';
import 'package:lorien/features/pathogens/services/pathogen_service.dart';

class PathogenDetailDialog extends ConsumerStatefulWidget {
  final Pathogen pathogen;

  const PathogenDetailDialog({
    super.key,
    required this.pathogen,
  });

  @override
  ConsumerState<PathogenDetailDialog> createState() => _PathogenDetailDialogState();
}

class _PathogenDetailDialogState extends ConsumerState<PathogenDetailDialog> {
  bool _isEditingName = false;
  bool _isEditingBasicInfo = false;
  bool _isEditingTransmission = false;

  // Controllers for editing
  late TextEditingController _nameController;
  late TextEditingController _classificationController;
  late TextEditingController _ntController;
  late TextEditingController _pathogenIdController;
  late TextEditingController _vaccineController;
  late TextEditingController _toxinController;
  late TextEditingController _transmissionController;
  late TextEditingController _abResistanceController;
  late TextEditingController _hostController;
  late TextEditingController _commensalController;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.pathogen.pathogenName);
    _classificationController = TextEditingController(text: widget.pathogen.classification ?? '');
    _ntController = TextEditingController(text: widget.pathogen.nt ?? '');
    _pathogenIdController = TextEditingController(text: widget.pathogen.pathogenId ?? '');
    _vaccineController = TextEditingController(text: widget.pathogen.vaccine ?? '');
    _toxinController = TextEditingController(text: widget.pathogen.toxin ?? '');
    _transmissionController = TextEditingController(text: widget.pathogen.transmission ?? '');
    _abResistanceController = TextEditingController(text: widget.pathogen.abResistance ?? '');
    _hostController = TextEditingController(text: widget.pathogen.host ?? '');
    _commensalController = TextEditingController(text: widget.pathogen.commensal ?? '');
  }

  @override
  void dispose() {
    _nameController.dispose();
    _classificationController.dispose();
    _ntController.dispose();
    _pathogenIdController.dispose();
    _vaccineController.dispose();
    _toxinController.dispose();
    _transmissionController.dispose();
    _abResistanceController.dispose();
    _hostController.dispose();
    _commensalController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final pathogenDetail = ref.watch(pathogenDetailProvider(widget.pathogen.id));

    return AlertDialog(
      title: _isEditingName
          ? Row(
              children: [
                const Icon(Icons.bug_report, color: Colors.red),
                const SizedBox(width: 8),
                Expanded(
                  child: TextField(
                    controller: _nameController,
                    style: const TextStyle(fontSize: 18),
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                      isDense: true,
                    ),
                  ),
                ),
                IconButton(
                  onPressed: _saveName,
                  icon: const Icon(Icons.check, color: Colors.green),
                ),
                IconButton(
                  onPressed: _cancelEditName,
                  icon: const Icon(Icons.close, color: Colors.red),
                ),
              ],
            )
          : Row(
              children: [
                const Icon(Icons.bug_report, color: Colors.red),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    widget.pathogen.pathogenName,
                    style: const TextStyle(fontSize: 18),
                  ),
                ),
                IconButton(
                  onPressed: () => setState(() => _isEditingName = true),
                  icon: const Icon(Icons.edit, color: Colors.blue),
                ),
              ],
            ),
      content: SizedBox(
        width: 600,
        height: 500,
        child: pathogenDetail.when(
          data: (data) => _buildContent(context, data),
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stack) => Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.error, size: 48, color: Colors.red),
                const SizedBox(height: 16),
                Text('Error loading pathogen details: $error'),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => ref.refresh(pathogenDetailProvider(widget.pathogen.id)),
                  child: const Text('Retry'),
                ),
              ],
            ),
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Close'),
        ),
      ],
    );
  }

  Widget _buildContent(BuildContext context, PathogenWithAssociations? data) {
    if (data == null) {
      return const Center(
        child: Text('Pathogen not found'),
      );
    }

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Basic information
          _buildEditableSection(
            'Basic Information',
            Icons.info,
            _isEditingBasicInfo,
            () => setState(() => _isEditingBasicInfo = true),
            () => _saveBasicInfo(),
            () => _cancelEditBasicInfo(),
            [
              _buildEditableRow('Classification', data.classification, _classificationController, _isEditingBasicInfo),
              _buildEditableRow('NT', data.nt, _ntController, _isEditingBasicInfo),
              _buildEditableRow('Pathogen ID', data.pathogenId, _pathogenIdController, _isEditingBasicInfo),
              _buildEditableRow('Vaccine', data.vaccine, _vaccineController, _isEditingBasicInfo),
              _buildEditableRow('Toxin', data.toxin, _toxinController, _isEditingBasicInfo),
            ],
          ),

          const SizedBox(height: 16),

          // Transmission and resistance
          _buildEditableSection(
            'Transmission & Resistance',
            Icons.warning,
            _isEditingTransmission,
            () => setState(() => _isEditingTransmission = true),
            () => _saveTransmission(),
            () => _cancelEditTransmission(),
            [
              _buildEditableRow('Transmission', data.transmission, _transmissionController, _isEditingTransmission, maxLines: 3),
              _buildEditableRow('Antibiotic Resistance', data.abResistance, _abResistanceController, _isEditingTransmission),
              _buildEditableRow('Host', data.host, _hostController, _isEditingTransmission),
              _buildEditableRow('Commensal', data.commensal, _commensalController, _isEditingTransmission),
            ],
          ),

          const SizedBox(height: 16),

          // Clinical information
          _buildSection(
            'Clinical Information',
            Icons.medical_services,
            [
              _buildInfoRow('Disease', data.disease),
              _buildInfoRow('Incubation', data.incubation),
              _buildInfoRow('Diagnosis', data.diagnosis),
              _buildInfoRow('Treatment', data.treatment),
              _buildInfoRow('Prevention', data.prevention),
            ],
          ),

          if (data.notes != null && data.notes!.isNotEmpty) ...[
            const SizedBox(height: 16),
            _buildSection(
              'Notes',
              Icons.note,
              [
                _buildInfoRow('Notes', data.notes),
              ],
            ),
          ],

          const SizedBox(height: 16),

          // Associations
          _buildSection(
            'Associations',
            Icons.link,
            data.associations
                .where((assoc) => assoc.value == 1)
                .map((assoc) => _buildAssociationRow(assoc))
                .toList(),
          ),

          const SizedBox(height: 16),

          // Metadata
          _buildSection(
            'Metadata',
            Icons.access_time,
            [
              _buildInfoRow('Created', _formatDate(data.createdAt)),
              _buildInfoRow('Updated', _formatDate(data.updatedAt)),
            ],
          ),
        ],
      ),
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
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.grey.shade50,
            border: Border.all(color: Colors.grey.shade300),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: children.isEmpty
                ? [
                    const Text(
                      'No information available',
                      style: TextStyle(
                        fontStyle: FontStyle.italic,
                        color: Colors.grey,
                      ),
                    ),
                  ]
                : children,
          ),
        ),
      ],
    );
  }

  Widget _buildInfoRow(String label, String? value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(
            child: Text(
              value ?? 'Not specified',
              style: TextStyle(
                color: value != null ? Colors.black : Colors.grey,
                fontStyle: value != null ? FontStyle.normal : FontStyle.italic,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAssociationRow(PathogenAssociation association) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          const Icon(Icons.check_circle, size: 16, color: Colors.green),
          const SizedBox(width: 8),
          Text(
            association.associationTypeName ?? 'Unknown Association',
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }

  String _formatDate(String dateString) {
    try {
      final date = DateTime.parse(dateString);
      return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return dateString;
    }
  }

  Widget _buildEditableSection(
    String title,
    IconData icon,
    bool isEditing,
    VoidCallback onEdit,
    VoidCallback onSave,
    VoidCallback onCancel,
    List<Widget> children,
  ) {
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
            const Spacer(),
            if (!isEditing)
              IconButton(
                onPressed: onEdit,
                icon: const Icon(Icons.edit, size: 16),
                tooltip: 'Edit $title',
              )
            else ...[
              IconButton(
                onPressed: onSave,
                icon: const Icon(Icons.check, color: Colors.green, size: 16),
                tooltip: 'Save changes',
              ),
              IconButton(
                onPressed: onCancel,
                icon: const Icon(Icons.close, color: Colors.red, size: 16),
                tooltip: 'Cancel editing',
              ),
            ],
          ],
        ),
        const SizedBox(height: 8),
        ...children,
      ],
    );
  }

  Widget _buildEditableRow(String label, String? value, TextEditingController controller, bool isEditing, {int maxLines = 1}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: isEditing
                ? TextField(
                    controller: controller,
                    maxLines: maxLines,
                    decoration: InputDecoration(
                      border: const OutlineInputBorder(),
                      isDense: true,
                      contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                    ),
                  )
                : Text(
                    value ?? 'Not specified',
                    style: TextStyle(
                      color: value == null ? Colors.grey : null,
                    ),
                  ),
          ),
        ],
      ),
    );
  }

  void _saveName() {
    // TODO: Implement save name API call
    setState(() => _isEditingName = false);
  }

  void _cancelEditName() {
    _nameController.text = widget.pathogen.pathogenName;
    setState(() => _isEditingName = false);
  }

  void _saveBasicInfo() {
    // TODO: Implement save basic info API call
    setState(() => _isEditingBasicInfo = false);
  }

  void _cancelEditBasicInfo() {
    _classificationController.text = widget.pathogen.classification ?? '';
    _ntController.text = widget.pathogen.nt ?? '';
    _pathogenIdController.text = widget.pathogen.pathogenId ?? '';
    _vaccineController.text = widget.pathogen.vaccine ?? '';
    _toxinController.text = widget.pathogen.toxin ?? '';
    setState(() => _isEditingBasicInfo = false);
  }

  void _saveTransmission() {
    // TODO: Implement save transmission API call
    setState(() => _isEditingTransmission = false);
  }

  void _cancelEditTransmission() {
    _transmissionController.text = widget.pathogen.transmission ?? '';
    _abResistanceController.text = widget.pathogen.abResistance ?? '';
    _hostController.text = widget.pathogen.host ?? '';
    _commensalController.text = widget.pathogen.commensal ?? '';
    setState(() => _isEditingTransmission = false);
  }
}
