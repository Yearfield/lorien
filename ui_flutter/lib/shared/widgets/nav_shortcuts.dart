import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'shortcuts_help.dart';

class NavShortcuts extends StatelessWidget {
  const NavShortcuts({super.key, required this.child});
  final Widget child;
  
  @override
  Widget build(BuildContext context) {
    return Shortcuts(
      shortcuts: <LogicalKeySet, Intent>{
        LogicalKeySet(LogicalKeyboardKey.escape): const _BackIntent(),
        LogicalKeySet(LogicalKeyboardKey.alt, LogicalKeyboardKey.arrowLeft): const _BackIntent(),
        LogicalKeySet(LogicalKeyboardKey.control, LogicalKeyboardKey.keyH): const _HomeIntent(),
        LogicalKeySet(LogicalKeyboardKey.control, LogicalKeyboardKey.slash): const _HelpIntent(),
      },
      child: Actions(
        actions: <Type, Action<Intent>>{
          _BackIntent: CallbackAction<_BackIntent>(onInvoke: (i) {
            final r = GoRouter.of(context);
            if (r.canPop()) r.pop();
            return null;
          }),
          _HomeIntent: CallbackAction<_HomeIntent>(onInvoke: (i) {
            GoRouter.of(context).go('/');
            return null;
          }),
          _HelpIntent: CallbackAction<_HelpIntent>(onInvoke: (i) {
            showShortcutsHelp(context);
            return null;
          }),
        },
        child: Focus(autofocus: true, child: child),
      ),
    );
  }
}

class _BackIntent extends Intent { 
  const _BackIntent(); 
}

class _HomeIntent extends Intent { 
  const _HomeIntent(); 
}

class _HelpIntent extends Intent { 
  const _HelpIntent(); 
}
