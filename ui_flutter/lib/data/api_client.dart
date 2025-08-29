import 'package:dio/dio.dart';
import 'package:pretty_dio_logger/pretty_dio_logger.dart';
import '../utils/env.dart';

class ApiClient {
  late final Dio _dio;
  late final String baseUrl;
  
  ApiClient() {
    baseUrl = resolveApiBaseUrl();
    _dio = Dio(BaseOptions(
      // Dio requires a trailing slash for reliable relative path joining.
      baseUrl: baseUrl, // must end with /api/v1/
      connectTimeout: const Duration(seconds: 2),
      receiveTimeout: const Duration(seconds: 5),
      sendTimeout: const Duration(seconds: 5),
      responseType: ResponseType.json,
      followRedirects: true,
      validateStatus: (code) => code != null && code >= 200 && code < 400,
    ));
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
        onRequest: (options, handler) {
          // Light logging with safe print of fully-resolved URL
          final url = Uri.parse(options.baseUrl).resolve(options.path).toString();
          // ignore: avoid_print
          print('[ApiClient] ${options.method} $url');
          handler.next(options);
        },
        onError: (error, handler) {
          // ignore: avoid_print
          print('[ApiClient:Error] ${error.type} ${error.message}');
          handler.next(error);
        },
      ),
    );
  }
  
  void setBaseUrl(String baseUrl) {
    this.baseUrl = baseUrl;
    _dio.options.baseUrl = baseUrl;
    // DEBUG: verify the base URL used by the client
    // ignore: avoid_print
    print('[ApiClient] baseUrl=${_dio.options.baseUrl}');
  }
  
  Dio get dio => _dio;
  
  /// Join a resource path to base URL. Enforces no leading slash and forbids embedding `/api/v1`.
  String _join(String path) {
    var p = path.trim();
    assert(!p.startsWith('/'), 'Path must be relative (no leading slash): $p');
    assert(!p.startsWith('api/v1') && !p.contains('/api/v1/'),
        'Path must NOT include /api/v1: $p');
    // Clean any accidental leading slash and double slashes
    p = p.replaceAll(RegExp(r'^/+'), '').replaceAll(RegExp(r'/+'), '/');
    return p;
  }

  // Helper methods for common HTTP operations with better error handling
  Future<Response<T>> get<T>(
    String resource, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final p = _join(resource);
      return await _dio.get<T>(
        p,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _normalizeDioError(e);
    }
  }
  
  Future<Response<T>> post<T>(
    String resource, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final p = _join(resource);
      return await _dio.post<T>(
        p,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _normalizeDioError(e);
    }
  }
  
  Future<Response<T>> put<T>(
    String resource, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final p = _join(resource);
      return await _dio.put<T>(
        p,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _normalizeDioError(e);
    }
  }
  
  Future<Response<T>> delete<T>(
    String resource, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final p = _join(resource);
      return await _dio.delete<T>(
        p,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _normalizeDioError(e);
    }
  }

  Object _normalizeDioError(DioException e) {
    // Connection refused / network down should not crash UI
    if (e.type == DioExceptionType.connectionError ||
        e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return ApiUnavailable(message: e.message ?? 'API unavailable');
    }
    return ApiFailure(message: e.message ?? 'Request failed', cause: e);
  }
}

class ApiUnavailable implements Exception {
  ApiUnavailable({required this.message});
  final String message;
  @override
  String toString() => 'ApiUnavailable($message)';
}

class ApiFailure implements Exception {
  ApiFailure({required this.message, this.cause});
  final String message;
  final Object? cause;
  @override
  String toString() => 'ApiFailure($message)';
}
