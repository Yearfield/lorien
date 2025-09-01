import 'package:flutter/material.dart';
import 'package:dio/dio.dart';

class ChainedCalculator extends StatefulWidget {
  const ChainedCalculator(
      {super.key, required this.baseUrl, required this.dio});
  final String baseUrl;
  final Dio dio;
  @override
  State<ChainedCalculator> createState() => _ChainedCalculatorState();
}

class _ChainedCalculatorState extends State<ChainedCalculator> {
  String? root, n1, n2, n3, n4, n5;
  int remainingLeaves = 0;
  List<String> optsRoot = [],
      opts1 = [],
      opts2 = [],
      opts3 = [],
      opts4 = [],
      opts5 = [];
  bool loading = false;

  @override
  void initState() {
    super.initState();
    _loadRoot();
  }

  Future<void> _loadRoot() async {
    setState(() => loading = true);
    final r = await widget.dio
        .get('${widget.baseUrl}/calc/options', queryParameters: {});
    setState(() {
      optsRoot = List<String>.from(r.data['roots'] ?? []);
      loading = false;
    });
  }

  Future<void> _loadNext({required int depth}) async {
    setState(() => loading = true);
    final r = await widget.dio.get('${widget.baseUrl}/calc/options',
        queryParameters: {
          'root': root,
          'n1': n1,
          'n2': n2,
          'n3': n3,
          'n4': n4
        });
    final d = r.data as Map<String, dynamic>;
    setState(() {
      remainingLeaves = d['remaining'] ?? (d['leaves']?.length ?? 0);
      opts1 = List<String>.from(d['n1'] ?? opts1);
      opts2 = List<String>.from(d['n2'] ?? opts2);
      opts3 = List<String>.from(d['n3'] ?? opts3);
      opts4 = List<String>.from(d['n4'] ?? opts4);
      opts5 = List<String>.from(d['n5'] ?? opts5);
      loading = false;
    });
  }

  void _resetFrom(int depth) {
    if (depth <= 1) {
      n1 = null;
      opts1 = [];
    }
    if (depth <= 2) {
      n2 = null;
      opts2 = [];
    }
    if (depth <= 3) {
      n3 = null;
      opts3 = [];
    }
    if (depth <= 4) {
      n4 = null;
      opts4 = [];
    }
    if (depth <= 5) {
      n5 = null;
      opts5 = [];
    }
    remainingLeaves = 0;
  }

  Widget _dd(String? val, List<String> opts, void Function(String?) onChanged,
      String hint) {
    return DropdownButton<String>(
      value: val,
      hint: Text(hint),
      items:
          opts.map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(),
      onChanged: (v) {
        onChanged(v);
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(12),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        _dd(root, optsRoot, (v) {
          setState(() => root = v);
          _resetFrom(1);
          _loadNext(depth: 1);
        }, 'Vital Measurement'),
        _dd(n1, opts1, (v) {
          setState(() => n1 = v);
          _resetFrom(2);
          _loadNext(depth: 2);
        }, 'Node 1'),
        _dd(n2, opts2, (v) {
          setState(() => n2 = v);
          _resetFrom(3);
          _loadNext(depth: 3);
        }, 'Node 2'),
        _dd(n3, opts3, (v) {
          setState(() => n3 = v);
          _resetFrom(4);
          _loadNext(depth: 4);
        }, 'Node 3'),
        _dd(n4, opts4, (v) {
          setState(() => n4 = v);
          _resetFrom(5);
          _loadNext(depth: 5);
        }, 'Node 4'),
        _dd(n5, opts5, (v) {
          setState(() => n5 = v);
          _loadNext(depth: 6);
        }, 'Node 5'),
        const SizedBox(height: 8),
        Text('Remaining leaf options: $remainingLeaves'),
        if (loading)
          const Padding(
              padding: EdgeInsets.all(8), child: CircularProgressIndicator()),
      ]),
    );
  }
}
