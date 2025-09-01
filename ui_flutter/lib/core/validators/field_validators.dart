final RegExp allowedChars = RegExp(r'^[A-Za-z0-9 ,\-]+$');

String? maxSevenWordsAndAllowed(String? v, {required String field}) {
  final s = (v ?? '').trim();
  if (s.isEmpty) return '$field is required';
  final words = s.split(RegExp(r'\s+')).where((x) => x.isNotEmpty).length;
  if (words > 7) return '$field must be ≤7 words';
  if (!allowedChars.hasMatch(s)) return '$field has disallowed characters';
  return null;
}
