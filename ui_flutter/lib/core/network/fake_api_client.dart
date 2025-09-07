import 'dart:math';
import '../http/api_client.dart';
import 'http_errors.dart';

/// In-memory fake API client for testing and development
class FakeApiClient implements ApiClient {
  final Map<String, dynamic> _state;
  final Map<String, bool> _toggles;

  FakeApiClient({
    Map<String, dynamic>? initialState,
    Map<String, bool>? toggles,
  }) : _state = initialState ?? _defaultState(),
        _toggles = toggles ?? {};

  static Map<String, dynamic> _defaultState() => {
    'nodes': <Map<String, dynamic>>[],
    'roots': <Map<String, dynamic>>[],
    'dictionary': <Map<String, dynamic>>[],
    'triage': <Map<String, dynamic>>[],
    'nextId': 1,
  };

  @override
  Future<Map<String, dynamic>> get(
    String path, {
    Map<String, dynamic>? query,
  }) async {
    await Future.delayed(const Duration(milliseconds: 100)); // Simulate network delay

    switch (path) {
      case '/health':
        return {
          'ok': true,
          'version': '0.9.0-beta.1',
          'db': {
            'wal': true,
            'foreign_keys': true,
            'page_size': 4096,
            'path': '/fake/db/path'
          },
          'features': {
            'llm': _toggles['llmReady'] ?? false,
            'csv_export': true,
          }
        };

      case '/tree/stats':
        final nodes = _state['nodes'] as List<Map<String, dynamic>>;
        final roots = _state['roots'] as List<Map<String, dynamic>>;
        return {
          'nodes': nodes.length,
          'roots': roots.length,
          'leaves': nodes.where((n) => n['isLeaf'] == true).length,
          'complete_paths': 1,
          'incomplete_parents': roots.length - 1,
        };

      case '/tree/next-incomplete-parent':
        if (_toggles['nextIncompleteNone'] == true) {
          throw NotFound404('No incomplete parents found');
        }
        final roots = _state['roots'] as List<Map<String, dynamic>>;
        if (roots.isEmpty) {
          throw NotFound404('No roots found');
        }
        return {
          'parent_id': roots.first['id'],
          'label': roots.first['label'],
          'depth': 0,
          'missing_slots': '2,3,4,5',
        };

      case '/dictionary':
        final dictionary = _state['dictionary'] as List<Map<String, dynamic>>;
        final type = query?['type'] as String?;
        final searchQuery = query?['query'] as String?;
        final limit = (query?['limit'] as int?) ?? 50;
        final offset = (query?['offset'] as int?) ?? 0;

        var filtered = dictionary;
        if (type != null) {
          filtered = filtered.where((item) => item['type'] == type).toList();
        }
        if (searchQuery != null && searchQuery.isNotEmpty) {
          filtered = filtered.where((item) => 
            item['term'].toString().toLowerCase().contains(searchQuery.toLowerCase())
          ).toList();
        }

        final paginated = filtered.skip(offset).take(limit).toList();
        return {
          'items': paginated,
          'total': filtered.length,
          'limit': limit,
          'offset': offset,
        };

      default:
        if (path.startsWith('/tree/') && path.endsWith('/children')) {
          final parentId = int.parse(path.split('/')[2]);
          final children = (_state['nodes'] as List<Map<String, dynamic>>)
              .where((n) => n['parentId'] == parentId)
              .toList();
          return {
            'parent_id': parentId,
            'children': children,
          };
        }
        throw NotFound404('Endpoint not found: $path');
    }
  }

