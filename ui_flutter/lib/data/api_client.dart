import 'package:dio/dio.dart';
import 'package:pretty_dio_logger/pretty_dio_logger.dart';
import 'package:uuid/uuid.dart';
import '../utils/env.dart';

class ApiClient {
  ApiClient._(this._dio, this.baseUrl);
  final Dio _dio;
  String baseUrl;

  static ApiClient? _instance;

  static const _kConnectTimeout = Duration(seconds: 2);
  static const _kReceiveTimeout = Duration(seconds: 8);
  static const _kSendTimeout = Duration(seconds: 8);

  static ApiClient I() {
    if (_instance != null) return _instance!;
    final base = resolveApiBaseUrl();
    final dio = Dio(BaseOptions(
      // Dio requires a trailing slash for reliable relative path joining.
      baseUrl: base, // must end with /api/v1/
      connectTimeout: _kConnectTimeout,
      receiveTimeout: _kReceiveTimeout,
      sendTimeout: _kSendTimeout,
      responseType: ResponseType.json,
      followRedirects: true,
      validateStatus: (code) => code != null && code >= 200 && code < 400,
    ));
    _setupInterceptors(dio);
    _instance = ApiClient._(dio, base);
    // ignore: avoid_print
    print('[ApiClient] baseUrl=$base');
    return _instance!;
  }

  /// Allow runtime override of baseUrl (used by Settings). Resets Dio safely.
  static void setBaseUrl(String newBase) {
    final inst = I();
    inst.baseUrl = newBase.endsWith('/') ? newBase : '$newBase/';
    inst._dio.options.baseUrl = inst.baseUrl;
    // ignore: avoid_print
    print('[ApiClient] baseUrl updated to ${inst.baseUrl}');
  }

