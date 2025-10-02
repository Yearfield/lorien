import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/api_config.dart';

class ConflictsRepo {
  final String base;

  ConflictsRepo(this.base);

  Future<List<Map<String, dynamic>>> scan() async {
    final response = await http.get(Uri.parse('$base/conflicts/scan'));
    if (response.statusCode != 200) {
      throw Exception('Scan failed: ${response.statusCode} ${response.body}');
    }
    final data = jsonDecode(response.body) as List;
    return data.cast<Map<String, dynamic>>();
  }

  Future<Map<String, dynamic>> resolve({
    required String label,
    required List<String> selected,
    bool dryRun = false,
  }) async {
    final response = await http.post(
      Uri.parse('$base/conflicts/resolve'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'label': label,
        'selected_children': selected,
        'dry_run': dryRun,
      }),
    );
    
    if (response.statusCode == 422) {
      throw Exception('Validation error: ${response.body}');
    }
    if (response.statusCode != 200) {
      throw Exception('Resolve failed: ${response.statusCode} ${response.body}');
    }
    
    return jsonDecode(response.body) as Map<String, dynamic>;
  }
}
