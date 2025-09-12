import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:dio/dio.dart';

import '../../../core/http/api_client.dart';
import '../../../widgets/layout/scroll_scaffold.dart';
import '../../../widgets/app_back_leading.dart';
import '../../../widgets/loading_indicator.dart';
import '../../../widgets/error_display.dart';
import 'vm_builder_enhanced_models.dart';
import 'vm_builder_enhanced_service.dart';

class VMBuilderEnhancedScreen extends ConsumerStatefulWidget {
  final String baseUrl;
  final Dio? client;
  
  const VMBuilderEnhancedScreen({
    super.key, 
    this.baseUrl = 'http://127.0.0.1:8000', 
    this.client
  });
  
  @override
  ConsumerState<VMBuilderEnhancedScreen> createState() => _VMBuilderEnhancedScreenState();
}

class _VMBuilderEnhancedScreenState extends ConsumerState<VMBuilderEnhancedScreen>
    with TickerProviderStateMixin {
  
  late TabController _tabController;
  late VMBuilderEnhancedService _service;
  
  // State
  List<VMBuilderDraft> _drafts = [];
  bool _isLoading = false;
  String? _error;
  VMBuilderStats? _stats;
  
  // Filters
  String? _statusFilter;
  int? _parentIdFilter;
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _service = VMBuilderEnhancedService(widget.client ?? ref.read(dioProvider));
    _loadData();
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }
  
  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    
    try {
      final futures = await Future.wait([
        _service.getDrafts(status: _statusFilter, parentId: _parentIdFilter),
        _service.getStats(),
      ]);
      
      if (mounted) {
        setState(() {
          _drafts = futures[0] as List<VMBuilderDraft>;
          _stats = futures[1] as VMBuilderStats;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }
  
  Future<void> _createDraft(int parentId) async {
    try {
      final draftData = {
        'children': [],
        'metadata': {
          'created_via': 'ui',
          'version': '1.0'
        }
      };
      
      final draft = await _service.createDraft(
        parentId: parentId,
        draftData: draftData,
        metadata: {'created_via': 'ui'}
      );
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Draft created: ${draft.id}')),
        );
        _loadData();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to create draft: $e')),
        );
      }
    }
  }
  
  Future<void> _planDraft(String draftId) async {
    try {
      final plan = await _service.planDraft(draftId);
      
      if (mounted) {
        showDialog(
          context: context,
          builder: (context) => VMBuilderPlanDialog(plan: plan),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to plan draft: $e')),
        );
      }
    }
  }
  
  Future<void> _publishDraft(String draftId, {bool force = false}) async {
    try {
      final result = await _service.publishDraft(draftId, force: force);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Draft published: ${result.operationsApplied} operations applied')),
        );
        _loadData();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to publish draft: $e')),
        );
      }
    }
  }
  
  Future<void> _deleteDraft(String draftId) async {
    try {
      await _service.deleteDraft(draftId);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Draft deleted')),
        );
        _loadData();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to delete draft: $e')),
        );
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return ScrollScaffold(
      title: 'VM Builder Enhanced',
      leading: const AppBackLeading(),
      actions: [
        IconButton(
          icon: const Icon(Icons.refresh),
          onPressed: _loadData,
        ),
        PopupMenuButton<String>(
          onSelected: (value) {
            setState(() {
              _statusFilter = value == 'all' ? null : value;
            });
            _loadData();
          },
          itemBuilder: (context) => [
            const PopupMenuItem(value: 'all', child: Text('All Statuses')),
            const PopupMenuItem(value: 'draft', child: Text('Draft')),
            const PopupMenuItem(value: 'planning', child: Text('Planning')),
            const PopupMenuItem(value: 'ready_to_publish', child: Text('Ready to Publish')),
            const PopupMenuItem(value: 'published', child: Text('Published')),
            const PopupMenuItem(value: 'failed', child: Text('Failed')),
          ],
        ),
      ],
      children: [
        // Stats overview
        if (_stats != null) _buildStatsOverview(),
        
        const SizedBox(height: 16),
        
        // Tab bar
        TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Drafts', icon: Icon(Icons.edit)),
            Tab(text: 'Planning', icon: Icon(Icons.analytics)),
            Tab(text: 'Published', icon: Icon(Icons.publish)),
          ],
        ),
        
        const SizedBox(height: 16),
        
        // Tab content
        Expanded(
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildDraftsTab(),
              _buildPlanningTab(),
              _buildPublishedTab(),
            ],
          ),
        ),
      ],
    );
  }
  
  Widget _buildStatsOverview() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'VM Builder Statistics',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _buildStatCard('Total Drafts', _stats!.totalDrafts.toString()),
                const SizedBox(width: 16),
                _buildStatCard('Published', _stats!.publishedDrafts.toString()),
                const SizedBox(width: 16),
                _buildStatCard('Recent (7d)', _stats!.recentDrafts.toString()),
              ],
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              children: _stats!.statusCounts.entries.map((entry) {
                return Chip(
                  label: Text('${entry.key}: ${entry.value}'),
                  backgroundColor: _getStatusColor(entry.key).withOpacity(0.1),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildStatCard(String label, String value) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.blue.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          children: [
            Text(
              value,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            Text(
              label,
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildDraftsTab() {
    if (_isLoading) {
      return const Center(child: LoadingIndicator());
    }
    
    if (_error != null) {
      return ErrorDisplay(
        error: _error!,
        onRetry: _loadData,
      );
    }
    
    if (_drafts.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.edit, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              'No drafts found',
              style: TextStyle(fontSize: 18, color: Colors.grey),
            ),
            SizedBox(height: 8),
            Text(
              'Create a new draft to get started',
              style: TextStyle(color: Colors.grey),
            ),
          ],
        ),
      );
    }
    
    return ListView.builder(
      itemCount: _drafts.length,
      itemBuilder: (context, index) {
        final draft = _drafts[index];
        return _buildDraftCard(draft);
      },
    );
  }
  
  Widget _buildDraftCard(VMBuilderDraft draft) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getStatusColor(draft.status),
          child: Icon(
            _getStatusIcon(draft.status),
            color: Colors.white,
          ),
        ),
        title: Text('Draft ${draft.id.substring(0, 8)}'),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Parent ID: ${draft.parentId}'),
            Text('Status: ${draft.status}'),
            Text('Updated: ${_formatDateTime(draft.updatedAt)}'),
          ],
        ),
        trailing: PopupMenuButton<String>(
          onSelected: (value) {
            switch (value) {
              case 'plan':
                _planDraft(draft.id);
                break;
              case 'publish':
                _publishDraft(draft.id);
                break;
              case 'delete':
                _deleteDraft(draft.id);
                break;
            }
          },
          itemBuilder: (context) => [
            if (draft.status == 'draft' || draft.status == 'planning')
              const PopupMenuItem(value: 'plan', child: Text('Plan')),
            if (draft.status == 'ready_to_publish')
              const PopupMenuItem(value: 'publish', child: Text('Publish')),
            if (draft.status != 'published')
              const PopupMenuItem(value: 'delete', child: Text('Delete')),
          ],
        ),
        onTap: () {
          // Navigate to draft detail
          context.go('/vm-builder/draft/${draft.id}');
        },
      ),
    );
  }
  
  Widget _buildPlanningTab() {
    final planningDrafts = _drafts.where((d) => 
      d.status == 'planning' || d.status == 'ready_to_publish'
    ).toList();
    
    if (planningDrafts.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.analytics, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              'No drafts in planning',
              style: TextStyle(fontSize: 18, color: Colors.grey),
            ),
          ],
        ),
      );
    }
    
    return ListView.builder(
      itemCount: planningDrafts.length,
      itemBuilder: (context, index) {
        final draft = planningDrafts[index];
        return _buildDraftCard(draft);
      },
    );
  }
  
  Widget _buildPublishedTab() {
    final publishedDrafts = _drafts.where((d) => d.status == 'published').toList();
    
    if (publishedDrafts.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.publish, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              'No published drafts',
              style: TextStyle(fontSize: 18, color: Colors.grey),
            ),
          ],
        ),
      );
    }
    
    return ListView.builder(
      itemCount: publishedDrafts.length,
      itemBuilder: (context, index) {
        final draft = publishedDrafts[index];
        return _buildDraftCard(draft);
      },
    );
  }
  
  Color _getStatusColor(String status) {
    switch (status) {
      case 'draft':
        return Colors.blue;
      case 'planning':
        return Colors.orange;
      case 'ready_to_publish':
        return Colors.green;
      case 'published':
        return Colors.purple;
      case 'failed':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
  
  IconData _getStatusIcon(String status) {
    switch (status) {
      case 'draft':
        return Icons.edit;
      case 'planning':
        return Icons.analytics;
      case 'ready_to_publish':
        return Icons.check_circle;
      case 'published':
        return Icons.publish;
      case 'failed':
        return Icons.error;
      default:
        return Icons.help;
    }
  }
  
  String _formatDateTime(String dateTime) {
    try {
      final dt = DateTime.parse(dateTime);
      return '${dt.day}/${dt.month}/${dt.year} ${dt.hour}:${dt.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return dateTime;
    }
  }
}

class VMBuilderPlanDialog extends StatelessWidget {
  final VMBuilderPlan plan;
  
  const VMBuilderPlanDialog({
    super.key,
    required this.plan,
  });
  
  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: Container(
        width: MediaQuery.of(context).size.width * 0.8,
        height: MediaQuery.of(context).size.height * 0.8,
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Text(
                  'Draft Plan',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // Plan summary
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Operations: ${plan.summary['total']}'),
                    Text('Can Publish: ${plan.canPublish ? 'Yes' : 'No'}'),
                    Text('Estimated Impact: ${plan.estimatedImpact}'),
                    if (plan.warnings.isNotEmpty) ...[
                      const SizedBox(height: 8),
                      const Text('Warnings:', style: TextStyle(fontWeight: FontWeight.bold)),
                      ...plan.warnings.map((w) => Text('• $w')),
                    ],
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Operations list
            const Text(
              'Operations',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            
            Expanded(
              child: ListView.builder(
                itemCount: plan.operations.length,
                itemBuilder: (context, index) {
                  final operation = plan.operations[index];
                  return _buildOperationCard(operation);
                },
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Action buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('Close'),
                ),
                const SizedBox(width: 8),
                if (plan.canPublish)
                  ElevatedButton(
                    onPressed: () {
                      Navigator.of(context).pop();
                      // TODO: Implement publish action
                    },
                    child: const Text('Publish'),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildOperationCard(VMBuilderOperation operation) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getOperationColor(operation.type),
          child: Icon(
            _getOperationIcon(operation.type),
            color: Colors.white,
            size: 16,
          ),
        ),
        title: Text(operation.description),
        subtitle: Text('Impact: ${operation.impactLevel}'),
        trailing: Chip(
          label: Text(operation.type.toUpperCase()),
          backgroundColor: _getOperationColor(operation.type).withOpacity(0.1),
        ),
      ),
    );
  }
  
  Color _getOperationColor(String type) {
    switch (type) {
      case 'create':
        return Colors.green;
      case 'update':
        return Colors.blue;
      case 'delete':
        return Colors.red;
      case 'move':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }
  
  IconData _getOperationIcon(String type) {
    switch (type) {
      case 'create':
        return Icons.add;
      case 'update':
        return Icons.edit;
      case 'delete':
        return Icons.delete;
      case 'move':
        return Icons.swap_horiz;
      default:
        return Icons.help;
    }
  }
}
