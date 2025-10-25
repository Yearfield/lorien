import 'package:freezed_annotation/freezed_annotation.dart';
import '../data/shortbow_models.dart';

part 'shortbow_state.freezed.dart';

@freezed
class ShortBowState with _$ShortBowState {
  const factory ShortBowState({
    @Default([]) List<ShortBowSymptom> symptoms,
    @Default([]) List<ShortBowSymptomLink> topSymptoms,
    @Default([]) List<ShortBowSymptomLink> currentLinkedSymptoms,
    @Default([]) List<String> selectedSymptoms,
    @Default([]) List<String> navigationHistory,
    String? currentSymptom,
    @Default([]) List<ShortBowCalculation> calculations,
    ShortBowStats? stats,
    @Default(false) bool isLoading,
    @Default(false) bool isNavigating,
    @Default(false) bool isCalculating,
    String? error,
  }) = _ShortBowState;
}
