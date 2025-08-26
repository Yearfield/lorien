import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../screens/splash_screen.dart';
import '../screens/home_screen.dart';
import '../screens/editor/editor_screen.dart';
import '../screens/editor/parent_detail_screen.dart';
import '../screens/flags/flags_screen.dart';
import '../screens/calc/calculator_screen.dart';
import '../screens/settings/settings_screen.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/splash',
    routes: [
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/',
        builder: (context, state) => const HomeScreen(),
      ),
      GoRoute(
        path: '/editor',
        builder: (context, state) => const EditorScreen(),
      ),
      GoRoute(
        path: '/editor/:parentId',
        builder: (context, state) {
          final parentId = int.parse(state.pathParameters['parentId']!);
          return ParentDetailScreen(parentId: parentId);
        },
      ),
      GoRoute(
        path: '/flags',
        builder: (context, state) => const FlagsScreen(),
      ),
      GoRoute(
        path: '/calculator',
        builder: (context, state) => const CalculatorScreen(),
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) => const SettingsScreen(),
      ),
    ],
  );
});
