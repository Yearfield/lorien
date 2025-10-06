class HealthResponse {
  final bool ok;
  final String status;
  final String version;
  final DatabaseInfo db;
  final Map<String, bool> features;
  final String? error;

  HealthResponse({
    required this.ok,
    required this.status,
    required this.version,
    required this.db,
    required this.features,
    this.error,
  });

  factory HealthResponse.fromJson(Map<String, dynamic> json) {
    return HealthResponse(
      ok: json['ok'] ?? false,
      status: json['status'] ?? 'unknown',
      version: json['version'] ?? 'unknown',
      db: DatabaseInfo.fromJson(json['db'] ?? {}),
      features: Map<String, bool>.from(json['features'] ?? {}),
      error: json['error'],
    );
  }
}

class DatabaseInfo {
  final String? path;
  final String? journalMode;
  final int tables;
  final int nodes;
  final String integrity;
  final int objects;

  DatabaseInfo({
    this.path,
    this.journalMode,
    required this.tables,
    required this.nodes,
    required this.integrity,
    required this.objects,
  });

  factory DatabaseInfo.fromJson(Map<String, dynamic> json) {
    return DatabaseInfo(
      path: json['path'],
      journalMode: json['journal_mode'],
      tables: json['tables'] ?? 0,
      nodes: json['nodes'] ?? 0,
      integrity: json['integrity'] ?? 'unknown',
      objects: json['objects'] ?? 0,
    );
  }

  bool get isHealthy => integrity.toLowerCase() == 'ok';
  bool get isWalMode => journalMode?.toLowerCase() == 'wal';
}
