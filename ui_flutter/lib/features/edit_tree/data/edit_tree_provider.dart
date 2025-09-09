import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../providers/lorien_api_provider.dart';
import '../../tree/data/tree_api.dart';
import 'edit_tree_repository.dart';

final editTreeRepositoryProvider = Provider<EditTreeRepository>((ref) {
  final api = ref.watch(lorienApiProvider);
  final treeApi = ref.watch(treeApiProvider);
  return EditTreeRepository(api, treeApi);
});
