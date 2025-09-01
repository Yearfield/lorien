import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

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
    return Scaffold(
      resizeToAvoidBottomInset: resizeToAvoidBottomInset,
      appBar: AppBar(
        leading: Semantics(
          label: 'Go back',
          button: true,
          child: IconButton(
            tooltip: 'Back',
            icon: const Icon(Icons.arrow_back),
            onPressed: canPop ? () => context.pop() : null,
          ),
        ),
        title: Text(title),
        actions: [
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
