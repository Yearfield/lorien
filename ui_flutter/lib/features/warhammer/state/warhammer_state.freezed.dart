// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'warhammer_state.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

/// @nodoc
mixin _$WarhammerState {
  List<Symptom> get symptoms => throw _privateConstructorUsedError;
  List<Disease> get diseases => throw _privateConstructorUsedError;
  WarhammerStats? get stats => throw _privateConstructorUsedError;
  SymptomComparison? get symptomComparison =>
      throw _privateConstructorUsedError;
  List<SymptomSynonym> get synonyms => throw _privateConstructorUsedError;
  bool get isLoading => throw _privateConstructorUsedError;
  bool get isCalculating => throw _privateConstructorUsedError;
  bool get isImporting => throw _privateConstructorUsedError;
  bool get isLoadingComparison => throw _privateConstructorUsedError;
  bool get isLoadingSynonyms => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;
  List<String> get selectedSymptoms => throw _privateConstructorUsedError;
  CalculationResponse? get lastCalculation =>
      throw _privateConstructorUsedError;
  List<SavedCalculation> get savedCalculations =>
      throw _privateConstructorUsedError;
  int get currentParentId => throw _privateConstructorUsedError;
  List<Map<String, dynamic>> get currentTreeOptions =>
      throw _privateConstructorUsedError;
  List<Map<String, dynamic>> get decisionTreeRoots =>
      throw _privateConstructorUsedError;

  /// Create a copy of WarhammerState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $WarhammerStateCopyWith<WarhammerState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $WarhammerStateCopyWith<$Res> {
  factory $WarhammerStateCopyWith(
          WarhammerState value, $Res Function(WarhammerState) then) =
      _$WarhammerStateCopyWithImpl<$Res, WarhammerState>;
  @useResult
  $Res call(
      {List<Symptom> symptoms,
      List<Disease> diseases,
      WarhammerStats? stats,
      SymptomComparison? symptomComparison,
      List<SymptomSynonym> synonyms,
      bool isLoading,
      bool isCalculating,
      bool isImporting,
      bool isLoadingComparison,
      bool isLoadingSynonyms,
      String? error,
      List<String> selectedSymptoms,
      CalculationResponse? lastCalculation,
      List<SavedCalculation> savedCalculations,
      int currentParentId,
      List<Map<String, dynamic>> currentTreeOptions,
      List<Map<String, dynamic>> decisionTreeRoots});

  $WarhammerStatsCopyWith<$Res>? get stats;
  $SymptomComparisonCopyWith<$Res>? get symptomComparison;
  $CalculationResponseCopyWith<$Res>? get lastCalculation;
}

