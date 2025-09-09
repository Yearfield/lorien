Map<String, String> mapPydanticFieldErrors(dynamic responseData) {
  final Map<String, String> out = {};
  final list = (responseData?['detail'] as List?) ?? const [];
  for (final item in list) {
    final loc = (item['loc'] as List?)?.join('.') ?? '';
    final msg = item['msg']?.toString() ?? '';
    final type = item['type']?.toString() ?? '';
    if (loc.contains('diagnostic_triage')) out['diagnostic_triage'] = msg;
    if (loc.contains('actions')) out['actions'] = msg;
    // Surface special types when helpful
    if (type.contains('value_error.children_count')) {
      out['children_count'] = msg;
    }
    if (type.contains('value_error.duplicate_child_label')) {
      out['duplicate_child_label'] = msg;
    }
  }
  return out;
}
