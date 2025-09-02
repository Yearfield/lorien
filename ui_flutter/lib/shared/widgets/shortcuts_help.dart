import 'package:flutter/material.dart';
import 'nav_shortcuts.dart';

Future<void> showShortcutsHelp(BuildContext context) async {
  await showDialog(
    context: context,
    builder: (_) => AlertDialog(
      title: const Text('Keyboard Shortcuts'),
      content: const Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Back: Esc or Alt + ←'),
          SizedBox(height: 4),
          Text('Home: Ctrl + H'),
          SizedBox(height: 4),
          Text('Help: Ctrl + /'),
          SizedBox(height: 4),
          Text('Scroll to top: T (on list)'),
        ],
      ),
      actions: [
        FilledButton(
          onPressed: () => Navigator.of(context).pop(), 
          child: const Text('Close')
        )
      ],
    ),
  );
}
