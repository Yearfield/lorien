import 'package:flutter/material.dart';

/// ScrollScaffold: a drop-in Scaffold that guarantees a scrollable body
/// and a fixed bottom action bar (no more overflow).
class ScrollScaffold extends StatelessWidget {
  const ScrollScaffold({
    super.key,
    required this.title,
    required this.children,
    this.actions = const <Widget>[],
    this.padding = const EdgeInsets.all(16),
  });

  final String title;
  final List<Widget> children;
  final List<Widget> actions; // e.g., Save / Test Connection
  final EdgeInsetsGeometry padding;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: ListView(
        padding: padding,
        children: children,
      ),
      bottomNavigationBar: actions.isEmpty
          ? null
          : SafeArea(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
                child: Row(children: _withGaps(actions, const SizedBox(width: 8))),
              ),
            ),
    );
  }

  static List<Widget> _withGaps(List<Widget> items, Widget gap) {
    if (items.isEmpty) return items;
    final out = <Widget>[];
    for (var i = 0; i < items.length; i++) {
      out.add(items[i]);
      if (i != items.length - 1) out.add(gap);
    }
    return out;
  }
}
