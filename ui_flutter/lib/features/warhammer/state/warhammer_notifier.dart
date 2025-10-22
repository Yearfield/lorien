import 'dart:io';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

import '../data/warhammer_models.dart';
import '../data/warhammer_repository.dart';
import 'warhammer_state.dart';

class WarhammerNotifier extends StateNotifier<WarhammerState> {
  final WarhammerRepository _repository;

  WarhammerNotifier({WarhammerRepository? repository})
      : _repository = repository ?? WarhammerRepository(),
        super(const WarhammerState()) {
    _loadInitialData();
  }

  /// Load initial data (symptoms, diseases, stats, decision tree symptoms)
  Future<void> _loadInitialData() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final futures = await Future.wait([
        _repository.getSymptoms(),
        _repository.getDiseases(),
        _repository.getStats(),
        fetchDecisionTreeRoots(),
      ]);

      final symptoms = futures[0] as List<Symptom>;
      final diseases = futures[1] as List<Disease>;
      final stats = futures[2] as WarhammerStats;
      final decisionTreeRoots = futures[3] as List<Map<String, dynamic>>;

      state = state.copyWith(
        symptoms: symptoms,
        diseases: diseases,
        stats: stats,
        decisionTreeRoots: decisionTreeRoots,
        currentTreeOptions: decisionTreeRoots, // Start with roots
        currentParentId: 0,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: _getErrorMessage(e),
      );
    }
  }

  /// Refresh all data
  Future<void> refresh() async {
    await _loadInitialData();
  }

  /// Add symptom to selection
  void addSymptom(String symptom) {
    if (state.selectedSymptoms.length >= 5) return;
    if (state.selectedSymptoms.contains(symptom)) return;

    final newSymptoms = [...state.selectedSymptoms, symptom];
    state = state.copyWith(
      selectedSymptoms: newSymptoms,
    );

    // Automatically calculate when 5 symptoms are selected
    if (newSymptoms.length == 5) {
      calculate();
    }
  }

  /// Remove symptom from selection
  void removeSymptom(String symptom) {
    state = state.copyWith(
      selectedSymptoms: state.selectedSymptoms.where((s) => s != symptom).toList(),
    );
  }

  /// Clear all selected symptoms
  void clearSelectedSymptoms() {
    state = state.copyWith(selectedSymptoms: []);
  }

  /// Calculate disease probabilities
  Future<void> calculate() async {
    if (state.selectedSymptoms.isEmpty || state.selectedSymptoms.length > 5) {
      state = state.copyWith(error: 'Please select 1-5 symptoms');
      return;
    }
    state = state.copyWith(isCalculating: true, error: null);
    try {
      final response = await _repository.calculateDiseaseProbabilities(state.selectedSymptoms);
      state = state.copyWith(
        isCalculating: false,
        lastCalculation: response,
      );
    } catch (e) {
      state = state.copyWith(isCalculating: false, error: 'Failed to calculate disease probabilities: $e');
    }
  }

  /// Save the last calculation
  Future<void> saveLastCalculation() async {
    if (state.lastCalculation?.calculationId == null) return;

    try {
      await _repository.saveCalculation(state.lastCalculation!.calculationId!);
      await _loadSavedCalculations();
    } catch (e) {
      state = state.copyWith(error: _getErrorMessage(e));
    }
  }

  /// Load saved calculations
  Future<void> _loadSavedCalculations() async {
    try {
      final calculations = await _repository.getSavedCalculations();
      state = state.copyWith(savedCalculations: calculations);
    } catch (e) {
      // Don't update error state for this, just log it
      print('Failed to load saved calculations: $e');
    }
  }

  /// Import diseases from file
  Future<void> importDiseases(File file) async {
    state = state.copyWith(isImporting: true, error: null);

    try {
      final result = await _repository.importDiseases(file);

      if (result.success) {
        // Refresh data after successful import
        await refresh();
      }

      state = state.copyWith(isImporting: false);
    } catch (e) {
      state = state.copyWith(
        isImporting: false,
        error: _getErrorMessage(e),
      );
    }
  }

  /// Import symptoms from file
  Future<void> importSymptoms(File file) async {
    state = state.copyWith(isImporting: true, error: null);

    try {
      final result = await _repository.importSymptoms(file);

      if (result.success) {
        // Refresh data after successful import
        await refresh();
      }

      state = state.copyWith(isImporting: false);
    } catch (e) {
      state = state.copyWith(
        isImporting: false,
        error: _getErrorMessage(e),
      );
    }
  }

  /// Import conditionals from file
  Future<void> importConditionals(File file) async {
    state = state.copyWith(isImporting: true, error: null);

    try {
      final result = await _repository.importConditionals(file);

      if (result.success) {
        // Refresh data after successful import
        await refresh();
      }

      state = state.copyWith(isImporting: false);
    } catch (e) {
      state = state.copyWith(
        isImporting: false,
        error: _getErrorMessage(e),
      );
    }
  }

  /// Clear error state
  void clearError() {
    state = state.copyWith(error: null);
  }

  /// Get user-friendly error message
  String _getErrorMessage(dynamic error) {
    if (error is Exception) {
      return error.toString();
    } else {
      return 'An unexpected error occurred';
    }
  }

  /// Fetch decision tree roots for initial symptom selection
  Future<List<Map<String, dynamic>>> fetchDecisionTreeRoots() async {
    try {
      final rootsResponse = await http.get(
        Uri.parse('http://localhost:8000/api/v1/tree/roots'),
      );

      if (rootsResponse.statusCode != 200) {
        throw Exception('Failed to fetch roots: ${rootsResponse.statusCode}');
      }

      final rootsData = jsonDecode(rootsResponse.body);
      final roots = rootsData['items'] as List;

      return roots.cast<Map<String, dynamic>>();
    } catch (e) {
      throw Exception('Failed to fetch decision tree roots: $e');
    }
  }

  /// Refresh decision tree data from VM Builder
  Future<void> refreshDecisionTreeData() async {
    try {
      state = state.copyWith(isLoading: true, error: null);

      // Fetch fresh decision tree roots
      final newRoots = await fetchDecisionTreeRoots();

      // Update state with new roots and reset navigation
      state = state.copyWith(
        decisionTreeRoots: newRoots,
        currentTreeOptions: newRoots,
        currentParentId: 0,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: 'Failed to refresh decision tree data: $e');
    }
  }

  /// Fetch children of a specific parent in the decision tree
  Future<List<Map<String, dynamic>>> fetchDecisionTreeChildren(int parentId) async {
    try {
      final childrenResponse = await http.get(
        Uri.parse('http://localhost:8000/api/v1/tree/children?parent_id=$parentId'),
      );

      if (childrenResponse.statusCode != 200) {
        throw Exception('Failed to fetch children: ${childrenResponse.statusCode}');
      }

      final childrenData = jsonDecode(childrenResponse.body);
      final children = childrenData['items'] as List;

      return children.cast<Map<String, dynamic>>();
    } catch (e) {
      throw Exception('Failed to fetch decision tree children: $e');
    }
  }

  /// Navigate to a specific node in the decision tree
  Future<void> navigateToTreeNode(int nodeId) async {
    try {
      final children = await fetchDecisionTreeChildren(nodeId);
      state = state.copyWith(
        currentTreeOptions: children,
        currentParentId: nodeId,
      );
    } catch (e) {
      state = state.copyWith(error: 'Failed to navigate tree: $e');
    }
  }

  /// Reset tree navigation to roots
  void resetTreeNavigation() {
    state = state.copyWith(
      currentTreeOptions: state.decisionTreeRoots,
      currentParentId: 0,
    );
  }

  /// Load symptom comparison between decision tree and Warhammer database
  Future<void> loadSymptomComparison() async {
    state = state.copyWith(isLoadingComparison: true, error: null);

    try {
      final comparison = await _repository.getSymptomComparison();
      state = state.copyWith(
        symptomComparison: comparison,
        isLoadingComparison: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoadingComparison: false,
        error: _getErrorMessage(e),
      );
    }
  }

  /// Load all symptom synonym mappings
  Future<void> loadSynonyms() async {
    state = state.copyWith(isLoadingSynonyms: true, error: null);

    try {
      final synonyms = await _repository.getSynonyms();
      state = state.copyWith(
        synonyms: synonyms,
        isLoadingSynonyms: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoadingSynonyms: false,
        error: _getErrorMessage(e),
      );
    }
  }

  /// Create a new symptom synonym mapping
  Future<void> createSynonym(String warhammerSymptom, String decisionTreeSymptom) async {
    try {
      final request = CreateSynonymRequest(
        warhammerSymptom: warhammerSymptom,
        decisionTreeSymptom: decisionTreeSymptom,
      );

      final newSynonym = await _repository.createSynonym(request);

      // Add to current synonyms list
      final updatedSynonyms = [...state.synonyms, newSynonym];
      state = state.copyWith(synonyms: updatedSynonyms);

      // Reload comparison to reflect the new synonym
      await loadSymptomComparison();
    } catch (e) {
      state = state.copyWith(error: _getErrorMessage(e));
    }
  }

  /// Delete a symptom synonym mapping
  Future<void> deleteSynonym(int synonymId) async {
    try {
      await _repository.deleteSynonym(synonymId);

      // Remove from current synonyms list
      final updatedSynonyms = state.synonyms.where((s) => s.id != synonymId).toList();
      state = state.copyWith(synonyms: updatedSynonyms);

      // Reload comparison to reflect the removed synonym
      await loadSymptomComparison();
    } catch (e) {
      state = state.copyWith(error: _getErrorMessage(e));
    }
  }
}

