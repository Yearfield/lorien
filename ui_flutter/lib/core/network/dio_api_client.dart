import 'package:dio/dio.dart';
import '../http/api_client.dart';
import 'http_errors.dart';

/// Production API client using Dio
class DioApiClient implements ApiClient {
  final Dio _dio;
  final String baseUrl;

  DioApiClient(this.baseUrl) : _dio = Dio(BaseOptions(
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  ));

  @override
  Future<Map<String, dynamic>> get(
    String path, {
    Map<String, dynamic>? query,
  }) async {
    try {
      final response = await _dio.get(
        '$baseUrl$path',
        queryParameters: query,
      );
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _mapDioException(e);
    }
  }

  @override
  Future<Map<String, dynamic>> post(
    String path, {
    Object? body,
    Map<String, dynamic>? query,
  }) async {
    try {
      final response = await _dio.post(
        '$baseUrl$path',
        data: body,
        queryParameters: query,
      );
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _mapDioException(e);
    }
  }

  @override
  Future<Map<String, dynamic>> put(
    String path, {
    Object? body,
  }) async {
    try {
      final response = await _dio.put(
        '$baseUrl$path',
        data: body,
      );
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _mapDioException(e);
    }
  }

  @override
  Future<Map<String, dynamic>> delete(String path) async {
    try {
      final response = await _dio.delete('$baseUrl$path');
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _mapDioException(e);
    }
  }

  @override
  Future<Map<String, dynamic>> postMultipart(
    String path, {
    required Map<String, dynamic> fields,
    List<MapEntry<String, List<int>>>? files,
  }) async {
    try {
      final formData = FormData();
      
      // Add fields
      for (final entry in fields.entries) {
        formData.fields.add(MapEntry(entry.key, entry.value.toString()));
      }
      
      // Add files
      if (files != null) {
        for (final file in files) {
          formData.files.add(MapEntry(
            file.key,
            MultipartFile.fromBytes(file.value),
          ));
        }
      }
      
      final response = await _dio.post(
        '$baseUrl$path',
        data: formData,
      );
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _mapDioException(e);
    }
  }

  ApiError _mapDioException(DioException e) {
    final statusCode = e.response?.statusCode ?? 0;
    final message = e.response?.data?['detail']?.toString() ?? e.message ?? 'Unknown error';
    
    switch (statusCode) {
      case 422:
        final detail = e.response?.data?['detail'];
        if (detail is List) {
          return Validation422(detail.cast<Map<String, dynamic>>());
        }
        return Validation422([{'msg': message}]);
      case 409:
        return Conflict409(message);
      case 404:
        return NotFound404(message);
      case 503:
        return ServiceUnavailable(message);
      default:
        return GenericApiError(statusCode, message);
    }
  }
}
