import 'package:flutter/material.dart';
import 'package:provider/provider.dart' as provider;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/api_config.dart';
import 'core/health_state.dart';
import 'shell/app_shell.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ProviderScope(
      child: provider.ChangeNotifierProvider(
        create: (_) => HealthState(),
        child: MaterialApp(
          title: 'Lorien',
          theme: ThemeData(useMaterial3: true, colorSchemeSeed: Colors.blue),
          home: const AppShell(),
        ),
      ),
    );
  }
}