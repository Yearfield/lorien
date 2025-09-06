import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../api/lorien_api.dart';
import '../../../providers/lorien_api_provider.dart';
import 'edit_tree_repository.dart';

final editTreeRepositoryProvider = Provider<EditTreeRepository>((ref) {
  final api = ref.watch(lorienApiProvider);
  return EditTreeRepository(api);
});
