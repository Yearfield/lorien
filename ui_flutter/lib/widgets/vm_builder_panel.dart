"""
VM Builder panel for creating and managing Vital Measurement drafts.

Provides UI for creating drafts, previewing changes, and publishing
VM Builder operations with diff preview.
"""

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class VMBuilderPanel extends StatefulWidget {
  final String apiBaseUrl;

  const VMBuilderPanel({
    Key? key,
    required this.apiBaseUrl,
  }) : super(key: key);

  @override
  State<VMBuilderPanel> createState() => _VMBuilderPanelState();
}

class _VMBuilderPanelState extends State<VMBuilderPanel> {
  List<Map<String, dynamic>> _drafts = [];
  Map<String, dynamic>? _selectedDraft;
  Map<String, dynamic>? _diffPlan;
  bool _isLoading = false;
  String? _error;
  int? _selectedParentId;

  @override
  void initState() {
    super.initState();
    _loadDrafts();
  }

  Future<void> _loadDrafts() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final response = await http.get(
        Uri.parse('${widget.apiBaseUrl}/api/v1/tree/vm/drafts'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _drafts = List<Map<String, dynamic>>.from(data['drafts'] ?? []);
        });
      } else {
        setState(() {
          _error = 'Failed to load drafts: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error loading drafts: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _createDraft(int parentId) async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final draftData = {
        "children": [],
        "metadata": {
          "created_by": "admin",
          "description": "New VM Builder draft"
        }
      };

      final response = await http.post(
        Uri.parse('${widget.apiBaseUrl}/api/v1/tree/vm/draft'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'parent_id': parentId,
          'draft_data': draftData,
          'actor': 'admin'
        }),
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Draft created successfully'),
            backgroundColor: Colors.green,
          ),
        );
        _loadDrafts();
      } else {
        final errorData = json.decode(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to create draft: ${errorData['detail']['message'] ?? 'Unknown error'}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error creating draft: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _loadDraft(String draftId) async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final response = await http.get(
        Uri.parse('${widget.apiBaseUrl}/api/v1/tree/vm/draft/$draftId'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _selectedDraft = data['draft'];
        });
      } else {
        setState(() {
          _error = 'Failed to load draft: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error loading draft: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _calculateDiff(String draftId) async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final response = await http.post(
        Uri.parse('${widget.apiBaseUrl}/api/v1/tree/vm/draft/$draftId/plan'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _diffPlan = data['diff'];
        });
      } else {
        final errorData = json.decode(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to calculate diff: ${errorData['detail']['message'] ?? 'Unknown error'}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error calculating diff: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _publishDraft(String draftId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Confirm Publish'),
        content: const Text('Are you sure you want to publish this draft? This will apply all changes to the tree.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Publish'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final response = await http.post(
        Uri.parse('${widget.apiBaseUrl}/api/v1/tree/vm/draft/$draftId/publish'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'actor': 'admin'}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Draft published successfully: ${data['result']['message']}'),
            backgroundColor: Colors.green,
          ),
        );
        _loadDrafts();
        _selectedDraft = null;
        _diffPlan = null;
      } else {
        final errorData = json.decode(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to publish: ${errorData['detail']['message'] ?? 'Unknown error'}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error publishing draft: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _deleteDraft(String draftId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Confirm Delete'),
        content: const Text('Are you sure you want to delete this draft? This action cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final response = await http.delete(
        Uri.parse('${widget.apiBaseUrl}/api/v1/tree/vm/draft/$draftId'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Draft deleted successfully'),
            backgroundColor: Colors.green,
          ),
        );
        _loadDrafts();
        if (_selectedDraft?['id'] == draftId) {
          _selectedDraft = null;
          _diffPlan = null;
        }
      } else {
        final errorData = json.decode(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to delete draft: ${errorData['detail']['message'] ?? 'Unknown error'}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error deleting draft: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(8.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'VM Builder',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.refresh),
                      onPressed: _isLoading ? null : _loadDrafts,
                    ),
                    ElevatedButton.icon(
                      onPressed: _isLoading ? null : _showCreateDraftDialog,
                      icon: const Icon(Icons.add),
                      label: const Text('New Draft'),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            if (_isLoading && _drafts.isEmpty)
              const Center(child: CircularProgressIndicator())
            else if (_error != null)
              Text(
                _error!,
                style: const TextStyle(color: Colors.red),
              )
            else if (_drafts.isEmpty)
              const Text('No drafts found')
            else
              _buildDraftsList(),
            
            if (_selectedDraft != null) ...[
              const SizedBox(height: 16),
              const Divider(),
              const SizedBox(height: 16),
              _buildDraftDetails(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDraftsList() {
    return Expanded(
      child: ListView.builder(
        itemCount: _drafts.length,
        itemBuilder: (context, index) {
          final draft = _drafts[index];
          return Card(
            margin: const EdgeInsets.symmetric(vertical: 4.0),
            child: ListTile(
              title: Text('Draft ${draft['id'].toString().substring(0, 8)}'),
              subtitle: Text('Parent: ${draft['parent_id']} • Status: ${draft['status']}'),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  IconButton(
                    icon: const Icon(Icons.visibility),
                    onPressed: () => _loadDraft(draft['id']),
                    tooltip: 'View Draft',
                  ),
                  IconButton(
                    icon: const Icon(Icons.delete),
                    onPressed: () => _deleteDraft(draft['id']),
                    tooltip: 'Delete Draft',
                  ),
                ],
              ),
              onTap: () => _loadDraft(draft['id']),
            ),
          );
        },
      ),
    );
  }

  Widget _buildDraftDetails() {
    if (_selectedDraft == null) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Draft Details',
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            Row(
              children: [
                ElevatedButton.icon(
                  onPressed: _isLoading ? null : () => _calculateDiff(_selectedDraft!['id']),
                  icon: const Icon(Icons.preview),
                  label: const Text('Preview Changes'),
                ),
                const SizedBox(width: 8),
                ElevatedButton.icon(
                  onPressed: _isLoading ? null : () => _publishDraft(_selectedDraft!['id']),
                  icon: const Icon(Icons.publish),
                  label: const Text('Publish'),
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 16),
        
        _buildDraftInfo(),
        
        if (_diffPlan != null) ...[
          const SizedBox(height: 16),
          _buildDiffPreview(),
        ],
      ],
    );
  }

  Widget _buildDraftInfo() {
    final draft = _selectedDraft!;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildInfoRow('ID', draft['id']),
        _buildInfoRow('Parent ID', draft['parent_id'].toString()),
        _buildInfoRow('Status', draft['status']),
        _buildInfoRow('Created', draft['created_at']),
        _buildInfoRow('Updated', draft['updated_at']),
        if (draft['published_at'] != null)
          _buildInfoRow('Published', draft['published_at']),
      ],
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(fontFamily: 'monospace'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDiffPreview() {
    if (_diffPlan == null) return const SizedBox.shrink();

    final operations = _diffPlan!['operations'] as List<dynamic>;
    final summary = _diffPlan!['summary'] as Map<String, dynamic>;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Changes Preview',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        
        _buildSummaryCard(summary),
        
        const SizedBox(height: 16),
        const Text(
          'Operations:',
          style: TextStyle(fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 8),
        
        ...operations.map((op) => _buildOperationCard(op)),
      ],
    );
  }

  Widget _buildSummaryCard(Map<String, dynamic> summary) {
    return Card(
      color: Colors.blue.shade50,
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _buildSummaryItem('Create', summary['create'] ?? 0, Colors.green),
            _buildSummaryItem('Update', summary['update'] ?? 0, Colors.orange),
            _buildSummaryItem('Delete', summary['delete'] ?? 0, Colors.red),
            _buildSummaryItem('Total', summary['total'] ?? 0, Colors.blue),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryItem(String label, int count, Color color) {
    return Column(
      children: [
        Text(
          count.toString(),
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: const TextStyle(fontSize: 12),
        ),
      ],
    );
  }

  Widget _buildOperationCard(Map<String, dynamic> operation) {
    final type = operation['type'] as String;
    Color color;
    IconData icon;

    switch (type) {
      case 'create':
        color = Colors.green;
        icon = Icons.add;
        break;
      case 'update':
        color = Colors.orange;
        icon = Icons.edit;
        break;
      case 'delete':
        color = Colors.red;
        icon = Icons.delete;
        break;
      default:
        color = Colors.grey;
        icon = Icons.help;
    }

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 2.0),
      child: ListTile(
        leading: Icon(icon, color: color),
        title: Text(
          '${type.toUpperCase()}: ${operation['label'] ?? operation['node_id']}',
          style: TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: _buildOperationDetails(operation),
      ),
    );
  }

  Widget _buildOperationDetails(Map<String, dynamic> operation) {
    final type = operation['type'] as String;
    
    switch (type) {
      case 'create':
        return Text('Slot: ${operation['slot']} • Leaf: ${operation['is_leaf']}');
      case 'update':
        return Text('${operation['old_label']} → ${operation['new_label']}');
      case 'delete':
        return Text('Slot: ${operation['slot']}');
      default:
        return Text('Node ID: ${operation['node_id']}');
    }
  }

  void _showCreateDraftDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Create New Draft'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              decoration: const InputDecoration(
                labelText: 'Parent ID',
                hintText: 'Enter parent node ID',
              ),
              keyboardType: TextInputType.number,
              onChanged: (value) {
                _selectedParentId = int.tryParse(value);
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: _selectedParentId != null
                ? () {
                    Navigator.of(context).pop();
                    _createDraft(_selectedParentId!);
                  }
                : null,
            child: const Text('Create'),
          ),
        ],
      ),
    );
  }
}
