import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/http/api_client.dart';

class DictionaryEntry {
  final int id;
  final String type;
  final String term;
  final String normalized;
  final String? hints;
  final String updatedAt;

  DictionaryEntry(this.id, this.type, this.term, this.normalized, this.hints, this.updatedAt);

  factory DictionaryEntry.fromJson(Map<String, dynamic> j) => DictionaryEntry(
    j['id'], j['type'], j['term'], j['normalized'], j['hints'], j['updated_at']
  );
}

class DictionaryPage {
  final List<DictionaryEntry> items;
  final int total;
  final int limit;
  final int offset;

  DictionaryPage(this.items, this.total, this.limit, this.offset);

  factory DictionaryPage.fromJson(Map<String, dynamic> j) => DictionaryPage(
    (j['items'] as List).map((e) => DictionaryEntry.fromJson(e)).toList(),
    j['total'], j['limit'], j['offset']
  );
}

final dictionaryRepositoryProvider = Provider<DictionaryRepository>((ref) {
  final dio = ref.read(dioProvider);
  return DictionaryRepository(dio);
});

final dictionarySuggestionsProvider = StateNotifierProvider.family<
    DictionarySuggestionsNotifier,
    AsyncValue<List<String>>,
    String>((ref, type) {
  return DictionarySuggestionsNotifier(ref.read(dictionaryRepositoryProvider), type);
});

class DictionarySuggestionsNotifier extends StateNotifier<AsyncValue<List<String>>> {
  final DictionaryRepository _repository;
  final String _type;
  Timer? _debounceTimer;

  DictionarySuggestionsNotifier(this._repository, this._type) : super(const AsyncValue.data([]));

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
  final Dio _dio;

  DictionaryRepository(this._dio);

  Future<DictionaryPage> list({
    String? type,
    String query = "",
    int limit = 50,
    int offset = 0
  }) async {
    final qp = {"query": query, "limit": limit, "offset": offset, if (type != null) "type": type};
    final r = await _dio.get('/dictionary', queryParameters: qp);
    return DictionaryPage.fromJson(r.data);
  }

  Future<DictionaryEntry> create({
    required String type,
    required String term,
    String? normalized,
    String? hints
  }) async {
    final r = await _dio.post('/dictionary', data: {
      "type": type, "term": term,
      if (normalized != null) "normalized": normalized,
      if (hints != null) "hints": hints
    });
    return DictionaryEntry.fromJson(r.data);
  }

  Future<DictionaryEntry> update(int id, {
    String? term,
    String? normalized,
    String? hints
  }) async {
    final r = await _dio.put('/dictionary/$id', data: {
      if (term != null) "term": term,
      if (normalized != null) "normalized": normalized,
      if (hints != null) "hints": hints
    });
    return DictionaryEntry.fromJson(r.data);
  }

  Future<void> delete(int id) async {
    await _dio.delete('/dictionary/$id');
  }

  Future<String> normalize(String type, String term) async {
    final r = await _dio.get('/dictionary/normalize',
      queryParameters: {"type": type, "term": term});
    return r.data['normalized'] as String;
  }

  Future<List<String>> getSuggestions(String type, String query, {int limit = 10}) async {
    if (query.trim().length < 2) return [];

    final r = await _dio.get('/dictionary', queryParameters: {
      "type": type,
      "query": query.trim(),
      "limit": limit,
      "offset": 0
    });

    final items = (r.data['items'] as List?) ?? [];
    return items.map((item) => (item as Map<String, dynamic>)['term'] as String).toList();
  }
}
