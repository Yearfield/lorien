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
import 'core/app_scroll_behavior.dart';

void main() {
  runZonedGuarded(() {
    WidgetsFlutterBinding.ensureInitialized();

    // Initialize the singleton API client early (no awaits).
    ApiClient.I();

    // Never perform async/prefs/network before runApp.
    FlutterError.onError = (details) {
      FlutterError.presentError(details);
      CrashReportService.recordFlutterError(details);
    };
    // Optionally fail fast only in debug:
    // BindingBase.debugZoneErrorsAreFatal = kDebugMode;

    runApp(const ProviderScope(child: LorienApp()));

    // Defer all startup work to after first frame.
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      await _startupAsync();
    });
  }, (e, st) => CrashReportService.recordZoneError(e, st));
}

Future<void> _startupAsync() async {
  try {
    // Load API base URL override lazily and reconfigure client.
    final prefs = await SharedPreferences.getInstance();
    final override = prefs.getString('api_base_override');
    if (override != null && override.trim().isNotEmpty) {
      ApiClient.setBaseUrl(override.trim());
    }

    // Optionally kick light, non-blocking probes via providers (post-frame).
    // e.g., context-free singletons, or rely on providers/screens to trigger lazily.
  } catch (e, st) {
    CrashReportService.recordZoneError(e, st);
  }
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
    // Defer async initialization to post-frame to avoid blocking first frame.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeAsync();
    });
  }

  Future<void> _initializeAsync() async {
    try {
      await ref.read(settingsControllerProvider).load();
    } catch (e, st) {
      CrashReportService.recordZoneError(e, st);
    }
  }

  @override
  Widget build(BuildContext context) {
    return NavShortcuts(
      child: MaterialApp.router(
        title: 'Lorien',
        theme: AppTheme.lightTheme.copyWith(
          splashFactory: NoSplash.splashFactory,
          highlightColor: Colors.transparent,
          hoverColor: Colors.transparent,
          visualDensity: VisualDensity.standard,
        ),
        darkTheme: AppTheme.darkTheme.copyWith(
          splashFactory: NoSplash.splashFactory,
          highlightColor: Colors.transparent,
          hoverColor: Colors.transparent,
          visualDensity: VisualDensity.standard,
        ),
        routerConfig: appRouter,
        debugShowCheckedModeBanner: false,
        builder: (context, child) => ScrollConfiguration(
          behavior: const AppScrollBehavior(),
          child: child ?? const SizedBox.shrink(),
        ),
      ),
    );
  }
}
