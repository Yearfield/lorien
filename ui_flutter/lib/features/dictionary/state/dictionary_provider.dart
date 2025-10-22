import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import '../data/dictionary_dto.dart';
import '../data/dictionary_repo.dart';
import '../../../core/api_config.dart';

part 'dictionary_provider.freezed.dart';

// Repository provider
final dictionaryRepoProvider = Provider<DictionaryRepo>((ref) {
  return DictionaryRepo(ApiConfig.base);
});

// Search state
@freezed
class DictionarySearchState with _$DictionarySearchState {
  const factory DictionarySearchState({
    @Default([]) List<DictionaryTerm> items,
    @Default(0) int total,
    @Default('') String query,
    @Default(false) bool isLoading,
    String? error,
  }) = _DictionarySearchState;
}

class DictionarySearchNotifier extends StateNotifier<DictionarySearchState> {
  final DictionaryRepo _repo;

  DictionarySearchNotifier(this._repo) : super(const DictionarySearchState());

  Future<void> search(String query) async {
    if (query.trim().isEmpty) {
      state = state.copyWith(
        items: [],
        total: 0,
        query: query,
        isLoading: false,
        error: null,
      );
      return;
    }

    state = state.copyWith(isLoading: true, error: null, query: query);

    try {
      final result = await _repo.searchTerms(query: query);

      // Update conflicts count for each term using the same system as Home pane
      final updatedItems = <DictionaryTerm>[];
      for (final term in result.items) {
        try {
          final conflicts = await _repo.getConflictsForTerm(term.term);
          final conflictsCount = conflicts.isNotEmpty ? conflicts.first['occurrences'] as int : 0;
          updatedItems.add(term.copyWith(conflictsCount: conflictsCount));
        } catch (e) {
          // If conflicts lookup fails, keep original term
          updatedItems.add(term);
        }
      }

      state = state.copyWith(
        items: updatedItems,
        total: result.total,
        isLoading: false,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  void clearSearch() {
    state = const DictionarySearchState();
  }

  /// Refresh the current search results
  Future<void> refresh() async {
    if (state.query.isNotEmpty) {
      await search(state.query);
    } else if (state.items.isNotEmpty) {
      // If no search query but we have items, refresh their conflict counts
      await _refreshConflictCounts();
    }
  }

  /// Refresh conflict counts for currently displayed terms
  Future<void> _refreshConflictCounts() async {
    if (state.items.isEmpty) return;

    final updatedItems = <DictionaryTerm>[];
    for (final term in state.items) {
      try {
        final conflicts = await _repo.getConflictsForTerm(term.term);
        final conflictsCount = conflicts.isNotEmpty ? conflicts.first['occurrences'] as int : 0;
        updatedItems.add(term.copyWith(conflictsCount: conflictsCount));
      } catch (e) {
        // If conflicts lookup fails, keep original term
        updatedItems.add(term);
      }
    }

    state = state.copyWith(items: updatedItems);
  }
}

final dictionarySearchProvider = StateNotifierProvider<DictionarySearchNotifier, DictionarySearchState>((ref) {
  final repo = ref.watch(dictionaryRepoProvider);
  return DictionarySearchNotifier(repo);
});

// Term details state
@freezed
class TermDetailsState with _$TermDetailsState {
  const factory TermDetailsState({
    DictionaryTerm? term,
    DictionaryTreeRelationships? relationships,
    @Default(false) bool isLoading,
    @Default(false) bool isUpdating,
    String? error,
  }) = _TermDetailsState;
}

class TermDetailsNotifier extends StateNotifier<TermDetailsState> {
  final DictionaryRepo _repo;

  TermDetailsNotifier(this._repo) : super(const TermDetailsState());

  Future<void> loadTerm(int termId) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final term = await _repo.getTermById(termId);
      final relationships = await _repo.getTreeRelationships(termId);

      // Get conflicts for this term using the same system as Home pane
      final conflicts = await _repo.getConflictsForTerm(term.term);
      final conflictsCount = conflicts.isNotEmpty ? conflicts.first['occurrences'] as int : 0;

      // Create updated term with correct conflicts count
      final updatedTerm = term.copyWith(conflictsCount: conflictsCount);

      state = state.copyWith(
        term: updatedTerm,
        relationships: relationships,
        isLoading: false,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> updateTerm({
    String? definition,
    List<String>? synonyms,
    bool? isRedFlag,
  }) async {
    if (state.term == null) return;

    state = state.copyWith(isUpdating: true, error: null);

    try {
      final updatedTerm = await _repo.updateTerm(
        termId: state.term!.id,
        definition: definition,
        synonyms: synonyms,
        isRedFlag: isRedFlag,
      );

      state = state.copyWith(
        term: updatedTerm,
        isUpdating: false,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isUpdating: false,
        error: e.toString(),
      );
    }
  }

  void clearTerm() {
    state = const TermDetailsState();
  }
}

final termDetailsProvider = StateNotifierProvider<TermDetailsNotifier, TermDetailsState>((ref) {
  final repo = ref.watch(dictionaryRepoProvider);
  return TermDetailsNotifier(repo);
});

// Dictionary stats state
@freezed
class DictionaryStatsState with _$DictionaryStatsState {
  const factory DictionaryStatsState({
    DictionaryStats? stats,
    @Default(false) bool isLoading,
    String? error,
  }) = _DictionaryStatsState;
}

class DictionaryStatsNotifier extends StateNotifier<DictionaryStatsState> {
  final DictionaryRepo _repo;

  DictionaryStatsNotifier(this._repo) : super(const DictionaryStatsState());

  Future<void> loadStats() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final stats = await _repo.getStats();
      state = state.copyWith(
        stats: stats,
        isLoading: false,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }
}

final dictionaryStatsProvider = StateNotifierProvider<DictionaryStatsNotifier, DictionaryStatsState>((ref) {
  final repo = ref.watch(dictionaryRepoProvider);
  return DictionaryStatsNotifier(repo);
});

// Export state
@freezed
class DictionaryExportState with _$DictionaryExportState {
  const factory DictionaryExportState({
    @Default(false) bool isExporting,
    String? error,
  }) = _DictionaryExportState;
}

class DictionaryExportNotifier extends StateNotifier<DictionaryExportState> {
  final DictionaryRepo _repo;

  DictionaryExportNotifier(this._repo) : super(const DictionaryExportState());

  Future<String?> exportCsv({
    bool includeSynonyms = true,
    bool includeRedFlags = true,
  }) async {
    state = state.copyWith(isExporting: true, error: null);

    try {
      final csvContent = await _repo.exportCsv(
        includeSynonyms: includeSynonyms,
        includeRedFlags: includeRedFlags,
      );

      state = state.copyWith(
        isExporting: false,
        error: null,
      );

      return csvContent;
    } catch (e) {
      state = state.copyWith(
        isExporting: false,
        error: e.toString(),
      );
      return null;
    }
  }
}

final dictionaryExportProvider = StateNotifierProvider<DictionaryExportNotifier, DictionaryExportState>((ref) {
  final repo = ref.watch(dictionaryRepoProvider);
  return DictionaryExportNotifier(repo);
});

// Upload state
@freezed
class DictionaryUploadState with _$DictionaryUploadState {
  const factory DictionaryUploadState({
    @Default(false) bool isUploading,
    @Default(false) bool isValidating,
    Map<String, dynamic>? uploadResult,
    Map<String, dynamic>? validationResult,
    String? error,
  }) = _DictionaryUploadState;
}

class DictionaryUploadNotifier extends StateNotifier<DictionaryUploadState> {
  final DictionaryRepo _repo;

  DictionaryUploadNotifier(this._repo) : super(const DictionaryUploadState());

  Future<void> validateFile(File file) async {
    state = state.copyWith(isValidating: true, error: null, validationResult: null);

    try {
      final result = await _repo.validateDictionaryFile(file);
      state = state.copyWith(
        isValidating: false,
        validationResult: result,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isValidating: false,
        error: e.toString(),
      );
    }
  }

  Future<void> uploadFile(
    File file, {
    bool updateExisting = true,
    bool createNewTerms = true,
    double minSimilarity = 0.8,
  }) async {
    state = state.copyWith(isUploading: true, error: null, uploadResult: null);

    try {
      final result = await _repo.uploadDictionary(
        file,
        updateExisting: updateExisting,
        createNewTerms: createNewTerms,
        minSimilarity: minSimilarity,
      );

      state = state.copyWith(
        isUploading: false,
        uploadResult: result,
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isUploading: false,
        error: e.toString(),
      );
    }
  }

  void clearResults() {
    state = const DictionaryUploadState();
  }
}

final dictionaryUploadProvider = StateNotifierProvider<DictionaryUploadNotifier, DictionaryUploadState>((ref) {
  final repo = ref.watch(dictionaryRepoProvider);
  return DictionaryUploadNotifier(repo);
});
