import 'package:dio/dio.dart';

class BaseUrlInterceptor extends Interceptor {
  BaseUrlInterceptor(this.getBase);
  final String Function() getBase;

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    if (options.path.startsWith('http')) return handler.next(options);
    final base = getBase().replaceAll(RegExp(r'\/$'), '');
    options.path = '$base${options.path.startsWith('/') ? '' : '/'}${options.path}';
    handler.next(options);
  }
}
