import 'package:dio/dio.dart';

class HttpClient {
  HttpClient(this.dio, {required this.baseUrl});
  final Dio dio;
  final String baseUrl;

  String _url(String path) {
    // tolerate leading slashes; ensure baseUrl ends without trailing slash
    final b = baseUrl.endsWith('/') ? baseUrl.substring(0, baseUrl.length - 1) : baseUrl;
    final p = path.startsWith('/') ? path.substring(1) : path;
    return '$b/$p';
  }

  Future<Map<String, dynamic>> getJson(String path, {Map<String, dynamic>? query}) async {
    final r = await dio.get(_url(path), queryParameters: query);
    return (r.data as Map).cast<String, dynamic>();
  }

  Future<Map<String, dynamic>> postJson(String path, {Object? body, Map<String, dynamic>? query}) async {
    final r = await dio.post(_url(path), data: body, queryParameters: query);
    return (r.data as Map).cast<String, dynamic>();
  }

  /// For endpoints that return a file (CSV/XLSX/etc.)
  Future<Response<List<int>>> postBytes(String path, {Object? body, Map<String, dynamic>? query}) {
    return dio.post<List<int>>(
      _url(path),
      data: body,
      queryParameters: query,
      options: Options(responseType: ResponseType.bytes),
    );
  }

  Future<Response> postMultipart(String path, {required FormData formData, Map<String, dynamic>? query}) {
    return dio.post(_url(path), data: formData, queryParameters: query, options: Options(contentType: 'multipart/form-data'));
  }
}
