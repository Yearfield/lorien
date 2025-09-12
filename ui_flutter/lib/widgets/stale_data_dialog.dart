"""
Dialog for handling stale data scenarios in concurrent editing.

Shows when a 412 Precondition Failed response is received,
indicating that data has been modified by another user.
"""

import 'package:flutter/material.dart';

class StaleDataDialog extends StatelessWidget {
  final String message;
  final VoidCallback onReload;
  final VoidCallback onDiscard;
  final VoidCallback? onRetry;

  const StaleDataDialog({
    Key? key,
    required this.message,
    required this.onReload,
    required this.onDiscard,
    this.onRetry,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Row(
        children: [
          Icon(Icons.warning, color: Colors.orange),
          SizedBox(width: 8),
          Text('Stale Data Detected'),
        ],
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(message),
          const SizedBox(height: 16),
          const Text(
            'What would you like to do?',
            style: TextStyle(fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 8),
          const Text(
            '• Reload: Get the latest data and retry your changes',
            style: TextStyle(fontSize: 12),
          ),
          const Text(
            '• Discard: Cancel your changes and keep current data',
            style: TextStyle(fontSize: 12),
          ),
          if (onRetry != null) ...[
            const Text(
              '• Retry: Attempt the operation again with current version',
              style: TextStyle(fontSize: 12),
            ),
          ],
        ],
      ),
      actions: [
        TextButton(
          onPressed: () {
            Navigator.of(context).pop();
            onDiscard();
          },
          child: const Text('Discard'),
        ),
        if (onRetry != null)
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              onRetry!();
            },
            child: const Text('Retry'),
          ),
        ElevatedButton(
          onPressed: () {
            Navigator.of(context).pop();
            onReload();
          },
          child: const Text('Reload'),
        ),
      ],
    );
  }

  static Future<void> show(
    BuildContext context, {
    required String message,
    required VoidCallback onReload,
    required VoidCallback onDiscard,
    VoidCallback? onRetry,
  }) {
    return showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => StaleDataDialog(
        message: message,
        onReload: onReload,
        onDiscard: onDiscard,
        onRetry: onRetry,
      ),
    );
  }
}

class ConcurrencyErrorHandler {
  /// Handle 412 Precondition Failed responses
  static Future<void> handlePreconditionFailed(
    BuildContext context, {
    required String message,
    required VoidCallback onReload,
    required VoidCallback onDiscard,
    VoidCallback? onRetry,
  }) {
    return StaleDataDialog.show(
      context,
      message: message,
      onReload: onReload,
      onDiscard: onDiscard,
      onRetry: onRetry,
    );
  }

  /// Handle 409 Conflict responses
  static Future<void> handleConflict(
    BuildContext context, {
    required String message,
    required VoidCallback onResolve,
    required VoidCallback onCancel,
  }) {
    return showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.error, color: Colors.red),
            SizedBox(width: 8),
            Text('Conflict Detected'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(message),
            const SizedBox(height: 16),
            const Text(
              'This usually means a slot is already occupied. You can:',
              style: TextStyle(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            const Text(
              '• Choose a different slot',
              style: TextStyle(fontSize: 12),
            ),
            const Text(
              '• Resolve the slot conflict',
              style: TextStyle(fontSize: 12),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              onCancel();
            },
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              onResolve();
            },
            child: const Text('Resolve'),
          ),
        ],
      ),
    );
  }

  /// Handle 401 Unauthorized responses
  static Future<void> handleUnauthorized(
    BuildContext context, {
    required String message,
    required VoidCallback onConfigureAuth,
    required VoidCallback onCancel,
  }) {
    return showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.lock, color: Colors.orange),
            SizedBox(width: 8),
            Text('Authentication Required'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(message),
            const SizedBox(height: 16),
            const Text(
              'This operation requires authentication. You can:',
              style: TextStyle(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            const Text(
              '• Configure authentication token in settings',
              style: TextStyle(fontSize: 12),
            ),
            const Text(
              '• Contact administrator for access',
              style: TextStyle(fontSize: 12),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              onCancel();
            },
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              onConfigureAuth();
            },
            child: const Text('Configure Auth'),
          ),
        ],
      ),
    );
  }
}