// Provider for WarhammerNotifier
final warhammerNotifierProvider = StateNotifierProvider<WarhammerNotifier, WarhammerState>((ref) {
  return WarhammerNotifier();
});

// Provider for symptoms list
final symptomsProvider = Provider<List<Symptom>>((ref) {
  final state = ref.watch(warhammerNotifierProvider);
  return state.symptoms;
});

// Provider for diseases list
final diseasesProvider = Provider<List<Disease>>((ref) {
  final state = ref.watch(warhammerNotifierProvider);
  return state.diseases;
});

// Provider for selected symptoms
final selectedSymptomsProvider = Provider<List<String>>((ref) {
  final state = ref.watch(warhammerNotifierProvider);
  return state.selectedSymptoms;
});

// Provider for last calculation result
final lastCalculationProvider = Provider<CalculationResponse?>((ref) {
  final state = ref.watch(warhammerNotifierProvider);
  return state.lastCalculation;
});

// Provider for Warhammer stats
final warhammerStatsProvider = Provider<WarhammerStats?>((ref) {
  final state = ref.watch(warhammerNotifierProvider);
  return state.stats;
});

// Provider for loading state
final warhammerLoadingProvider = Provider<bool>((ref) {
  final state = ref.watch(warhammerNotifierProvider);
  return state.isLoading;
});

