import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'features/vm_builder/data/vm_repo.dart';
import 'features/vm_builder/state/vm_provider.dart';
import 'features/vm_builder/ui/vm_builder_screen.dart';

void main() {
  const baseUrl = String.fromEnvironment('API_BASE', defaultValue: 'http://127.0.0.1:8000/api/v1');
  runApp(MyApp(baseUrl: baseUrl));
}

class MyApp extends StatelessWidget {
  final String baseUrl;
  const MyApp({super.key, required this.baseUrl});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => VmState(VmRepo(baseUrl))),
      ],
      child: MaterialApp(
        title: 'VM Builder',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
        ),
        home: VmBuilderScreen(baseUrl: baseUrl),
      ),
    );
  }
}