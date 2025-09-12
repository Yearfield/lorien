import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../responsive/mobile_layout.dart';

/// Mobile-specific navigation components
class MobileNavigation {
  /// Create a mobile-optimized bottom navigation bar
  static Widget createBottomNavBar({
    required int currentIndex,
    required List<BottomNavItem> items,
    required Function(int) onTap,
  }) {
    return BottomNavigationBar(
      currentIndex: currentIndex,
      onTap: onTap,
      type: BottomNavigationBarType.fixed,
      items: items.map((item) => BottomNavigationBarItem(
        icon: Icon(item.icon),
        activeIcon: Icon(item.activeIcon ?? item.icon),
        label: item.label,
      )).toList(),
    );
  }

  /// Create a mobile-optimized drawer
  static Widget createDrawer({
    required List<DrawerItem> items,
    required String? currentRoute,
    required Function(String) onTap,
  }) {
    return Drawer(
      child: Column(
        children: [
          // Header
          const DrawerHeader(
            decoration: BoxDecoration(
              color: Colors.blue,
            ),
            child: Center(
              child: Text(
                'Lorien',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          // Menu items
          Expanded(
            child: ListView.builder(
              itemCount: items.length,
              itemBuilder: (context, index) {
                final item = items[index];
                final isSelected = currentRoute == item.route;
                
                return ListTile(
                  leading: Icon(
                    item.icon,
                    color: isSelected ? Colors.blue : null,
                  ),
                  title: Text(
                    item.label,
                    style: TextStyle(
                      color: isSelected ? Colors.blue : null,
                      fontWeight: isSelected ? FontWeight.bold : null,
                    ),
                  ),
                  selected: isSelected,
                  onTap: () => onTap(item.route),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  /// Create a mobile-optimized app bar
  static PreferredSizeWidget createAppBar({
    required String title,
    List<Widget>? actions,
    bool showBackButton = true,
    bool centerTitle = true,
  }) {
    return AppBar(
      title: Text(title),
      centerTitle: centerTitle,
      actions: actions,
      automaticallyImplyLeading: showBackButton,
    );
  }

  /// Create a mobile-optimized floating action button
  static Widget createFAB({
    required VoidCallback onPressed,
    required IconData icon,
    String? tooltip,
    Color? backgroundColor,
    Color? foregroundColor,
  }) {
    return FloatingActionButton(
      onPressed: onPressed,
      tooltip: tooltip,
      backgroundColor: backgroundColor,
      foregroundColor: foregroundColor,
      child: Icon(icon),
    );
  }

  /// Create a mobile-optimized tab bar
  static Widget createTabBar({
    required List<TabItem> tabs,
    required TabController controller,
  }) {
    return TabBar(
      controller: controller,
      isScrollable: true,
      tabs: tabs.map((tab) => Tab(
        icon: tab.icon != null ? Icon(tab.icon) : null,
        text: tab.label,
      )).toList(),
    );
  }

  /// Create a mobile-optimized tab bar view
  static Widget createTabBarView({
    required List<Widget> children,
    required TabController controller,
  }) {
    return TabBarView(
      controller: controller,
      children: children,
    );
  }
}

/// Bottom navigation item model
class BottomNavItem {
  final IconData icon;
  final IconData? activeIcon;
  final String label;
  final String route;

  const BottomNavItem({
    required this.icon,
    this.activeIcon,
    required this.label,
    required this.route,
  });
}

/// Drawer item model
class DrawerItem {
  final IconData icon;
  final String label;
  final String route;

  const DrawerItem({
    required this.icon,
    required this.label,
    required this.route,
  });
}

/// Tab item model
class TabItem {
  final IconData? icon;
  final String label;

  const TabItem({
    this.icon,
    required this.label,
  });
}

/// Mobile-specific responsive scaffold
class MobileScaffold extends StatelessWidget {
  final String title;
  final Widget body;
  final List<Widget>? actions;
  final Widget? floatingActionButton;
  final Widget? drawer;
  final Widget? bottomNavigationBar;
  final bool showBackButton;
  final bool centerTitle;

  const MobileScaffold({
    super.key,
    required this.title,
    required this.body,
    this.actions,
    this.floatingActionButton,
    this.drawer,
    this.bottomNavigationBar,
    this.showBackButton = true,
    this.centerTitle = true,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: MobileNavigation.createAppBar(
        title: title,
        actions: actions,
        showBackButton: showBackButton,
        centerTitle: centerTitle,
      ),
      body: ResponsiveBuilder(
        builder: (context, isMobile, isTablet, isDesktop) {
          return Padding(
            padding: MobileLayout.getPadding(context),
            child: body,
          );
        },
      ),
      drawer: drawer,
      floatingActionButton: floatingActionButton,
      bottomNavigationBar: bottomNavigationBar,
    );
  }
}

/// Mobile-specific responsive page wrapper
class MobilePage extends StatelessWidget {
  final String title;
  final Widget child;
  final List<Widget>? actions;
  final Widget? floatingActionButton;
  final Widget? drawer;
  final Widget? bottomNavigationBar;
  final bool showBackButton;
  final bool centerTitle;

  const MobilePage({
    super.key,
    required this.title,
    required this.child,
    this.actions,
    this.floatingActionButton,
    this.drawer,
    this.bottomNavigationBar,
    this.showBackButton = true,
    this.centerTitle = true,
  });

  @override
  Widget build(BuildContext context) {
    return MobileScaffold(
      title: title,
      body: child,
      actions: actions,
      floatingActionButton: floatingActionButton,
      drawer: drawer,
      bottomNavigationBar: bottomNavigationBar,
      showBackButton: showBackButton,
      centerTitle: centerTitle,
    );
  }
}

/// Mobile-specific responsive list tile
class MobileListTile extends StatelessWidget {
  final String title;
  final String? subtitle;
  final IconData? leading;
  final Widget? trailing;
  final VoidCallback? onTap;
  final bool enabled;

  const MobileListTile({
    super.key,
    required this.title,
    this.subtitle,
    this.leading,
    this.trailing,
    this.onTap,
    this.enabled = true,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: leading != null ? Icon(leading) : null,
      title: ResponsiveText(
        title,
        style: Theme.of(context).textTheme.titleMedium,
      ),
      subtitle: subtitle != null
          ? ResponsiveText(
              subtitle!,
              style: Theme.of(context).textTheme.bodyMedium,
            )
          : null,
      trailing: trailing,
      onTap: enabled ? onTap : null,
      enabled: enabled,
    );
  }
}

/// Mobile-specific responsive dialog
class MobileDialog extends StatelessWidget {
  final String title;
  final Widget content;
  final List<Widget>? actions;
  final bool scrollable;

  const MobileDialog({
    super.key,
    required this.title,
    required this.content,
    this.actions,
    this.scrollable = false,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: ResponsiveText(
        title,
        style: Theme.of(context).textTheme.headlineSmall,
      ),
      content: scrollable
          ? SingleChildScrollView(child: content)
          : content,
      actions: actions,
    );
  }
}

/// Mobile-specific responsive snackbar
class MobileSnackBar {
  static void show(
    BuildContext context,
    String message, {
    Color? backgroundColor,
    Duration duration = const Duration(seconds: 3),
    SnackBarAction? action,
  }) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: ResponsiveText(
          message,
          style: const TextStyle(color: Colors.white),
        ),
        backgroundColor: backgroundColor,
        duration: duration,
        action: action,
      ),
    );
  }

  static void showSuccess(BuildContext context, String message) {
    show(
      context,
      message,
      backgroundColor: Colors.green,
    );
  }

  static void showError(BuildContext context, String message) {
    show(
      context,
      message,
      backgroundColor: Colors.red,
    );
  }

  static void showInfo(BuildContext context, String message) {
    show(
      context,
      message,
      backgroundColor: Colors.blue,
    );
  }
}
