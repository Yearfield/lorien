import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

typedef BusyGetter = bool Function();

class RouteGuard extends StatelessWidget {
  const RouteGuard({
    super.key, 
    required this.isBusy, 
    required this.child, 
    this.confirmMessage
  });
  
  final BusyGetter isBusy;
  final Widget child;
  final String? confirmMessage;

  Future<bool> _confirm(BuildContext context) async {
    final go = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Operation in progress'),
        content: Text(
          confirmMessage ?? 'An operation is running. Do you want to leave and cancel it?'
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false), 
            child: const Text('Stay')
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(true), 
            child: const Text('Leave')
          ),
        ],
      ),
    );
    return go ?? false;
  }

  @override
  Widget build(BuildContext context) {
    return WillPopScope(
      onWillPop: () async {
        if (!isBusy()) return true;
        return _confirm(context);
      },
      child: GuardScope(
        isBusy: isBusy, 
        confirm: () => _confirm(context), 
        child: child
      ),
    );
  }
}

class GuardScope extends InheritedWidget {
  const GuardScope({
    super.key,
    required this.isBusy, 
    required this.confirm, 
    required super.child
  });
  
  final BusyGetter isBusy;
  final Future<bool> Function() confirm;
  
  static GuardScope? of(BuildContext c) => 
      c.dependOnInheritedWidgetOfExactType<GuardScope>();
  
  @override 
  bool updateShouldNotify(covariant GuardScope old) => 
      isBusy() != old.isBusy();
}

/// Use from AppScaffold leading/back to decide disable/confirm behavior.
bool navGuardedPop(BuildContext context) {
  final scope = GuardScope.of(context);
  final r = GoRouter.of(context);
  if (r.canPop() == false) return false;
  if (scope?.isBusy.call() == true) {
    scope?.confirm.call().then((go) { 
      if (go) r.pop(); 
    });
    return false;
  }
  r.pop();
  return true;
}
