import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/api_client.dart';
import '../data/repos/tree_repository.dart';
import '../data/repos/triage_repository.dart';
import '../data/repos/flags_repository.dart';
import '../data/repos/calc_repository.dart';

// Repository Providers
final treeRepositoryProvider = Provider<TreeRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return TreeRepository(apiClient);
});

final triageRepositoryProvider = Provider<TriageRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return TriageRepository(apiClient);
});

final flagsRepositoryProvider = Provider<FlagsRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return FlagsRepository(apiClient);
});

final calcRepositoryProvider = Provider<CalcRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return CalcRepository(apiClient);
});

// State Providers for Tree Operations
final childrenProvider = FutureProvider.family<List<ChildSlotDTO>, int>((ref, parentId) async {
  final repository = ref.watch(treeRepositoryProvider);
  return await repository.getChildren(parentId);
});

final nextIncompleteParentProvider = FutureProvider<IncompleteParentDTO?>((ref) async {
  final repository = ref.watch(treeRepositoryProvider);
  return await repository.getNextIncompleteParent();
});

// State Providers for Triage Operations
final triageProvider = FutureProvider.family<TriageDTO?, int>((ref, nodeId) async {
  final repository = ref.watch(triageRepositoryProvider);
  return await repository.getTriage(nodeId);
});

// State Providers for Flags Operations
final flagsSearchProvider = FutureProvider.family<List<RedFlagDTO>, String>((ref, query) async {
  final repository = ref.watch(flagsRepositoryProvider);
  return await repository.searchFlags(query);
});

// State Providers for Calculator Operations
final healthProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final repository = ref.watch(calcRepositoryProvider);
  return await repository.getHealth();
});

final csvExportProvider = FutureProvider<String>((ref) async {
  final repository = ref.watch(calcRepositoryProvider);
  return await repository.exportCsv();
});
