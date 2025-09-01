Map<String, String> mapPydanticFieldErrors(dynamic responseData) {
  final Map<String, String> out = {};
  final list = (responseData?['detail'] as List?) ?? const [];
  for (final item in list) {
    final loc = (item['loc'] as List?)?.join('.') ?? '';
    final msg = item['msg']?.toString() ?? '';
    if (loc.contains('diagnostic_triage')) out['diagnostic_triage'] = msg;
    if (loc.contains('actions')) out['actions'] = msg;
  }
  return out;
}
