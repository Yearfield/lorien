import 'package:flutter/material.dart';
import 'package:lorien/features/pathogens/models/pathogen_models.dart';

class PathogenList extends StatelessWidget {
  final List<Pathogen> pathogens;
  final Function(Pathogen) onPathogenTap;
  final String searchQuery;

  const PathogenList({
    super.key,
    required this.pathogens,
    required this.onPathogenTap,
    required this.searchQuery,
  });

  @override
  Widget build(BuildContext context) {
    if (pathogens.isEmpty) {
      return _buildEmptyState();
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: pathogens.length,
      itemBuilder: (context, index) {
        final pathogen = pathogens[index];
        return _buildPathogenCard(pathogen);
      },
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            searchQuery.isNotEmpty ? Icons.search_off : Icons.bug_report,
            size: 64,
            color: Colors.grey,
          ),
          const SizedBox(height: 16),
          Text(
            searchQuery.isNotEmpty
                ? 'No pathogens found matching "$searchQuery"'
                : 'No pathogens in database',
            style: const TextStyle(
              fontSize: 18,
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            searchQuery.isNotEmpty
                ? 'Try adjusting your search terms'
                : 'Import pathogen data to get started',
            style: const TextStyle(
              fontSize: 14,
              color: Colors.grey,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPathogenCard(Pathogen pathogen) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.red.shade100,
          child: Icon(
            Icons.bug_report,
            color: Colors.red.shade700,
          ),
        ),
        title: Text(
          pathogen.pathogenName,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (pathogen.classification != null) ...[
              const SizedBox(height: 4),
              Text(
                'Classification: ${pathogen.classification}',
                style: const TextStyle(fontSize: 12),
              ),
            ],
            if (pathogen.disease != null) ...[
              const SizedBox(height: 2),
              Text(
                'Disease: ${pathogen.disease}',
                style: const TextStyle(fontSize: 12),
              ),
            ],
            if (pathogen.transmission != null) ...[
              const SizedBox(height: 2),
              Text(
                'Transmission: ${pathogen.transmission}',
                style: const TextStyle(fontSize: 12),
              ),
            ],
            const SizedBox(height: 4),
            Row(
              children: [
                Icon(
                  Icons.access_time,
                  size: 12,
                  color: Colors.grey.shade600,
                ),
                const SizedBox(width: 4),
                Text(
                  _formatDate(pathogen.updatedAt),
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey.shade600,
                  ),
                ),
              ],
            ),
          ],
        ),
        trailing: const Icon(Icons.chevron_right),
        onTap: () => onPathogenTap(pathogen),
      ),
    );
  }

  String _formatDate(String dateString) {
    try {
      final date = DateTime.parse(dateString);
      final now = DateTime.now();
      final difference = now.difference(date);

      if (difference.inDays > 0) {
        return '${difference.inDays}d ago';
      } else if (difference.inHours > 0) {
        return '${difference.inHours}h ago';
      } else if (difference.inMinutes > 0) {
        return '${difference.inMinutes}m ago';
      } else {
        return 'Just now';
      }
    } catch (e) {
      return 'Unknown';
    }
  }
}
