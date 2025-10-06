import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/services/health_service.dart';
import '../data/dto/health_dto.dart';

final healthServiceProvider = Provider<HealthService>((ref) {
  return HealthService();
});

final healthStateProvider = StateNotifierProvider<HealthStateNotifier, HealthState>((ref) {
  final healthService = ref.watch(healthServiceProvider);
  return HealthStateNotifier(healthService);
});

class HealthState {
  final HealthResponse? healthResponse;
  final bool isLoading;
  final bool isRefreshing;
  final DateTime? lastChecked;
  final String? error;

  HealthState({
    this.healthResponse,
    this.isLoading = false,
    this.isRefreshing = false,
    this.lastChecked,
    this.error,
  });

  HealthState copyWith({
    HealthResponse? healthResponse,
    bool? isLoading,
    bool? isRefreshing,
    DateTime? lastChecked,
    String? error,
  }) {
    return HealthState(
      healthResponse: healthResponse ?? this.healthResponse,
      isLoading: isLoading ?? this.isLoading,
      isRefreshing: isRefreshing ?? this.isRefreshing,
      lastChecked: lastChecked ?? this.lastChecked,
      error: error ?? this.error,
    );
  }

  bool get isOnline => healthResponse?.ok ?? false;
  bool get hasError => error != null;
}

class HealthStateNotifier extends StateNotifier<HealthState> {
  final HealthService _healthService;

  HealthStateNotifier(this._healthService) : super(HealthState()) {
    loadHealthStatus();
  }

  Future<void> loadHealthStatus() async {
    state = state.copyWith(isLoading: true, error: null);
    
    try {
      final healthResponse = await _healthService.getHealthStatus();
      state = state.copyWith(
        healthResponse: healthResponse,
        isLoading: false,
        lastChecked: DateTime.now(),
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> refreshHealthStatus() async {
    state = state.copyWith(isRefreshing: true, error: null);
    
    try {
      final healthResponse = await _healthService.getHealthStatus();
      state = state.copyWith(
        healthResponse: healthResponse,
        isRefreshing: false,
        lastChecked: DateTime.now(),
        error: null,
      );
    } catch (e) {
      state = state.copyWith(
        isRefreshing: false,
        error: e.toString(),
      );
    }
  }

  Future<bool> testConnection() async {
    return await _healthService.testConnection();
  }
}
