import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../state/app_settings_provider.dart';

class SplashScreen extends ConsumerStatefulWidget {
  const SplashScreen({super.key});

  @override
  ConsumerState<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends ConsumerState<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _performHealthCheck();
  }

  Future<void> _performHealthCheck() async {
    // Wait a bit for the UI to show
    await Future.delayed(const Duration(milliseconds: 500));

    final baseUrl = ref.read(apiBaseUrlProvider.notifier).state;
    final connectionNotifier = ref.read(connectionStatusProvider.notifier);

    await connectionNotifier.testConnection(baseUrl);

    if (mounted) {
      final status = ref.read(connectionStatusProvider);

      if (status == ConnectionStatus.connected) {
        context.go('/');
      } else {
        context.go('/settings');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // App Logo/Icon
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                color: Theme.of(context).primaryColor,
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Icon(
                Icons.account_tree,
                size: 60,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 24),

            // App Title
            Text(
              'Decision Tree Manager',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 8),

            Text(
              'Cross-platform decision tree management',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey[600],
                  ),
            ),
            const SizedBox(height: 48),

            // Loading indicator
            const CircularProgressIndicator(),
            const SizedBox(height: 16),

            Text(
              'Checking connection...',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey[500],
                  ),
            ),
          ],
        ),
      ),
    );
  }
}