/// @nodoc
class _$WarhammerStateCopyWithImpl<$Res, $Val extends WarhammerState>
    implements $WarhammerStateCopyWith<$Res> {
  _$WarhammerStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of WarhammerState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? symptoms = null,
    Object? diseases = null,
    Object? stats = freezed,
    Object? symptomComparison = freezed,
    Object? synonyms = null,
    Object? isLoading = null,
    Object? isCalculating = null,
    Object? isImporting = null,
    Object? isLoadingComparison = null,
    Object? isLoadingSynonyms = null,
    Object? error = freezed,
    Object? selectedSymptoms = null,
    Object? lastCalculation = freezed,
    Object? savedCalculations = null,
    Object? currentParentId = null,
    Object? currentTreeOptions = null,
    Object? decisionTreeRoots = null,
  }) {
    return _then(_value.copyWith(
      symptoms: null == symptoms
          ? _value.symptoms
          : symptoms // ignore: cast_nullable_to_non_nullable
              as List<Symptom>,
      diseases: null == diseases
          ? _value.diseases
          : diseases // ignore: cast_nullable_to_non_nullable
              as List<Disease>,
      stats: freezed == stats
          ? _value.stats
          : stats // ignore: cast_nullable_to_non_nullable
              as WarhammerStats?,
      symptomComparison: freezed == symptomComparison
          ? _value.symptomComparison
          : symptomComparison // ignore: cast_nullable_to_non_nullable
              as SymptomComparison?,
      synonyms: null == synonyms
          ? _value.synonyms
          : synonyms // ignore: cast_nullable_to_non_nullable
              as List<SymptomSynonym>,
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      isCalculating: null == isCalculating
          ? _value.isCalculating
          : isCalculating // ignore: cast_nullable_to_non_nullable
              as bool,
      isImporting: null == isImporting
          ? _value.isImporting
          : isImporting // ignore: cast_nullable_to_non_nullable
              as bool,
      isLoadingComparison: null == isLoadingComparison
          ? _value.isLoadingComparison
          : isLoadingComparison // ignore: cast_nullable_to_non_nullable
              as bool,
      isLoadingSynonyms: null == isLoadingSynonyms
          ? _value.isLoadingSynonyms
          : isLoadingSynonyms // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      selectedSymptoms: null == selectedSymptoms
          ? _value.selectedSymptoms
          : selectedSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      lastCalculation: freezed == lastCalculation
          ? _value.lastCalculation
          : lastCalculation // ignore: cast_nullable_to_non_nullable
              as CalculationResponse?,
      savedCalculations: null == savedCalculations
          ? _value.savedCalculations
          : savedCalculations // ignore: cast_nullable_to_non_nullable
              as List<SavedCalculation>,
      currentParentId: null == currentParentId
          ? _value.currentParentId
          : currentParentId // ignore: cast_nullable_to_non_nullable
              as int,
      currentTreeOptions: null == currentTreeOptions
          ? _value.currentTreeOptions
          : currentTreeOptions // ignore: cast_nullable_to_non_nullable
              as List<Map<String, dynamic>>,
      decisionTreeRoots: null == decisionTreeRoots
          ? _value.decisionTreeRoots
          : decisionTreeRoots // ignore: cast_nullable_to_non_nullable
              as List<Map<String, dynamic>>,
    ) as $Val);
  }

  /// Create a copy of WarhammerState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $WarhammerStatsCopyWith<$Res>? get stats {
    if (_value.stats == null) {
      return null;
    }

    return $WarhammerStatsCopyWith<$Res>(_value.stats!, (value) {
      return _then(_value.copyWith(stats: value) as $Val);
    });
  }

  /// Create a copy of WarhammerState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $SymptomComparisonCopyWith<$Res>? get symptomComparison {
    if (_value.symptomComparison == null) {
      return null;
    }

    return $SymptomComparisonCopyWith<$Res>(_value.symptomComparison!, (value) {
      return _then(_value.copyWith(symptomComparison: value) as $Val);
    });
  }

  /// Create a copy of WarhammerState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $CalculationResponseCopyWith<$Res>? get lastCalculation {
    if (_value.lastCalculation == null) {
      return null;
    }

    return $CalculationResponseCopyWith<$Res>(_value.lastCalculation!, (value) {
      return _then(_value.copyWith(lastCalculation: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$WarhammerStateImplCopyWith<$Res>
    implements $WarhammerStateCopyWith<$Res> {
  factory _$$WarhammerStateImplCopyWith(_$WarhammerStateImpl value,
          $Res Function(_$WarhammerStateImpl) then) =
      __$$WarhammerStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {List<Symptom> symptoms,
      List<Disease> diseases,
      WarhammerStats? stats,
      SymptomComparison? symptomComparison,
      List<SymptomSynonym> synonyms,
      bool isLoading,
      bool isCalculating,
      bool isImporting,
      bool isLoadingComparison,
      bool isLoadingSynonyms,
      String? error,
      List<String> selectedSymptoms,
      CalculationResponse? lastCalculation,
      List<SavedCalculation> savedCalculations,
      int currentParentId,
      List<Map<String, dynamic>> currentTreeOptions,
      List<Map<String, dynamic>> decisionTreeRoots});

  @override
  $WarhammerStatsCopyWith<$Res>? get stats;
  @override
  $SymptomComparisonCopyWith<$Res>? get symptomComparison;
  @override
  $CalculationResponseCopyWith<$Res>? get lastCalculation;
}

/// @nodoc
class __$$WarhammerStateImplCopyWithImpl<$Res>
    extends _$WarhammerStateCopyWithImpl<$Res, _$WarhammerStateImpl>
    implements _$$WarhammerStateImplCopyWith<$Res> {
  __$$WarhammerStateImplCopyWithImpl(
      _$WarhammerStateImpl _value, $Res Function(_$WarhammerStateImpl) _then)
      : super(_value, _then);

  /// Create a copy of WarhammerState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? symptoms = null,
    Object? diseases = null,
    Object? stats = freezed,
    Object? symptomComparison = freezed,
    Object? synonyms = null,
    Object? isLoading = null,
    Object? isCalculating = null,
    Object? isImporting = null,
    Object? isLoadingComparison = null,
    Object? isLoadingSynonyms = null,
    Object? error = freezed,
    Object? selectedSymptoms = null,
    Object? lastCalculation = freezed,
    Object? savedCalculations = null,
    Object? currentParentId = null,
    Object? currentTreeOptions = null,
    Object? decisionTreeRoots = null,
  }) {
    return _then(_$WarhammerStateImpl(
      symptoms: null == symptoms
          ? _value._symptoms
          : symptoms // ignore: cast_nullable_to_non_nullable
              as List<Symptom>,
      diseases: null == diseases
          ? _value._diseases
          : diseases // ignore: cast_nullable_to_non_nullable
              as List<Disease>,
      stats: freezed == stats
          ? _value.stats
          : stats // ignore: cast_nullable_to_non_nullable
              as WarhammerStats?,
      symptomComparison: freezed == symptomComparison
          ? _value.symptomComparison
          : symptomComparison // ignore: cast_nullable_to_non_nullable
              as SymptomComparison?,
      synonyms: null == synonyms
          ? _value._synonyms
          : synonyms // ignore: cast_nullable_to_non_nullable
              as List<SymptomSynonym>,
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      isCalculating: null == isCalculating
          ? _value.isCalculating
          : isCalculating // ignore: cast_nullable_to_non_nullable
              as bool,
      isImporting: null == isImporting
          ? _value.isImporting
          : isImporting // ignore: cast_nullable_to_non_nullable
              as bool,
      isLoadingComparison: null == isLoadingComparison
          ? _value.isLoadingComparison
          : isLoadingComparison // ignore: cast_nullable_to_non_nullable
              as bool,
      isLoadingSynonyms: null == isLoadingSynonyms
          ? _value.isLoadingSynonyms
          : isLoadingSynonyms // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
      selectedSymptoms: null == selectedSymptoms
          ? _value._selectedSymptoms
          : selectedSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      lastCalculation: freezed == lastCalculation
          ? _value.lastCalculation
          : lastCalculation // ignore: cast_nullable_to_non_nullable
              as CalculationResponse?,
      savedCalculations: null == savedCalculations
          ? _value._savedCalculations
          : savedCalculations // ignore: cast_nullable_to_non_nullable
              as List<SavedCalculation>,
      currentParentId: null == currentParentId
          ? _value.currentParentId
          : currentParentId // ignore: cast_nullable_to_non_nullable
              as int,
      currentTreeOptions: null == currentTreeOptions
          ? _value._currentTreeOptions
          : currentTreeOptions // ignore: cast_nullable_to_non_nullable
              as List<Map<String, dynamic>>,
      decisionTreeRoots: null == decisionTreeRoots
          ? _value._decisionTreeRoots
          : decisionTreeRoots // ignore: cast_nullable_to_non_nullable
              as List<Map<String, dynamic>>,
    ));
  }
}

/// @nodoc

class _$WarhammerStateImpl implements _WarhammerState {
  const _$WarhammerStateImpl(
      {final List<Symptom> symptoms = const [],
      final List<Disease> diseases = const [],
      this.stats,
      this.symptomComparison,
      final List<SymptomSynonym> synonyms = const [],
      this.isLoading = false,
      this.isCalculating = false,
      this.isImporting = false,
      this.isLoadingComparison = false,
      this.isLoadingSynonyms = false,
      this.error,
      final List<String> selectedSymptoms = const [],
      this.lastCalculation,
      final List<SavedCalculation> savedCalculations = const [],
      this.currentParentId = 0,
      final List<Map<String, dynamic>> currentTreeOptions = const [],
      final List<Map<String, dynamic>> decisionTreeRoots = const []})
      : _symptoms = symptoms,
        _diseases = diseases,
        _synonyms = synonyms,
        _selectedSymptoms = selectedSymptoms,
        _savedCalculations = savedCalculations,
        _currentTreeOptions = currentTreeOptions,
        _decisionTreeRoots = decisionTreeRoots;

  final List<Symptom> _symptoms;
  @override
  @JsonKey()
  List<Symptom> get symptoms {
    if (_symptoms is EqualUnmodifiableListView) return _symptoms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_symptoms);
  }

  final List<Disease> _diseases;
  @override
  @JsonKey()
  List<Disease> get diseases {
    if (_diseases is EqualUnmodifiableListView) return _diseases;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_diseases);
  }

  @override
  final WarhammerStats? stats;
  @override
  final SymptomComparison? symptomComparison;
  final List<SymptomSynonym> _synonyms;
  @override
  @JsonKey()
  List<SymptomSynonym> get synonyms {
    if (_synonyms is EqualUnmodifiableListView) return _synonyms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_synonyms);
  }

  @override
  @JsonKey()
  final bool isLoading;
  @override
  @JsonKey()
  final bool isCalculating;
  @override
  @JsonKey()
  final bool isImporting;
  @override
  @JsonKey()
  final bool isLoadingComparison;
  @override
  @JsonKey()
  final bool isLoadingSynonyms;
  @override
  final String? error;
  final List<String> _selectedSymptoms;
  @override
  @JsonKey()
  List<String> get selectedSymptoms {
    if (_selectedSymptoms is EqualUnmodifiableListView)
      return _selectedSymptoms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_selectedSymptoms);
  }

  @override
  final CalculationResponse? lastCalculation;
  final List<SavedCalculation> _savedCalculations;
  @override
  @JsonKey()
  List<SavedCalculation> get savedCalculations {
    if (_savedCalculations is EqualUnmodifiableListView)
      return _savedCalculations;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_savedCalculations);
  }

  @override
  @JsonKey()
  final int currentParentId;
  final List<Map<String, dynamic>> _currentTreeOptions;
  @override
  @JsonKey()
  List<Map<String, dynamic>> get currentTreeOptions {
    if (_currentTreeOptions is EqualUnmodifiableListView)
      return _currentTreeOptions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_currentTreeOptions);
  }

  final List<Map<String, dynamic>> _decisionTreeRoots;
  @override
  @JsonKey()
  List<Map<String, dynamic>> get decisionTreeRoots {
    if (_decisionTreeRoots is EqualUnmodifiableListView)
      return _decisionTreeRoots;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_decisionTreeRoots);
  }

  @override
  String toString() {
    return 'WarhammerState(symptoms: $symptoms, diseases: $diseases, stats: $stats, symptomComparison: $symptomComparison, synonyms: $synonyms, isLoading: $isLoading, isCalculating: $isCalculating, isImporting: $isImporting, isLoadingComparison: $isLoadingComparison, isLoadingSynonyms: $isLoadingSynonyms, error: $error, selectedSymptoms: $selectedSymptoms, lastCalculation: $lastCalculation, savedCalculations: $savedCalculations, currentParentId: $currentParentId, currentTreeOptions: $currentTreeOptions, decisionTreeRoots: $decisionTreeRoots)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$WarhammerStateImpl &&
            const DeepCollectionEquality().equals(other._symptoms, _symptoms) &&
            const DeepCollectionEquality().equals(other._diseases, _diseases) &&
            (identical(other.stats, stats) || other.stats == stats) &&
            (identical(other.symptomComparison, symptomComparison) ||
                other.symptomComparison == symptomComparison) &&
            const DeepCollectionEquality().equals(other._synonyms, _synonyms) &&
            (identical(other.isLoading, isLoading) ||
                other.isLoading == isLoading) &&
            (identical(other.isCalculating, isCalculating) ||
                other.isCalculating == isCalculating) &&
            (identical(other.isImporting, isImporting) ||
                other.isImporting == isImporting) &&
            (identical(other.isLoadingComparison, isLoadingComparison) ||
                other.isLoadingComparison == isLoadingComparison) &&
            (identical(other.isLoadingSynonyms, isLoadingSynonyms) ||
                other.isLoadingSynonyms == isLoadingSynonyms) &&
            (identical(other.error, error) || other.error == error) &&
            const DeepCollectionEquality()
                .equals(other._selectedSymptoms, _selectedSymptoms) &&
            (identical(other.lastCalculation, lastCalculation) ||
                other.lastCalculation == lastCalculation) &&
            const DeepCollectionEquality()
                .equals(other._savedCalculations, _savedCalculations) &&
            (identical(other.currentParentId, currentParentId) ||
                other.currentParentId == currentParentId) &&
            const DeepCollectionEquality()
                .equals(other._currentTreeOptions, _currentTreeOptions) &&
            const DeepCollectionEquality()
                .equals(other._decisionTreeRoots, _decisionTreeRoots));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(_symptoms),
      const DeepCollectionEquality().hash(_diseases),
      stats,
      symptomComparison,
      const DeepCollectionEquality().hash(_synonyms),
      isLoading,
      isCalculating,
      isImporting,
      isLoadingComparison,
      isLoadingSynonyms,
      error,
      const DeepCollectionEquality().hash(_selectedSymptoms),
      lastCalculation,
      const DeepCollectionEquality().hash(_savedCalculations),
      currentParentId,
      const DeepCollectionEquality().hash(_currentTreeOptions),
      const DeepCollectionEquality().hash(_decisionTreeRoots));

  /// Create a copy of WarhammerState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$WarhammerStateImplCopyWith<_$WarhammerStateImpl> get copyWith =>
      __$$WarhammerStateImplCopyWithImpl<_$WarhammerStateImpl>(
          this, _$identity);
}

