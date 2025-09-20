import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

class VmRepo {
  final String base; // e.g., http://127.0.0.1:8000/api/v1

  VmRepo(this.base);

  Future<List<Map<String, dynamic>>> getRoots() async {
    final r = await http.get(Uri.parse('$base/tree/roots'));
    if (r.statusCode != 200) throw Exception('roots failed');
    final json = jsonDecode(r.body);
    return (json['items'] as List).cast<Map<String, dynamic>>();
  }

  Future<List<Map<String, dynamic>>> getChildren(int parentId) async {
    final r = await http.get(Uri.parse('$base/tree/children?parent_id=$parentId'));
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

  Future<void> deleteRoot(int rootId) async {
    final r = await http.delete(Uri.parse('$base/tree/root?root_id=$rootId'));
    if (r.statusCode != 200) {
      throw Exception('delete root failed: ${r.statusCode} ${r.body}');
    }
  }

  Future<Map<String, dynamic>> getNode(int nodeId) async {
    final r = await http.get(Uri.parse('$base/tree/node?node_id=$nodeId'));
    if (r.statusCode != 200) throw Exception('get node failed');
    return (jsonDecode(r.body) as Map<String, dynamic>);
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
}
