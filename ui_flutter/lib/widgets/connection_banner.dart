import 'package:flutter/material.dart';
import 'package:dio/dio.dart';

class ConnectionBanner extends StatelessWidget {
  final Future<Response<dynamic>> Function() healthCall;
  const ConnectionBanner({super.key, required this.healthCall});

  @override Widget build(BuildContext context) {
    return FutureBuilder<Response<dynamic>>(
      future: healthCall(),
      builder: (ctx, snap){
        if (snap.connectionState == ConnectionState.waiting) {
          return const LinearProgressIndicator();
        }
        if (snap.hasError || (snap.data?.statusCode ?? 500) != 200) {
          return const ListTile(leading: Icon(Icons.cloud_off, color: Colors.red), title: Text('Disconnected'));
        }
        return const ListTile(leading: Icon(Icons.cloud_done, color: Colors.green), title: Text('Connected'));
      },
    );
  }
}
