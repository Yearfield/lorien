import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:lorien/features/pathogens/providers/pathogen_providers.dart';
import 'package:lorien/features/pathogens/models/pathogen_models.dart';
import 'package:lorien/features/pathogens/ui/pathogen_import_dialog.dart';
import 'package:lorien/features/pathogens/ui/pathogen_detail_dialog.dart';
import 'package:lorien/features/pathogens/ui/pathogen_create_dialog.dart';
import 'package:lorien/features/pathogens/ui/pathogen_search_bar.dart';
import 'package:lorien/features/pathogens/ui/pathogen_stats_card.dart';
import 'package:lorien/features/pathogens/ui/pathogen_list.dart';
import 'package:lorien/features/pathogens/ui/association_filter_chips.dart';

class PathogenPane extends ConsumerStatefulWidget {
  const PathogenPane({super.key});

  @override
  ConsumerState<PathogenPane> createState() => _PathogenPaneState();
}

class _PathogenPaneState extends ConsumerState<PathogenPane> {
  String _searchQuery = '';
  String? _selectedAssociationFilter;
  bool _showOnlyWithAssociations = false;

  @override
  void initState() {
    super.initState();
    // Load initial data
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(pathogenListProvider.notifier).loadPathogens();
      ref.read(associationTypesProvider.notifier).loadAssociationTypes();
      ref.read(pathogenStatsProvider.notifier).loadStats();
    });
  }

  void _handleImport() {
    showDialog(
      context: context,
      builder: (context) => const PathogenImportDialog(),
    );
  }

  void _handleAddPathogen() {
    showDialog(
      context: context,
      builder: (context) => const PathogenCreateDialog(),
    );
  }

  void _handlePathogenTap(Pathogen pathogen) {
    showDialog(
      context: context,
      builder: (context) => PathogenDetailDialog(pathogen: pathogen),
    );
  }

  void _handleSearchChanged(String query) {
    _searchQuery = query;
    ref.read(pathogenListProvider.notifier).searchPathogens(query);
  }

  void _handleAssociationFilterChanged(String? filter) {
    _selectedAssociationFilter = filter;
    ref.read(pathogenListProvider.notifier).filterByAssociation(filter);
  }

  void _handleShowOnlyWithAssociationsChanged(bool value) {
    _showOnlyWithAssociations = value;
    ref.read(pathogenListProvider.notifier).filterByAssociations(value);
  }

  @override
  Widget build(BuildContext context) {
    final pathogenList = ref.watch(pathogenListProvider);
    final associationTypes = ref.watch(associationTypesProvider);
    final stats = ref.watch(pathogenStatsProvider);

    return Column(
      children: [
        // Header with import button
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              const Icon(Icons.bug_report, size: 24, color: Colors.red),
              const SizedBox(width: 8),
              const Text(
                'P Builder',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              ElevatedButton.icon(
                onPressed: _handleAddPathogen,
                icon: const Icon(Icons.add),
                label: const Text('+Pathogen'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                ),
              ),
              const SizedBox(width: 8),
              ElevatedButton.icon(
                onPressed: _handleImport,
                icon: const Icon(Icons.upload_file),
                label: const Text('Import Data'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ),
        ),

        // Stats card
        stats.when(
          data: (statsData) => statsData != null
              ? Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0),
                  child: PathogenStatsCard(stats: statsData),
                )
              : const SizedBox.shrink(),
          loading: () => const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16.0),
            child: Card(
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Center(child: CircularProgressIndicator()),
              ),
            ),
          ),
          error: (error, stack) => const SizedBox.shrink(),
        ),

        const SizedBox(height: 16),

        // Search and filters
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0),
          child: Column(
            children: [
              PathogenSearchBar(
                onSearchChanged: _handleSearchChanged,
                searchQuery: _searchQuery,
              ),
              const SizedBox(height: 12),
              associationTypes.when(
                data: (types) => AssociationFilterChips(
                  associationTypes: types,
                  selectedFilter: _selectedAssociationFilter,
                  onFilterChanged: _handleAssociationFilterChanged,
                  showOnlyWithAssociations: _showOnlyWithAssociations,
                  onShowOnlyWithAssociationsChanged: _handleShowOnlyWithAssociationsChanged,
                ),
                loading: () => const SizedBox.shrink(),
                error: (error, stack) => const SizedBox.shrink(),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // Pathogen list
        Expanded(
          child: pathogenList.when(
            data: (pathogens) => PathogenList(
              pathogens: pathogens,
              onPathogenTap: _handlePathogenTap,
              searchQuery: _searchQuery,
            ),
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (error, stack) => Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error, size: 48, color: Colors.red),
                  const SizedBox(height: 16),
                  Text('Error loading pathogens: $error'),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () => ref.refresh(pathogenListProvider),
                    child: const Text('Retry'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}
