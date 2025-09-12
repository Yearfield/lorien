import 'package:dio/dio.dart';
import 'vm_builder_enhanced_models.dart';

class VMBuilderEnhancedService {
  final Dio _dio;

  VMBuilderEnhancedService(this._dio);

  Future<List<VMBuilderDraft>> getDrafts({
    String? status,
    int? parentId,
    int limit = 50,
    int offset = 0,
  }) async {
    final queryParams = <String, dynamic>{
      'limit': limit,
      'offset': offset,
    };
    
    if (status != null) queryParams['status'] = status;
    if (parentId != null) queryParams['parent_id'] = parentId;

    final response = await _dio.get(
      '/vm-builder/drafts',
      queryParameters: queryParams,
    );

    final data = response.data as Map<String, dynamic>;
    final draftListResponse = VMBuilderDraftListResponse.fromJson(data);
    return draftListResponse.drafts;
  }

  Future<VMBuilderDraft> getDraft(String draftId) async {
    final response = await _dio.get('/vm-builder/drafts/$draftId');
    return VMBuilderDraft.fromJson(response.data as Map<String, dynamic>);
  }

  Future<VMBuilderDraft> createDraft({
    required int parentId,
    required Map<String, dynamic> draftData,
    Map<String, dynamic>? metadata,
  }) async {
    final request = VMBuilderCreateRequest(
      parentId: parentId,
      draftData: draftData,
      metadata: metadata,
    );

    final response = await _dio.post(
      '/vm-builder/drafts',
      data: request.toJson(),
    );

    return VMBuilderDraft.fromJson(response.data as Map<String, dynamic>);
  }

  Future<VMBuilderDraft> updateDraft({
    required String draftId,
    required Map<String, dynamic> draftData,
    Map<String, dynamic>? metadata,
  }) async {
    final request = VMBuilderUpdateRequest(
      draftData: draftData,
      metadata: metadata,
    );

    final response = await _dio.put(
      '/vm-builder/drafts/$draftId',
      data: request.toJson(),
    );

    return VMBuilderDraft.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> deleteDraft(String draftId) async {
    await _dio.delete('/vm-builder/drafts/$draftId');
  }

  Future<VMBuilderPlan> planDraft(String draftId) async {
    final response = await _dio.post('/vm-builder/drafts/$draftId/plan');
    
    final data = response.data as Map<String, dynamic>;
    final planData = data['plan'] as Map<String, dynamic>;
    
    return VMBuilderPlan.fromJson(planData);
  }

  Future<VMBuilderPublishResult> publishDraft({
    required String draftId,
    bool force = false,
    String? reason,
  }) async {
    final request = VMBuilderPublishRequest(
      force: force,
      reason: reason,
    );

    final response = await _dio.post(
      '/vm-builder/drafts/$draftId/publish',
      data: request.toJson(),
    );

    return VMBuilderPublishResult.fromJson(response.data as Map<String, dynamic>);
  }

  Future<VMBuilderStats> getStats() async {
    final response = await _dio.get('/vm-builder/stats');
    
    final data = response.data as Map<String, dynamic>;
    final statsData = data['stats'] as Map<String, dynamic>;
    
    return VMBuilderStats.fromJson(statsData);
  }

  Future<List<VMBuilderAuditEntry>> getDraftAuditHistory({
    required String draftId,
    int limit = 50,
    int offset = 0,
  }) async {
    final response = await _dio.get(
      '/vm-builder/drafts/$draftId/audit',
      queryParameters: {
        'limit': limit,
        'offset': offset,
      },
    );

    final data = response.data as Map<String, dynamic>;
    final auditResponse = VMBuilderAuditResponse.fromJson(data);
    
    return auditResponse.auditEntries;
  }

  // Helper methods for common operations
  Future<VMBuilderDraft> createDraftForParent({
    required int parentId,
    List<Map<String, dynamic>> children = const [],
    Map<String, dynamic>? metadata,
  }) async {
    final draftData = {
      'children': children,
      'metadata': {
        'created_via': 'ui',
        'version': '1.0',
        ...?metadata,
      },
    };

    return createDraft(
      parentId: parentId,
      draftData: draftData,
      metadata: metadata,
    );
  }

  Future<VMBuilderDraft> updateDraftChildren({
    required String draftId,
    required List<Map<String, dynamic>> children,
    Map<String, dynamic>? metadata,
  }) async {
    final draft = await getDraft(draftId);
    final currentData = Map<String, dynamic>.from(draft.metadata);
    
    final updatedData = {
      ...currentData,
      'children': children,
    };

    return updateDraft(
      draftId: draftId,
      draftData: updatedData,
      metadata: metadata,
    );
  }

  Future<bool> canPublishDraft(String draftId) async {
    try {
      final plan = await planDraft(draftId);
      return plan.canPublish;
    } catch (e) {
      return false;
    }
  }

  Future<List<String>> getDraftWarnings(String draftId) async {
    try {
      final plan = await planDraft(draftId);
      return plan.warnings;
    } catch (e) {
      return ['Failed to load plan: $e'];
    }
  }

  Future<List<VMBuilderValidationIssue>> getDraftValidationIssues(String draftId) async {
    try {
      final plan = await planDraft(draftId);
      return plan.validationIssues;
    } catch (e) {
      return [
        VMBuilderValidationIssue(
          severity: 'error',
          message: 'Failed to load validation: $e',
        ),
      ];
    }
  }

  // Batch operations
  Future<List<VMBuilderDraft>> createDraftsForParents({
    required List<int> parentIds,
    Map<String, dynamic>? metadata,
  }) async {
    final futures = parentIds.map((parentId) => 
      createDraftForParent(
        parentId: parentId,
        metadata: metadata,
      )
    );
    
    return Future.wait(futures);
  }

  Future<List<VMBuilderPlan>> planDrafts(List<String> draftIds) async {
    final futures = draftIds.map((draftId) => planDraft(draftId));
    return Future.wait(futures);
  }

  Future<List<VMBuilderPublishResult>> publishDrafts({
    required List<String> draftIds,
    bool force = false,
    String? reason,
  }) async {
    final futures = draftIds.map((draftId) => 
      publishDraft(
        draftId: draftId,
        force: force,
        reason: reason,
      )
    );
    
    return Future.wait(futures);
  }

  // Utility methods
  String getDraftStatusDisplayName(String status) {
    switch (status) {
      case 'draft':
        return 'Draft';
      case 'planning':
        return 'Planning';
      case 'ready_to_publish':
        return 'Ready to Publish';
      case 'publishing':
        return 'Publishing';
      case 'published':
        return 'Published';
      case 'failed':
        return 'Failed';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  }

  String getOperationTypeDisplayName(String type) {
    switch (type) {
      case 'create':
        return 'Create';
      case 'update':
        return 'Update';
      case 'delete':
        return 'Delete';
      case 'move':
        return 'Move';
      case 'reorder':
        return 'Reorder';
      default:
        return type;
    }
  }

  String getImpactLevelDisplayName(String impactLevel) {
    switch (impactLevel) {
      case 'low':
        return 'Low Impact';
      case 'medium':
        return 'Medium Impact';
      case 'high':
        return 'High Impact';
      case 'critical':
        return 'Critical Impact';
      default:
        return impactLevel;
    }
  }

  String getSeverityDisplayName(String severity) {
    switch (severity) {
      case 'info':
        return 'Info';
      case 'warning':
        return 'Warning';
      case 'error':
        return 'Error';
      case 'critical':
        return 'Critical';
      default:
        return severity;
    }
  }
}
