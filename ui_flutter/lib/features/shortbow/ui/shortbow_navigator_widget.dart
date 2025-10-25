import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../state/shortbow_notifier.dart';
import '../state/shortbow_state.dart';

class ShortBowNavigatorWidget extends ConsumerStatefulWidget {
  const ShortBowNavigatorWidget({super.key});

  @override
  ConsumerState<ShortBowNavigatorWidget> createState() => _ShortBowNavigatorWidgetState();
}

class _ShortBowNavigatorWidgetState extends ConsumerState<ShortBowNavigatorWidget> {
  String? _currentSymptomForNavigation;

  @override
  void initState() {
    super.initState();
    // Load initial data when widget is created
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(shortBowNotifierProvider.notifier).refresh().then((_) {
        // Start with top symptoms after data is loaded
        ref.read(shortBowNotifierProvider.notifier).startWithTopSymptoms();
      });
    });
  }


  @override
  Widget build(BuildContext context) {
    final shortBowState = ref.watch(shortBowNotifierProvider);
    final isLoading = ref.watch(shortBowLoadingProvider);
    final isNavigating = ref.watch(shortBowNavigatingProvider);
    final isCalculating = ref.watch(shortBowCalculatingProvider);
    final error = ref.watch(shortBowErrorProvider);


    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Icon(Icons.navigation, size: 24, color: Colors.blue[700]),
              const SizedBox(width: 8),
              const Text(
                'Symptom Navigator',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Instructions
          Card(
            color: Colors.blue[50],
            child: Padding(
              padding: const EdgeInsets.all(12.0),
              child: Row(
                children: [
                  Icon(Icons.info_outline, color: Colors.blue[700], size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Select any symptom from the dropdown below to start building a diagnostic path. Each selection will show related symptoms to continue the navigation.',
                      style: TextStyle(color: Colors.blue[800], fontSize: 14),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Selected symptoms chips
          if (shortBowState.selectedSymptoms.isNotEmpty) ...[
            const Text(
              'Selected Symptoms:',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: shortBowState.selectedSymptoms.map((symptom) {
                return Chip(
                  label: Text(symptom),
                  deleteIcon: const Icon(Icons.close, size: 18),
                  onDeleted: () {
                    ref.read(shortBowNotifierProvider.notifier).removeSymptom(symptom);
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 16),
          ],

          // Navigation section
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Navigate Symptoms',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 8),

                  // Interactive symptom calculator dropdown
                  Builder(
                    builder: (context) {
                      final items = _buildSymptomItems(shortBowState);
                      return DropdownButtonFormField<String>(
                        key: ValueKey('symptom_dropdown_${_currentSymptomForNavigation ?? 'initial'}_${items.length}_${shortBowState.selectedSymptoms.length}'),
                        value: null, // Always null to prevent assertion errors
                        decoration: InputDecoration(
                          labelText: _currentSymptomForNavigation == null
                              ? 'Select a symptom to start navigation'
                              : 'Select a symptom linked to "$_currentSymptomForNavigation"',
                          border: const OutlineInputBorder(),
                          helperText: _currentSymptomForNavigation == null
                              ? 'Choose from all available symptoms to start navigation'
                              : 'Choose from symptoms most strongly linked to your selection',
                        ),
                        items: items,
                        onChanged: isLoading || isNavigating ? null : (value) {
                          if (value != null) {
                            setState(() {
                              _currentSymptomForNavigation = value;
                            });
                            // Add to selected symptoms
                            ref.read(shortBowNotifierProvider.notifier).addSymptom(value);
                            // Navigate to get linked symptoms
                            ref.read(shortBowNotifierProvider.notifier).navigateToSymptom(value);
                          }
                        },
                      );
                    },
                  ),

                  const SizedBox(height: 16),

                  // Action buttons
                  Row(
                    children: [
                      ElevatedButton.icon(
                        onPressed: shortBowState.selectedSymptoms.isNotEmpty
                            ? () {
                                ref.read(shortBowNotifierProvider.notifier).clearSelectedSymptoms();
                                setState(() {
                                  _currentSymptomForNavigation = null;
                                });
                              }
                            : null,
                        icon: const Icon(Icons.clear),
                        label: const Text('Clear All'),
                      ),
                      const SizedBox(width: 8),
                      // Go back button - only show if we have navigation history
                      if (shortBowState.navigationHistory.isNotEmpty)
                        ElevatedButton.icon(
                          onPressed: () {
                            ref.read(shortBowNotifierProvider.notifier).goBack();
                            setState(() {
                              // Update current symptom for navigation based on new history
                              final newHistory = shortBowState.navigationHistory;
                              _currentSymptomForNavigation = newHistory.isNotEmpty
                                  ? newHistory.last
                                  : null;
                            });
                          },
                          icon: const Icon(Icons.arrow_back),
                          label: const Text('Go Back'),
                        ),
                      if (shortBowState.navigationHistory.isNotEmpty) const SizedBox(width: 8),
                      ElevatedButton.icon(
                        onPressed: shortBowState.selectedSymptoms.isNotEmpty && !isCalculating
                            ? () {
                                ref.read(shortBowNotifierProvider.notifier).saveCalculation();
                              }
                            : null,
                        icon: isCalculating
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.save),
                        label: Text(isCalculating ? 'Creating Tree...' : 'Save as Decision Tree Branch'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16),

          // Linked symptoms section
          if (shortBowState.currentLinkedSymptoms.isNotEmpty) ...[
            const Text(
              'Linked Symptoms:',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: shortBowState.currentLinkedSymptoms.map((link) {
                    return ListTile(
                      title: Text(link.toSymptom),
                      subtitle: Text('Probability: ${(link.probability * 100).toStringAsFixed(1)}%'),
                      trailing: shortBowState.selectedSymptoms.contains(link.toSymptom)
                          ? const Icon(Icons.check, color: Colors.green)
                          : IconButton(
                              icon: const Icon(Icons.add),
                              onPressed: () {
                                ref.read(shortBowNotifierProvider.notifier).selectSymptom(link.toSymptom);
                              },
                            ),
                    );
                  }).toList(),
                ),
              ),
            ),
          ],

          const SizedBox(height: 16),

          // Calculations history
          if (shortBowState.calculations.isNotEmpty) ...[
            const Text(
              'Recent Calculations:',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: shortBowState.calculations.take(5).map((calc) {
                    return ListTile(
                      title: Text('${calc.initialSymptom} → ${calc.selectedSymptoms.join(', ')}'),
                      subtitle: Text(calc.calculationDate),
                      trailing: calc.saved
                          ? const Icon(Icons.bookmark, color: Colors.blue)
                          : IconButton(
                              icon: const Icon(Icons.bookmark_border),
                              onPressed: () {
                                ref.read(shortBowNotifierProvider.notifier).saveCalculationById(calc.id);
                              },
                            ),
                    );
                  }).toList(),
                ),
              ),
            ),
          ],

          // Error display
          if (error != null) ...[
            const SizedBox(height: 16),
            Card(
              color: Colors.red[50],
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    Icon(Icons.error_outline, color: Colors.red[700]),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        error,
                        style: TextStyle(color: Colors.red[700]),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],

          // Loading indicator
          if (isLoading || isNavigating) ...[
            const SizedBox(height: 16),
            const Center(
              child: CircularProgressIndicator(),
            ),
          ],
        ],
      ),
    );
  }



  List<DropdownMenuItem<String>> _buildSymptomItems(ShortBowState state) {
    final items = <DropdownMenuItem<String>>[];
    final usedValues = <String>{};

    // If we have a current symptom for navigation, show linked symptoms
    if (_currentSymptomForNavigation != null && state.currentLinkedSymptoms.isNotEmpty) {
      for (final link in state.currentLinkedSymptoms) {
        // Skip if already selected or already used
        if (!state.selectedSymptoms.contains(link.toSymptom) &&
            !usedValues.contains(link.toSymptom)) {
          items.add(DropdownMenuItem(
            value: link.toSymptom,
            child: Text('${link.toSymptom} (${(link.probability * 100).toStringAsFixed(1)}%)'),
          ));
          usedValues.add(link.toSymptom);
        }
      }
    } else {
      // Show all available symptoms for initial selection
      if (state.symptoms.isNotEmpty) {
        for (final symptom in state.symptoms) {
          if (!state.selectedSymptoms.contains(symptom.symptomName) &&
              !usedValues.contains(symptom.symptomName)) {
            items.add(DropdownMenuItem(
              value: symptom.symptomName,
              child: Text(symptom.symptomName),
            ));
            usedValues.add(symptom.symptomName);
          }
        }
      }

      // Add top symptoms as additional options if available
      if (state.topSymptoms.isNotEmpty) {
        for (final link in state.topSymptoms) {
          // Skip if already selected or already used
          if (!state.selectedSymptoms.contains(link.toSymptom) &&
              !usedValues.contains(link.toSymptom)) {
            items.add(DropdownMenuItem(
              value: link.toSymptom,
              child: Text('${link.toSymptom} (${(link.probability * 100).toStringAsFixed(1)}%) - Top Link'),
            ));
            usedValues.add(link.toSymptom);
          }
        }
      }
    }

    return items;
  }
}
