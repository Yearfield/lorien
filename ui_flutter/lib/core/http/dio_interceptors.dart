import 'package:dio/dio.dart';

class BaseUrlInterceptor extends Interceptor {
  BaseUrlInterceptor(this.getBase);
  final String Function() getBase;

  @override
  void onRequest(RequestOptions opts, RequestInterceptorHandler h) {
    if (opts.path.startsWith('http')) return h.next(opts);
    final base = getBase().replaceAll(RegExp(r'\/$'), '');
    opts.path = '$base${opts.path.startsWith('/') ? '' : '/'}${opts.path}';
    h.next(opts);
  }
}
