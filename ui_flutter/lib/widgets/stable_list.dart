import 'package:flutter/material.dart';

class StableList extends StatelessWidget {
  final int itemCount;
  final IndexedWidgetBuilder itemBuilder;
  final EdgeInsetsGeometry? padding;
  final Key? storageKey;
  
  const StableList({
    super.key,
    required this.itemCount,
    required this.itemBuilder,
    this.padding,
    this.storageKey,
  });
  
  @override
  Widget build(BuildContext context) {
    return RepaintBoundary(
      child: ListView.builder(
        key: storageKey ?? const PageStorageKey('stable_list'),
        padding: padding,
        addAutomaticKeepAlives: true,
        addRepaintBoundaries: true,
        cacheExtent: 1200,
        itemCount: itemCount,
        itemBuilder: itemBuilder,
      ),
    );
  }
}
