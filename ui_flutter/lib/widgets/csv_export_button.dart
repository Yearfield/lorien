import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

class CsvExportButton extends StatelessWidget {
  final Uri endpoint; // e.g., Uri.parse('$base/calc/export?vm=BP&n1=Pain&n2=Sharp...')
  final String fileName;
  final String label;
  
  const CsvExportButton({
    super.key, 
    required this.endpoint, 
    required this.fileName, 
    required this.label
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton.icon(
      icon: const Icon(Icons.download),
      label: Text(label),
      onPressed: () => _exportCsv(context),
    );
  }

  Future<void> _exportCsv(BuildContext context) async {
    try {
      // Show loading indicator
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => const Center(
          child: CircularProgressIndicator(),
        ),
      );

      // Download CSV data
      final response = await http.get(endpoint);
      
      // Hide loading indicator
      Navigator.of(context).pop();

      if (response.statusCode != 200) {
        _showError(context, 'Export failed: ${response.statusCode}');
        return;
      }

      // Save to temporary file
      final dir = await getTemporaryDirectory();
      final file = File('${dir.path}/$fileName');
      await file.writeAsBytes(response.bodyBytes);

      // Handle platform-specific export
      if (Platform.isAndroid || Platform.isIOS) {
        // Mobile: Open share sheet
        await Share.shareXFiles(
          [XFile(file.path)], 
          text: 'Lorien CSV export: $fileName'
        );
      } else {
        // Desktop: Show save location and save
        _showDesktopSaveDialog(context, file);
      }
    } catch (e) {
      // Hide loading indicator if still showing
      if (Navigator.of(context).canPop()) {
        Navigator.of(context).pop();
      }
      _showError(context, 'Export failed: $e');
    }
  }

  void _showDesktopSaveDialog(BuildContext context, File file) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('CSV Export Complete'),
        content: Text('File saved to: ${file.path}'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _showError(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }
}
