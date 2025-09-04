import 'package:go_router/go_router.dart';
import '../../features/home/ui/home_screen.dart';
import '../../features/outcomes/ui/outcomes_list_screen.dart';
import '../../features/outcomes/ui/outcomes_detail_screen.dart';
import '../../features/calculator/ui/calculator_screen.dart';
import '../../features/dictionary/ui/dictionary_screen.dart';
import '../../features/flags/ui/flags_screen.dart';
import '../../features/settings/ui/settings_screen.dart';
import '../../features/settings/ui/about_status_page.dart';
import '../../features/workspace/ui/workspace_screen.dart';

final appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(path: '/', builder: (_, __) => const HomeScreen()),
    GoRoute(path: '/outcomes', builder: (_, __) => const OutcomesListScreen()),
    GoRoute(
      path: '/outcomes/:id',
      builder: (ctx, st) =>
          OutcomesDetailScreen(
            outcomeId: st.pathParameters['id']!,
            vm: st.uri.queryParameters['vm'],
          ),
    ),
    GoRoute(path: '/calculator', builder: (_, __) => const CalculatorScreen()),
    GoRoute(path: '/dictionary', builder: (_, __) => const DictionaryScreen()),
    GoRoute(path: '/flags', builder: (_, __) => const FlagsScreen()),
    GoRoute(path: '/settings', builder: (_, __) => const SettingsScreen()),
    GoRoute(path: '/about', builder: (_, __) => const AboutStatusPage()),
    GoRoute(path: '/workspace', builder: (_, __) => const WorkspaceScreen()),
  ],
);
