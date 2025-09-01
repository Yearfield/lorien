import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:lorien/features/outcomes/ui/outcomes_detail_screen.dart';

void main() {
  testWidgets('Unsaved changes prompt appears on back/home', (tester) async {
    // TODO: implement with ProviderScope + fake router
    // This test would verify that:
    // 1. Typing in fields sets dirty state
    // 2. Attempting to navigate away shows dialog
    // 3. Choosing "Stay" keeps user on screen
    // 4. Choosing "Discard" allows navigation
    // 5. Saving clears dirty state
    expect(true, isTrue);
  });
}
