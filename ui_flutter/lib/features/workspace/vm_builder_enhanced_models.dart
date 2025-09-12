import 'package:freezed_annotation/freezed_annotation.dart';

part 'vm_builder_enhanced_models.freezed.dart';
part 'vm_builder_enhanced_models.g.dart';

@freezed
class VMBuilderDraft with _$VMBuilderDraft {
  const factory VMBuilderDraft({
    required String id,
    required String createdAt,
    required String updatedAt,
    required int parentId,
    required String status,
    String? publishedAt,
    String? publishedBy,
    Map<String, dynamic>? planData,
    List<Map<String, dynamic>>? validationData,
    @Default({}) Map<String, dynamic> metadata,
  }) = _VMBuilderDraft;

  factory VMBuilderDraft.fromJson(Map<String, dynamic> json) =>
      _$VMBuilderDraftFromJson(json);
}

@freezed
class VMBuilderStats with _$VMBuilderStats {
  const factory VMBuilderStats({
    required int totalDrafts,
    required Map<String, int> statusCounts,
    required int recentDrafts,
    required int publishedDrafts,
  }) = _VMBuilderStats;

  factory VMBuilderStats.fromJson(Map<String, dynamic> json) =>
      _$VMBuilderStatsFromJson(json);
}

@freezed
class VMBuilderPlan with _$VMBuilderPlan {
  const factory VMBuilderPlan({
    required String draftId,
    required int parentId,
    required List<VMBuilderOperation> operations,
    required Map<String, int> summary,
    required List<VMBuilderValidationIssue> validationIssues,
    required String estimatedImpact,
    required bool canPublish,
    required List<String> warnings,
  }) = _VMBuilderPlan;

  factory VMBuilderPlan.fromJson(Map<String, dynamic> json) =>
      _$VMBuilderPlanFromJson(json);
}

@freezed
class VMBuilderOperation with _$VMBuilderOperation {
  const factory VMBuilderOperation({
    required String type,
    int? nodeId,
    Map<String, dynamic>? oldData,
    Map<String, dynamic>? newData,
    required String impactLevel,
    required String description,
    @Default([]) List<int> affectedChildren,
  }) = _VMBuilderOperation;

  factory VMBuilderOperation.fromJson(Map<String, dynamic> json) =>
      _$VMBuilderOperationFromJson(json);
}

@freezed
class VMBuilderValidationIssue with _$VMBuilderValidationIssue {
  const factory VMBuilderValidationIssue({
    required String severity,
    required String message,
    String? field,
    String? suggestion,
    String? code,
  }) = _VMBuilderValidationIssue;

  factory VMBuilderValidationIssue.fromJson(Map<String, dynamic> json) =>
      _$VMBuilderValidationIssueFromJson(json);
}

@freezed
class VMBuilderPublishResult with _$VMBuilderPublishResult {
  const factory VMBuilderPublishResult({
    required bool success,
    required String message,
    required int operationsApplied,
    int? auditId,
    required Map<String, int> summary,
  }) = _VMBuilderPublishResult;

  factory VMBuilderPublishResult.fromJson(Map<String, dynamic> json) =>
      _$VMBuilderPublishResultFromJson(json);
}

@freezed
class VMBuilderCreateRequest with _$VMBuilderCreateRequest {
  const factory VMBuilderCreateRequest({
    required int parentId,
    required Map<String, dynamic> draftData,
    Map<String, dynamic>? metadata,
  }) = _VMBuilderCreateRequest;

  factory VMBuilderCreateRequest.fromJson(Map<String, dynamic> json) =>
      _$VMBuilderCreateRequestFromJson(json);
}

@freezed
class VMBuilderUpdateRequest with _$VMBuilderUpdateRequest {
  const factory VMBuilderUpdateRequest({
    required Map<String, dynamic> draftData,
    Map<String, dynamic>? metadata,
  }) = _VMBuilderUpdateRequest;

  factory VMBuilderUpdateRequest.fromJson(Map<String, dynamic> json) =>
      _$VMBuilderUpdateRequestFromJson(json);
}

@freezed
class VMBuilderPublishRequest with _$VMBuilderPublishRequest {
  const factory VMBuilderPublishRequest({
    @Default(false) bool force,
    String? reason,
  }) = _VMBuilderPublishRequest;

  factory VMBuilderPublishRequest.fromJson(Map<String, dynamic> json) =>
      _$VMBuilderPublishRequestFromJson(json);
}

@freezed
class VMBuilderDraftListResponse with _$VMBuilderDraftListResponse {
  const factory VMBuilderDraftListResponse({
    required List<VMBuilderDraft> drafts,
    required int total,
    String? statusFilter,
  }) = _VMBuilderDraftListResponse;

  factory VMBuilderDraftListResponse.fromJson(Map<String, dynamic> json) =>
      _$VMBuilderDraftListResponseFromJson(json);
}

@freezed
class VMBuilderAuditEntry with _$VMBuilderAuditEntry {
  const factory VMBuilderAuditEntry({
    required int id,
    required String action,
    required String actor,
    required String timestamp,
    Map<String, dynamic>? beforeState,
    Map<String, dynamic>? afterState,
    required bool success,
    required String message,
    Map<String, dynamic>? metadata,
  }) = _VMBuilderAuditEntry;

  factory VMBuilderAuditEntry.fromJson(Map<String, dynamic> json) =>
      _$VMBuilderAuditEntryFromJson(json);
}

@freezed
class VMBuilderAuditResponse with _$VMBuilderAuditResponse {
  const factory VMBuilderAuditResponse({
    required String draftId,
    required List<VMBuilderAuditEntry> auditEntries,
    required int total,
    required int limit,
    required int offset,
  }) = _VMBuilderAuditResponse;

  factory VMBuilderAuditResponse.fromJson(Map<String, dynamic> json) =>
      _$VMBuilderAuditResponseFromJson(json);
}
