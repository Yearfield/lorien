import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'core/router/app_router.dart';
import 'theme/app_theme.dart';
import 'features/settings/logic/settings_controller.dart';
import 'shared/widgets/nav_shortcuts.dart';
import 'data/api_client.dart';
import 'core/crash_report_service.dart';

void main() {
  runZonedGuarded(() async {
    WidgetsFlutterBinding.ensureInitialized();

    // Initialize the singleton API client early
    ApiClient.I();

    // Load API base URL override from preferences
    final prefs = await SharedPreferences.getInstance();
    final override = prefs.getString('api_base_override');
    if (override != null && override.trim().isNotEmpty) {
      ApiClient.setBaseUrl(override);
    }

    FlutterError.onError = (details) {
      FlutterError.presentError(details);
      // Local-only; remote upload optional and guarded
      CrashReportService.recordFlutterError(details);
    };
    // Optionally fail fast only in debug:
    // BindingBase.debugZoneErrorsAreFatal = kDebugMode;

    runApp(const ProviderScope(child: LorienApp()));
  }, (e, st) {
    CrashReportService.recordZoneError(e, st);
  });
}

class LorienApp extends ConsumerStatefulWidget {
  const LorienApp({super.key});
  @override
  ConsumerState<LorienApp> createState() => _S();
}

class _S extends ConsumerState<LorienApp> {
  @override
  void initState() {
    super.initState();
    ref.read(settingsControllerProvider).load();
  }

  @override
  Widget build(BuildContext context) {
    return NavShortcuts(
      child: MaterialApp.router(
        title: 'Lorien',
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        routerConfig: appRouter,
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}
