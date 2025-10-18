import 'package:flutter/material.dart';
import 'package:lorien/features/pathogens/models/pathogen_models.dart';

class PathogenStatsCard extends StatelessWidget {
  final PathogenStats stats;

  const PathogenStatsCard({
    super.key,
    required this.stats,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.analytics, color: Colors.blue),
                SizedBox(width: 8),
                Text(
                  'Database Statistics',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'Total Pathogens',
                    stats.totalPathogens.toString(),
                    Icons.bug_report,
                    Colors.red,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Total Associations',
                    stats.totalAssociations.toString(),
                    Icons.link,
                    Colors.blue,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'With Associations',
                    stats.pathogensWithAssociations.toString(),
                    Icons.check_circle,
                    Colors.green,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Avg. Associations',
                    stats.averageAssociationsPerPathogen.toStringAsFixed(1),
                    Icons.trending_up,
                    Colors.orange,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon, Color color) {
    return Column(
      children: [
        Icon(icon, size: 32, color: color),
        const SizedBox(height: 8),
        Text(
          value,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            color: Colors.grey,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}
