final RegExp allowedChars = RegExp(r'^[A-Za-z0-9 ,\-]+$');

// Prohibited tokens: dosing/route/time patterns
final RegExp prohibitedTokens = RegExp(
  r'\b(\d+(\.\d+)?\s*(mg|g|mcg|ml|kg|iu)|'
  r'(iv|im|sc|po|pr|sl|inh|top|ophth|otic|nas|rect|vag|epid|transd|subq)|'
  r'(q\d*h|q\d+|bid|tid|qid|prn|stat|od|hs|ac|pc|qam|qpm|qhs|qod))\b',
  caseSensitive: false
);

String? maxSevenWordsAndAllowed(String? v, {required String field}) {
  final s = (v ?? '').trim();
  if (s.isEmpty) return '$field is required';
  final words = s.split(RegExp(r'\s+')).where((x) => x.isNotEmpty).length;
  if (words > 7) return '$field must be ≤7 words';
  if (!allowedChars.hasMatch(s)) return '$field has disallowed characters';
  if (prohibitedTokens.hasMatch(s)) {
    return '$field contains prohibited tokens (dosing/route/time: mg, ml, IV, q6h, etc.)';
  }
  return null;
}
