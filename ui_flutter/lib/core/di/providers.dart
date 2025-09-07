import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../http/api_client.dart';
import '../network/dio_api_client.dart';
import '../network/fake_api_client.dart';
import '../../core/services/health_service.dart';
import '../api/health_api.dart';
import '../api/tree_api.dart';
import '../api/dictionary_api.dart';
import '../api/import_api.dart';
import '../api/outcomes_api.dart';

/// Provider for determining whether to use fake backend
final useFakeBackendProvider = StateProvider<bool>((_) => false);

/// Main API client provider that switches between real and fake implementations
final apiClientProvider = Provider<ApiClient>((ref) {
  final useFake = ref.watch(useFakeBackendProvider);
  final baseUrl = ref.watch(baseUrlProvider);
  
  if (useFake) {
    return FakeApiClient();
  } else {
    return DioApiClient(baseUrl);
  }
});

/// Convenience provider for fake API client (for testing)
final fakeApiClientProvider = Provider<FakeApiClient>((ref) {
  return FakeApiClient();
});

/// API service providers
final healthApiProvider = Provider<HealthApi>((ref) {
  return DefaultHealthApi(ref.read(apiClientProvider));
});

final treeApiProvider = Provider<TreeApi>((ref) {
  return DefaultTreeApi(ref.read(apiClientProvider));
});

final dictionaryApiProvider = Provider<DictionaryApi>((ref) {
  return DefaultDictionaryApi(ref.read(apiClientProvider));
});

final importApiProvider = Provider<ImportApi>((ref) {
  return DefaultImportApi(ref.read(apiClientProvider));
});

final outcomesApiProvider = Provider<OutcomesApi>((ref) {
  return DefaultOutcomesApi(ref.read(apiClientProvider));
});
