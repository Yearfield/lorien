import 'package:flutter/material.dart';

class FieldErrorText extends StatelessWidget {
  const FieldErrorText(this.text, {super.key});
  final String? text;
  @override
  Widget build(BuildContext context) {
    if (text == null || text!.isEmpty) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(top: 6),
      child: Text(text!,
          style: TextStyle(color: Theme.of(context).colorScheme.error)),
    );
  }
}
