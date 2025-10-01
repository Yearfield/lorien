import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../widgets/connection_banner.dart';
import '../core/health_state.dart';
import '../core/api_config.dart';
import '../features/home/ui/home_pane.dart';
import '../features/vm_builder/ui/vm_builder_screen.dart';
import '../features/outcomes/ui/outcomes_pane.dart';
import '../features/flags/ui/flags_pane.dart';
import '../features/settings/ui/settings_pane.dart';
import '../features/vm_builder/state/vm_provider.dart';
import '../features/vm_builder/data/vm_repo.dart';

class AppShell extends StatefulWidget {
  const AppShell({super.key});
  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _index = 1; // default to VM Builder (the star of the show)

  @override
  void initState() {
    super.initState();
    // Do an initial health check
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<HealthState>().check();
    });
  }

  Widget _paneFor(int idx) {
    switch (idx) {
      case 0: return const HomePane();
      case 1: return VmBuilderScreen(baseUrl: ApiConfig.base);
      case 2: return const OutcomesPane();
      case 3: return const FlagsPane();
      case 4: return const SettingsPane();
      default: return const HomePane();
    }
  }

  @override
  Widget build(BuildContext context) {
    // Provide VM state here so the pane can be re-used in a larger app context
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => VmState(VmRepo(ApiConfig.base))),
      ],
      child: Scaffold(
        appBar: AppBar(title: const Text('Lorien')),
        body: Row(
          children: [
            NavigationRail(
              selectedIndex: _index,
              onDestinationSelected: (i) => setState(() => _index = i),
              labelType: NavigationRailLabelType.all,
              destinations: const [
                NavigationRailDestination(icon: Icon(Icons.home), label: Text('Home')),
                NavigationRailDestination(icon: Icon(Icons.account_tree), label: Text('VM Builder')),
                NavigationRailDestination(icon: Icon(Icons.assignment), label: Text('Outcomes')),
                NavigationRailDestination(icon: Icon(Icons.flag), label: Text('Flags')),
                NavigationRailDestination(icon: Icon(Icons.settings), label: Text('Settings')),
              ],
            ),
            const VerticalDivider(width: 1),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const ConnectionBanner(),
                  Expanded(child: _paneFor(_index)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
