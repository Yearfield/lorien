import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:dio/dio.dart';
import '../../providers/settings_provider.dart';
import '../../data/triage_repository.dart';
import '../../models/triage_models.dart';
import '../../services/telemetry_client.dart';
import 'outcomes_detail_screen.dart';

class OutcomesListScreen extends StatefulWidget {
  final bool llmEnabled;

  const OutcomesListScreen({super.key, required this.llmEnabled});

  @override
  State<OutcomesListScreen> createState() => _OutcomesListScreenState();
}

class _OutcomesListScreenState extends State<OutcomesListScreen> {
  late final Dio _dio;
  late TriageRepository _repo;
  late TelemetryClient _telemetry;

  final TextEditingController _searchController = TextEditingController();
  String _selectedVm = '';
  final List<TriageLeaf> _leaves = [];
  bool _loading = false;
  String? _error;
  int _totalCount = 0;
  final int _pageSize = 20;
  int _currentPage = 0;
  bool _hasMore = true;
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final base = context.read<SettingsProvider>().baseUrl;
    const analytics = String.fromEnvironment('ANALYTICS_ENABLED',
            defaultValue: 'false') ==
        'true';
    _dio = Dio();
    _repo = TriageRepository(dio: _dio, baseUrl: base);
    _telemetry = TelemetryClient(dio: _dio, baseUrl: base, enabled: analytics);
    _telemetry.event('outcomes_open');
    _search();
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
            _scrollController.position.maxScrollExtent - 200 &&
        _hasMore &&
        !_loading) {
      _currentPage++;
      _search();
    }
  }

  Future<void> _search() async {
    if (_loading) return;
    setState(() => _loading = true);
    try {
      final (list, total) = await _repo.searchLeaves(query: _buildQuery());
      _leaves.addAll(list);
      _totalCount = total;
      _hasMore = _leaves.length < _totalCount;
    } catch (e) {
      _error = e.toString();
    } finally {
      setState(() => _loading = false);
    }
  }

  String _buildQuery() {
    final q = _searchController.text.trim();
    // Simple search string; server matches substrings across fields
    return [
      if (_selectedVm.isNotEmpty) 'vm:"$_selectedVm"',
      if (q.isNotEmpty) q,
    ].join(' ').trim();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Outcomes')),
      body: Column(
        children: [
          _SearchBar(
              vmFilter: _selectedVm,
              onVmChanged: (v) {
                setState(() => _selectedVm = v);
                _search();
              },
              controller: _searchController,
              onSubmit: () => _search()),
          Padding(
              padding: const EdgeInsets.all(8),
              child: Align(
                  alignment: Alignment.centerLeft,
                  child: Text('$_totalCount results',
                      style: Theme.of(context).textTheme.labelMedium))),
          Expanded(
            child: _leaves.isEmpty && !_loading
                ? const Center(
                    child: Text(
                        'No leaves found — import a workbook or complete parents first.'))
                : NotificationListener<ScrollNotification>(
                    onNotification: (n) {
                      if (n.metrics.pixels >= n.metrics.maxScrollExtent - 200 &&
                          !_loading &&
                          _leaves.length < _totalCount) {
                        _currentPage++;
                        _search();
                      }
                      return false;
                    },
                    child: ListView.builder(
                      controller: _scrollController,
                      itemCount: _leaves.length + (_loading ? 1 : 0),
                      itemBuilder: (c, i) {
                        if (i >= _leaves.length) {
                          return const Padding(
                              padding: EdgeInsets.all(16),
                              child:
                                  Center(child: CircularProgressIndicator()));
                        }
                        final it = _leaves[i];
                        return ListTile(
                          title: Text(it.vitalMeasurement),
                          subtitle: Text(
                              '${it.path}\nTriage: ${it.diagnosticTriage}\nActions: ${it.actions}',
                              maxLines: 3,
                              overflow: TextOverflow.ellipsis),
                          isThreeLine: true,
                          onTap: () {
                            _telemetry.event('outcomes_open_detail');
                            Navigator.of(context).push(MaterialPageRoute(
                                builder: (_) => OutcomesDetailScreen(
                                    nodeId: it.nodeId,
                                    llmEnabled: widget.llmEnabled)));
                          },
                        );
                      },
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}

class _SearchBar extends StatelessWidget {
  final String vmFilter;
  final void Function(String) onVmChanged;
  final TextEditingController controller;
  final VoidCallback onSubmit;
  const _SearchBar(
      {required this.vmFilter,
      required this.onVmChanged,
      required this.controller,
      required this.onSubmit});
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(8),
      child: Row(children: [
        Expanded(
            child: TextField(
                controller: controller,
                decoration: const InputDecoration(
                    prefixIcon: Icon(Icons.search),
                    hintText: 'Search (label/triage/actions)…'),
                onSubmitted: (_) => onSubmit())),
        const SizedBox(width: 8),
        SizedBox(
            width: 200,
            child: TextField(
                decoration:
                    const InputDecoration(label: Text('Vital Measurement')),
                onSubmitted: (_) => onSubmit(),
                onChanged: onVmChanged)),
      ]),
    );
  }
}
