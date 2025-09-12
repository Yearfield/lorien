import 'package:freezed_annotation/freezed_annotation.dart';

part 'large_workbook_models.freezed.dart';
part 'large_workbook_models.g.dart';

@freezed
class LargeImportJob with _$LargeImportJob {
  const factory LargeImportJob({
    required String id,
    required String filename,
    required int totalRows,
    required int chunkSize,
    required String status,
    String? progressData,
    required String createdAt,
    String? startedAt,
    String? completedAt,
    String? errorMessage,
    Map<String, dynamic>? metadata,
  }) = _LargeImportJob;

  factory LargeImportJob.fromJson(Map<String, dynamic> json) =>
      _$LargeImportJobFromJson(json);
}

@freezed
class ImportProgress with _$ImportProgress {
  const factory ImportProgress({
    required int totalRows,
    required int processedRows,
    required int currentChunk,
    required int totalChunks,
    required double percentage,
    String? estimatedRemaining,
    String? currentOperation,
  }) = _ImportProgress;

  factory ImportProgress.fromJson(Map<String, dynamic> json) =>
      _$ImportProgressFromJson(json);
}

@freezed
class ChunkResult with _$ChunkResult {
  const factory ChunkResult({
    required int rowsProcessed,
    required int createdRoots,
    required int createdNodes,
    required int updatedNodes,
    required int updatedOutcomes,
    required List<String> errors,
    required List<String> warnings,
  }) = _ChunkResult;

  factory ChunkResult.fromJson(Map<String, dynamic> json) =>
      _$ChunkResultFromJson(json);
}

@freezed
class ImportJobResponse with _$ImportJobResponse {
  const factory ImportJobResponse({
    required String jobId,
    required String status,
    required String message,
    int? totalRows,
    int? chunkSize,
    int? totalChunks,
  }) = _ImportJobResponse;

  factory ImportJobResponse.fromJson(Map<String, dynamic> json) =>
      _$ImportJobResponseFromJson(json);
}

@freezed
class ProgressResponse with _$ProgressResponse {
  const factory ProgressResponse({
    required String jobId,
    required ImportProgress progress,
    required Map<String, dynamic> statistics,
  }) = _ProgressResponse;

  factory ProgressResponse.fromJson(Map<String, dynamic> json) =>
      _$ProgressResponseFromJson(json);
}

@freezed
class ChunkResponse with _$ChunkResponse {
  const factory ChunkResponse({
    required int chunkId,
    required int chunkIndex,
    required int startRow,
    required int endRow,
    required String status,
  }) = _ChunkResponse;

  factory ChunkResponse.fromJson(Map<String, dynamic> json) =>
      _$ChunkResponseFromJson(json);
}

@freezed
class ImportStatistics with _$ImportStatistics {
  const factory ImportStatistics({
    required Map<String, dynamic> chunkStatistics,
    required Map<String, dynamic> performanceStatistics,
  }) = _ImportStatistics;

  factory ImportStatistics.fromJson(Map<String, dynamic> json) =>
      _$ImportStatisticsFromJson(json);
}

@freezed
class CreateImportJobRequest with _$CreateImportJobRequest {
  const factory CreateImportJobRequest({
    required String filePath,
    @Default(1000) int chunkSize,
    @Default('row_based') String strategy,
    Map<String, dynamic>? metadata,
  }) = _CreateImportJobRequest;

  factory CreateImportJobRequest.fromJson(Map<String, dynamic> json) =>
      _$CreateImportJobRequestFromJson(json);
}

@freezed
class ImportJobSummary with _$ImportJobSummary {
  const factory ImportJobSummary({
    required String id,
    required String filename,
    required int totalRows,
    required int chunkSize,
    required String status,
    required String createdAt,
    String? startedAt,
    String? completedAt,
    String? errorMessage,
  }) = _ImportJobSummary;

  factory ImportJobSummary.fromJson(Map<String, dynamic> json) =>
      _$ImportJobSummaryFromJson(json);
}

@freezed
class PerformanceMetrics with _$PerformanceMetrics {
  const factory PerformanceMetrics({
    required double avgDurationMs,
    required int minDurationMs,
    required int maxDurationMs,
    required int totalRowsProcessed,
  }) = _PerformanceMetrics;

  factory PerformanceMetrics.fromJson(Map<String, dynamic> json) =>
      _$PerformanceMetricsFromJson(json);
}

@freezed
class ChunkStatistics with _$ChunkStatistics {
  const factory ChunkStatistics({
    required int totalChunks,
    required int completedChunks,
    required int failedChunks,
    required int processingChunks,
    required int pendingChunks,
  }) = _ChunkStatistics;

  factory ChunkStatistics.fromJson(Map<String, dynamic> json) =>
      _$ChunkStatisticsFromJson(json);
}

@freezed
class ImportJobDetails with _$ImportJobDetails {
  const factory ImportJobDetails({
    required LargeImportJob job,
    required ImportStatistics statistics,
    ImportProgress? progress,
  }) = _ImportJobDetails;

  factory ImportJobDetails.fromJson(Map<String, dynamic> json) =>
      _$ImportJobDetailsFromJson(json);
}

@freezed
class ImportJobListResponse with _$ImportJobListResponse {
  const factory ImportJobListResponse({
    required List<LargeImportJob> jobs,
    required int total,
    String? statusFilter,
  }) = _ImportJobListResponse;

  factory ImportJobListResponse.fromJson(Map<String, dynamic> json) =>
      _$ImportJobListResponseFromJson(json);
}

@freezed
class ImportJobAction with _$ImportJobAction {
  const factory ImportJobAction({
    required String action,
    required String jobId,
    String? reason,
    Map<String, dynamic>? metadata,
  }) = _ImportJobAction;

  factory ImportJobAction.fromJson(Map<String, dynamic> json) =>
      _$ImportJobActionFromJson(json);
}

@freezed
class ImportJobActionResponse with _$ImportJobActionResponse {
  const factory ImportJobActionResponse({
    required bool success,
    required String message,
    String? jobId,
    String? newStatus,
  }) = _ImportJobActionResponse;

  factory ImportJobActionResponse.fromJson(Map<String, dynamic> json) =>
      _$ImportJobActionResponseFromJson(json);
}

@freezed
class ImportJobFilter with _$ImportJobFilter {
  const factory ImportJobFilter({
    String? status,
    String? filename,
    DateTime? createdAfter,
    DateTime? createdBefore,
    int? minRows,
    int? maxRows,
  }) = _ImportJobFilter;

  factory ImportJobFilter.fromJson(Map<String, dynamic> json) =>
      _$ImportJobFilterFromJson(json);
}

@freezed
class ImportJobSort with _$ImportJobSort {
  const factory ImportJobSort({
    @Default('created_at') String field,
    @Default('desc') String direction,
  }) = _ImportJobSort;

  factory ImportJobSort.fromJson(Map<String, dynamic> json) =>
      _$ImportJobSortFromJson(json);
}

@freezed
class ImportJobQuery with _$ImportJobQuery {
  const factory ImportJobQuery({
    ImportJobFilter? filter,
    ImportJobSort? sort,
    @Default(50) int limit,
    @Default(0) int offset,
  }) = _ImportJobQuery;

  factory ImportJobQuery.fromJson(Map<String, dynamic> json) =>
      _$ImportJobQueryFromJson(json);
}
