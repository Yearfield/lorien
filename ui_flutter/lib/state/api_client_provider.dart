import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/api_client.dart';

/// Provider for the API client instance
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient.I();
});
