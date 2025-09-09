import 'package:dio/dio.dart';
import 'package:http_mock_adapter/http_mock_adapter.dart';

class DioTestHarness {
  final Dio dio = Dio();
  late final DioAdapter adapter;
  
  DioTestHarness() {
    adapter = DioAdapter(dio: dio);
  }
}
