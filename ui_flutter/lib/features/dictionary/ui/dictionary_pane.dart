import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../state/dictionary_provider.dart';
import '../data/dictionary_dto.dart';
import 'term_details_dialog.dart';
import 'dictionary_stats_dialog.dart';
import 'dictionary_upload_dialog.dart';

class DictionaryPane extends ConsumerStatefulWidget {
  const DictionaryPane({super.key});

  @override
  ConsumerState<DictionaryPane> createState() => _DictionaryPaneState();
}

class _DictionaryPaneState extends ConsumerState<DictionaryPane> {
  final TextEditingController _searchController = TextEditingController();
  final FocusNode _searchFocusNode = FocusNode();

  @override
  void initState() {
    super.initState();
    // Load stats when the pane is initialized
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(dictionaryStatsProvider.notifier).loadStats();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    _searchFocusNode.dispose();
    super.dispose();
  }

  void _onSearchChanged(String query) {
    // Debounce search - only search if user stops typing for 300ms
    Future.delayed(const Duration(milliseconds: 300), () {
      if (_searchController.text == query) {
        ref.read(dictionarySearchProvider.notifier).search(query);
      }
    });
  }

  void _showTermDetails(DictionaryTerm term) {
    showDialog(
      context: context,
      builder: (context) => TermDetailsDialog(termId: term.id),
    );
  }

  void _showStats() {
    showDialog(
      context: context,
      builder: (context) => const DictionaryStatsDialog(),
    );
  }

  Future<void> _exportCsv() async {
    final exportNotifier = ref.read(dictionaryExportProvider.notifier);
    final csvContent = await exportNotifier.exportCsv();

    if (csvContent != null) {
      // TODO: Implement file save dialog
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('CSV exported successfully'),
          duration: Duration(seconds: 2),
        ),
      );
    } else {
      final exportState = ref.read(dictionaryExportProvider);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Export failed: ${exportState.error ?? 'Unknown error'}'),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
    }
  }

  Future<void> _uploadFile() async {
    showDialog(
      context: context,
      builder: (context) => const DictionaryUploadDialog(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final searchState = ref.watch(dictionarySearchProvider);
    final exportState = ref.watch(dictionaryExportProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Medical Dictionary'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              ref.read(dictionarySearchProvider.notifier).refresh();
              ref.read(dictionaryStatsProvider.notifier).loadStats();
            },
            tooltip: 'Refresh Dictionary',
          ),
          IconButton(
            icon: const Icon(Icons.analytics_outlined),
            onPressed: _showStats,
            tooltip: 'Dictionary Statistics',
          ),
          IconButton(
            icon: const Icon(Icons.download),
            onPressed: exportState.isExporting ? null : _exportCsv,
            tooltip: 'Export CSV',
          ),
          IconButton(
            icon: const Icon(Icons.upload),
            onPressed: _uploadFile,
            tooltip: 'Upload Dictionary',
          ),
        ],
      ),
      body: Column(
        children: [
          // Search bar
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              controller: _searchController,
              focusNode: _searchFocusNode,
              decoration: InputDecoration(
                hintText: 'Search medical terms...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          ref.read(dictionarySearchProvider.notifier).clearSearch();
                        },
                      )
                    : null,
                border: const OutlineInputBorder(),
              ),
              onChanged: _onSearchChanged,
              textInputAction: TextInputAction.search,
            ),
          ),

          // Results
          Expanded(
            child: _buildResults(searchState),
          ),
        ],
      ),
    );
  }

  Widget _buildResults(DictionarySearchState searchState) {
    if (searchState.query.isEmpty) {
      return _buildWelcomeMessage();
    }

    if (searchState.isLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Searching...'),
          ],
        ),
      );
    }

    if (searchState.error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              'Search Error',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              searchState.error!,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                ref.read(dictionarySearchProvider.notifier).search(searchState.query);
              },
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (searchState.items.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.search_off,
              size: 64,
              color: Theme.of(context).colorScheme.outline,
            ),
            const SizedBox(height: 16),
            Text(
              'No Results Found',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              'No terms found for "${searchState.query}"',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
      );
    }

    return Column(
      children: [
        // Results header
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0),
          child: Row(
            children: [
              Text(
                'Found ${searchState.total} term${searchState.total == 1 ? '' : 's'}',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const Spacer(),
              if (searchState.total > searchState.items.length)
                Text(
                  'Showing ${searchState.items.length}',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
            ],
          ),
        ),
        const SizedBox(height: 8),

        // Results list
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            itemCount: searchState.items.length,
            itemBuilder: (context, index) {
              final term = searchState.items[index];
              return _buildTermCard(term);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildWelcomeMessage() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.medical_services,
            size: 80,
            color: Theme.of(context).colorScheme.primary,
          ),
          const SizedBox(height: 24),
          Text(
            'Medical Dictionary',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 16),
          Text(
            'Search for medical terms to view definitions,\nsynonyms, and tree relationships.',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyLarge,
          ),
          const SizedBox(height: 32),
          ElevatedButton.icon(
            onPressed: () {
              _searchFocusNode.requestFocus();
            },
            icon: const Icon(Icons.search),
            label: const Text('Start Searching'),
          ),
        ],
      ),
    );
  }

  Widget _buildTermCard(DictionaryTerm term) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        title: Text(
          term.term,
          style: const TextStyle(fontWeight: FontWeight.w500),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (term.definition != null && term.definition!.isNotEmpty)
              Text(term.definition!),
            const SizedBox(height: 4),
            Row(
              children: [
                if (term.isRedFlag)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.red.shade100,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      'Red Flag',
                      style: TextStyle(
                        color: Colors.red.shade700,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                if (term.isRedFlag) const SizedBox(width: 8),
                if (term.avgChildrenCount > 0)
                  Text(
                    '${term.avgChildrenCount} children',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                if (term.conflictsCount > 0) ...[
                  if (term.avgChildrenCount > 0) const SizedBox(width: 8),
                  Text(
                    '${term.conflictsCount} conflicts',
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                      fontSize: 12,
                    ),
                  ),
                ],
              ],
            ),
          ],
        ),
        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
        onTap: () => _showTermDetails(term),
      ),
    );
  }
}
