import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/health_service.dart';
import 'dio_interceptors.dart';

/// Abstract API client interface for network operations
abstract class ApiClient {
  /// GET request with optional query parameters
  Future<Map<String, dynamic>> get(
    String path, {
    Map<String, dynamic>? query,
  });

  /// POST request with optional body and query parameters
  Future<Map<String, dynamic>> post(
    String path, {
    Object? body,
    Map<String, dynamic>? query,
  });

  /// PUT request with optional body
  Future<Map<String, dynamic>> put(
    String path, {
    Object? body,
  });

  /// DELETE request
  Future<Map<String, dynamic>> delete(String path);

  /// POST multipart request for file uploads
  Future<Map<String, dynamic>> postMultipart(
    String path, {
    required Map<String, dynamic> fields,
    List<MapEntry<String, List<int>>>? files,
  });
}

final dioProvider = Provider<Dio>((ref) {
  final d = Dio(BaseOptions(
    connectTimeout: const Duration(seconds: 8),
    receiveTimeout: const Duration(seconds: 8),
  ));
  d.interceptors.add(BaseUrlInterceptor(() => ref.read(baseUrlProvider)));
  return d;
});
