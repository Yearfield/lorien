import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'route_guard.dart';
import 'shortcuts_help.dart';

class AppScaffold extends StatelessWidget {
  const AppScaffold({
    super.key,
    required this.title,
    required this.body,
    this.actions,
    this.floatingActionButton,
    this.bottomNavigationBar,
    this.persistentFooterButtons,
    this.resizeToAvoidBottomInset,
  });
  
  final String title;
  final Widget body;
  final List<Widget>? actions;
  final Widget? floatingActionButton;
  final Widget? bottomNavigationBar;
  final List<Widget>? persistentFooterButtons;
  final bool? resizeToAvoidBottomInset;

  @override
  Widget build(BuildContext context) {
    final canPop = GoRouter.of(context).canPop();
    final busy = GuardScope.of(context)?.isBusy.call() ?? false;
    return Scaffold(
      resizeToAvoidBottomInset: resizeToAvoidBottomInset,
      appBar: AppBar(
        leading: Semantics(
          label: 'Go back',
          button: true,
          child: IconButton(
            tooltip: 'Back',
            icon: const Icon(Icons.arrow_back),
            onPressed: (canPop && !busy) ? () => navGuardedPop(context) : null,
          ),
        ),
        title: Text(title),
        actions: [
          // Help / shortcuts
          Semantics(
            label: 'Keyboard shortcuts and help',
            button: true,
            child: IconButton(
              tooltip: 'Help / Shortcuts',
              icon: const Icon(Icons.help_outline),
              onPressed: () => showShortcutsHelp(context),
            ),
          ),
          Semantics(
            label: 'Go home',
            button: true,
            child: IconButton(
              tooltip: 'Home',
              icon: const Icon(Icons.home),
              onPressed: () => context.go('/'),
            ),
          ),
          ...(actions ?? const []),
        ],
      ),
      body: body,
      floatingActionButton: floatingActionButton,
      bottomNavigationBar: bottomNavigationBar,
      persistentFooterButtons: persistentFooterButtons,
    );
  }
}
