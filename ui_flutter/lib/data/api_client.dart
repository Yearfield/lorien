import 'package:dio/dio.dart';
import 'package:pretty_dio_logger/pretty_dio_logger.dart';

class ApiClient {
  late final Dio _dio;
  
  ApiClient() {
    _dio = Dio();
    _setupInterceptors();
  }
  
  void _setupInterceptors() {
    // Add pretty logger for development
    _dio.interceptors.add(
      PrettyDioLogger(
        requestHeader: true,
        requestBody: true,
        responseBody: true,
        responseHeader: false,
        error: true,
        compact: true,
        maxWidth: 90,
      ),
    );
    
    // Add error interceptor
    _dio.interceptors.add(
      InterceptorsWrapper(
        onError: (error, handler) {
          // Handle specific error cases
          String msg;
          if (error.type == DioExceptionType.connectionTimeout) {
            msg = 'Connection timeout. Please check your network connection.';
          } else if (error.type == DioExceptionType.connectionError) {
            msg = 'Unable to connect to server. Please check the API URL.';
          } else if (error.response?.statusCode == 422) {
            final detail = error.response?.data is Map ? (error.response?.data['detail'] ?? '') : '';
            msg = 'Validation error: ${detail.toString().isEmpty ? 'Invalid data' : detail}';
          } else if (error.response?.statusCode == 409) {
            final detail = error.response?.data is Map ? (error.response?.data['detail'] ?? '') : '';
            msg = 'Conflict: ${detail.toString().isEmpty ? 'Resource conflict' : detail}';
          } else {
            msg = error.message ?? 'Request failed';
          }
          
          // Create a new DioException with the custom message
          final customError = DioException(
            requestOptions: error.requestOptions,
            response: error.response,
            type: error.type,
            error: msg,
          );
          
          handler.next(customError);
        },
      ),
    );
  }
  
  void setBaseUrl(String baseUrl) {
    _dio.options.baseUrl = baseUrl;
    // DEBUG: verify the base URL used by the client
    // ignore: avoid_print
    print('[ApiClient] baseUrl=${_dio.options.baseUrl}');
  }
  
  Dio get dio => _dio;
  
  // Helper methods for common HTTP operations
  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return _dio.get<T>(
      path,
      queryParameters: queryParameters,
      options: options,
    );
  }
  
  Future<Response<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return _dio.post<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }
  
  Future<Response<T>> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return _dio.put<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }
  
  Future<Response<T>> delete<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return _dio.delete<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }
}
