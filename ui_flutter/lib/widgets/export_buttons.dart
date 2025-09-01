import 'dart:io';
import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

class ExportButtons extends StatelessWidget {
  final Dio dio;
  final String baseUrl;
  const ExportButtons({super.key, required this.dio, required this.baseUrl});

  Future<void> _download(BuildContext ctx, String path, String fname) async {
    final tmp = await getTemporaryDirectory();
    final file = File('${tmp.path}/$fname');
    final resp = await dio.get('$baseUrl$path',
        options: Options(responseType: ResponseType.bytes));
    await file.writeAsBytes(resp.data);
    if (Platform.isAndroid || Platform.isIOS) {
      await Share.shareXFiles([XFile(file.path)], text: 'Lorien export');
    } else {
      ScaffoldMessenger.of(ctx)
          .showSnackBar(SnackBar(content: Text('Saved: ${file.path}')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Row(children: [
      ElevatedButton.icon(
          onPressed: () =>
              _download(context, '/calc/export', 'lorien_calc_export.csv'),
          icon: const Icon(Icons.download),
          label: const Text('Export CSV')),
      const SizedBox(width: 8),
      OutlinedButton.icon(
          onPressed: () => _download(
              context, '/calc/export.xlsx', 'lorien_calc_export.xlsx'),
          icon: const Icon(Icons.table_view),
          label: const Text('Export XLSX')),
    ]);
  }
}
