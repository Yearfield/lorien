class ApiPaths {
  /// Prefix for all API routes.
  /// API is now versioned under /api/v1.
  static const String prefix = '/api/v1';

  static String _p(String path) => '$prefix$path';

  // Health
  static String get health => _p('/health');

  // Tree
  static String treeChildren(int parentId) => _p('/tree/$parentId/children');
  static String treeUpsertChildren(int parentId) => _p('/tree/$parentId/children');
  static String treeUpsertChild(int parentId) => _p('/tree/$parentId/child');
  // BUGFIX: must use _p(...) rather than a raw const string
  static String get treeNextIncomplete => _p('/tree/next-incomplete-parent');

  // Triage
  static String triage(int nodeId) => _p('/triage/$nodeId');

  // Flags
  static String get flagsSearch => _p('/flags/search');
  static String get flagsAssign => _p('/flags/assign');

  // Calculator
  static String get calcExport => _p('/calc/export');
}
