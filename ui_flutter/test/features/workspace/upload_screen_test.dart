import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/testing.dart';
import 'package:http/http.dart' as http;

import 'package:lorien/features/workspace/upload_screen.dart';

void main() {
  testWidgets('UploadScreen renders basic UI elements', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: UploadScreen()));
    expect(find.text('Workspace → Upload'), findsOneWidget);
    expect(find.text('Select & Upload (.xlsx/.csv)'), findsOneWidget);
    expect(find.text('Status: idle'), findsOneWidget);
  });

  testWidgets('UploadScreen shows proper app bar', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: UploadScreen()));
    
    // Verify app bar exists with correct title
    expect(find.byType(AppBar), findsOneWidget);
    expect(find.text('Workspace → Upload'), findsOneWidget);
  });

  testWidgets('UploadScreen has proper layout structure', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: UploadScreen()));
    
    // Verify main structure
    expect(find.byType(Scaffold), findsOneWidget);
    expect(find.byType(Column), findsOneWidget);
    
    // Verify status chip
    expect(find.byType(Chip), findsOneWidget);
  });

  testWidgets('UploadScreen shows button text', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: UploadScreen()));
    
    // Just verify the button text exists, regardless of widget type
    expect(find.text('Select & Upload (.xlsx/.csv)'), findsOneWidget);
  });

  testWidgets('UploadScreen shows status chip', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: UploadScreen()));
    
    // Verify status chip shows initial state
    expect(find.text('Status: idle'), findsOneWidget);
  });
}
