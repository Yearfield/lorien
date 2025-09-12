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
import 'large_workbook_models.dart';
import 'large_workbook_service.dart';

class LargeWorkbookScreen extends ConsumerStatefulWidget {
  final String baseUrl;
  final Dio? client;
  
  const LargeWorkbookScreen({
    super.key, 
    this.baseUrl = 'http://127.0.0.1:8000', 
    this.client
  });
  
  @override
  ConsumerState<LargeWorkbookScreen> createState() => _LargeWorkbookScreenState();
}

class _LargeWorkbookScreenState extends ConsumerState<LargeWorkbookScreen>
    with TickerProviderStateMixin {
  
  late TabController _tabController;
  late LargeWorkbookService _service;
  
  // State
  List<LargeImportJob> _jobs = [];
  bool _isLoading = false;
  String? _error;
  Map<String, ImportProgress> _progressCache = {};
  
  // Filters
  String? _statusFilter;
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _service = LargeWorkbookService(widget.client ?? ref.read(dioProvider));
    _loadJobs();
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }
  
  Future<void> _loadJobs() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    
    try {
      final jobs = await _service.listImportJobs(status: _statusFilter);
      
      if (mounted) {
        setState(() {
          _jobs = jobs;
          _isLoading = false;
        });
        
        // Load progress for active jobs
        _loadProgressForActiveJobs();
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
  
  Future<void> _loadProgressForActiveJobs() async {
    for (final job in _jobs) {
      if (job.status == 'processing' || job.status == 'pending') {
        try {
          final progress = await _service.getImportProgress(job.id);
          if (mounted) {
            setState(() {
              _progressCache[job.id] = progress;
            });
          }
        } catch (e) {
          // Ignore progress loading errors
        }
      }
    }
  }
  
  Future<void> _createImportJob(String filePath) async {
    try {
      final result = await _service.createImportJob(
        filePath: filePath,
        chunkSize: 1000,
        strategy: 'row_based'
      );
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Import job created: ${result.jobId}')),
        );
        _loadJobs();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to create import job: $e')),
        );
      }
    }
  }
  
  Future<void> _startJob(String jobId) async {
    try {
      await _service.startImportJob(jobId);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Import job started')),
        );
        _loadJobs();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to start job: $e')),
        );
      }
    }
  }
  
  Future<void> _pauseJob(String jobId) async {
    try {
      await _service.pauseImportJob(jobId);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Import job paused')),
        );
        _loadJobs();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to pause job: $e')),
        );
      }
    }
  }
  
  Future<void> _resumeJob(String jobId) async {
    try {
      await _service.resumeImportJob(jobId);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Import job resumed')),
        );
        _loadJobs();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to resume job: $e')),
        );
      }
    }
  }
  
  Future<void> _cancelJob(String jobId) async {
    try {
      await _service.cancelImportJob(jobId);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Import job cancelled')),
        );
        _loadJobs();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to cancel job: $e')),
        );
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return ScrollScaffold(
      title: 'Large Workbook Manager',
      leading: const AppBackLeading(),
      actions: [
        IconButton(
          icon: const Icon(Icons.refresh),
          onPressed: _loadJobs,
        ),
        PopupMenuButton<String>(
          onSelected: (value) {
            setState(() {
              _statusFilter = value == 'all' ? null : value;
            });
            _loadJobs();
          },
          itemBuilder: (context) => [
            const PopupMenuItem(value: 'all', child: Text('All Statuses')),
            const PopupMenuItem(value: 'pending', child: Text('Pending')),
            const PopupMenuItem(value: 'processing', child: Text('Processing')),
            const PopupMenuItem(value: 'paused', child: Text('Paused')),
            const PopupMenuItem(value: 'completed', child: Text('Completed')),
            const PopupMenuItem(value: 'failed', child: Text('Failed')),
            const PopupMenuItem(value: 'cancelled', child: Text('Cancelled')),
          ],
        ),
      ],
      children: [
        // Tab bar
        TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Import Jobs', icon: Icon(Icons.upload)),
            Tab(text: 'Progress', icon: Icon(Icons.analytics)),
            Tab(text: 'Statistics', icon: Icon(Icons.bar_chart)),
          ],
        ),
        
        const SizedBox(height: 16),
        
        // Tab content
        Expanded(
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildImportJobsTab(),
              _buildProgressTab(),
              _buildStatisticsTab(),
            ],
          ),
        ),
      ],
    );
  }
  
  Widget _buildImportJobsTab() {
    if (_isLoading) {
      return const Center(child: LoadingIndicator());
    }
    
    if (_error != null) {
      return ErrorDisplay(
        error: _error!,
        onRetry: _loadJobs,
      );
    }
    
    if (_jobs.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.upload, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              'No import jobs found',
              style: TextStyle(fontSize: 18, color: Colors.grey),
            ),
            SizedBox(height: 8),
            Text(
              'Create a new import job to get started',
              style: TextStyle(color: Colors.grey),
            ),
          ],
        ),
      );
    }
    
    return ListView.builder(
      itemCount: _jobs.length,
      itemBuilder: (context, index) {
        final job = _jobs[index];
        return _buildJobCard(job);
      },
    );
  }
  
  Widget _buildJobCard(LargeImportJob job) {
    final progress = _progressCache[job.id];
    
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getStatusColor(job.status),
          child: Icon(
            _getStatusIcon(job.status),
            color: Colors.white,
          ),
        ),
        title: Text(job.filename),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Status: ${job.status}'),
            Text('Rows: ${job.totalRows} | Chunks: ${job.totalChunks}'),
            if (progress != null) ...[
              const SizedBox(height: 4),
              LinearProgressIndicator(
                value: progress.percentage / 100,
                backgroundColor: Colors.grey[300],
              ),
              const SizedBox(height: 4),
              Text('${progress.percentage.toStringAsFixed(1)}% - ${progress.processedRows}/${progress.totalRows} rows'),
              if (progress.estimatedRemaining != null)
                Text('ETA: ${progress.estimatedRemaining}'),
            ],
          ],
        ),
        trailing: PopupMenuButton<String>(
          onSelected: (value) {
            switch (value) {
              case 'start':
                _startJob(job.id);
                break;
              case 'pause':
                _pauseJob(job.id);
                break;
              case 'resume':
                _resumeJob(job.id);
                break;
              case 'cancel':
                _cancelJob(job.id);
                break;
              case 'details':
                _showJobDetails(job);
                break;
            }
          },
          itemBuilder: (context) => [
            if (job.status == 'pending')
              const PopupMenuItem(value: 'start', child: Text('Start')),
            if (job.status == 'processing')
              const PopupMenuItem(value: 'pause', child: Text('Pause')),
            if (job.status == 'paused')
              const PopupMenuItem(value: 'resume', child: Text('Resume')),
            if (job.status == 'processing' || job.status == 'pending')
              const PopupMenuItem(value: 'cancel', child: Text('Cancel')),
            const PopupMenuItem(value: 'details', child: Text('Details')),
          ],
        ),
        onTap: () => _showJobDetails(job),
      ),
    );
  }
  
  Widget _buildProgressTab() {
    final activeJobs = _jobs.where((job) => 
      job.status == 'processing' || job.status == 'pending'
    ).toList();
    
    if (activeJobs.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.analytics, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              'No active jobs',
              style: TextStyle(fontSize: 18, color: Colors.grey),
            ),
          ],
        ),
      );
    }
    
    return ListView.builder(
      itemCount: activeJobs.length,
      itemBuilder: (context, index) {
        final job = activeJobs[index];
        final progress = _progressCache[job.id];
        
        if (progress == null) {
          return const ListTile(
            leading: CircularProgressIndicator(),
            title: Text('Loading progress...'),
          );
        }
        
        return Card(
          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  job.filename,
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                
                // Progress bar
                LinearProgressIndicator(
                  value: progress.percentage / 100,
                  backgroundColor: Colors.grey[300],
                ),
                const SizedBox(height: 8),
                
                // Progress details
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('${progress.percentage.toStringAsFixed(1)}%'),
                    Text('${progress.processedRows}/${progress.totalRows} rows'),
                  ],
                ),
                
                const SizedBox(height: 8),
                
                // Chunk progress
                Text('Chunks: ${progress.currentChunk}/${progress.totalChunks}'),
                
                if (progress.estimatedRemaining != null) ...[
                  const SizedBox(height: 4),
                  Text('ETA: ${progress.estimatedRemaining}'),
                ],
                
                if (progress.currentOperation != null) ...[
                  const SizedBox(height: 4),
                  Text('Operation: ${progress.currentOperation}'),
                ],
              ],
            ),
          ),
        );
      },
    );
  }
  
  Widget _buildStatisticsTab() {
    // This would show overall statistics
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.bar_chart, size: 64, color: Colors.grey),
          SizedBox(height: 16),
          Text(
            'Statistics coming soon',
            style: TextStyle(fontSize: 18, color: Colors.grey),
          ),
        ],
      ),
    );
  }
  
  void _showJobDetails(LargeImportJob job) {
    showDialog(
      context: context,
      builder: (context) => LargeWorkbookJobDetailsDialog(
        job: job,
        progress: _progressCache[job.id],
        onStart: () => _startJob(job.id),
        onPause: () => _pauseJob(job.id),
        onResume: () => _resumeJob(job.id),
        onCancel: () => _cancelJob(job.id),
      ),
    );
  }
  
  Color _getStatusColor(String status) {
    switch (status) {
      case 'pending':
        return Colors.blue;
      case 'processing':
        return Colors.orange;
      case 'paused':
        return Colors.yellow[700]!;
      case 'completed':
        return Colors.green;
      case 'failed':
        return Colors.red;
      case 'cancelled':
        return Colors.grey;
      default:
        return Colors.grey;
    }
  }
  
  IconData _getStatusIcon(String status) {
    switch (status) {
      case 'pending':
        return Icons.schedule;
      case 'processing':
        return Icons.sync;
      case 'paused':
        return Icons.pause;
      case 'completed':
        return Icons.check_circle;
      case 'failed':
        return Icons.error;
      case 'cancelled':
        return Icons.cancel;
      default:
        return Icons.help;
    }
  }
}

