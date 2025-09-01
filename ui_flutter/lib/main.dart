import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/router/app_router.dart';
import 'theme/app_theme.dart';
import 'features/settings/logic/settings_controller.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ProviderScope(child: LorienApp()));
}

class LorienApp extends ConsumerStatefulWidget {
  const LorienApp({super.key});
  @override 
  ConsumerState<LorienApp> createState() => _S();
}

class _S extends ConsumerState<LorienApp> {
  @override 
  void initState() { 
    super.initState(); 
    ref.read(settingsControllerProvider).load(); 
  }
  
  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Lorien',
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      routerConfig: appRouter,
      debugShowCheckedModeBanner: false,
    );
  }
}
