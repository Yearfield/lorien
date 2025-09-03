import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Shows a Back chevron when Navigator.canPop() is true, otherwise a Home button.
class AppBackLeading extends StatelessWidget {
  const AppBackLeading({super.key});

  @override
  Widget build(BuildContext context) {
    final canPop = Navigator.of(context).canPop();
    if (canPop) {
      return IconButton(
        icon: const Icon(Icons.arrow_back),
        onPressed: () => Navigator.of(context).maybePop(),
        tooltip: 'Back',
      );
    } else {
      return IconButton(
        icon: const Icon(Icons.home),
        onPressed: () {
          // GoRouter preferred; fallback to Navigator if not using go_router.
          try {
            context.go('/');
          } catch (_) {
            Navigator.of(context).pushNamedAndRemoveUntil('/', (r) => false);
          }
        },
        tooltip: 'Home',
      );
    }
  }
}
