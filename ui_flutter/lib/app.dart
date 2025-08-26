import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'routing/app_router.dart';
import 'theme/app_theme.dart';
import 'state/app_settings_provider.dart';

class DecisionTreeManagerApp extends ConsumerWidget {
  const DecisionTreeManagerApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);
    final themeMode = ref.watch(themeModeProvider);
    
    return MaterialApp.router(
      title: 'Decision Tree Manager',
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeMode,
      routerConfig: router,
      debugShowCheckedModeBanner: false,
    );
  }
}
