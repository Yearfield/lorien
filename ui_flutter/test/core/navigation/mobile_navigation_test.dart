import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/core/navigation/mobile_navigation.dart';

void main() {
  group('MobileNavigation', () {
    testWidgets('createBottomNavBar creates correct navigation bar', (tester) async {
      final items = [
        const BottomNavItem(
          icon: Icons.home,
          label: 'Home',
          route: '/',
        ),
        const BottomNavItem(
          icon: Icons.settings,
          label: 'Settings',
          route: '/settings',
        ),
      ];

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            bottomNavigationBar: MobileNavigation.createBottomNavBar(
              currentIndex: 0,
              items: items,
              onTap: (index) {},
            ),
          ),
        ),
      );

      expect(find.byType(BottomNavigationBar), findsOneWidget);
      expect(find.text('Home'), findsOneWidget);
      expect(find.text('Settings'), findsOneWidget);
    });

    testWidgets('createDrawer creates correct drawer', (tester) async {
      final items = [
        const DrawerItem(
          icon: Icons.home,
          label: 'Home',
          route: '/',
        ),
        const DrawerItem(
          icon: Icons.settings,
          label: 'Settings',
          route: '/settings',
        ),
      ];

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            drawer: MobileNavigation.createDrawer(
              items: items,
              currentRoute: '/',
              onTap: (route) {},
            ),
          ),
        ),
      );

      expect(find.byType(Drawer), findsOneWidget);
      expect(find.text('Lorien'), findsOneWidget);
      expect(find.text('Home'), findsOneWidget);
      expect(find.text('Settings'), findsOneWidget);
    });

    testWidgets('createAppBar creates correct app bar', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            appBar: MobileNavigation.createAppBar(
              title: 'Test Title',
              actions: [const Icon(Icons.more_vert)],
            ),
          ),
        ),
      );

      expect(find.byType(AppBar), findsOneWidget);
      expect(find.text('Test Title'), findsOneWidget);
      expect(find.byIcon(Icons.more_vert), findsOneWidget);
    });

    testWidgets('createFAB creates correct floating action button', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            floatingActionButton: MobileNavigation.createFAB(
              onPressed: () {},
              icon: Icons.add,
              tooltip: 'Add',
            ),
          ),
        ),
      );

      expect(find.byType(FloatingActionButton), findsOneWidget);
      expect(find.byIcon(Icons.add), findsOneWidget);
    });

    testWidgets('createTabBar creates correct tab bar', (tester) async {
      final tabs = [
        const TabItem(icon: Icons.home, label: 'Home'),
        const TabItem(icon: Icons.settings, label: 'Settings'),
      ];

      await tester.pumpWidget(
        MaterialApp(
          home: DefaultTabController(
            length: 2,
            child: Scaffold(
              appBar: AppBar(
                bottom: MobileNavigation.createTabBar(
                  tabs: tabs,
                  controller: DefaultTabController.of(tester.element(find.byType(DefaultTabController))).controller,
                ),
              ),
            ),
          ),
        ),
      );

      expect(find.byType(TabBar), findsOneWidget);
      expect(find.text('Home'), findsOneWidget);
      expect(find.text('Settings'), findsOneWidget);
    });
  });

  group('MobileScaffold', () {
    testWidgets('creates correct scaffold structure', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: MobileScaffold(
            title: 'Test Title',
            body: const Text('Test Body'),
          ),
        ),
      );

      expect(find.byType(Scaffold), findsOneWidget);
      expect(find.byType(AppBar), findsOneWidget);
      expect(find.text('Test Title'), findsOneWidget);
      expect(find.text('Test Body'), findsOneWidget);
    });

    testWidgets('includes floating action button when provided', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: MobileScaffold(
            title: 'Test Title',
            body: const Text('Test Body'),
            floatingActionButton: const FloatingActionButton(
              onPressed: null,
              child: Icon(Icons.add),
            ),
          ),
        ),
      );

      expect(find.byType(FloatingActionButton), findsOneWidget);
    });

    testWidgets('includes drawer when provided', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: MobileScaffold(
            title: 'Test Title',
            body: const Text('Test Body'),
            drawer: const Drawer(child: Text('Drawer Content')),
          ),
        ),
      );

      expect(find.byType(Drawer), findsOneWidget);
    });

    testWidgets('includes bottom navigation bar when provided', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: MobileScaffold(
            title: 'Test Title',
            body: const Text('Test Body'),
            bottomNavigationBar: const BottomNavigationBar(
              items: [
                BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
              ],
            ),
          ),
        ),
      );

      expect(find.byType(BottomNavigationBar), findsOneWidget);
    });
  });

  group('MobilePage', () {
    testWidgets('creates correct page structure', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: MobilePage(
            title: 'Test Title',
            child: const Text('Test Content'),
          ),
        ),
      );

      expect(find.byType(Scaffold), findsOneWidget);
      expect(find.byType(AppBar), findsOneWidget);
      expect(find.text('Test Title'), findsOneWidget);
      expect(find.text('Test Content'), findsOneWidget);
    });
  });

  group('MobileListTile', () {
    testWidgets('creates correct list tile', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MobileListTile(
              title: 'Test Title',
              subtitle: 'Test Subtitle',
              leading: Icons.home,
              trailing: const Icon(Icons.arrow_forward),
              onTap: () {},
            ),
          ),
        ),
      );

      expect(find.byType(ListTile), findsOneWidget);
      expect(find.text('Test Title'), findsOneWidget);
      expect(find.text('Test Subtitle'), findsOneWidget);
      expect(find.byIcon(Icons.home), findsOneWidget);
      expect(find.byIcon(Icons.arrow_forward), findsOneWidget);
    });

    testWidgets('handles tap correctly', (tester) async {
      bool tapped = false;
      
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MobileListTile(
              title: 'Test Title',
              onTap: () => tapped = true,
            ),
          ),
        ),
      );

      await tester.tap(find.byType(ListTile));
      expect(tapped, isTrue);
    });

    testWidgets('respects enabled state', (tester) async {
      bool tapped = false;
      
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MobileListTile(
              title: 'Test Title',
              enabled: false,
              onTap: () => tapped = true,
            ),
          ),
        ),
      );

      await tester.tap(find.byType(ListTile));
      expect(tapped, isFalse);
    });
  });

  group('MobileDialog', () {
    testWidgets('creates correct dialog', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () => showDialog(
                  context: context,
                  builder: (context) => MobileDialog(
                    title: 'Test Title',
                    content: const Text('Test Content'),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(),
                        child: const Text('OK'),
                      ),
                    ],
                  ),
                ),
                child: const Text('Show Dialog'),
              ),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Show Dialog'));
      await tester.pumpAndSettle();

      expect(find.byType(AlertDialog), findsOneWidget);
      expect(find.text('Test Title'), findsOneWidget);
      expect(find.text('Test Content'), findsOneWidget);
      expect(find.text('OK'), findsOneWidget);
    });

    testWidgets('handles scrollable content', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () => showDialog(
                  context: context,
                  builder: (context) => MobileDialog(
                    title: 'Test Title',
                    content: const Column(
                      children: List.generate(20, (i) => Text('Item $i')),
                    ),
                    scrollable: true,
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(),
                        child: const Text('OK'),
                      ),
                    ],
                  ),
                ),
                child: const Text('Show Dialog'),
              ),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Show Dialog'));
      await tester.pumpAndSettle();

      expect(find.byType(AlertDialog), findsOneWidget);
      expect(find.byType(SingleChildScrollView), findsOneWidget);
    });
  });

  group('MobileSnackBar', () {
    testWidgets('show displays snackbar', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () => MobileSnackBar.show(context, 'Test Message'),
                child: const Text('Show SnackBar'),
              ),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Show SnackBar'));
      await tester.pumpAndSettle();

      expect(find.byType(SnackBar), findsOneWidget);
      expect(find.text('Test Message'), findsOneWidget);
    });

    testWidgets('showSuccess displays success snackbar', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () => MobileSnackBar.showSuccess(context, 'Success Message'),
                child: const Text('Show Success'),
              ),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Show Success'));
      await tester.pumpAndSettle();

      expect(find.byType(SnackBar), findsOneWidget);
      expect(find.text('Success Message'), findsOneWidget);
    });

    testWidgets('showError displays error snackbar', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () => MobileSnackBar.showError(context, 'Error Message'),
                child: const Text('Show Error'),
              ),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Show Error'));
      await tester.pumpAndSettle();

      expect(find.byType(SnackBar), findsOneWidget);
      expect(find.text('Error Message'), findsOneWidget);
    });

    testWidgets('showInfo displays info snackbar', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () => MobileSnackBar.showInfo(context, 'Info Message'),
                child: const Text('Show Info'),
              ),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Show Info'));
      await tester.pumpAndSettle();

      expect(find.byType(SnackBar), findsOneWidget);
      expect(find.text('Info Message'), findsOneWidget);
    });
  });
}
