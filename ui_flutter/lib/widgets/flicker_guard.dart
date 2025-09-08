import 'package:flutter/material.dart';

class FlickerGuard extends StatelessWidget {
  final Widget child;
  final Key? repaintKey;
  
  const FlickerGuard({
    super.key,
    required this.child,
    this.repaintKey,
  });
  
  @override
  Widget build(BuildContext context) {
    return RepaintBoundary(
      key: repaintKey,
      child: AnimatedSwitcher(
        duration: const Duration(milliseconds: 120),
        switchInCurve: Curves.easeOut,
        switchOutCurve: Curves.easeIn,
        child: child,
      ),
    );
  }
}
