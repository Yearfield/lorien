import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:file_picker/file_picker.dart';

class VmRepo {
  final String base; // e.g., http://127.0.0.1:8000/api/v1

  VmRepo(this.base);

  Future<Map<String, dynamic>> importPreview(Uint8List bytes) async {
    final uri = Uri.parse('$base/import/preview');
    final req = http.MultipartRequest('POST', uri)
      ..files.add(http.MultipartFile.fromBytes('file', bytes, filename: 'import.csv', contentType: MediaType('text', 'csv')));
    final streamed = await req.send();
    final r = await http.Response.fromStream(streamed);
    if (r.statusCode != 200) {
      throw Exception('preview failed: ${r.statusCode} ${r.body}');
    }
    return jsonDecode(r.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> importApply(Uint8List bytes, {bool enforceFive = true, String mode = 'append'}) async {
    final uri = Uri.parse('$base/import?mode=$mode&enforce_five=${enforceFive ? 'true' : 'false'}');
    final req = http.MultipartRequest('POST', uri)
      ..files.add(http.MultipartFile.fromBytes('file', bytes, filename: 'import.csv', contentType: MediaType('text', 'csv')));
    final streamed = await req.send();
    final r = await http.Response.fromStream(streamed);
    if (r.statusCode == 422) {
      throw Exception('validation: ${r.body}');
    }
    if (r.statusCode != 200) {
      throw Exception('import failed: ${r.statusCode} ${r.body}');
    }
    return jsonDecode(r.body) as Map<String, dynamic>;
  }

  Future<List<Map<String, dynamic>>> getRoots() async {
    final r = await http.get(Uri.parse('$base/tree/roots'));
    if (r.statusCode != 200) throw Exception('roots failed');
    final json = jsonDecode(r.body);
    return (json['items'] as List).cast<Map<String, dynamic>>();
  }

  Future<List<Map<String, dynamic>>> getChildren(int parentId, {bool onlyRed = false}) async {
    final uri = Uri.parse('$base/tree/children?parent_id=$parentId&only_red=${onlyRed ? 'true' : 'false'}');
    final r = await http.get(uri);
    if (r.statusCode != 200) throw Exception('children failed');
    final json = jsonDecode(r.body);
    return (json['items'] as List).cast<Map<String, dynamic>>();
  }

  Future<void> putChildren(int parentId, List<String> labels) async {
    final body = jsonEncode({
      "parent_id": parentId,
      "children": labels.map((e) => {"label": e}).toList(),
    });
    final r = await http.put(
      Uri.parse('$base/tree/children'),
      headers: {'Content-Type': 'application/json'},
      body: body,
    );
    if (r.statusCode != 200) {
      throw Exception('save failed: ${r.statusCode} ${r.body}');
    }
  }

  Future<void> addChild(int parentId, String label) async {
    // Add a single child safely without affecting existing children
    final body = jsonEncode({
      "parent_id": parentId,
      "label": label,
    });
    final r = await http.post(
      Uri.parse('$base/tree/child'),
      headers: {'Content-Type': 'application/json'},
      body: body,
    );
    if (r.statusCode != 200 && r.statusCode != 201) {
      throw Exception('add child failed: ${r.statusCode} ${r.body}');
    }
  }

  Future<void> deleteRoot(int rootId) async {
    final uri = Uri.parse('$base/tree/roots/$rootId');
    final r = await http.delete(uri);
    if (r.statusCode != 204) {
      throw Exception('delete root failed: ${r.statusCode} ${r.body}');
    }
  }

  Future<Map<String, dynamic>> getNode(int nodeId) async {
    final r = await http.get(Uri.parse('$base/tree/node?node_id=$nodeId'));
    if (r.statusCode != 200) throw Exception('get node failed');
    return (jsonDecode(r.body) as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>?> getParentInfo(int parentId) async {
    try {
      final nodeInfo = await getNode(parentId);
      return {
        'label': nodeInfo['label'],
        'depth': nodeInfo['depth'],
      };
    } catch (e) {
      return null; // Parent not found
    }
  }

  Future<List<Map<String, dynamic>>> findParentsByLabel(String label) async {
    final response = await http.get(Uri.parse('$base/tree/search-by-label?label=${Uri.encodeQueryComponent(label)}'));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return List<Map<String, dynamic>>.from(data['items'] ?? []);
    } else {
      throw Exception('Search failed: ${response.statusCode} ${response.body}');
    }
  }

  Future<void> renameParent(int parentId, String newName) async {
    final response = await http.put(
      Uri.parse('$base/tree/node/$parentId/rename'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'label': newName}),
    );

    if (response.statusCode != 200) {
      throw Exception('Rename failed: ${response.statusCode} ${response.body}');
    }
  }

  Future<void> mergeParents(int currentParentId, int existingParentId, List<String> selectedChildren) async {
    final response = await http.post(
      Uri.parse('$base/tree/merge-parents'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'current_parent_id': currentParentId,
        'existing_parent_id': existingParentId,
        'selected_children': selectedChildren,
      }),
    );

    if (response.statusCode != 200) {
      throw Exception('Merge failed: ${response.statusCode} ${response.body}');
    }
  }

  // mode: "replace" or "append"
  Future<Map<String, dynamic>> importFile(String mode, Uint8List bytes, String filename) async {
    final uri = Uri.parse('$base/import?mode=$mode');
    final req = http.MultipartRequest('POST', uri);
    req.files.add(http.MultipartFile.fromBytes(
      'file',
      bytes,
      filename: filename,
      contentType: filename.toLowerCase().endsWith('.csv')
          ? MediaType('text', 'csv')
          : MediaType('application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    ));
    final streamed = await req.send();
    final res = await http.Response.fromStream(streamed);
    if (res.statusCode != 200 && res.statusCode != 201) {
      throw Exception('import failed: ${res.statusCode} ${res.body}');
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>?> nextUnderfilled({int? rootId, int? afterId}) async {
    final q = <String>[];
    if (rootId != null) q.add('root_id=$rootId');
    if (afterId != null) q.add('after_id=$afterId');
    final uri = Uri.parse('$base/tree/next-underfilled${q.isEmpty ? '' : '?'+q.join('&')}');
    final r = await http.get(uri);
    if (r.statusCode == 204) {
      return null;
    }
    if (r.statusCode != 200) {
      throw Exception('next-underfilled failed: ${r.statusCode} ${r.body}');
    }
    final data = jsonDecode(r.body);
    if (data is Map<String, dynamic>) {
      return data;
    }
    return null;
  }

  Future<void> setEdgeFlag(int parentId, int childId, bool red) async {
    final r = await http.put(Uri.parse('$base/tree/edge/flag'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'parent_id': parentId, 'child_id': childId, 'red_flag': red}));
    if (r.statusCode != 200) throw Exception('edge flag failed: ${r.statusCode} ${r.body}');
  }

  Future<List<Map<String, dynamic>>> findCloneCandidates(String label) async {
    final r = await http.get(Uri.parse('$base/tree/clone/candidates?label=${Uri.encodeQueryComponent(label)}'));
    if (r.statusCode != 200) throw Exception('clone candidates failed: ${r.statusCode} ${r.body}');
    final items = (jsonDecode(r.body)['items'] as List).cast<Map<String, dynamic>>();
    return items;
  }

  Future<Map<String, dynamic>> cloneSubtree({required int sourceId, required int destParentId}) async {
    final r = await http.post(Uri.parse('$base/tree/clone'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'source_id': sourceId, 'dest_parent_id': destParentId}));
    if (r.statusCode != 200) throw Exception('clone failed: ${r.statusCode} ${r.body}');
    return jsonDecode(r.body) as Map<String, dynamic>;
  }

  Future<List<Map<String, dynamic>>> ancestors(int nodeId) async {
    final uri = Uri.parse('$base/tree/ancestors?node_id=$nodeId');
    final r = await http.get(uri);
    if (r.statusCode != 200) throw Exception('ancestors failed: ${r.statusCode}');
    final data = jsonDecode(r.body) as Map<String, dynamic>;
    return (data['items'] as List).cast<Map<String, dynamic>>();
  }

  Future<String?> exportCsv({int? rootId}) async {
    final qs = [
      'format=csv',
      if (rootId != null) 'root_ids=$rootId',
    ].join('&');
    final uri = Uri.parse('$base/tree/export?$qs');

    // Prompt user for save location
    final ts = DateTime.now().toIso8601String().replaceAll(':', '-');
    final suggested = 'lorien_export_$ts.csv';
    final savePath = await FilePicker.platform.saveFile(
      dialogTitle: 'Save Export File',
      fileName: suggested,
      type: FileType.custom,
      allowedExtensions: ['csv'],
    );
    if (savePath == null) {
      // user canceled
      return null;
    }

    final r = await http.get(uri);
    if (r.statusCode != 200) {
      throw Exception('export failed: ${r.statusCode} ${r.body}');
    }
    final file = File(savePath);
    await file.writeAsBytes(r.bodyBytes);
    return savePath;
  }

  Future<Map<String, dynamic>> createRoot(String label) async {
    final uri = Uri.parse('$base/tree/roots');
    final r = await http.post(uri, headers: {'Content-Type': 'application/json'}, body: jsonEncode({'label': label}));
    if (r.statusCode != 201) throw Exception('create root failed: ${r.statusCode} ${r.body}');
    return jsonDecode(r.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> deleteNodeDryRun(int nodeId) async {
    final uri = Uri.parse('$base/tree/node/$nodeId?dry_run=true');
    final res = await http.delete(uri);
    if (res.statusCode != 200) {
      throw Exception('delete dry run failed: ${res.statusCode} ${res.body}');
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> deleteNodeApply(int nodeId) async {
    final uri = Uri.parse('$base/tree/node/$nodeId?dry_run=false');
    final res = await http.delete(uri);
    if (res.statusCode != 200) {
      throw Exception('delete apply failed: ${res.statusCode} ${res.body}');
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> restoreSubtree(Map<String, dynamic> snapshot) async {
    final uri = Uri.parse('$base/tree/subtree/restore');
    final res = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'snapshot': snapshot})
    );
    if (res.statusCode != 200) {
      throw Exception('restore failed: ${res.statusCode} ${res.body}');
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }
}
