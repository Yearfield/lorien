import 'dart:convert';
import 'package:http/http.dart' as http;

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
}
