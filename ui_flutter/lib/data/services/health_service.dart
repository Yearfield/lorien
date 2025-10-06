import 'package:dio/dio.dart';
import '../dto/health_dto.dart';
import '../../core/api_config.dart';

class HealthService {
  final Dio _dio;

  HealthService({Dio? dio}) : _dio = dio ?? Dio();

  Future<HealthResponse> getHealthStatus() async {
    try {
      final response = await _dio.get('${ApiConfig.base}/health');
      return HealthResponse.fromJson(response.data);
    } on DioException catch (e) {
      // Return error response for network issues
      return HealthResponse(
        ok: false,
        status: 'error',
        version: 'unknown',
        db: DatabaseInfo(
          tables: 0,
          nodes: 0,
          integrity: 'error',
          objects: 0,
        ),
        features: {},
        error: e.message ?? 'Network error',
      );
    } catch (e) {
      // Return error response for other issues
      return HealthResponse(
        ok: false,
        status: 'error',
        version: 'unknown',
        db: DatabaseInfo(
          tables: 0,
          nodes: 0,
          integrity: 'error',
          objects: 0,
        ),
        features: {},
        error: e.toString(),
      );
    }
  }

  Future<bool> testConnection() async {
    try {
      final response = await _dio.get('${ApiConfig.base}/live');
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