class LargeWorkbookJobDetailsDialog extends StatelessWidget {
  final LargeImportJob job;
  final ImportProgress? progress;
  final VoidCallback? onStart;
  final VoidCallback? onPause;
  final VoidCallback? onResume;
  final VoidCallback? onCancel;
  
  const LargeWorkbookJobDetailsDialog({
    super.key,
    required this.job,
    this.progress,
    this.onStart,
    this.onPause,
    this.onResume,
    this.onCancel,
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
                  'Job Details',
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
            
            // Job information
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Filename: ${job.filename}'),
                    Text('Status: ${job.status}'),
                    Text('Total Rows: ${job.totalRows}'),
                    Text('Chunk Size: ${job.chunkSize}'),
                    Text('Total Chunks: ${job.totalChunks}'),
                    Text('Created: ${_formatDateTime(job.createdAt)}'),
                    if (job.startedAt != null)
                      Text('Started: ${_formatDateTime(job.startedAt!)}'),
                    if (job.completedAt != null)
                      Text('Completed: ${_formatDateTime(job.completedAt!)}'),
                    if (job.errorMessage != null)
                      Text('Error: ${job.errorMessage}'),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Progress information
            if (progress != null) ...[
              const Text(
                'Progress',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      LinearProgressIndicator(
                        value: progress!.percentage / 100,
                        backgroundColor: Colors.grey[300],
                      ),
                      const SizedBox(height: 8),
                      Text('${progress!.percentage.toStringAsFixed(1)}% complete'),
                      Text('${progress!.processedRows}/${progress!.totalRows} rows processed'),
                      Text('Chunk ${progress!.currentChunk}/${progress!.totalChunks}'),
                      if (progress!.estimatedRemaining != null)
                        Text('ETA: ${progress!.estimatedRemaining}'),
                      if (progress!.currentOperation != null)
                        Text('Operation: ${progress!.currentOperation}'),
                    ],
                  ),
                ),
              ),
            ],
            
            const Spacer(),
            
            // Action buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('Close'),
                ),
                const SizedBox(width: 8),
                if (job.status == 'pending' && onStart != null)
                  ElevatedButton(
                    onPressed: onStart,
                    child: const Text('Start'),
                  ),
                if (job.status == 'processing' && onPause != null)
                  ElevatedButton(
                    onPressed: onPause,
                    child: const Text('Pause'),
                  ),
                if (job.status == 'paused' && onResume != null)
                  ElevatedButton(
                    onPressed: onResume,
                    child: const Text('Resume'),
                  ),
                if ((job.status == 'processing' || job.status == 'pending') && onCancel != null)
                  ElevatedButton(
                    onPressed: onCancel,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                    ),
                    child: const Text('Cancel'),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
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
