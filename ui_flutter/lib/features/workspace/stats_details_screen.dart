import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class StatsDetailsScreen extends StatefulWidget {
  final String baseUrl;
  final String kind; // 'roots' | 'leaves' | 'nodes' | 'complete5' | 'complete_same' | 'complete_diff' | 'incomplete_lt4' | 'saturated'
  
  const StatsDetailsScreen({
    super.key, 
    required this.baseUrl, 
    required this.kind,
  });
  
  @override
  State<StatsDetailsScreen> createState() => _StatsDetailsState();
}

class _StatsDetailsState extends State<StatsDetailsScreen> {
  final _q = TextEditingController();
  int _limit = 50, _offset = 0, _total = 0;
  List<Map<String, dynamic>> _items = [];
  bool _loading = false;

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final b = widget.baseUrl;
      late Uri u;
      final qstr = Uri.encodeQueryComponent(_q.text);
      
      switch (widget.kind) {
        case 'roots':
          // Use the same endpoint as Calculator; it returns {items,total,...}
          u = Uri.parse('$b/api/v1/tree/root-options?limit=$_limit&offset=$_offset&q=$qstr');
          break;
        case 'leaves':
          u = Uri.parse('$b/api/v1/tree/leaves?limit=$_limit&offset=$_offset&q=$qstr');
          break;
        case 'complete5':
          u = Uri.parse('$b/api/v1/tree/parents/query?filter=complete5&limit=$_limit&offset=$_offset&q=$qstr');
          break;
        case 'complete_same':
          u = Uri.parse('$b/api/v1/tree/parents/query?filter=complete_same&limit=$_limit&offset=$_offset&q=$qstr');
          break;
        case 'complete_diff':
          u = Uri.parse('$b/api/v1/tree/parents/query?filter=complete_diff&limit=$_limit&offset=$_offset&q=$qstr');
          break;
        case 'incomplete_lt4':
          u = Uri.parse('$b/api/v1/tree/parents/query?filter=incomplete_lt4&limit=$_limit&offset=$_offset&q=$qstr');
          break;
        case 'saturated':
          u = Uri.parse('$b/api/v1/tree/parents/query?filter=saturated&limit=$_limit&offset=$_offset&q=$qstr');
          break;
        default:
          u = Uri.parse('$b/api/v1/tree/export-json?limit=$_limit&offset=$_offset');
      }
      
      final r = await http.get(u);
      if (r.statusCode != 200) {
        if (!mounted) return;
        setState(() { _items = []; _total = 0; _loading = false; });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Load failed (${r.statusCode})')),
        );
        return;
      }
      
      final j = jsonDecode(r.body);
      List items;
      if (j is Map && j['items'] is List) {
        items = j['items'];
      } else if (j is List) {
        items = j;
      } else if (j is Map && j['roots'] is List) { // legacy shape fallback
        items = j['roots'];
      } else {
        items = const [];
      }
      
      setState(() {
        _items = items.cast<Map<String, dynamic>>();
        _total = (j is Map && j['total'] is int) ? j['total'] : _items.length;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _loading = false);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
    }
  }

  Future<void> _delete(int nodeId) async {
    final b = widget.baseUrl;
    final ok = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Delete node?'),
        content: const Text('This removes the node and its subtree. Continue?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Delete'),
          ),
        ],
      ),
    ) ?? false;
    
    if (!ok) return;
    
    final r = await http.delete(Uri.parse('$b/api/v1/tree/$nodeId'));
    if (r.statusCode == 200) _load();
  }

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Details: ${widget.kind}')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _q,
                    decoration: const InputDecoration(
                      prefixIcon: Icon(Icons.search),
                      hintText: 'Search',
                    ),
                    onSubmitted: (_) => _load(),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: _load,
                  child: const Text('Search'),
                ),
              ],
            ),
          ),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : _items.isEmpty
                    ? const Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.inbox_outlined, size: 64, color: Colors.grey),
                            SizedBox(height: 16),
                            Text('No items found', style: TextStyle(fontSize: 18, color: Colors.grey)),
                            SizedBox(height: 8),
                            Text('Try adjusting your search or filters', style: TextStyle(color: Colors.grey)),
                          ],
                        ),
                      )
                    : ListView.separated(
                        itemCount: _items.length,
                        separatorBuilder: (_, __) => const Divider(height: 1),
                        itemBuilder: (_, i) {
                          final it = _items[i];
                          final id = it['id'] ?? it['node_id'] ?? 0;
                          final label = it['label'] ?? it['Vital Measurement'] ?? '—';
                          final meta = 'depth=${it['depth'] ?? '-'} • children=${it['child_count'] ?? '-'}';
                          
                          return ListTile(
                            title: Text(label),
                            subtitle: Text(meta),
                            trailing: IconButton(
                              icon: const Icon(Icons.delete_outline),
                              onPressed: () => _delete(id),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}