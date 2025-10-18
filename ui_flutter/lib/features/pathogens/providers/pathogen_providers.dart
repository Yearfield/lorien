import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lorien/features/pathogens/models/pathogen_models.dart';
import 'package:lorien/features/pathogens/services/pathogen_service.dart';

// Service provider
final pathogenServiceProvider = Provider<PathogenService>((ref) {
  return PathogenService();
});

// Pathogen list provider
final pathogenListProvider = StateNotifierProvider<PathogenListNotifier, AsyncValue<List<Pathogen>>>((ref) {
  final service = ref.watch(pathogenServiceProvider);
  return PathogenListNotifier(service);
});

// Association types provider
final associationTypesProvider = StateNotifierProvider<AssociationTypesNotifier, AsyncValue<List<AssociationType>>>((ref) {
  final service = ref.watch(pathogenServiceProvider);
  return AssociationTypesNotifier(service);
});

// Pathogen stats provider
final pathogenStatsProvider = StateNotifierProvider<PathogenStatsNotifier, AsyncValue<PathogenStats?>>((ref) {
  final service = ref.watch(pathogenServiceProvider);
  return PathogenStatsNotifier(service);
});

// Pathogen detail provider
final pathogenDetailProvider = StateNotifierProvider.family<PathogenDetailNotifier, AsyncValue<PathogenWithAssociations?>, int>((ref, pathogenId) {
  final service = ref.watch(pathogenServiceProvider);
  return PathogenDetailNotifier(service, pathogenId);
});

// Import result provider
final pathogenImportResultProvider = StateProvider<PathogenImportResult?>((ref) => null);

class PathogenListNotifier extends StateNotifier<AsyncValue<List<Pathogen>>> {
  final PathogenService _service;
  String _searchQuery = '';
  String? _associationFilter;
  bool _showOnlyWithAssociations = false;

  PathogenListNotifier(this._service) : super(const AsyncValue.loading()) {
    loadPathogens();
  }

  Future<void> loadPathogens() async {
    state = const AsyncValue.loading();
    try {
      final pathogens = await _service.getPathogens();
      state = AsyncValue.data(pathogens);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  Future<void> searchPathogens(String query) async {
    _searchQuery = query;
    await _applyFilters();
  }

  Future<void> filterByAssociation(String? filter) async {
    _associationFilter = filter;
    await _applyFilters();
  }

  Future<void> filterByAssociations(bool showOnlyWithAssociations) async {
    _showOnlyWithAssociations = showOnlyWithAssociations;
    await _applyFilters();
  }

  Future<void> _applyFilters() async {
    try {
      final pathogens = await _service.getPathogens(
        search: _searchQuery.isNotEmpty ? _searchQuery : null,
        associationFilter: _associationFilter,
        showOnlyWithAssociations: _showOnlyWithAssociations,
      );
      state = AsyncValue.data(pathogens);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }
}

class AssociationTypesNotifier extends StateNotifier<AsyncValue<List<AssociationType>>> {
  final PathogenService _service;

  AssociationTypesNotifier(this._service) : super(const AsyncValue.loading());

  Future<void> loadAssociationTypes() async {
    state = const AsyncValue.loading();
    try {
      final types = await _service.getAssociationTypes();
      state = AsyncValue.data(types);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }
}

class PathogenStatsNotifier extends StateNotifier<AsyncValue<PathogenStats?>> {
  final PathogenService _service;

  PathogenStatsNotifier(this._service) : super(const AsyncValue.loading());

  Future<void> loadStats() async {
    state = const AsyncValue.loading();
    try {
      final stats = await _service.getPathogenStats();
      state = AsyncValue.data(stats);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }
}

class PathogenDetailNotifier extends StateNotifier<AsyncValue<PathogenWithAssociations?>> {
  final PathogenService _service;
  final int _pathogenId;

  PathogenDetailNotifier(this._service, this._pathogenId) : super(const AsyncValue.loading()) {
    loadPathogenDetail();
  }

  Future<void> loadPathogenDetail() async {
    state = const AsyncValue.loading();
    try {
      final pathogen = await _service.getPathogenWithAssociations(_pathogenId);
      state = AsyncValue.data(pathogen);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }
}