abstract class _WarhammerState implements WarhammerState {
  const factory _WarhammerState(
          {final List<Symptom> symptoms,
          final List<Disease> diseases,
          final WarhammerStats? stats,
          final SymptomComparison? symptomComparison,
          final List<SymptomSynonym> synonyms,
          final bool isLoading,
          final bool isCalculating,
          final bool isImporting,
          final bool isLoadingComparison,
          final bool isLoadingSynonyms,
          final String? error,
          final List<String> selectedSymptoms,
          final CalculationResponse? lastCalculation,
          final List<SavedCalculation> savedCalculations,
          final int currentParentId,
          final List<Map<String, dynamic>> currentTreeOptions,
          final List<Map<String, dynamic>> decisionTreeRoots}) =
      _$WarhammerStateImpl;

  @override
  List<Symptom> get symptoms;
  @override
  List<Disease> get diseases;
  @override
  WarhammerStats? get stats;
  @override
  SymptomComparison? get symptomComparison;
  @override
  List<SymptomSynonym> get synonyms;
  @override
  bool get isLoading;
  @override
  bool get isCalculating;
  @override
  bool get isImporting;
  @override
  bool get isLoadingComparison;
  @override
  bool get isLoadingSynonyms;
  @override
  String? get error;
  @override
  List<String> get selectedSymptoms;
  @override
  CalculationResponse? get lastCalculation;
  @override
  List<SavedCalculation> get savedCalculations;
  @override
  int get currentParentId;
  @override
  List<Map<String, dynamic>> get currentTreeOptions;
  @override
  List<Map<String, dynamic>> get decisionTreeRoots;

