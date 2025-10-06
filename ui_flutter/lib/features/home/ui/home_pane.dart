import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/services.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:io';
import 'package:path/path.dart' as p;
import '../../../core/api_config.dart';
import '../data/conflicts_repo.dart';
import '../state/conflicts_provider.dart';

final conflictsProvider = ChangeNotifierProvider<ConflictsState>((ref) {
  return ConflictsState(ConflictsRepo(ApiConfig.base))..scan();
});

class HomePane extends StatelessWidget {
  const HomePane({super.key});

  @override
  Widget build(BuildContext context) {
    return const _HomeDashboard();
  }
}

class _HomeDashboard extends ConsumerWidget {
  const _HomeDashboard();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final conflictsState = ref.watch(conflictsProvider);
    
    return Stack(
      children: [
        SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Conflicts Panel
              _ConflictsCard(),
              const SizedBox(height: 16),
              // Export Panel
              _ExportCard(),
              const SizedBox(height: 16),
              // New Submission Panel
              _NewSubmissionCard(),
            ],
          ),
        ),
        if (conflictsState.isBusy)
          Container(
            color: Colors.black12,
            alignment: Alignment.center,
            child: const CircularProgressIndicator(),
          ),
      ],
    );
  }
}

class _ConflictsCard extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final conflictsState = ref.watch(conflictsProvider);
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Text(
                  'Conflicts',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                FilledButton.icon(
                  onPressed: conflictsState.isBusy ? null : () => conflictsState.scan(),
                  icon: const Icon(Icons.search),
                  label: const Text('Scan'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (conflictsState.error != null)
              MaterialBanner(
                backgroundColor: Colors.red.shade50,
                content: Text(
                  conflictsState.error!,
                  style: const TextStyle(color: Colors.red),
                ),
                actions: [
                  TextButton(
                    onPressed: () {
                      conflictsState.clearError();
                      conflictsState.scan();
                    },
                    child: const Text('Retry'),
                  ),
                ],
              ),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Left list
                Expanded(
                  flex: 2,
                  child: Column(
                    children: [
                      for (int i = 0; i < conflictsState.items.length; i++)
                        ListTile(
                          title: Text('${conflictsState.items[i]["label"]}'),
                          subtitle: Text('${conflictsState.items[i]["occurrences"]} parents • union=${(conflictsState.items[i]["union_children"] as List).length}'),
                          onTap: () => conflictsState.selectConflict(i),
                          selected: conflictsState.selectedConflict == conflictsState.items[i],
                        ),
                      if (conflictsState.items.isEmpty)
                        const Padding(
                          padding: EdgeInsets.all(16),
                          child: Text('No conflicts found'),
                        ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                // Right detail
                Expanded(
                  flex: 3,
                  child: _ConflictDetail(),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _ConflictDetail extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final conflictsState = ref.watch(conflictsProvider);
    final conflict = conflictsState.selectedConflict;
    
    if (conflict == null) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('Select a conflict to review…'),
        ),
      );
    }
    
    final union = conflictsState.unionOptions.isNotEmpty
        ? List<String>.from(conflictsState.unionOptions)
        : List<String>.from(conflict['union_children'] as List);
    final parents = List<Map<String, dynamic>>.from(conflict['parents'] as List);
    final skippedParents = conflict['skipped_parents'] is List
        ? List<Map<String, dynamic>>.from(conflict['skipped_parents'] as List)
        : <Map<String, dynamic>>[];
    final hasEligibleParents = parents.isNotEmpty;
    final canSubmit = hasEligibleParents &&
        conflictsState.unionSelected.isNotEmpty &&
        conflictsState.unionSelected.length <= 5;
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Resolve: ${conflict["label"]}',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final label in union)
                  FilterChip(
                    label: Text(label),
                    selected: conflictsState.unionSelected.contains(label),
                    onSelected: (_) => conflictsState.toggleUnionChild(label),
                  ),
              ],
            ),
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text(
                'Selected (${conflictsState.unionSelected.length}/5)',
                style: TextStyle(
                  color: conflictsState.unionSelected.length > 5 ? Colors.red : null,
                ),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Occurrences (${parents.length})',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            SizedBox(
              height: 140,
              child: ListView.builder(
                itemCount: parents.length,
                itemBuilder: (_, i) => ListTile(
                  dense: true,
                  title: Text('D${parents[i]["depth"]} • Parent #${parents[i]["parent_id"]}'),
                  subtitle: Text((parents[i]["children"] as List).join(', ')),
                ),
              ),
            ),
            if (skippedParents.isNotEmpty) ...[
              const SizedBox(height: 12),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Skipped due to max depth (${skippedParents.length})',
                      style: TextStyle(
                        color: Colors.orange.shade800,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    for (final skip in skippedParents)
                      ListTile(
                        dense: true,
                        contentPadding: EdgeInsets.zero,
                        leading: Icon(
                          Icons.block,
                          size: 20,
                          color: Colors.orange.shade700,
                        ),
                        title: Text('D${skip["depth"]} • Parent #${skip["parent_id"]}'),
                        subtitle: Text(
                          (skip['children'] is List && (skip['children'] as List).isNotEmpty)
                              ? (skip['children'] as List).join(', ')
                              : 'Existing children unchanged',
                        ),
                      ),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 12),
            Row(
              children: [
                OutlinedButton.icon(
                  icon: const Icon(Icons.visibility),
                  label: const Text('Dry run'),
                  onPressed: canSubmit
                      ? () async {
                          final result = await conflictsState.dryRun();
                          if (result == null) return;

                          if (context.mounted) {
                            showDialog(
                              context: context,
                              builder: (_) => AlertDialog(
                                title: const Text('Dry run'),
                                content: SingleChildScrollView(
                                  child: Text(result.toString()),
                                ),
                                actions: [
                                  TextButton(
                                    onPressed: () => Navigator.pop(context),
                                    child: const Text('Close'),
                                  ),
                                ],
                              ),
                            );
                          }
                        }
                      : null,
                ),
                const SizedBox(width: 8),
                OutlinedButton.icon(
                  icon: const Icon(Icons.add),
                  label: const Text('Add child'),
                  onPressed: conflictsState.isBusy || !hasEligibleParents
                      ? null
                      : () async {
                          final controller = TextEditingController();
                          final newLabel = await showDialog<String>(
                            context: context,
                            builder: (dialogContext) => AlertDialog(
                              title: const Text('Add child'),
                              content: TextField(
                                controller: controller,
                                autofocus: true,
                                decoration: const InputDecoration(
                                  labelText: 'Child label',
                                  hintText: 'Enter child name',
                                ),
                              ),
                              actions: [
                                TextButton(
                                  onPressed: () => Navigator.of(dialogContext).pop(),
                                  child: const Text('Cancel'),
                                ),
                                TextButton(
                                  onPressed: () => Navigator.of(dialogContext).pop(controller.text),
                                  child: const Text('Add'),
                                ),
                              ],
                            ),
                          );
                          controller.dispose();

                          if (newLabel == null) {
                            return;
                          }

                          final added = conflictsState.addUnionChild(newLabel);
                          if (!added && context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Child already exists or label is empty'),
                              ),
                            );
                          }
                        },
                ),
                const SizedBox(width: 8),
                FilledButton.icon(
                  icon: const Icon(Icons.check),
                  label: const Text('Apply'),
                  onPressed: canSubmit
                      ? () async {
                          final result = await conflictsState.apply();
                          if (result == null) return;

                          if (context.mounted) {
                            final updatedCount = (result['updated_parents'] as int?) ?? 0;
                            final skippedCount = (result['skipped_parents'] is List)
                                ? (result['skipped_parents'] as List).length
                                : 0;
                            final message = skippedCount > 0
                                ? 'Updated $updatedCount parents; skipped $skippedCount at max depth'
                                : 'Resolved and updated $updatedCount parents';
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text(message)),
                            );
                          }
                        }
                      : null,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _ExportCard extends StatefulWidget {
  @override
  State<_ExportCard> createState() => _ExportCardState();
}

class _ExportCardState extends State<_ExportCard> {
  String _fmt = 'csv';
  int _maxDepth = 0; // 0 = unlimited
  bool _onlyRed = false;
  bool _includeMeta = false;
  DateTime? _lastExport;
  List<Map<String, dynamic>> _roots = [];
  final Set<int> _selectedRootIds = {};
  bool _loadingRoots = false;

  @override
  void initState() {
    super.initState();
    _loadRoots();
  }

  Future<void> _loadRoots() async {
    setState(() => _loadingRoots = true);
    try {
      final response = await http.get(Uri.parse('${ApiConfig.base}/tree/roots'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _roots = List<Map<String, dynamic>>.from(data['items'] ?? []);
        });
      }
    } catch (e) {
      // Silently fail - roots are optional
    } finally {
      setState(() => _loadingRoots = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Export',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            // Format selection
            Row(
              children: [
                const Text('Format:'),
                const SizedBox(width: 12),
                Radio<String>(
                  value: 'csv',
                  groupValue: _fmt,
                  onChanged: (v) => setState(() => _fmt = v!),
                ),
                const Text('CSV'),
                const SizedBox(width: 12),
                Radio<String>(
                  value: 'xlsx',
                  groupValue: _fmt,
                  onChanged: (v) => setState(() => _fmt = v!),
                ),
                const Text('XLSX'),
              ],
            ),
            const SizedBox(height: 12),
            // Filters
            Wrap(
              spacing: 16,
              runSpacing: 8,
              children: [
                // Max depth
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text('Max depth:'),
                    const SizedBox(width: 8),
                    SizedBox(
                      width: 80,
                      child: TextField(
                        keyboardType: TextInputType.number,
                        decoration: const InputDecoration(
                          hintText: '0=all',
                          border: OutlineInputBorder(),
                          contentPadding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        ),
                        onChanged: (v) {
                          _maxDepth = int.tryParse(v) ?? 0;
                        },
                      ),
                    ),
                  ],
                ),
                // Only red
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Checkbox(
                      value: _onlyRed,
                      onChanged: (v) => setState(() => _onlyRed = v ?? false),
                    ),
                    const Text('Only red'),
                  ],
                ),
                // Include meta
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Checkbox(
                      value: _includeMeta,
                      onChanged: (v) => setState(() => _includeMeta = v ?? false),
                    ),
                    const Text('Include meta'),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 12),
            // Root selection
            if (_roots.isNotEmpty) ...[
              const Text('Roots (optional):'),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: _roots.map((root) {
                  final id = root['id'] as int;
                  final label = root['label'] as String;
                  final selected = _selectedRootIds.contains(id);
                  return FilterChip(
                    label: Text(label),
                    selected: selected,
                    onSelected: (v) {
                      setState(() {
                        if (v) {
                          _selectedRootIds.add(id);
                        } else {
                          _selectedRootIds.remove(id);
                        }
                      });
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: 12),
            ],
            // Action buttons
            Row(
              children: [
                FilledButton.icon(
                  icon: const Icon(Icons.download),
                  label: const Text('Export'),
                  onPressed: _loadingRoots ? null : () async {
                    final url = _buildUrl(filenameHint: 'lorien_export.$_fmt');
                    final uri = Uri.parse(url);
                    try {
                      final savedPath = await _saveExportWithDialog(uri);
                      if (!mounted) return;
                      if (savedPath != null) {
                        setState(() => _lastExport = DateTime.now());
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Export saved to $savedPath')),
                        );
                      }
                    } catch (e) {
                      if (!mounted) return;
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Export error: $e')),
                      );
                    }
                  },
                ),
                const SizedBox(width: 8),
                OutlinedButton.icon(
                  icon: const Icon(Icons.copy),
                  label: const Text('Copy URL'),
                  onPressed: () {
                    final url = _buildUrl(filenameHint: 'lorien_export.$_fmt');
                    Clipboard.setData(ClipboardData(text: url));
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('URL copied to clipboard')),
                    );
                  },
                ),
              ],
            ),
            if (_lastExport != null) ...[
              const SizedBox(height: 8),
              Text(
                'Last export: ${_lastExport!.toString().substring(0, 19)}',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _buildUrl({required String filenameHint}) {
    final params = <String, String>{
      'format': _fmt,
      'filename': filenameHint,
    };
    if (_maxDepth > 0) params['max_depth'] = _maxDepth.toString();
    if (_onlyRed) params['only_red'] = 'true';
    if (_includeMeta) params['include_meta'] = 'true';
    if (_selectedRootIds.isNotEmpty) {
      params['root_ids'] = _selectedRootIds.join(',');
    }
    final qp = params.entries.map((e) => '${Uri.encodeQueryComponent(e.key)}=${Uri.encodeQueryComponent(e.value)}').join('&');
    return '${ApiConfig.base}/tree/export?$qp';
  }

  /// HEAD -> infer filename/extension -> Save As -> streamed GET -> write bytes
  Future<String?> _saveExportWithDialog(Uri uri) async {
    // 1) HEAD to get headers (filename, content-type)
    String contentType = '';
    String? serverFilename;
    try {
      final head = await http.head(uri);
      if (head.statusCode == 200) {
        contentType = (head.headers['content-type'] ?? '').toLowerCase();
        serverFilename = _filenameFromDisposition(head.headers['content-disposition']);
      }
    } catch (_) {
      // ignore; we'll proceed without HEAD
    }

    // 2) Decide extension & suggested name
    final isXlsx = contentType.startsWith('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') || uri.queryParameters['format'] == 'xlsx';
    final ext = isXlsx ? 'xlsx' : 'csv';
    String suggested = serverFilename ?? 'lorien_export.$ext';
    if (!suggested.toLowerCase().endsWith('.$ext')) {
      suggested = '$suggested.$ext';
    }

    // 3) Ask user where to save
    final savePath = await FilePicker.platform.saveFile(
      dialogTitle: 'Save Export File',
      fileName: suggested,
      type: FileType.custom,
      allowedExtensions: [ext],
    );
    if (savePath == null) {
      return null; // user cancelled
    }
    var finalPath = savePath;
    if (!finalPath.toLowerCase().endsWith('.$ext')) {
      finalPath = '$finalPath.$ext';
    }

    // 4) Streamed GET and write to disk as bytes
    final req = http.Request('GET', uri);
    final resp = await req.send();
    if (resp.statusCode != 200) {
      final body = await resp.stream.bytesToString();
      throw Exception('Export failed: ${resp.statusCode} $body');
    }
    // Create file + ensure directory
    final outFile = File(finalPath);
    await outFile.parent.create(recursive: true);
    final sink = outFile.openWrite();

    // Optionally peek first 4 bytes for XLSX magic "PK" (do not consume twice)
    // We'll buffer first chunk ourselves
    List<int>? firstChunk;
    await for (final chunk in resp.stream) {
      firstChunk ??= chunk;
      sink.add(chunk);
    }
    await sink.flush();
    await sink.close();

    // 5) Self-check for XLSX magic if we think it's xlsx
    try {
      if (isXlsx) {
        final raf = await outFile.open(mode: FileMode.read);
        final bytes = await raf.read(4);
        await raf.close();
        final magic = String.fromCharCodes(bytes.take(2));
        if (magic != 'PK') {
          // Not a blocker, but helpful warning in console
          // ignore: avoid_print
          print('Warning: XLSX file does not start with PK; saved anyway at $finalPath');
        }
      }
    } catch (_) {
      // ignore self-check failures
    }
    return finalPath;
  }

  String? _filenameFromDisposition(String? dispo) {
    if (dispo == null || dispo.isEmpty) return null;
    final m = RegExp(r'filename\*?=("{0,1})([^";]+)\1', caseSensitive: false).firstMatch(dispo);
    if (m != null && m.groupCount >= 2) {
      return m.group(2);
    }
    return null;
  }
}

class _NewSubmissionCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            Text(
              'New Submission',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 12),
            Text(
              'Coming soon. This pane will handle new dataset submissions and bulk change proposals.',
            ),
          ],
        ),
      ),
    );
  }
}
