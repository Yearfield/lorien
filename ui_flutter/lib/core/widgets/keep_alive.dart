import 'package:flutter/widgets.dart';

class KeepAlive extends StatefulWidget {
  final Widget child;
  const KeepAlive({super.key, required this.child});
  
  @override
  State<KeepAlive> createState() => _KeepAliveState();
}

class _KeepAliveState extends State<KeepAlive> with AutomaticKeepAliveClientMixin {
  @override
  bool get wantKeepAlive => true;
  
  @override
  Widget build(BuildContext context) {
    super.build(context);
    return widget.child;
  }
}
