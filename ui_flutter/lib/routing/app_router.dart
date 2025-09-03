import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../features/workspace/ui/workspace_screen.dart';
import '../features/flags/ui/flags_screen.dart';
import '../screens/settings_screen.dart';
import '../screens/about/about_screen.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    routes: [
      GoRoute(
        path: '/',
        builder: (_, __) => const WorkspaceScreen(),
      ),
      GoRoute(
        path: '/flags',
        builder: (_, __) => const FlagsScreen(),
      ),
      GoRoute(
        path: '/settings',
        builder: (_, __) => const SettingsScreen(),
      ),
      GoRoute(
        path: '/about',
        builder: (_, __) => const AboutScreen(),
      ),
    ],
    // Optional: basic error page
    errorBuilder: (_, state) => Scaffold(
      appBar: AppBar(title: const Text('Not found')),
      body: Center(child: Text('Route not found: ${state.uri}')),
    ),
    debugLogDiagnostics: false,
  );
});
