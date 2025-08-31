class TriageLeaf {
  final int nodeId;
  final String vitalMeasurement;
  final String path; // VM → Node1..5 textual path
  final String diagnosticTriage;
  final String actions;
  final DateTime? updatedAt;

  TriageLeaf({
    required this.nodeId,
    required this.vitalMeasurement,
    required this.path,
    required this.diagnosticTriage,
    required this.actions,
    this.updatedAt,
  });

  factory TriageLeaf.fromJson(Map<String,dynamic> j) => TriageLeaf(
    nodeId: j['node_id'],
    vitalMeasurement: j['vital_measurement'] ?? '',
    path: j['path'] ?? '',
    diagnosticTriage: j['diagnostic_triage'] ?? '',
    actions: j['actions'] ?? '',
    updatedAt: j['updated_at'] != null ? DateTime.tryParse(j['updated_at']) : null,
  );
}

class TriageDetail {
  final int nodeId;
  String diagnosticTriage;
  String actions;
  final bool isLeaf;

  TriageDetail({required this.nodeId, required this.diagnosticTriage, required this.actions, required this.isLeaf});

  factory TriageDetail.fromJson(Map<String,dynamic> j) => TriageDetail(
    nodeId: j['node_id'],
    diagnosticTriage: j['diagnostic_triage'] ?? '',
    actions: j['actions'] ?? '',
    isLeaf: j['is_leaf'] ?? true,
  );
}

class LlmFillRequest {
  final String root;
  final List<String> nodes; // length 5
  final String triageStyle;   // 'diagnosis-only' | 'referral-only'
  final String actionsStyle;  // 'diagnosis-only' | 'referral-only'
  final bool apply; // whether to apply suggestions directly
  
  LlmFillRequest({
    required this.root, 
    required this.nodes, 
    required this.triageStyle, 
    required this.actionsStyle,
    this.apply = false,
  });
  
  Map<String, dynamic> toJson() => {
    'root': root, 
    'nodes': nodes, 
    'triage_style': triageStyle, 
    'actions_style': actionsStyle,
    'apply': apply,
  };
}
