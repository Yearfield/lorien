import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import '../api/lorien_api.dart';
import '../data/api_client.dart';

// Provider for LorienApi client
final lorienApiProvider = Provider<LorienApi>((ref) {
  final apiClient = ApiClient.I();
  // Create Dio instance and use ApiClient's baseUrl
  final dio = Dio(BaseOptions(
    baseUrl: apiClient.baseUrl,
    connectTimeout: const Duration(seconds: 2),
    receiveTimeout: const Duration(seconds: 8),
    sendTimeout: const Duration(seconds: 8),
    responseType: ResponseType.json,
    followRedirects: true,
    validateStatus: (code) => code != null && code >= 200 && code < 400,
  ));
  return LorienApi(dio: dio, baseUrl: apiClient.baseUrl);
});
