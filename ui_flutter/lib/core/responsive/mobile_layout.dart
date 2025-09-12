import 'package:flutter/material.dart';

/// Mobile-specific layout utilities and breakpoints
class MobileLayout {
  static const double mobileBreakpoint = 600;
  static const double tabletBreakpoint = 900;
  static const double desktopBreakpoint = 1200;

  /// Check if current screen size is mobile
  static bool isMobile(BuildContext context) {
    return MediaQuery.of(context).size.width < mobileBreakpoint;
  }

  /// Check if current screen size is tablet
  static bool isTablet(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    return width >= mobileBreakpoint && width < tabletBreakpoint;
  }

  /// Check if current screen size is desktop
  static bool isDesktop(BuildContext context) {
    return MediaQuery.of(context).size.width >= desktopBreakpoint;
  }

  /// Get appropriate padding for current screen size
  static EdgeInsets getPadding(BuildContext context) {
    if (isMobile(context)) {
      return const EdgeInsets.all(8.0);
    } else if (isTablet(context)) {
      return const EdgeInsets.all(16.0);
    } else {
      return const EdgeInsets.all(24.0);
    }
  }

  /// Get appropriate margin for current screen size
  static EdgeInsets getMargin(BuildContext context) {
    if (isMobile(context)) {
      return const EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0);
    } else if (isTablet(context)) {
      return const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0);
    } else {
      return const EdgeInsets.symmetric(horizontal: 24.0, vertical: 12.0);
    }
  }

  /// Get appropriate font size for current screen size
  static double getFontSize(BuildContext context, double baseSize) {
    if (isMobile(context)) {
      return baseSize * 0.9;
    } else if (isTablet(context)) {
      return baseSize;
    } else {
      return baseSize * 1.1;
    }
  }

  /// Get appropriate icon size for current screen size
  static double getIconSize(BuildContext context, double baseSize) {
    if (isMobile(context)) {
      return baseSize * 0.8;
    } else if (isTablet(context)) {
      return baseSize;
    } else {
      return baseSize * 1.2;
    }
  }

  /// Get appropriate button height for current screen size
  static double getButtonHeight(BuildContext context) {
    if (isMobile(context)) {
      return 44.0; // iOS minimum touch target
    } else if (isTablet(context)) {
      return 48.0;
    } else {
      return 52.0;
    }
  }

  /// Get appropriate spacing between elements
  static double getSpacing(BuildContext context, double baseSpacing) {
    if (isMobile(context)) {
      return baseSpacing * 0.75;
    } else if (isTablet(context)) {
      return baseSpacing;
    } else {
      return baseSpacing * 1.25;
    }
  }

  /// Get appropriate grid cross axis count for current screen size
  static int getGridCrossAxisCount(BuildContext context, {int mobile = 1, int tablet = 2, int desktop = 3}) {
    if (isMobile(context)) {
      return mobile;
    } else if (isTablet(context)) {
      return tablet;
    } else {
      return desktop;
    }
  }

  /// Get appropriate card elevation for current screen size
  static double getCardElevation(BuildContext context) {
    if (isMobile(context)) {
      return 2.0;
    } else if (isTablet(context)) {
      return 4.0;
    } else {
      return 6.0;
    }
  }

  /// Get appropriate border radius for current screen size
  static double getBorderRadius(BuildContext context, double baseRadius) {
    if (isMobile(context)) {
      return baseRadius * 0.8;
    } else if (isTablet(context)) {
      return baseRadius;
    } else {
      return baseRadius * 1.2;
    }
  }
}

/// Mobile-specific responsive widget that adapts to screen size
class ResponsiveWidget extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget? desktop;

  const ResponsiveWidget({
    super.key,
    required this.mobile,
    this.tablet,
    this.desktop,
  });

  @override
  Widget build(BuildContext context) {
    if (MobileLayout.isDesktop(context) && desktop != null) {
      return desktop!;
    } else if (MobileLayout.isTablet(context) && tablet != null) {
      return tablet!;
    } else {
      return mobile;
    }
  }
}

/// Mobile-specific responsive builder
class ResponsiveBuilder extends StatelessWidget {
  final Widget Function(BuildContext context, bool isMobile, bool isTablet, bool isDesktop) builder;

  const ResponsiveBuilder({
    super.key,
    required this.builder,
  });

  @override
  Widget build(BuildContext context) {
    return builder(
      context,
      MobileLayout.isMobile(context),
      MobileLayout.isTablet(context),
      MobileLayout.isDesktop(context),
    );
  }
}

