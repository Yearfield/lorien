import 'package:flutter/material.dart';

class ScrollToTopFab extends StatefulWidget {
  const ScrollToTopFab({super.key, required this.controller});
  final ScrollController controller;

  @override
  State<ScrollToTopFab> createState() => _S();
}

class _S extends State<ScrollToTopFab> {
  bool _show = false;

  @override
  void initState() {
    super.initState();
    widget.controller.addListener(() {
      final now = widget.controller.offset > 300;
      if (now != _show) setState(() => _show = now);
    });
  }

  @override
  Widget build(BuildContext context) {
    if (!_show) return const SizedBox.shrink();
    return FloatingActionButton(
      onPressed: () => widget.controller.animateTo(0,
          duration: const Duration(milliseconds: 300), curve: Curves.easeOut),
      child: const Icon(Icons.arrow_upward),
    );
  }
}
