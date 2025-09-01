import 'package:flutter/material.dart';

void showSuccess(BuildContext c, String msg) =>
    ScaffoldMessenger.of(c).showSnackBar(SnackBar(content: Text(msg)));

void showError(BuildContext c, String msg) =>
    ScaffoldMessenger.of(c).showSnackBar(
      SnackBar(
        content: Text(msg), 
        backgroundColor: Theme.of(c).colorScheme.error
      )
    );
