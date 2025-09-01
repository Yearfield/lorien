import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/services/health_service.dart';

final settingsControllerProvider = Provider((ref) => SettingsController(ref));

class SettingsController {
  SettingsController(this._ref);
  final Ref _ref;
  static const _kBase = 'base_url';

  Future<void> load() async {
    final sp = await SharedPreferences.getInstance();
    final v = sp.getString(_kBase) ?? _ref.read(baseUrlProvider);
    _ref.read(baseUrlProvider.notifier).state =
        v ?? 'http://127.0.0.1:8000/api/v1';
  }

  Future<void> save(String base) async {
    final sp = await SharedPreferences.getInstance();
    await sp.setString(_kBase, base);
    _ref.read(baseUrlProvider.notifier).state = base;
  }
}