  @override
  Future<Map<String, dynamic>> post(
    String path, {
    Object? body,
    Map<String, dynamic>? query,
  }) async {
    await Future.delayed(const Duration(milliseconds: 100));

    switch (path) {
      case '/tree/roots':
        final data = body as Map<String, dynamic>;
        final label = data['label'] as String;
        
        // Check for duplicates
        final roots = _state['roots'] as List<Map<String, dynamic>>;
        if (roots.any((r) => r['label'].toString().toLowerCase() == label.toLowerCase())) {
          throw Validation422([
            {
              'loc': ['body', 'label'],
              'msg': 'Vital Measurement with this label already exists',
              'type': 'value_error.duplicate_vm'
            }
          ]);
        }

        final rootId = _state['nextId']++;
        final root = {
          'id': rootId,
          'label': label,
          'depth': 0,
          'parentId': null,
          'slot': 0,
          'isLeaf': false,
        };
        roots.add(root);

        // Create 5 child slots
        final nodes = _state['nodes'] as List<Map<String, dynamic>>;
        for (int slot = 1; slot <= 5; slot++) {
          final childId = _state['nextId']++;
          nodes.add({
            'id': childId,
            'parentId': rootId,
            'depth': 1,
            'slot': slot,
            'label': 'Slot $slot',
            'isLeaf': false,
          });
        }

        return {
          'root_id': rootId,
          'label': label,
          'children_created': 5,
        };

      case '/dictionary':
        final data = body as Map<String, dynamic>;
        final term = data['term'] as String;
        final type = data['type'] as String;
        
        // Check for duplicates
        final dictionary = _state['dictionary'] as List<Map<String, dynamic>>;
        if (dictionary.any((d) => 
            d['type'] == type && d['term'].toString().toLowerCase() == term.toLowerCase())) {
          throw Validation422([
            {
              'loc': ['body', 'term'],
              'msg': 'Term already exists for this type',
              'type': 'value_error.duplicate_term'
            }
          ]);
        }

        final id = _state['nextId']++;
        final normalized = term.toLowerCase().trim();
        final entry = {
          'id': id,
          'type': type,
          'term': term,
          'normalized': normalized,
          'hints': data['hints'],
          'updated_at': DateTime.now().toIso8601String(),
        };
        dictionary.add(entry);

        return entry;

      case '/import':
        if (_toggles['importHeaderMismatch'] == true) {
          throw Validation422([
            {
              'loc': ['body', 'file'],
              'msg': 'CSV header mismatch',
              'type': 'value_error.csv_schema',
              'ctx': {
                'first_offending_row': 0,
                'col_index': 0,
                'expected': ['Vital Measurement', 'Node 1', 'Node 2', 'Node 3', 'Node 4', 'Node 5', 'Diagnostic Triage', 'Actions'],
                'received': ['Wrong', 'Header'],
                'error_counts': {'header': 1}
              }
            }
          ]);
        }

        return {
          'status': 'success',
          'rows_processed': 1,
          'created': {
            'roots': 1,
            'nodes': 3,
          },
          'updated': {
            'nodes': 0,
            'outcomes': 1,
          }
        };

      default:
        throw NotFound404('Endpoint not found: $path');
    }
  }

  @override
  Future<Map<String, dynamic>> put(
    String path, {
    Object? body,
  }) async {
    await Future.delayed(const Duration(milliseconds: 100));

    if (path.startsWith('/triage/')) {
      final nodeId = int.parse(path.split('/')[2]);
      final data = body as Map<String, dynamic>;
      
      // Validate word count (≤7 words per field)
      final diagnosis = data['diagnostic_triage'] as String? ?? '';
      final actions = data['actions'] as String? ?? '';
      
      if (diagnosis.split(' ').length > 7) {
        throw Validation422([
          {
            'loc': ['body', 'diagnostic_triage'],
            'msg': 'Diagnostic triage must be 7 words or less',
            'type': 'value_error.word_limit'
          }
        ]);
      }
      
      if (actions.split(' ').length > 7) {
        throw Validation422([
          {
            'loc': ['body', 'actions'],
            'msg': 'Actions must be 7 words or less',
            'type': 'value_error.word_limit'
          }
        ]);
      }

      // Validate regex pattern
      final regex = RegExp(r'^[A-Za-z0-9 ,\-]+$');
      if (!regex.hasMatch(diagnosis) || !regex.hasMatch(actions)) {
        throw Validation422([
          {
            'loc': ['body'],
            'msg': 'Fields must contain only alphanumeric characters, spaces, commas, and hyphens',
            'type': 'value_error.invalid_characters'
          }
        ]);
      }

      final triage = _state['triage'] as List<Map<String, dynamic>>;
      final existingIndex = triage.indexWhere((t) => t['node_id'] == nodeId);
      
      final triageData = {
        'node_id': nodeId,
        'diagnostic_triage': diagnosis,
        'actions': actions,
        'updated_at': DateTime.now().toIso8601String(),
      };

      if (existingIndex >= 0) {
        triage[existingIndex] = triageData;
      } else {
        triage.add(triageData);
      }

      return triageData;
    }

    throw NotFound404('Endpoint not found: $path');
  }

  @override
  Future<Map<String, dynamic>> delete(String path) async {
    await Future.delayed(const Duration(milliseconds: 100));
    
    if (path.startsWith('/dictionary/')) {
      final id = int.parse(path.split('/')[2]);
      final dictionary = _state['dictionary'] as List<Map<String, dynamic>>;
      dictionary.removeWhere((d) => d['id'] == id);
      return {'ok': true};
    }

    throw NotFound404('Endpoint not found: $path');
  }

  @override
  Future<Map<String, dynamic>> postMultipart(
    String path, {
    required Map<String, dynamic> fields,
    List<MapEntry<String, List<int>>>? files,
  }) async {
    // For multipart requests, delegate to regular post
    return post(path, body: fields);
  }

  /// Toggle flags for testing different scenarios
  void setToggle(String key, bool value) {
    _toggles[key] = value;
  }

  /// Get current state for debugging
  Map<String, dynamic> getState() => Map.from(_state);
}
