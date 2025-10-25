import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/api_config.dart';
import '../data/shortbow_models.dart';
import '../data/shortbow_repository.dart';
import 'shortbow_state.dart';

class ShortBowNotifier extends StateNotifier<ShortBowState> {
  final ShortBowRepository _repository;

  ShortBowNotifier({ShortBowRepository? repository})
      : _repository = repository ?? ShortBowRepository(baseUrl: ApiConfig.base),
        super(const ShortBowState()) {
    _loadInitialData();
  }

  /// Load initial data (symptoms, stats, top symptoms)
  Future<void> _loadInitialData() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final futures = await Future.wait([
        _repository.getSymptoms(),
        _repository.getStats(),
        _repository.getTopSymptoms(),
      ]);

      final symptoms = futures[0] as List<ShortBowSymptom>;
      final stats = futures[1] as ShortBowStats;
      final topSymptoms = futures[2] as List<ShortBowSymptomLink>;

      state = state.copyWith(
        symptoms: symptoms,
        stats: stats,
        topSymptoms: topSymptoms,
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

  /// Navigate to get linked symptoms for current symptom
  Future<void> navigateToSymptom(String symptom) async {
    if (state.selectedSymptoms.contains(symptom)) return;

    // Add to navigation history
    final newHistory = [...state.navigationHistory, symptom];

    state = state.copyWith(
      isNavigating: true,
      error: null,
      currentSymptom: symptom,
      navigationHistory: newHistory,
    );

    try {
      final request = ShortBowNavigationRequest(
        currentSymptom: symptom,
        exclude: state.selectedSymptoms,
      );

      final response = await _repository.navigateSymptoms(request);

      state = state.copyWith(
        currentLinkedSymptoms: response.topLinked,
        isNavigating: false,
      );
    } catch (e) {
      state = state.copyWith(
        isNavigating: false,
        error: _getErrorMessage(e),
      );
    }
  }

  /// Select a symptom (add to selected list)
  void selectSymptom(String symptom) {
    if (state.selectedSymptoms.length >= 5) return;
    if (state.selectedSymptoms.contains(symptom)) return;

    final newSymptoms = [...state.selectedSymptoms, symptom];
    state = state.copyWith(selectedSymptoms: newSymptoms);

    // Navigate to get linked symptoms for the newly selected symptom
    navigateToSymptom(symptom);
  }

  /// Add a symptom to selection (alias for selectSymptom)
  void addSymptom(String symptom) {
    selectSymptom(symptom);
  }

  /// Remove symptom from selection
  void removeSymptom(String symptom) {
    state = state.copyWith(
      selectedSymptoms: state.selectedSymptoms.where((s) => s != symptom).toList(),
    );
  }

  /// Clear all selected symptoms
  void clearSelectedSymptoms() {
    state = state.copyWith(
      selectedSymptoms: [],
      currentLinkedSymptoms: [],
      currentSymptom: null,
      navigationHistory: [],
    );
  }

  /// Go back to previous symptom in navigation history
  void goBack() {
    if (state.navigationHistory.isEmpty) return;

    final newHistory = List<String>.from(state.navigationHistory);
    newHistory.removeLast();

    state = state.copyWith(
      navigationHistory: newHistory,
      currentSymptom: newHistory.isNotEmpty ? newHistory.last : null,
    );

    // If we have a current symptom, navigate to it to get linked symptoms
    if (state.currentSymptom != null) {
      navigateToSymptom(state.currentSymptom!);
    } else {
      // If no current symptom, clear linked symptoms and show top symptoms
      state = state.copyWith(
        currentLinkedSymptoms: [],
      );
    }
  }

  /// Save current calculation as decision tree branch
  Future<void> saveCalculation() async {
    if (state.selectedSymptoms.isEmpty) {
      state = state.copyWith(
        error: 'No symptoms selected. Please use the symptom navigator to select symptoms before saving.',
      );
      return;
    }

    if (state.selectedSymptoms.length < 2) {
      state = state.copyWith(
        error: 'Please select at least 2 symptoms to create a meaningful decision tree path.',
      );
      return;
    }

    state = state.copyWith(isCalculating: true, error: null);

    try {
      // Create hierarchical decision tree using the new endpoint
      final treeResponse = await _repository.createDecisionTree(state.selectedSymptoms);

      // Also save as ShortBow calculation for history
      final request = ShortBowCalculationRequest(
        initialSymptom: state.selectedSymptoms.first,
        selectedSymptoms: state.selectedSymptoms,
      );
      await _repository.createCalculation(request);

      // Refresh calculations list
      await _loadCalculations();

      state = state.copyWith(
        isCalculating: false,
        error: null,
      );

      // Show success message (could be displayed in UI)
      print('✅ Decision tree branch created successfully!');
      print('   Root ID: ${treeResponse['root_id']}');
      print('   Path: ${state.selectedSymptoms.join(' → ')}');
      print('   Symptoms created: ${treeResponse['symptoms_created']}');
    } catch (e) {
      state = state.copyWith(
        isCalculating: false,
        error: _getErrorMessage(e),
      );
    }
  }

  /// Load calculations history
  Future<void> _loadCalculations() async {
    try {
      final calculations = await _repository.getCalculations();
      state = state.copyWith(calculations: calculations);
    } catch (e) {
      // Don't update error state for calculations loading
      print('Failed to load calculations: $e');
    }
  }

  /// Load calculations on demand
  Future<void> loadCalculations() async {
    await _loadCalculations();
  }

  /// Save a specific calculation
  Future<void> saveCalculationById(int id) async {
    try {
      await _repository.saveCalculation(id);
      await _loadCalculations(); // Refresh the list
    } catch (e) {
      state = state.copyWith(error: _getErrorMessage(e));
    }
  }

  /// Start navigation with top symptoms
  void startWithTopSymptoms() {
    state = state.copyWith(
      currentLinkedSymptoms: state.topSymptoms,
      currentSymptom: null,
    );
  }

  /// Import symptom matrix from file
  Future<void> importMatrix(File file) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      await _repository.importMatrix(file);
      // Refresh data after successful import
      await _loadInitialData();
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: _getErrorMessage(e),
      );
    }
  }

  /// Get error message from exception
  String _getErrorMessage(dynamic error) {
    if (error.toString().contains('Failed to')) {
      return error.toString();
    }
    return 'An unexpected error occurred: $error';
  }
}

// Providers
final shortBowNotifierProvider = StateNotifierProvider<ShortBowNotifier, ShortBowState>(
  (ref) => ShortBowNotifier(),
);

final shortBowLoadingProvider = Provider<bool>((ref) {
  return ref.watch(shortBowNotifierProvider).isLoading;
});

final shortBowNavigatingProvider = Provider<bool>((ref) {
  return ref.watch(shortBowNotifierProvider).isNavigating;
});

final shortBowCalculatingProvider = Provider<bool>((ref) {
  return ref.watch(shortBowNotifierProvider).isCalculating;
});

final shortBowErrorProvider = Provider<String?>((ref) {
  return ref.watch(shortBowNotifierProvider).error;
});
