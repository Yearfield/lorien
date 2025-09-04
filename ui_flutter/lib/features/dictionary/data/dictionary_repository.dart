import 'package:dio/dio.dart';
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
}
