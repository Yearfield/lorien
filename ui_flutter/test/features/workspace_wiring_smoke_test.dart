import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ui_flutter/features/workspace/ui/workspace_screen.dart';

void main() {
  testWidgets('Workspace shows Replace toggle & Calculator button', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: WorkspaceScreen(),
        ),
      ),
    );
    
    expect(find.textContaining('Replace existing data'), findsOneWidget);
    expect(find.text('Open Calculator'), findsOneWidget);
    expect(find.text('Clear workspace (keep dictionary)'), findsOneWidget);
    expect(find.text('Fix Incomplete Parents'), findsOneWidget);
    expect(find.text('Fix Same parent BUT different children'), findsOneWidget);
  });
}
