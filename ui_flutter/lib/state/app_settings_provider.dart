import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/api_client.dart';
import '../utils/env.dart';

// API Client Provider
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

// API Base URL Provider
final apiBaseUrlProvider = StateNotifierProvider<ApiBaseUrlNotifier, String>((ref) {
  return ApiBaseUrlNotifier();
});

class ApiBaseUrlNotifier extends StateNotifier<String> {
  ApiBaseUrlNotifier() : super(Env.defaultBaseUrl) {
    _loadBaseUrl();
  }

  Future<void> _loadBaseUrl() async {
    final baseUrl = await Env.getApiBaseUrl();
    state = baseUrl;
  }

  Future<void> setBaseUrl(String baseUrl) async {
    await Env.setApiBaseUrl(baseUrl);
    state = baseUrl;
  }
}

// Theme Mode Provider
final themeModeProvider = StateNotifierProvider<ThemeModeNotifier, ThemeMode>((ref) {
  return ThemeModeNotifier();
});

class ThemeModeNotifier extends StateNotifier<ThemeMode> {
  ThemeModeNotifier() : super(ThemeMode.system) {
    _loadThemeMode();
  }

  Future<void> _loadThemeMode() async {
    final themeModeString = await Env.getThemeMode();
    switch (themeModeString) {
      case 'light':
        state = ThemeMode.light;
        break;
      case 'dark':
        state = ThemeMode.dark;
        break;
      default:
        state = ThemeMode.system;
    }
  }

  Future<void> setThemeMode(ThemeMode themeMode) async {
    String themeModeString;
    switch (themeMode) {
      case ThemeMode.light:
        themeModeString = 'light';
        break;
      case ThemeMode.dark:
        themeModeString = 'dark';
        break;
      default:
        themeModeString = 'system';
    }
    await Env.setThemeMode(themeModeString);
    state = themeMode;
  }
}

// Connection Status Provider
final connectionStatusProvider = StateNotifierProvider<ConnectionStatusNotifier, ConnectionStatus>((ref) {
  return ConnectionStatusNotifier(ref.read(apiClientProvider));
});

enum ConnectionStatus {
  unknown,
  connected,
  disconnected,
  error,
}

class ConnectionStatusNotifier extends StateNotifier<ConnectionStatus> {
  final ApiClient _apiClient;

  ConnectionStatusNotifier(this._apiClient) : super(ConnectionStatus.unknown);

  Future<void> testConnection(String baseUrl) async {
    state = ConnectionStatus.unknown;
    
    try {
      _apiClient.setBaseUrl(baseUrl);
      final response = await _apiClient.get('/health');
      
      if (response.statusCode == 200) {
        state = ConnectionStatus.connected;
      } else {
        state = ConnectionStatus.error;
      }
    } catch (e) {
      state = ConnectionStatus.disconnected;
    }
  }

  void reset() {
    state = ConnectionStatus.unknown;
  }
}
