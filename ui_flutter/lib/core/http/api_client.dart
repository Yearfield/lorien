import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/health_service.dart';
import 'dio_interceptors.dart';

final dioProvider = Provider<Dio>((ref) {
  final d = Dio(BaseOptions(
    connectTimeout: const Duration(seconds: 8),
    receiveTimeout: const Duration(seconds: 8),
  ));
  d.interceptors.add(BaseUrlInterceptor(() => ref.read(baseUrlProvider)));
  return d;
});
