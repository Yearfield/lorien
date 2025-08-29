import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';
import 'data/api_client.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize the client early for a single shared instance/logging.
  ApiClient();
  
  runApp(
    const ProviderScope(
      child: DecisionTreeManagerApp(),
    ),
  );
}
