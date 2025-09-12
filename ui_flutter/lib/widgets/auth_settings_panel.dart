"""
Authentication settings panel for managing auth tokens and concurrency.

Provides UI for configuring authentication tokens and handling
concurrent edit scenarios.
"""

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class AuthSettingsPanel extends StatefulWidget {
  final String apiBaseUrl;
  final Function(String)? onTokenChanged;

  const AuthSettingsPanel({
    Key? key,
    required this.apiBaseUrl,
    this.onTokenChanged,
  }) : super(key: key);

  @override
  State<AuthSettingsPanel> createState() => _AuthSettingsPanelState();
}

class _AuthSettingsPanelState extends State<AuthSettingsPanel> {
  final _tokenController = TextEditingController();
  bool _isLoading = false;
  bool _authEnabled = false;
  String? _error;
  String? _success;

  @override
  void initState() {
    super.initState();
    _loadAuthSettings();
  }

  Future<void> _loadAuthSettings() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final prefs = await SharedPreferences.getInstance();
      final savedToken = prefs.getString('auth_token');
      
      if (savedToken != null) {
        _tokenController.text = savedToken;
        _authEnabled = true;
      }

      // Check if auth is enabled on the backend
      final response = await http.get(
        Uri.parse('${widget.apiBaseUrl}/api/v1/concurrency/conflict-resolution-info'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        setState(() {
          _authEnabled = true;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error loading auth settings: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _saveToken() async {
    if (_tokenController.text.trim().isEmpty) {
      setState(() {
        _error = 'Token cannot be empty';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _error = null;
      _success = null;
    });

    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth_token', _tokenController.text.trim());
      
      setState(() {
        _authEnabled = true;
        _success = 'Authentication token saved successfully';
      });

      // Notify parent widget
      if (widget.onTokenChanged != null) {
        widget.onTokenChanged!(_tokenController.text.trim());
      }
    } catch (e) {
      setState(() {
        _error = 'Error saving token: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _clearToken() async {
    setState(() {
      _isLoading = true;
      _error = null;
      _success = null;
    });

    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('auth_token');
      
      setState(() {
        _tokenController.clear();
        _authEnabled = false;
        _success = 'Authentication token cleared';
      });

      // Notify parent widget
      if (widget.onTokenChanged != null) {
        widget.onTokenChanged!('');
      }
    } catch (e) {
      setState(() {
        _error = 'Error clearing token: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _testToken() async {
    if (_tokenController.text.trim().isEmpty) {
      setState(() {
        _error = 'Please enter a token to test';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _error = null;
      _success = null;
    });

    try {
      final response = await http.get(
        Uri.parse('${widget.apiBaseUrl}/api/v1/concurrency/conflict-resolution-info'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${_tokenController.text.trim()}',
        },
      );

      if (response.statusCode == 200) {
        setState(() {
          _success = 'Token is valid and working';
        });
      } else if (response.statusCode == 401) {
        setState(() {
          _error = 'Token is invalid or expired';
        });
      } else {
        setState(() {
          _error = 'Unexpected response: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Error testing token: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(8.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Authentication & Concurrency',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            
            if (_isLoading)
              const Center(child: CircularProgressIndicator())
            else
              _buildAuthContent(),
          ],
        ),
      ),
    );
  }

  Widget _buildAuthContent() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Auth status
        _buildAuthStatus(),
        
        const SizedBox(height: 16),
        
        // Token input
        _buildTokenInput(),
        
        const SizedBox(height: 16),
        
        // Action buttons
        _buildActionButtons(),
        
        const SizedBox(height: 16),
        
        // Concurrency info
        _buildConcurrencyInfo(),
      ],
    );
  }

  Widget _buildAuthStatus() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: _authEnabled ? Colors.green.withOpacity(0.1) : Colors.orange.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: _authEnabled ? Colors.green : Colors.orange,
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Icon(
            _authEnabled ? Icons.lock : Icons.lock_open,
            color: _authEnabled ? Colors.green : Colors.orange,
            size: 20,
          ),
          const SizedBox(width: 8),
          Text(
            _authEnabled ? 'Authentication Enabled' : 'Authentication Disabled',
            style: TextStyle(
              fontWeight: FontWeight.w600,
              color: _authEnabled ? Colors.green : Colors.orange,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTokenInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Authentication Token',
          style: TextStyle(fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: _tokenController,
          decoration: const InputDecoration(
            hintText: 'Enter your authentication token',
            border: OutlineInputBorder(),
            prefixIcon: Icon(Icons.key),
          ),
          obscureText: true,
          enabled: !_isLoading,
        ),
        const SizedBox(height: 4),
        const Text(
          'Optional: Set AUTH_TOKEN environment variable on the backend to enable authentication for write operations.',
          style: TextStyle(fontSize: 12, color: Colors.grey),
        ),
      ],
    );
  }

  Widget _buildActionButtons() {
    return Row(
      children: [
        ElevatedButton.icon(
          onPressed: _isLoading ? null : _saveToken,
          icon: _isLoading 
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.save),
          label: const Text('Save Token'),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.blue,
            foregroundColor: Colors.white,
          ),
        ),
        const SizedBox(width: 8),
        ElevatedButton.icon(
          onPressed: _isLoading ? null : _testToken,
          icon: const Icon(Icons.check),
          label: const Text('Test Token'),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.green,
            foregroundColor: Colors.white,
          ),
        ),
        const SizedBox(width: 8),
        ElevatedButton.icon(
          onPressed: _isLoading ? null : _clearToken,
          icon: const Icon(Icons.clear),
          label: const Text('Clear'),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.red,
            foregroundColor: Colors.white,
          ),
        ),
      ],
    );
  }

  Widget _buildConcurrencyInfo() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blue.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.info, color: Colors.blue, size: 20),
              SizedBox(width: 8),
              Text(
                'Concurrency Control',
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: Colors.blue,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          const Text(
            'The system supports optimistic concurrency control:',
            style: TextStyle(fontSize: 12),
          ),
          const SizedBox(height: 4),
          const Text(
            '• 412 Precondition Failed: Data modified by another user',
            style: TextStyle(fontSize: 12),
          ),
          const Text(
            '• 409 Conflict: Slot already occupied',
            style: TextStyle(fontSize: 12),
          ),
          const Text(
            '• Use If-Match header for version checking',
            style: TextStyle(fontSize: 12),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _tokenController.dispose();
    super.dispose();
  }
}
