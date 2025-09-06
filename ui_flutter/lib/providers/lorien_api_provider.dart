import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/lorien_api.dart';
import '../data/api_client.dart';

// Provider for LorienApi client
final lorienApiProvider = Provider<LorienApi>((ref) {
  final apiClient = ApiClient.I();
  return LorienApi(apiClient);
});