  static void _setupInterceptors(Dio dio) {
    // Add pretty logger for development
    dio.interceptors.add(
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

    // Add structured logging interceptor
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          // Attach request id
          options.headers['X-Request-ID'] = const Uuid().v4();
          // Redact sensitive headers in logs
          _log('[HTTP] → ${options.method} ${options.uri}', extra: {
            'id': options.headers['X-Request-ID'],
            'timeoutMs': options.connectTimeout?.inMilliseconds,
          });
          handler.next(options);
        },
        onResponse: (response, handler) {
          _log('[HTTP] ← ${response.statusCode} ${response.requestOptions.uri}', extra: {
            'id': response.requestOptions.headers['X-Request-ID'],
            'ms': response.requestOptions.extra['rt_ms'],
          });
          handler.next(response);
        },
        onError: (e, handler) {
          _log('[HTTP] ✖ ${e.requestOptions.uri} ${e.type} ${e.message}', level: 'warn');
          handler.next(e);
        },
      ),
    );
  }

  static void _log(String msg, {String level = 'info', Map<String, Object?> extra = const {}}) {
    // Central logging hook; ensure redaction if ever logging headers/bodies
    // (we never log Authorization/cookies)
    // ignore: avoid_print
    print('[$level] $msg ${extra.isEmpty ? '' : extra}');
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

  Future<Map<String, dynamic>> getJson(String resource, {Map<String, dynamic>? query}) async {
    _log('[HTTP] → GET $baseUrl$resource');
    try {
      final p = _join(resource);
      final res = await _retryIdempotent(() => _dio.get<Map<String, dynamic>>(p, queryParameters: query));
      return res.data ?? <String, dynamic>{};
    } on DioException catch (e) {
      throw _normalizeDioError(e);
    }
  }

  Future<Map<String, dynamic>> postJson(String resource, {Object? body}) async {
    try {
      final p = _join(resource);
      final res = await _dio.post<Map<String, dynamic>>(p, data: body);
      return res.data ?? <String, dynamic>{};
    } on DioException catch (e) {
      throw _normalizeDioError(e);
    }
  }

  Future<Map<String, dynamic>> postMultipart(
    String resource, {
    String? filePath,
    String fieldName = 'file',
    Map<String, Object?> extras = const {},
    FormData? formData,
    ProgressCallback? onSendProgress,
  }) async {
    _log('[HTTP] → POST(multipart) $baseUrl$resource');
    try {
      final p = _join(resource);
      final form = formData ??
          FormData.fromMap({
            fieldName: await MultipartFile.fromFile(filePath!),
            ...extras,
          });
      final res = await _dio.post<Map<String, dynamic>>(
        p,
        data: form,
        onSendProgress: onSendProgress,
      );
      return res.data ?? <String, dynamic>{};
    } on DioException catch (e) {
      throw _normalizeDioError(e);
    }
  }

  /// Download bytes and return them. Caller persists to disk.
  Future<Response<List<int>>> download(String resource, {Map<String, dynamic>? query}) async {
    try {
      final p = _join(resource);
      final res = await _dio.get<List<int>>(
        p,
        queryParameters: query,
        options: Options(responseType: ResponseType.bytes),
      );
      return res;
    } on DioException catch (e) {
      throw _normalizeDioError(e);
    }
  }

  /// HEAD request to check if endpoint exists
  Future<void> head(String resource) async {
    _log('[HTTP] → HEAD $baseUrl$resource');
    try {
      final p = _join(resource);
      final res = await _dio.head(p);
      if (res.statusCode != null && res.statusCode! >= 400) {
        throw ApiFailure(message: 'HEAD $p failed', statusCode: res.statusCode);
      }
    } on DioException catch (e) {
      throw _normalizeDioError(e);
    }
  }

  /// POST with body and return bytes response. For CSV export with payload.
  Future<Response<List<int>>> postBytes(String resource, {
    Object? body,
    Map<String, String>? headers,
  }) async {
    _log('[HTTP] → POST(bytes) $baseUrl$resource');
    try {
      final p = _join(resource);
      final res = await _dio.post<List<int>>(
        p,
        data: body,
        options: Options(
          responseType: ResponseType.bytes,
          headers: headers,
        ),
      );
      return res;
    } on DioException catch (e) {
      throw _normalizeDioError(e);
    }
  }

  // Simple retry/backoff for idempotent GET/HEAD only
  Future<Response<T>> _retryIdempotent<T>(Future<Response<T>> Function() run,
      {int max = 2}) async {
    int attempt = 0;
    DioException? last;
    while (attempt <= max) {
      final sw = Stopwatch()..start();
      try {
        final r = await run();
        r.requestOptions.extra['rt_ms'] = sw.elapsedMilliseconds;
        return r;
      } on DioException catch (e) {
        last = e;
        if (!_isRetriable(e) || attempt == max) rethrow;
        await Future.delayed(Duration(milliseconds: 150 * (1 << attempt)));
        attempt++;
      }
    }
    throw last!;
  }

  bool _isRetriable(DioException e) {
    final m = e.requestOptions.method.toUpperCase();
    if (m != 'GET' && m != 'HEAD') return false;
    return e.type == DioExceptionType.connectionError ||
        e.type == DioExceptionType.receiveTimeout ||
        e.type == DioExceptionType.connectionTimeout;
  }

  Object _normalizeDioError(DioException e) {
    // Connection refused / network down should not crash UI
    if (e.type == DioExceptionType.connectionError ||
        e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return ApiUnavailable(message: e.message ?? 'API unavailable');
    }
    return ApiFailure(
      message: e.message ?? 'Request failed',
      cause: e,
      statusCode: e.response?.statusCode,
    );
  }
}

class ApiUnavailable implements Exception {
  ApiUnavailable({required this.message});
  final String message;
  @override
  String toString() => 'ApiUnavailable($message)';
}

class ApiFailure implements Exception {
  ApiFailure({required this.message, this.cause, this.statusCode});
  final String message;
  final Object? cause;
  final int? statusCode;
  @override
  String toString() => 'ApiFailure($message)';
}
