import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/features/vm_builder/state/vm_provider.dart';
import 'package:lorien/features/vm_builder/data/vm_repo.dart';

void main() {
  group('Real API Save Tests', () {
    late VmState vmState;
    late VmRepo realRepo;
    List<String> toastMessages = [];

    setUp(() {
      realRepo = VmRepo('http://127.0.0.1:8000/api/v1');
      vmState = VmState(realRepo);
      vmState.toast = (message) => toastMessages.add(message);
    });

    tearDown(() {
      toastMessages.clear();
    });

    test('Should save child to real API and persist in UI', () async {
      // Use parent 3 which has 4 children (room for 1 more)
      vmState.currentParentId = 3;
      vmState.children = ['Visual Disturbances', 'Nausea', 'Confusion', 'Photophobia', 'Test Real Child'];

      // Execute save
      await vmState.save();

      print('Toast messages: $toastMessages');

      // Verify success message
      expect(toastMessages.any((msg) => msg.contains('1 child(ren) added successfully')), isTrue);

      // Verify UI state is updated
      expect(vmState.children.length, equals(5), reason: 'UI should show 5 children after save');
      expect(vmState.children.contains('Test Real Child'), isTrue, reason: 'UI should contain the new child');
      expect(vmState.childrenWithMeta.length, equals(5), reason: 'childrenWithMeta should have 5 items');

      // Verify the child was actually added to the database
      final children = await realRepo.getChildren(3);
      expect(children.length, equals(5), reason: 'Database should have 5 children');
      expect(children.any((child) => child['label'] == 'Test Real Child'), isTrue, reason: 'Database should contain the new child');
    });

    test('Should handle parent with 5 children (should fail)', () async {
      // Use parent 1 which has 5 children (no room)
      vmState.currentParentId = 1;
      vmState.children = ['Headache', 'Chest Pain', 'Nausea', 'Vomiting', 'Myalgia', 'Test Child'];

      // Execute save
      await vmState.save();

      print('Toast messages: $toastMessages');

      // Verify error message
      expect(toastMessages.any((msg) => msg.contains('Cannot add "Test Child": Parent already has 5 children')), isTrue);

      // Verify UI state is not updated (should still show 5 children)
      expect(vmState.children.length, equals(5), reason: 'UI should still show 5 children after failed save');
      expect(vmState.children.contains('Test Child'), isFalse, reason: 'UI should not contain the failed child');
    });
  });
}
