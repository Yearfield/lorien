import '../http/api_client.dart';

/// Import API interface
abstract class ImportApi {
  Future<Map<String, dynamic>> importExcel({
    required Map<String, dynamic> fields,
    List<MapEntry<String, List<int>>>? files,
  });
}

/// Default implementation using ApiClient
class DefaultImportApi implements ImportApi {
  final ApiClient _client;

  DefaultImportApi(this._client);

  @override
  Future<Map<String, dynamic>> importExcel({
    required Map<String, dynamic> fields,
    List<MapEntry<String, List<int>>>? files,
  }) async {
    return await _client.postMultipart('/import', fields: fields, files: files);
  }
}