// Provider for calculating state
final warhammerCalculatingProvider = Provider<bool>((ref) {
  final state = ref.watch(warhammerNotifierProvider);
  return state.isCalculating;
});

// Provider for importing state
final warhammerImportingProvider = Provider<bool>((ref) {
  final state = ref.watch(warhammerNotifierProvider);
  return state.isImporting;
});

// Provider for error state
final warhammerErrorProvider = Provider<String?>((ref) {
  final state = ref.watch(warhammerNotifierProvider);
  return state.error;
});

// Provider for current tree options (roots or children)
final currentTreeOptionsProvider = Provider<List<Map<String, dynamic>>>((ref) {
  final state = ref.watch(warhammerNotifierProvider);
  return state.currentTreeOptions;
});

// Provider for decision tree roots
final decisionTreeRootsProvider = Provider<List<Map<String, dynamic>>>((ref) {
  final state = ref.watch(warhammerNotifierProvider);
  return state.decisionTreeRoots;
});

// Provider for symptom comparison
final symptomComparisonProvider = Provider<SymptomComparison?>((ref) {
  final state = ref.watch(warhammerNotifierProvider);
  return state.symptomComparison;
});

// Provider for symptom comparison loading state
final symptomComparisonLoadingProvider = Provider<bool>((ref) {
  final state = ref.watch(warhammerNotifierProvider);
  return state.isLoadingComparison;
});

// Provider for synonyms
final synonymsProvider = Provider<List<SymptomSynonym>>((ref) {
  final state = ref.watch(warhammerNotifierProvider);
  return state.synonyms;
});

// Provider for synonyms loading state
final synonymsLoadingProvider = Provider<bool>((ref) {
  final state = ref.watch(warhammerNotifierProvider);
  return state.isLoadingSynonyms;
});
