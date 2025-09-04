import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import '../../../core/http/api_client.dart';
import 'edit_tree_repository.dart';

// Provider for the base URL
final apiBaseUrlProvider = StateProvider<String>((ref) => 'http://127.0.0.1:8000/api/v1');

final editTreeRepositoryProvider = Provider<EditTreeRepository>((ref) {
  final Dio dio = ref.watch(dioProvider);
  final String base = ref.watch(apiBaseUrlProvider);
  return EditTreeRepository(dio, base);
});
