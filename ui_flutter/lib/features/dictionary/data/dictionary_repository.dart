import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../api/lorien_api.dart';
import '../../../providers/lorien_api_provider.dart';

class DictionaryEntry {
  final int id;
  final String type;
  final String term;
  final String normalized;
  final String? hints;
  final String updatedAt;
  final bool? isRedFlag;

  DictionaryEntry(this.id, this.type, this.term, this.normalized, this.hints,
      this.updatedAt, this.isRedFlag);

  factory DictionaryEntry.fromJson(Map<String, dynamic> j) => DictionaryEntry(
      j['id'],
      j['type'],
      j['term'],
      j['normalized'],
      j['hints'],
      j['updated_at'],
      j['is_red_flag']);
}

class DictionaryPage {
  final List<DictionaryEntry> items;
  final int total;
  final int limit;
  final int offset;

  DictionaryPage(this.items, this.total, this.limit, this.offset);

  factory DictionaryPage.fromJson(Map<String, dynamic> j) => DictionaryPage(
      (j['items'] as List).map((e) => DictionaryEntry.fromJson(e)).toList(),
      j['total'],
      j['limit'],
      j['offset']);

  DictionaryPage copyWith({
    List<DictionaryEntry>? items,
    int? total,
    int? limit,
    int? offset,
  }) {
    return DictionaryPage(
      items ?? this.items,
      total ?? this.total,
      limit ?? this.limit,
      offset ?? this.offset,
    );
  }
}

final dictionaryRepositoryProvider = Provider<DictionaryRepository>((ref) {
  final api = ref.read(lorienApiProvider);
  return DictionaryRepository(api);
});

final dictionarySuggestionsProvider = StateNotifierProvider.family<
    DictionarySuggestionsNotifier,
    AsyncValue<List<String>>,
    String>((ref, type) {
  return DictionarySuggestionsNotifier(
      ref.read(dictionaryRepositoryProvider), type);
});

class DictionarySuggestionsNotifier
    extends StateNotifier<AsyncValue<List<String>>> {
  final DictionaryRepository _repository;
  final String _type;
  Timer? _debounceTimer;

  DictionarySuggestionsNotifier(this._repository, this._type)
      : super(const AsyncValue.data([]));

  void searchDebounced(String query) {
    _debounceTimer?.cancel();
    _debounceTimer = Timer(const Duration(milliseconds: 300), () {
      search(query);
    });
  }

  Future<void> search(String query) async {
    if (query.trim().length < 2) {
      state = const AsyncValue.data([]);
      return;
    }

    state = const AsyncValue.loading();

    try {
      final suggestions = await _repository.getSuggestions(_type, query);
      state = AsyncValue.data(suggestions);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  @override
  void dispose() {
    _debounceTimer?.cancel();
    super.dispose();
  }
}

class DictionaryRepository {
  final LorienApi _api;

  DictionaryRepository(this._api);

  Future<DictionaryPage> list(
      {String? type,
      String query = "",
      int limit = 50,
      int offset = 0,
      bool onlyRedFlags = false,
      String? sort,
      String? direction}) async {
    final r = await _api.dictionaryList(
        type: type,
        query: query,
        limit: limit,
        offset: offset,
        onlyRedFlags: onlyRedFlags,
        sort: sort,
        direction: direction);
    return DictionaryPage.fromJson(r);
  }

  Future<DictionaryEntry> create(
      {required String type,
      required String term,
      String? normalized,
      String? hints,
      bool? isRedFlag}) async {
    final data = {
      "type": type,
      "term": term,
      if (normalized != null) "normalized": normalized,
      if (hints != null) "hints": hints,
      if (isRedFlag != null) "is_red_flag": isRedFlag
    };
    final r = await _api.dictionaryCreate(data);
    return DictionaryEntry.fromJson(r);
  }

  Future<DictionaryEntry> update(int id,
      {String? term,
      String? normalized,
      String? hints,
      bool? isRedFlag}) async {
    final data = {
      if (term != null) "term": term,
      if (normalized != null) "normalized": normalized,
      if (hints != null) "hints": hints,
      if (isRedFlag != null) "is_red_flag": isRedFlag
    };
    final r = await _api.dictionaryUpdate(id, data);
    return DictionaryEntry.fromJson(r);
  }

  Future<void> delete(int id) async {
    await _api.dictionaryDelete(id);
  }

  Future<String> normalize(String type, String term) async {
    final r = await _api.dictionaryNormalize(type, term);
    return r;
  }

  Future<List<String>> getSuggestions(String type, String query,
      {int limit = 10}) async {
    if (query.trim().length < 2) return [];

    try {
      final suggestions = await _api.dictionarySuggest(
          type: 'node_label', query: query, limit: limit);
      return suggestions.map((item) => item['term'] as String).toList();
    } catch (e) {
      // Fallback to empty list on error
      return [];
    }
  }

  Future<String> exportCsv(
      {String? type, String? query, bool onlyRedFlags = false}) async {
    final qp = {
      if (type != null) "type": type,
      if (query != null && query.isNotEmpty) "query": query,
      if (onlyRedFlags) "only_red_flags": onlyRedFlags
    };
    final r = await _api.client.getJson('dictionary/export/csv', query: qp);
    return r as String;
  }

  Future<Map<String, dynamic>> importFile(String filePath) async {
    final response = await _api.dictionaryImportFromPath(filePath);
    return response.data as Map<String, dynamic>;
  }
}
