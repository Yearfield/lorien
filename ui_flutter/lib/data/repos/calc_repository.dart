import 'package:dio/dio.dart';
import '../api_client.dart';
import '../api_paths.dart';

class CalcRepository {
  final ApiClient _apiClient;

  CalcRepository(this._apiClient);

  /// Export calculator data as CSV
  Future<String> exportCsv() async {
    try {
      final response = await _apiClient.get(
        ApiPaths.calcExport,
        options: Options(
          responseType: ResponseType.plain,
          headers: {
            'Accept': 'text/csv',
          },
        ),
      );

      if (response.statusCode == 200) {
        return response.data as String;
      }

      throw Exception('Failed to export CSV: ${response.statusCode}');
    } on DioException catch (e) {
      throw Exception('Network error: ${e.message}');
    }
  }

  /// Get health information including version
  Future<Map<String, dynamic>> getHealth() async {
    try {
      final response = await _apiClient.get(ApiPaths.health);

      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>;
      }

      throw Exception('Failed to get health: ${response.statusCode}');
    } on DioException catch (e) {
      throw Exception('Network error: ${e.message}');
    }
  }
}
