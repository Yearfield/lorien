import 'package:flutter/material.dart';

class WordCounter extends StatelessWidget {
  const WordCounter(this.text, {super.key});
  final String text;

  int get wordCount {
    final trimmed = text.trim();
    if (trimmed.isEmpty) return 0;
    return trimmed.split(RegExp(r'\s+')).where((x) => x.isNotEmpty).length;
  }

  @override
  Widget build(BuildContext context) {
    return Text('$wordCount/7', style: Theme.of(context).textTheme.bodySmall);
  }
}
