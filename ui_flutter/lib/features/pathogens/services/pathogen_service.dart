import 'dart:io';
import 'package:dio/dio.dart';
import 'package:lorien/features/pathogens/models/pathogen_models.dart';
import 'package:lorien/core/api_config.dart';

class PathogenService {
  final Dio _dio;

  PathogenService({Dio? dio}) : _dio = dio ?? Dio();

  Future<List<Pathogen>> getPathogens({
    String? search,
    String? associationFilter,
    bool showOnlyWithAssociations = false,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (search != null && search.isNotEmpty) {
        queryParams['search'] = search;
      }
      if (associationFilter != null) {
        queryParams['association_filter'] = associationFilter;
      }
      if (showOnlyWithAssociations) {
        queryParams['show_only_with_associations'] = 'true';
      }

      final response = await _dio.get(
        '${ApiConfig.base}/pathogens/',
        queryParameters: queryParams,
      );

      final List<dynamic> data = response.data;
      return data.map((json) => Pathogen.fromJson(json)).toList();
    } catch (e) {
      throw Exception('Failed to fetch pathogens: $e');
    }
  }

  Future<PathogenWithAssociations?> getPathogenWithAssociations(int pathogenId) async {
    try {
      final response = await _dio.get('${ApiConfig.base}/pathogens/$pathogenId');
      return PathogenWithAssociations.fromJson(response.data);
    } catch (e) {
      if (e is DioException && e.response?.statusCode == 404) {
        return null;
      }
      throw Exception('Failed to fetch pathogen details: $e');
    }
  }

  Future<List<AssociationType>> getAssociationTypes() async {
    try {
      final response = await _dio.get('${ApiConfig.base}/pathogens/association-types/');
      final List<dynamic> data = response.data;
      // The API returns a list of strings, not objects
      return data.map((name) => AssociationType.fromString(name.toString())).toList();
    } catch (e) {
      throw Exception('Failed to fetch association types: $e');
    }
  }

  Future<PathogenStats?> getPathogenStats() async {
    try {
      final response = await _dio.get('${ApiConfig.base}/pathogens/stats/summary');
      return PathogenStats.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to fetch pathogen stats: $e');
    }
  }

  Future<PathogenImportResult> importPathogens(File file) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(file.path),
      });

      final response = await _dio.post(
        '${ApiConfig.base}/pathogens/import',
        data: formData,
        options: Options(
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        ),
      );

      return PathogenImportResult.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to import pathogens: $e');
    }
  }

  Future<void> deletePathogen(int pathogenId) async {
    try {
      await _dio.delete('${ApiConfig.base}/pathogens/$pathogenId');
    } catch (e) {
      throw Exception('Failed to delete pathogen: $e');
    }
  }

  Future<Pathogen> createPathogen(PathogenProperties properties) async {
    try {
      final response = await _dio.post(
        '${ApiConfig.base}/pathogens/',
        data: properties.toJson(),
      );
      return Pathogen.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to create pathogen: $e');
    }
  }

  Future<Pathogen> updatePathogen(int pathogenId, PathogenProperties properties) async {
    try {
      final response = await _dio.put(
        '${ApiConfig.base}/pathogens/$pathogenId',
        data: properties.toJson(),
      );
      return Pathogen.fromJson(response.data);
    } catch (e) {
      throw Exception('Failed to update pathogen: $e');
    }
  }
}
