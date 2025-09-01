import 'package:flutter/foundation.dart';

class SettingsProvider with ChangeNotifier {
  String _baseUrl = const String.fromEnvironment('LORIEN_API_BASE',
      defaultValue: 'http://127.0.0.1:8000/api/v1');
  String get baseUrl => _baseUrl;

  set baseUrl(String v) {
    if (v != _baseUrl) {
      _baseUrl = v;
      notifyListeners();
    }
  }
}
