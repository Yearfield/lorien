class ApiPaths {
  /// Resource paths for API endpoints.
  /// Base URL already includes /api/v1/, so paths are resource-only.
  /// All paths must NOT start with / and must NOT include /api/v1.

  // Health
  static String get health => 'health';

  // Tree
  static String treeChildren(int parentId) => 'tree/$parentId/children';
  static String treeUpsertChildren(int parentId) => 'tree/$parentId/children';
  static String treeUpsertChild(int parentId) => 'tree/$parentId/child';
  static String get treeNextIncomplete => 'tree/next-incomplete-parent';

  // Triage
  static String triage(int nodeId) => 'triage/$nodeId';

  // Outcomes (triage alias)
  static String outcomes(int nodeId) => 'outcomes/$nodeId';

  // Flags
  static String get flags => 'flags';
  static String get flagsSearch => 'flags/search';
  static String get flagsAssign => 'flags/assign';

  // Calculator
  static String get calcExport => 'calc/export';
}
