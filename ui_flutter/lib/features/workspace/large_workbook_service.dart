import 'package:dio/dio.dart';
import 'large_workbook_models.dart';

class LargeWorkbookService {
  final Dio _dio;

  LargeWorkbookService(this._dio);

  Future<ImportJobResponse> createImportJob({
    required String filePath,
    int chunkSize = 1000,
    String strategy = 'row_based',
    Map<String, dynamic>? metadata,
  }) async {
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(filePath),
      'chunk_size': chunkSize,
      'strategy': strategy,
      if (metadata != null) 'metadata': jsonEncode(metadata),
    });

    final response = await _dio.post(
      '/large-workbook/import/create-job',
      data: formData,
    );

    return ImportJobResponse.fromJson(response.data as Map<String, dynamic>);
  }

  Future<ImportJobResponse> startImportJob(String jobId) async {
    final response = await _dio.post('/large-workbook/import/$jobId/start');
    return ImportJobResponse.fromJson(response.data as Map<String, dynamic>);
  }

  Future<ImportJobResponse> pauseImportJob(String jobId) async {
    final response = await _dio.post('/large-workbook/import/$jobId/pause');
    return ImportJobResponse.fromJson(response.data as Map<String, dynamic>);
  }

  Future<ImportJobResponse> resumeImportJob(String jobId) async {
    final response = await _dio.post('/large-workbook/import/$jobId/resume');
    return ImportJobResponse.fromJson(response.data as Map<String, dynamic>);
  }

  Future<ImportJobResponse> cancelImportJob(String jobId) async {
    final response = await _dio.post('/large-workbook/import/$jobId/cancel');
    return ImportJobResponse.fromJson(response.data as Map<String, dynamic>);
  }

  Future<ProgressResponse> getImportProgress(String jobId) async {
    final response = await _dio.get('/large-workbook/import/$jobId/progress');
    return ProgressResponse.fromJson(response.data as Map<String, dynamic>);
  }

  Future<List<ChunkResponse>> getImportChunks(
    String jobId, {
    String? status,
  }) async {
    final queryParams = <String, dynamic>{};
    if (status != null) queryParams['status'] = status;

    final response = await _dio.get(
      '/large-workbook/import/$jobId/chunks',
      queryParameters: queryParams,
    );

    final data = response.data as List<dynamic>;
    return data
        .map((item) => ChunkResponse.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<List<LargeImportJob>> listImportJobs({
    String? status,
    int limit = 50,
    int offset = 0,
  }) async {
    final queryParams = <String, dynamic>{
      'limit': limit,
      'offset': offset,
    };
    if (status != null) queryParams['status'] = status;

    final response = await _dio.get(
      '/large-workbook/import/jobs',
      queryParameters: queryParams,
    );

    final data = response.data as List<dynamic>;
    return data
        .map((item) => LargeImportJob.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<ImportJobDetails> getImportJobDetails(String jobId) async {
    final response = await _dio.get('/large-workbook/import/$jobId/statistics');
    return ImportJobDetails.fromJson(response.data as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> getImportStatistics(String jobId) async {
    final response = await _dio.get('/large-workbook/import/$jobId/statistics');
    return response.data as Map<String, dynamic>;
  }

  Future<String> exportProgressCsv(String jobId) async {
    final response = await _dio.get(
      '/large-workbook/import/$jobId/export-progress',
      options: Options(responseType: ResponseType.plain),
    );
    return response.data as String;
  }

  // Helper methods for common operations
  Future<LargeImportJob> getImportJob(String jobId) async {
    final jobs = await listImportJobs();
    final job = jobs.firstWhere((j) => j.id == jobId);
    if (job == null) {
      throw Exception('Import job $jobId not found');
    }
    return job;
  }

  Future<bool> isJobActive(String jobId) async {
    try {
      final job = await getImportJob(jobId);
      return job.status == 'processing' || job.status == 'pending';
    } catch (e) {
      return false;
    }
  }

  Future<bool> isJobCompleted(String jobId) async {
    try {
      final job = await getImportJob(jobId);
      return job.status == 'completed';
    } catch (e) {
      return false;
    }
  }

  Future<bool> isJobFailed(String jobId) async {
    try {
      final job = await getImportJob(jobId);
      return job.status == 'failed';
    } catch (e) {
      return false;
    }
  }

  Future<ImportProgress?> getJobProgress(String jobId) async {
    try {
      final progress = await getImportProgress(jobId);
      return progress.progress;
    } catch (e) {
      return null;
    }
  }

  // Batch operations
  Future<List<ImportJobResponse>> startMultipleJobs(List<String> jobIds) async {
    final futures = jobIds.map((jobId) => startImportJob(jobId));
    return Future.wait(futures);
  }

  Future<List<ImportJobResponse>> pauseMultipleJobs(List<String> jobIds) async {
    final futures = jobIds.map((jobId) => pauseImportJob(jobId));
    return Future.wait(futures);
  }

  Future<List<ImportJobResponse>> resumeMultipleJobs(List<String> jobIds) async {
    final futures = jobIds.map((jobId) => resumeImportJob(jobId));
    return Future.wait(futures);
  }

  Future<List<ImportJobResponse>> cancelMultipleJobs(List<String> jobIds) async {
    final futures = jobIds.map((jobId) => cancelImportJob(jobId));
    return Future.wait(futures);
  }

  // Utility methods
  String getStatusDisplayName(String status) {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'processing':
        return 'Processing';
      case 'paused':
        return 'Paused';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  }

  String getStatusDescription(String status) {
    switch (status) {
      case 'pending':
        return 'Job is waiting to be processed';
      case 'processing':
        return 'Job is currently being processed';
      case 'paused':
        return 'Job processing has been paused';
      case 'completed':
        return 'Job has been completed successfully';
      case 'failed':
        return 'Job processing failed';
      case 'cancelled':
        return 'Job has been cancelled';
      default:
        return 'Unknown status';
    }
  }

  String getChunkStatusDisplayName(String status) {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'processing':
        return 'Processing';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  }

  String formatDuration(int milliseconds) {
    final seconds = milliseconds / 1000;
    if (seconds < 60) {
      return '${seconds.toStringAsFixed(1)}s';
    } else if (seconds < 3600) {
      final minutes = seconds / 60;
      return '${minutes.toStringAsFixed(1)}m';
    } else {
      final hours = seconds / 3600;
      return '${hours.toStringAsFixed(1)}h';
    }
  }

  String formatFileSize(int bytes) {
    if (bytes < 1024) {
      return '${bytes}B';
    } else if (bytes < 1024 * 1024) {
      return '${(bytes / 1024).toStringAsFixed(1)}KB';
    } else if (bytes < 1024 * 1024 * 1024) {
      return '${(bytes / (1024 * 1024)).toStringAsFixed(1)}MB';
    } else {
      return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(1)}GB';
    }
  }

  String formatPercentage(double percentage) {
    return '${percentage.toStringAsFixed(1)}%';
  }

  String formatRowCount(int rows) {
    if (rows < 1000) {
      return rows.toString();
    } else if (rows < 1000000) {
      return '${(rows / 1000).toStringAsFixed(1)}K';
    } else {
      return '${(rows / 1000000).toStringAsFixed(1)}M';
    }
  }

  // Validation methods
  bool isValidChunkSize(int chunkSize) {
    return chunkSize >= 100 && chunkSize <= 10000;
  }

  bool isValidStrategy(String strategy) {
    return ['row_based', 'size_based', 'memory_based'].contains(strategy);
  }

  bool isValidStatus(String status) {
    return [
      'pending',
      'processing',
      'paused',
      'completed',
      'failed',
      'cancelled'
    ].contains(status);
  }

  // Error handling
  String getErrorMessage(dynamic error) {
    if (error is DioException) {
      switch (error.type) {
        case DioExceptionType.connectionTimeout:
          return 'Connection timeout - please check your network';
        case DioExceptionType.sendTimeout:
          return 'Send timeout - please try again';
        case DioExceptionType.receiveTimeout:
          return 'Receive timeout - please try again';
        case DioExceptionType.badResponse:
          final statusCode = error.response?.statusCode;
          if (statusCode == 404) {
            return 'Import job not found';
          } else if (statusCode == 400) {
            return 'Invalid request - please check your parameters';
          } else if (statusCode == 422) {
            return 'Validation error - please check your file format';
          } else if (statusCode == 500) {
            return 'Server error - please try again later';
          }
          return 'Request failed with status $statusCode';
        case DioExceptionType.cancel:
          return 'Request was cancelled';
        case DioExceptionType.connectionError:
          return 'Connection error - please check your network';
        case DioExceptionType.badCertificate:
          return 'Certificate error - please check your connection';
        case DioExceptionType.unknown:
          return 'Unknown error occurred';
      }
    }
    return error.toString();
  }
}
