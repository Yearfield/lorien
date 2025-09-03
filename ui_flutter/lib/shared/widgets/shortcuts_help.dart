import 'package:flutter/material.dart';

class ShortcutsHelp extends StatelessWidget {
  const ShortcutsHelp({super.key});

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Keyboard Shortcuts'),
      content: const Text(
        '?: Show this help\n'
        'g h: Go to Home\n'
        'g f: Go to Flags\n'
        'g s: Go to Settings\n'
        'g a: Go to About\n',
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Close'),
        ),
      ],
    );
  }
}