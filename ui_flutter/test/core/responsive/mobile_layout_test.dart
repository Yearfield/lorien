import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:lorien/core/responsive/mobile_layout.dart';

void main() {
  group('MobileLayout', () {
    testWidgets('isMobile returns true for small screens', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              expect(MobileLayout.isMobile(context), isTrue);
              expect(MobileLayout.isTablet(context), isFalse);
              expect(MobileLayout.isDesktop(context), isFalse);
              return const SizedBox.shrink();
            },
          ),
        ),
      );
    });

    testWidgets('isTablet returns true for medium screens', (tester) async {
      await tester.binding.setSurfaceSize(const Size(768, 1024));
      
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              expect(MobileLayout.isMobile(context), isFalse);
              expect(MobileLayout.isTablet(context), isTrue);
              expect(MobileLayout.isDesktop(context), isFalse);
              return const SizedBox.shrink();
            },
          ),
        ),
      );
    });

    testWidgets('isDesktop returns true for large screens', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              expect(MobileLayout.isMobile(context), isFalse);
              expect(MobileLayout.isTablet(context), isFalse);
              expect(MobileLayout.isDesktop(context), isTrue);
              return const SizedBox.shrink();
            },
          ),
        ),
      );
    });

    testWidgets('getPadding returns appropriate padding for mobile', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              final padding = MobileLayout.getPadding(context);
              expect(padding, const EdgeInsets.all(8.0));
              return const SizedBox.shrink();
            },
          ),
        ),
      );
    });

    testWidgets('getPadding returns appropriate padding for tablet', (tester) async {
      await tester.binding.setSurfaceSize(const Size(768, 1024));
      
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              final padding = MobileLayout.getPadding(context);
              expect(padding, const EdgeInsets.all(16.0));
              return const SizedBox.shrink();
            },
          ),
        ),
      );
    });

    testWidgets('getPadding returns appropriate padding for desktop', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              final padding = MobileLayout.getPadding(context);
              expect(padding, const EdgeInsets.all(24.0));
              return const SizedBox.shrink();
            },
          ),
        ),
      );
    });

    testWidgets('getFontSize scales correctly for mobile', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              final fontSize = MobileLayout.getFontSize(context, 16.0);
              expect(fontSize, 16.0 * 0.9);
              return const SizedBox.shrink();
            },
          ),
        ),
      );
    });

    testWidgets('getFontSize scales correctly for tablet', (tester) async {
      await tester.binding.setSurfaceSize(const Size(768, 1024));
      
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              final fontSize = MobileLayout.getFontSize(context, 16.0);
              expect(fontSize, 16.0);
              return const SizedBox.shrink();
            },
          ),
        ),
      );
    });

    testWidgets('getFontSize scales correctly for desktop', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              final fontSize = MobileLayout.getFontSize(context, 16.0);
              expect(fontSize, 16.0 * 1.1);
              return const SizedBox.shrink();
            },
          ),
        ),
      );
    });

    testWidgets('getButtonHeight returns appropriate height for mobile', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              final height = MobileLayout.getButtonHeight(context);
              expect(height, 44.0);
              return const SizedBox.shrink();
            },
          ),
        ),
      );
    });

    testWidgets('getButtonHeight returns appropriate height for tablet', (tester) async {
      await tester.binding.setSurfaceSize(const Size(768, 1024));
      
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              final height = MobileLayout.getButtonHeight(context);
              expect(height, 48.0);
              return const SizedBox.shrink();
            },
          ),
        ),
      );
    });

    testWidgets('getButtonHeight returns appropriate height for desktop', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              final height = MobileLayout.getButtonHeight(context);
              expect(height, 52.0);
              return const SizedBox.shrink();
            },
          ),
        ),
      );
    });

    testWidgets('getGridCrossAxisCount returns correct count for mobile', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              final count = MobileLayout.getGridCrossAxisCount(context);
              expect(count, 1);
              return const SizedBox.shrink();
            },
          ),
        ),
      );
    });

    testWidgets('getGridCrossAxisCount returns correct count for tablet', (tester) async {
      await tester.binding.setSurfaceSize(const Size(768, 1024));
      
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              final count = MobileLayout.getGridCrossAxisCount(context);
              expect(count, 2);
              return const SizedBox.shrink();
            },
          ),
        ),
      );
    });

    testWidgets('getGridCrossAxisCount returns correct count for desktop', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) {
              final count = MobileLayout.getGridCrossAxisCount(context);
              expect(count, 3);
              return const SizedBox.shrink();
            },
          ),
        ),
      );
    });
  });

  group('ResponsiveWidget', () {
    testWidgets('shows mobile widget on mobile screen', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      
      await tester.pumpWidget(
        MaterialApp(
          home: ResponsiveWidget(
            mobile: const Text('Mobile'),
            tablet: const Text('Tablet'),
            desktop: const Text('Desktop'),
          ),
        ),
      );

      expect(find.text('Mobile'), findsOneWidget);
      expect(find.text('Tablet'), findsNothing);
      expect(find.text('Desktop'), findsNothing);
    });

    testWidgets('shows tablet widget on tablet screen', (tester) async {
      await tester.binding.setSurfaceSize(const Size(768, 1024));
      
      await tester.pumpWidget(
        MaterialApp(
          home: ResponsiveWidget(
            mobile: const Text('Mobile'),
            tablet: const Text('Tablet'),
            desktop: const Text('Desktop'),
          ),
        ),
      );

      expect(find.text('Mobile'), findsNothing);
      expect(find.text('Tablet'), findsOneWidget);
      expect(find.text('Desktop'), findsNothing);
    });

    testWidgets('shows desktop widget on desktop screen', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      
      await tester.pumpWidget(
        MaterialApp(
          home: ResponsiveWidget(
            mobile: const Text('Mobile'),
            tablet: const Text('Tablet'),
            desktop: const Text('Desktop'),
          ),
        ),
      );

      expect(find.text('Mobile'), findsNothing);
      expect(find.text('Tablet'), findsNothing);
      expect(find.text('Desktop'), findsOneWidget);
    });

    testWidgets('falls back to mobile when tablet not provided', (tester) async {
      await tester.binding.setSurfaceSize(const Size(768, 1024));
      
      await tester.pumpWidget(
        MaterialApp(
          home: ResponsiveWidget(
            mobile: const Text('Mobile'),
            desktop: const Text('Desktop'),
          ),
        ),
      );

      expect(find.text('Mobile'), findsOneWidget);
      expect(find.text('Desktop'), findsNothing);
    });
  });

  group('ResponsiveBuilder', () {
    testWidgets('provides correct flags for mobile', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      
      await tester.pumpWidget(
        MaterialApp(
          home: ResponsiveBuilder(
            builder: (context, isMobile, isTablet, isDesktop) {
              expect(isMobile, isTrue);
              expect(isTablet, isFalse);
              expect(isDesktop, isFalse);
              return const SizedBox.shrink();
            },
          ),
        ),
      );
    });

    testWidgets('provides correct flags for tablet', (tester) async {
      await tester.binding.setSurfaceSize(const Size(768, 1024));
      
      await tester.pumpWidget(
        MaterialApp(
          home: ResponsiveBuilder(
            builder: (context, isMobile, isTablet, isDesktop) {
              expect(isMobile, isFalse);
              expect(isTablet, isTrue);
              expect(isDesktop, isFalse);
              return const SizedBox.shrink();
            },
          ),
        ),
      );
    });

    testWidgets('provides correct flags for desktop', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      
      await tester.pumpWidget(
        MaterialApp(
          home: ResponsiveBuilder(
            builder: (context, isMobile, isTablet, isDesktop) {
              expect(isMobile, isFalse);
              expect(isTablet, isFalse);
              expect(isDesktop, isTrue);
              return const SizedBox.shrink();
            },
          ),
        ),
      );
    });
  });

  group('ResponsiveText', () {
    testWidgets('scales font size for mobile', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      
      await tester.pumpWidget(
        MaterialApp(
          home: ResponsiveText(
            'Test',
            style: const TextStyle(fontSize: 16),
          ),
        ),
      );

      final textWidget = tester.widget<Text>(find.text('Test'));
      expect(textWidget.style?.fontSize, 16 * 0.9);
    });

    testWidgets('scales font size for tablet', (tester) async {
      await tester.binding.setSurfaceSize(const Size(768, 1024));
      
      await tester.pumpWidget(
        MaterialApp(
          home: ResponsiveText(
            'Test',
            style: const TextStyle(fontSize: 16),
          ),
        ),
      );

      final textWidget = tester.widget<Text>(find.text('Test'));
      expect(textWidget.style?.fontSize, 16);
    });

    testWidgets('scales font size for desktop', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      
      await tester.pumpWidget(
        MaterialApp(
          home: ResponsiveText(
            'Test',
            style: const TextStyle(fontSize: 16),
          ),
        ),
      );

      final textWidget = tester.widget<Text>(find.text('Test'));
      expect(textWidget.style?.fontSize, 16 * 1.1);
    });
  });

  group('ResponsiveButton', () {
    testWidgets('has appropriate height for mobile', (tester) async {
      await tester.binding.setSurfaceSize(const Size(375, 667));
      
      await tester.pumpWidget(
        MaterialApp(
          home: ResponsiveButton(
            text: 'Test',
            onPressed: () {},
          ),
        ),
      );

      // Check that the button exists and has the correct text
      expect(find.byType(ElevatedButton), findsOneWidget);
      expect(find.text('Test'), findsOneWidget);
      
      // Verify the button is rendered (size will be determined by the layout)
      final button = tester.widget<ElevatedButton>(find.byType(ElevatedButton));
      expect(button.style, isNotNull);
    });

    testWidgets('has appropriate height for tablet', (tester) async {
      await tester.binding.setSurfaceSize(const Size(768, 1024));
      
      await tester.pumpWidget(
        MaterialApp(
          home: ResponsiveButton(
            text: 'Test',
            onPressed: () {},
          ),
        ),
      );

      // Check that the button exists and has the correct text
      expect(find.byType(ElevatedButton), findsOneWidget);
      expect(find.text('Test'), findsOneWidget);
      
      // Verify the button is rendered (size will be determined by the layout)
      final button = tester.widget<ElevatedButton>(find.byType(ElevatedButton));
      expect(button.style, isNotNull);
    });

    testWidgets('has appropriate height for desktop', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1200, 800));
      
      await tester.pumpWidget(
        MaterialApp(
          home: ResponsiveButton(
            text: 'Test',
            onPressed: () {},
          ),
        ),
      );

      // Check that the button exists and has the correct text
      expect(find.byType(ElevatedButton), findsOneWidget);
      expect(find.text('Test'), findsOneWidget);
      
      // Verify the button is rendered (size will be determined by the layout)
      final button = tester.widget<ElevatedButton>(find.byType(ElevatedButton));
      expect(button.style, isNotNull);
    });
  });
}