  /// Create a copy of WarhammerState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$WarhammerStateImplCopyWith<_$WarhammerStateImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
mixin _$WarhammerCalculationState {
  List<String> get selectedSymptoms => throw _privateConstructorUsedError;
  CalculationResponse? get result => throw _privateConstructorUsedError;
  bool get isCalculating => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;

  /// Create a copy of WarhammerCalculationState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $WarhammerCalculationStateCopyWith<WarhammerCalculationState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $WarhammerCalculationStateCopyWith<$Res> {
  factory $WarhammerCalculationStateCopyWith(WarhammerCalculationState value,
          $Res Function(WarhammerCalculationState) then) =
      _$WarhammerCalculationStateCopyWithImpl<$Res, WarhammerCalculationState>;
  @useResult
  $Res call(
      {List<String> selectedSymptoms,
      CalculationResponse? result,
      bool isCalculating,
      String? error});

  $CalculationResponseCopyWith<$Res>? get result;
}

/// @nodoc
class _$WarhammerCalculationStateCopyWithImpl<$Res,
        $Val extends WarhammerCalculationState>
    implements $WarhammerCalculationStateCopyWith<$Res> {
  _$WarhammerCalculationStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of WarhammerCalculationState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? selectedSymptoms = null,
    Object? result = freezed,
    Object? isCalculating = null,
    Object? error = freezed,
  }) {
    return _then(_value.copyWith(
      selectedSymptoms: null == selectedSymptoms
          ? _value.selectedSymptoms
          : selectedSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      result: freezed == result
          ? _value.result
          : result // ignore: cast_nullable_to_non_nullable
              as CalculationResponse?,
      isCalculating: null == isCalculating
          ? _value.isCalculating
          : isCalculating // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }

  /// Create a copy of WarhammerCalculationState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $CalculationResponseCopyWith<$Res>? get result {
    if (_value.result == null) {
      return null;
    }

    return $CalculationResponseCopyWith<$Res>(_value.result!, (value) {
      return _then(_value.copyWith(result: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$WarhammerCalculationStateImplCopyWith<$Res>
    implements $WarhammerCalculationStateCopyWith<$Res> {
  factory _$$WarhammerCalculationStateImplCopyWith(
          _$WarhammerCalculationStateImpl value,
          $Res Function(_$WarhammerCalculationStateImpl) then) =
      __$$WarhammerCalculationStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {List<String> selectedSymptoms,
      CalculationResponse? result,
      bool isCalculating,
      String? error});

  @override
  $CalculationResponseCopyWith<$Res>? get result;
}

/// @nodoc
class __$$WarhammerCalculationStateImplCopyWithImpl<$Res>
    extends _$WarhammerCalculationStateCopyWithImpl<$Res,
        _$WarhammerCalculationStateImpl>
    implements _$$WarhammerCalculationStateImplCopyWith<$Res> {
  __$$WarhammerCalculationStateImplCopyWithImpl(
      _$WarhammerCalculationStateImpl _value,
      $Res Function(_$WarhammerCalculationStateImpl) _then)
      : super(_value, _then);

  /// Create a copy of WarhammerCalculationState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? selectedSymptoms = null,
    Object? result = freezed,
    Object? isCalculating = null,
    Object? error = freezed,
  }) {
    return _then(_$WarhammerCalculationStateImpl(
      selectedSymptoms: null == selectedSymptoms
          ? _value._selectedSymptoms
          : selectedSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      result: freezed == result
          ? _value.result
          : result // ignore: cast_nullable_to_non_nullable
              as CalculationResponse?,
      isCalculating: null == isCalculating
          ? _value.isCalculating
          : isCalculating // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc

class _$WarhammerCalculationStateImpl implements _WarhammerCalculationState {
  const _$WarhammerCalculationStateImpl(
      {final List<String> selectedSymptoms = const [],
      this.result,
      this.isCalculating = false,
      this.error})
      : _selectedSymptoms = selectedSymptoms;

  final List<String> _selectedSymptoms;
  @override
  @JsonKey()
  List<String> get selectedSymptoms {
    if (_selectedSymptoms is EqualUnmodifiableListView)
      return _selectedSymptoms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_selectedSymptoms);
  }

  @override
  final CalculationResponse? result;
  @override
  @JsonKey()
  final bool isCalculating;
  @override
  final String? error;

  @override
  String toString() {
    return 'WarhammerCalculationState(selectedSymptoms: $selectedSymptoms, result: $result, isCalculating: $isCalculating, error: $error)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$WarhammerCalculationStateImpl &&
            const DeepCollectionEquality()
                .equals(other._selectedSymptoms, _selectedSymptoms) &&
            (identical(other.result, result) || other.result == result) &&
            (identical(other.isCalculating, isCalculating) ||
                other.isCalculating == isCalculating) &&
            (identical(other.error, error) || other.error == error));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(_selectedSymptoms),
      result,
      isCalculating,
      error);

  /// Create a copy of WarhammerCalculationState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$WarhammerCalculationStateImplCopyWith<_$WarhammerCalculationStateImpl>
      get copyWith => __$$WarhammerCalculationStateImplCopyWithImpl<
          _$WarhammerCalculationStateImpl>(this, _$identity);
}

abstract class _WarhammerCalculationState implements WarhammerCalculationState {
  const factory _WarhammerCalculationState(
      {final List<String> selectedSymptoms,
      final CalculationResponse? result,
      final bool isCalculating,
      final String? error}) = _$WarhammerCalculationStateImpl;

  @override
  List<String> get selectedSymptoms;
  @override
  CalculationResponse? get result;
  @override
  bool get isCalculating;
  @override
  String? get error;

  /// Create a copy of WarhammerCalculationState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$WarhammerCalculationStateImplCopyWith<_$WarhammerCalculationStateImpl>
      get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
mixin _$WarhammerImportState {
  bool get isImportingDiseases => throw _privateConstructorUsedError;
  bool get isImportingSymptoms => throw _privateConstructorUsedError;
  bool get isImportingConditionals => throw _privateConstructorUsedError;
  ImportResultResponse? get lastImportResult =>
      throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;

  /// Create a copy of WarhammerImportState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $WarhammerImportStateCopyWith<WarhammerImportState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $WarhammerImportStateCopyWith<$Res> {
  factory $WarhammerImportStateCopyWith(WarhammerImportState value,
          $Res Function(WarhammerImportState) then) =
      _$WarhammerImportStateCopyWithImpl<$Res, WarhammerImportState>;
  @useResult
  $Res call(
      {bool isImportingDiseases,
      bool isImportingSymptoms,
      bool isImportingConditionals,
      ImportResultResponse? lastImportResult,
      String? error});

  $ImportResultResponseCopyWith<$Res>? get lastImportResult;
}

/// @nodoc
class _$WarhammerImportStateCopyWithImpl<$Res,
        $Val extends WarhammerImportState>
    implements $WarhammerImportStateCopyWith<$Res> {
  _$WarhammerImportStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of WarhammerImportState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? isImportingDiseases = null,
    Object? isImportingSymptoms = null,
    Object? isImportingConditionals = null,
    Object? lastImportResult = freezed,
    Object? error = freezed,
  }) {
    return _then(_value.copyWith(
      isImportingDiseases: null == isImportingDiseases
          ? _value.isImportingDiseases
          : isImportingDiseases // ignore: cast_nullable_to_non_nullable
              as bool,
      isImportingSymptoms: null == isImportingSymptoms
          ? _value.isImportingSymptoms
          : isImportingSymptoms // ignore: cast_nullable_to_non_nullable
              as bool,
      isImportingConditionals: null == isImportingConditionals
          ? _value.isImportingConditionals
          : isImportingConditionals // ignore: cast_nullable_to_non_nullable
              as bool,
      lastImportResult: freezed == lastImportResult
          ? _value.lastImportResult
          : lastImportResult // ignore: cast_nullable_to_non_nullable
              as ImportResultResponse?,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }

  /// Create a copy of WarhammerImportState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $ImportResultResponseCopyWith<$Res>? get lastImportResult {
    if (_value.lastImportResult == null) {
      return null;
    }

    return $ImportResultResponseCopyWith<$Res>(_value.lastImportResult!,
        (value) {
      return _then(_value.copyWith(lastImportResult: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$WarhammerImportStateImplCopyWith<$Res>
    implements $WarhammerImportStateCopyWith<$Res> {
  factory _$$WarhammerImportStateImplCopyWith(_$WarhammerImportStateImpl value,
          $Res Function(_$WarhammerImportStateImpl) then) =
      __$$WarhammerImportStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool isImportingDiseases,
      bool isImportingSymptoms,
      bool isImportingConditionals,
      ImportResultResponse? lastImportResult,
      String? error});

  @override
  $ImportResultResponseCopyWith<$Res>? get lastImportResult;
}

/// @nodoc
class __$$WarhammerImportStateImplCopyWithImpl<$Res>
    extends _$WarhammerImportStateCopyWithImpl<$Res, _$WarhammerImportStateImpl>
    implements _$$WarhammerImportStateImplCopyWith<$Res> {
  __$$WarhammerImportStateImplCopyWithImpl(_$WarhammerImportStateImpl _value,
      $Res Function(_$WarhammerImportStateImpl) _then)
      : super(_value, _then);

  /// Create a copy of WarhammerImportState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? isImportingDiseases = null,
    Object? isImportingSymptoms = null,
    Object? isImportingConditionals = null,
    Object? lastImportResult = freezed,
    Object? error = freezed,
  }) {
    return _then(_$WarhammerImportStateImpl(
      isImportingDiseases: null == isImportingDiseases
          ? _value.isImportingDiseases
          : isImportingDiseases // ignore: cast_nullable_to_non_nullable
              as bool,
      isImportingSymptoms: null == isImportingSymptoms
          ? _value.isImportingSymptoms
          : isImportingSymptoms // ignore: cast_nullable_to_non_nullable
              as bool,
      isImportingConditionals: null == isImportingConditionals
          ? _value.isImportingConditionals
          : isImportingConditionals // ignore: cast_nullable_to_non_nullable
              as bool,
      lastImportResult: freezed == lastImportResult
          ? _value.lastImportResult
          : lastImportResult // ignore: cast_nullable_to_non_nullable
              as ImportResultResponse?,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc

class _$WarhammerImportStateImpl implements _WarhammerImportState {
  const _$WarhammerImportStateImpl(
      {this.isImportingDiseases = false,
      this.isImportingSymptoms = false,
      this.isImportingConditionals = false,
      this.lastImportResult,
      this.error});

  @override
  @JsonKey()
  final bool isImportingDiseases;
  @override
  @JsonKey()
  final bool isImportingSymptoms;
  @override
  @JsonKey()
  final bool isImportingConditionals;
  @override
  final ImportResultResponse? lastImportResult;
  @override
  final String? error;

  @override
  String toString() {
    return 'WarhammerImportState(isImportingDiseases: $isImportingDiseases, isImportingSymptoms: $isImportingSymptoms, isImportingConditionals: $isImportingConditionals, lastImportResult: $lastImportResult, error: $error)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$WarhammerImportStateImpl &&
            (identical(other.isImportingDiseases, isImportingDiseases) ||
                other.isImportingDiseases == isImportingDiseases) &&
            (identical(other.isImportingSymptoms, isImportingSymptoms) ||
                other.isImportingSymptoms == isImportingSymptoms) &&
            (identical(
                    other.isImportingConditionals, isImportingConditionals) ||
                other.isImportingConditionals == isImportingConditionals) &&
            (identical(other.lastImportResult, lastImportResult) ||
                other.lastImportResult == lastImportResult) &&
            (identical(other.error, error) || other.error == error));
  }

  @override
  int get hashCode => Object.hash(runtimeType, isImportingDiseases,
      isImportingSymptoms, isImportingConditionals, lastImportResult, error);

  /// Create a copy of WarhammerImportState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$WarhammerImportStateImplCopyWith<_$WarhammerImportStateImpl>
      get copyWith =>
          __$$WarhammerImportStateImplCopyWithImpl<_$WarhammerImportStateImpl>(
              this, _$identity);
}

abstract class _WarhammerImportState implements WarhammerImportState {
  const factory _WarhammerImportState(
      {final bool isImportingDiseases,
      final bool isImportingSymptoms,
      final bool isImportingConditionals,
      final ImportResultResponse? lastImportResult,
      final String? error}) = _$WarhammerImportStateImpl;

  @override
  bool get isImportingDiseases;
  @override
  bool get isImportingSymptoms;
  @override
  bool get isImportingConditionals;
  @override
  ImportResultResponse? get lastImportResult;
  @override
  String? get error;

  /// Create a copy of WarhammerImportState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$WarhammerImportStateImplCopyWith<_$WarhammerImportStateImpl>
      get copyWith => throw _privateConstructorUsedError;
}