/// Mobile-specific responsive text widget
class ResponsiveText extends StatelessWidget {
  final String text;
  final TextStyle? style;
  final TextAlign? textAlign;
  final int? maxLines;
  final TextOverflow? overflow;

  const ResponsiveText(
    this.text, {
    super.key,
    this.style,
    this.textAlign,
    this.maxLines,
    this.overflow,
  });

  @override
  Widget build(BuildContext context) {
    final baseFontSize = style?.fontSize ?? 16.0;
    final responsiveFontSize = MobileLayout.getFontSize(context, baseFontSize);
    
    final responsiveStyle = style?.copyWith(
      fontSize: responsiveFontSize,
    );

    return Text(
      text,
      style: responsiveStyle,
      textAlign: textAlign,
      maxLines: maxLines,
      overflow: overflow,
    );
  }
}

/// Mobile-specific responsive button
class ResponsiveButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final ButtonStyle? style;
  final IconData? icon;
  final bool isFullWidth;

  const ResponsiveButton({
    super.key,
    required this.text,
    this.onPressed,
    this.style,
    this.icon,
    this.isFullWidth = false,
  });

  @override
  Widget build(BuildContext context) {
    final buttonHeight = MobileLayout.getButtonHeight(context);
    final fontSize = MobileLayout.getFontSize(context, 16.0);
    final padding = MobileLayout.getPadding(context);

    final buttonStyle = (style ?? ElevatedButton.styleFrom()).copyWith(
      minimumSize: MaterialStateProperty.all(
        Size(isFullWidth ? double.infinity : 0, buttonHeight),
      ),
      textStyle: MaterialStateProperty.all(
        TextStyle(fontSize: fontSize),
      ),
      padding: MaterialStateProperty.all(padding),
    );

    Widget button = ElevatedButton(
      onPressed: onPressed,
      style: buttonStyle,
      child: icon != null
          ? Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  icon,
                  size: MobileLayout.getIconSize(context, 20.0),
                ),
                const SizedBox(width: 8),
                Text(text),
              ],
            )
          : Text(text),
    );

    if (isFullWidth) {
      return SizedBox(
        width: double.infinity,
        child: button,
      );
    }

    return button;
  }
}

/// Mobile-specific responsive card
class ResponsiveCard extends StatelessWidget {
  final Widget child;
  final EdgeInsets? padding;
  final EdgeInsets? margin;
  final Color? color;
  final double? elevation;
  final BorderRadius? borderRadius;

  const ResponsiveCard({
    super.key,
    required this.child,
    this.padding,
    this.margin,
    this.color,
    this.elevation,
    this.borderRadius,
  });

  @override
  Widget build(BuildContext context) {
    final cardElevation = elevation ?? MobileLayout.getCardElevation(context);
    final cardPadding = padding ?? MobileLayout.getPadding(context);
    final cardMargin = margin ?? MobileLayout.getMargin(context);
    final cardBorderRadius = borderRadius ?? 
        BorderRadius.circular(MobileLayout.getBorderRadius(context, 8.0));

    return Card(
      elevation: cardElevation,
      margin: cardMargin,
      color: color,
      shape: RoundedRectangleBorder(
        borderRadius: cardBorderRadius,
      ),
      child: Padding(
        padding: cardPadding,
        child: child,
      ),
    );
  }
}

/// Mobile-specific responsive grid view
class ResponsiveGridView extends StatelessWidget {
  final List<Widget> children;
  final double? childAspectRatio;
  final double? crossAxisSpacing;
  final double? mainAxisSpacing;
  final int? mobileCrossAxisCount;
  final int? tabletCrossAxisCount;
  final int? desktopCrossAxisCount;

  const ResponsiveGridView({
    super.key,
    required this.children,
    this.childAspectRatio,
    this.crossAxisSpacing,
    this.mainAxisSpacing,
    this.mobileCrossAxisCount,
    this.tabletCrossAxisCount,
    this.desktopCrossAxisCount,
  });

  @override
  Widget build(BuildContext context) {
    final crossAxisCount = MobileLayout.getGridCrossAxisCount(
      context,
      mobile: mobileCrossAxisCount ?? 1,
      tablet: tabletCrossAxisCount ?? 2,
      desktop: desktopCrossAxisCount ?? 3,
    );

    final spacing = MobileLayout.getSpacing(context, 8.0);

    return GridView.builder(
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        childAspectRatio: childAspectRatio ?? 1.0,
        crossAxisSpacing: crossAxisSpacing ?? spacing,
        mainAxisSpacing: mainAxisSpacing ?? spacing,
      ),
      itemCount: children.length,
      itemBuilder: (context, index) => children[index],
    );
  }
}
