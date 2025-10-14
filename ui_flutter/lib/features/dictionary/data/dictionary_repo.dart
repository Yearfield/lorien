import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'dictionary_dto.dart';

class DictionaryRepo {
  final String base; // e.g., http://127.0.0.1:8000/api/v1

  DictionaryRepo(this.base);

  Future<DictionarySearchResult> searchTerms({
    required String query,
    int limit = 50,
    int offset = 0,
  }) async {
    final uri = Uri.parse('$base/dictionary/search').replace(
      queryParameters: {
        'q': query,
        'limit': limit.toString(),
        'offset': offset.toString(),
      },
    );

    final response = await http.get(uri);
    if (response.statusCode != 200) {
      throw Exception('Search failed: ${response.statusCode} ${response.body}');
    }

    return DictionarySearchResult.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<DictionaryTerm> getTermById(int termId) async {
    final uri = Uri.parse('$base/dictionary/$termId');
    final response = await http.get(uri);

    if (response.statusCode == 404) {
      throw Exception('Term not found');
    }
    if (response.statusCode != 200) {
      throw Exception('Failed to get term: ${response.statusCode} ${response.body}');
    }

    return DictionaryTerm.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<DictionaryTerm> getTermByName(String termName) async {
    final uri = Uri.parse('$base/dictionary/term/${Uri.encodeComponent(termName)}');
    final response = await http.get(uri);

    if (response.statusCode == 404) {
      throw Exception('Term not found');
    }
    if (response.statusCode != 200) {
      throw Exception('Failed to get term: ${response.statusCode} ${response.body}');
    }

    return DictionaryTerm.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<DictionaryTerm> updateTerm({
    required int termId,
    String? definition,
    List<String>? synonyms,
    bool? isRedFlag,
  }) async {
    final uri = Uri.parse('$base/dictionary/$termId');

    final requestBody = <String, dynamic>{};
    if (definition != null) requestBody['definition'] = definition;
    if (synonyms != null) requestBody['synonyms'] = synonyms;
    if (isRedFlag != null) requestBody['is_red_flag'] = isRedFlag;

    final response = await http.put(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(requestBody),
    );

    if (response.statusCode == 404) {
      throw Exception('Term not found');
    }
    if (response.statusCode != 200) {
      throw Exception('Failed to update term: ${response.statusCode} ${response.body}');
    }

    return DictionaryTerm.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<String> exportCsv({
    bool includeSynonyms = true,
    bool includeRedFlags = true,
  }) async {
    final uri = Uri.parse('$base/dictionary/export/csv').replace(
      queryParameters: {
        'include_synonyms': includeSynonyms.toString(),
        'include_red_flags': includeRedFlags.toString(),
      },
    );

    final response = await http.get(uri);
    if (response.statusCode != 200) {
      throw Exception('Export failed: ${response.statusCode} ${response.body}');
    }

    return response.body;
  }

  Future<DictionaryStats> getStats() async {
    final uri = Uri.parse('$base/dictionary/stats');
    final response = await http.get(uri);

    if (response.statusCode != 200) {
      throw Exception('Failed to get stats: ${response.statusCode} ${response.body}');
    }

    return DictionaryStats.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<DictionaryTreeRelationships> getTreeRelationships(int termId) async {
    final uri = Uri.parse('$base/dictionary/tree/$termId/relationships');
    final response = await http.get(uri);

    if (response.statusCode == 404) {
      throw Exception('Term not found');
    }
    if (response.statusCode != 200) {
      throw Exception('Failed to get relationships: ${response.statusCode} ${response.body}');
    }

    return DictionaryTreeRelationships.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<Map<String, dynamic>> uploadDictionary(
    File file, {
    bool updateExisting = true,
    bool createNewTerms = true,
    double minSimilarity = 0.8,
  }) async {
    final uri = Uri.parse('$base/dictionary/upload').replace(
      queryParameters: {
        'update_existing': updateExisting.toString(),
        'create_new_terms': createNewTerms.toString(),
        'min_similarity': minSimilarity.toString(),
      },
    );

    final request = http.MultipartRequest('POST', uri);
    request.files.add(
      await http.MultipartFile.fromPath('file', file.path),
    );

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode != 200) {
      throw Exception('Upload failed: ${response.statusCode} ${response.body}');
    }

    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> validateDictionaryFile(File file) async {
    final uri = Uri.parse('$base/dictionary/upload/validate');
    final request = http.MultipartRequest('POST', uri);

    request.files.add(
      await http.MultipartFile.fromPath('file', file.path),
    );

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode != 200) {
      throw Exception('Validation failed: ${response.statusCode} ${response.body}');
    }

    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  // Rename and merge operations
  Future<DictionaryTerm> renameTerm(int termId, String newTerm) async {
    final uri = Uri.parse('$base/dictionary/$termId/rename');
    final response = await http.put(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'new_term': newTerm}),
    );

    if (response.statusCode == 409) {
      throw Exception('Term already exists. Use merge operation instead.');
    }
    if (response.statusCode == 404) {
      throw Exception('Term not found');
    }
    if (response.statusCode != 200) {
      throw Exception('Rename failed: ${response.statusCode} ${response.body}');
    }

    return DictionaryTerm.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<Map<String, dynamic>> mergeTerms(
    int sourceTermId,
    int targetTermId, {
    List<String> selectedChildren = const [],
  }) async {
    final uri = Uri.parse('$base/dictionary/$sourceTermId/merge');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'target_term_id': targetTermId,
        'selected_children': selectedChildren,
      }),
    );

    if (response.statusCode == 404) {
      throw Exception('Source or target term not found');
    }
    if (response.statusCode == 422) {
      throw Exception('Cannot have more than 5 children');
    }
    if (response.statusCode != 200) {
      throw Exception('Merge failed: ${response.statusCode} ${response.body}');
    }

    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getRenameConflicts(int termId, String newTerm) async {
    final uri = Uri.parse('$base/dictionary/$termId/rename-conflicts').replace(
      queryParameters: {'new_term': newTerm},
    );
    final response = await http.get(uri);

    if (response.statusCode == 404) {
      throw Exception('Term not found');
    }
    if (response.statusCode != 200) {
      throw Exception('Failed to get rename conflicts: ${response.statusCode} ${response.body}');
    }

    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getMergeConflicts(int sourceTermId, int targetTermId) async {
    final uri = Uri.parse('$base/dictionary/$sourceTermId/merge-conflicts').replace(
      queryParameters: {'target_term_id': targetTermId.toString()},
    );
    final response = await http.get(uri);

    if (response.statusCode == 404) {
      throw Exception('Source or target term not found');
    }
    if (response.statusCode != 200) {
      throw Exception('Failed to get merge conflicts: ${response.statusCode} ${response.body}');
    }

    return jsonDecode(response.body) as Map<String, dynamic>;
  }
}
