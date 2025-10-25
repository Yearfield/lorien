// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'shortbow_state.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

/// @nodoc
mixin _$ShortBowState {
  List<ShortBowSymptom> get symptoms => throw _privateConstructorUsedError;
  List<ShortBowSymptomLink> get topSymptoms =>
      throw _privateConstructorUsedError;
  List<ShortBowSymptomLink> get currentLinkedSymptoms =>
      throw _privateConstructorUsedError;
  List<String> get selectedSymptoms => throw _privateConstructorUsedError;
  List<String> get navigationHistory => throw _privateConstructorUsedError;
  String? get currentSymptom => throw _privateConstructorUsedError;
  List<ShortBowCalculation> get calculations =>
      throw _privateConstructorUsedError;
  ShortBowStats? get stats => throw _privateConstructorUsedError;
  bool get isLoading => throw _privateConstructorUsedError;
  bool get isNavigating => throw _privateConstructorUsedError;
  bool get isCalculating => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;

  /// Create a copy of ShortBowState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ShortBowStateCopyWith<ShortBowState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ShortBowStateCopyWith<$Res> {
  factory $ShortBowStateCopyWith(
          ShortBowState value, $Res Function(ShortBowState) then) =
      _$ShortBowStateCopyWithImpl<$Res, ShortBowState>;
  @useResult
  $Res call(
      {List<ShortBowSymptom> symptoms,
      List<ShortBowSymptomLink> topSymptoms,
      List<ShortBowSymptomLink> currentLinkedSymptoms,
      List<String> selectedSymptoms,
      List<String> navigationHistory,
      String? currentSymptom,
      List<ShortBowCalculation> calculations,
      ShortBowStats? stats,
      bool isLoading,
      bool isNavigating,
      bool isCalculating,
      String? error});

  $ShortBowStatsCopyWith<$Res>? get stats;
}

/// @nodoc
class _$ShortBowStateCopyWithImpl<$Res, $Val extends ShortBowState>
    implements $ShortBowStateCopyWith<$Res> {
  _$ShortBowStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ShortBowState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? symptoms = null,
    Object? topSymptoms = null,
    Object? currentLinkedSymptoms = null,
    Object? selectedSymptoms = null,
    Object? navigationHistory = null,
    Object? currentSymptom = freezed,
    Object? calculations = null,
    Object? stats = freezed,
    Object? isLoading = null,
    Object? isNavigating = null,
    Object? isCalculating = null,
    Object? error = freezed,
  }) {
    return _then(_value.copyWith(
      symptoms: null == symptoms
          ? _value.symptoms
          : symptoms // ignore: cast_nullable_to_non_nullable
              as List<ShortBowSymptom>,
      topSymptoms: null == topSymptoms
          ? _value.topSymptoms
          : topSymptoms // ignore: cast_nullable_to_non_nullable
              as List<ShortBowSymptomLink>,
      currentLinkedSymptoms: null == currentLinkedSymptoms
          ? _value.currentLinkedSymptoms
          : currentLinkedSymptoms // ignore: cast_nullable_to_non_nullable
              as List<ShortBowSymptomLink>,
      selectedSymptoms: null == selectedSymptoms
          ? _value.selectedSymptoms
          : selectedSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      navigationHistory: null == navigationHistory
          ? _value.navigationHistory
          : navigationHistory // ignore: cast_nullable_to_non_nullable
              as List<String>,
      currentSymptom: freezed == currentSymptom
          ? _value.currentSymptom
          : currentSymptom // ignore: cast_nullable_to_non_nullable
              as String?,
      calculations: null == calculations
          ? _value.calculations
          : calculations // ignore: cast_nullable_to_non_nullable
              as List<ShortBowCalculation>,
      stats: freezed == stats
          ? _value.stats
          : stats // ignore: cast_nullable_to_non_nullable
              as ShortBowStats?,
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      isNavigating: null == isNavigating
          ? _value.isNavigating
          : isNavigating // ignore: cast_nullable_to_non_nullable
              as bool,
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

  /// Create a copy of ShortBowState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $ShortBowStatsCopyWith<$Res>? get stats {
    if (_value.stats == null) {
      return null;
    }

    return $ShortBowStatsCopyWith<$Res>(_value.stats!, (value) {
      return _then(_value.copyWith(stats: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$ShortBowStateImplCopyWith<$Res>
    implements $ShortBowStateCopyWith<$Res> {
  factory _$$ShortBowStateImplCopyWith(
          _$ShortBowStateImpl value, $Res Function(_$ShortBowStateImpl) then) =
      __$$ShortBowStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {List<ShortBowSymptom> symptoms,
      List<ShortBowSymptomLink> topSymptoms,
      List<ShortBowSymptomLink> currentLinkedSymptoms,
      List<String> selectedSymptoms,
      List<String> navigationHistory,
      String? currentSymptom,
      List<ShortBowCalculation> calculations,
      ShortBowStats? stats,
      bool isLoading,
      bool isNavigating,
      bool isCalculating,
      String? error});

  @override
  $ShortBowStatsCopyWith<$Res>? get stats;
}

/// @nodoc
class __$$ShortBowStateImplCopyWithImpl<$Res>
    extends _$ShortBowStateCopyWithImpl<$Res, _$ShortBowStateImpl>
    implements _$$ShortBowStateImplCopyWith<$Res> {
  __$$ShortBowStateImplCopyWithImpl(
      _$ShortBowStateImpl _value, $Res Function(_$ShortBowStateImpl) _then)
      : super(_value, _then);

  /// Create a copy of ShortBowState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? symptoms = null,
    Object? topSymptoms = null,
    Object? currentLinkedSymptoms = null,
    Object? selectedSymptoms = null,
    Object? navigationHistory = null,
    Object? currentSymptom = freezed,
    Object? calculations = null,
    Object? stats = freezed,
    Object? isLoading = null,
    Object? isNavigating = null,
    Object? isCalculating = null,
    Object? error = freezed,
  }) {
    return _then(_$ShortBowStateImpl(
      symptoms: null == symptoms
          ? _value._symptoms
          : symptoms // ignore: cast_nullable_to_non_nullable
              as List<ShortBowSymptom>,
      topSymptoms: null == topSymptoms
          ? _value._topSymptoms
          : topSymptoms // ignore: cast_nullable_to_non_nullable
              as List<ShortBowSymptomLink>,
      currentLinkedSymptoms: null == currentLinkedSymptoms
          ? _value._currentLinkedSymptoms
          : currentLinkedSymptoms // ignore: cast_nullable_to_non_nullable
              as List<ShortBowSymptomLink>,
      selectedSymptoms: null == selectedSymptoms
          ? _value._selectedSymptoms
          : selectedSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      navigationHistory: null == navigationHistory
          ? _value._navigationHistory
          : navigationHistory // ignore: cast_nullable_to_non_nullable
              as List<String>,
      currentSymptom: freezed == currentSymptom
          ? _value.currentSymptom
          : currentSymptom // ignore: cast_nullable_to_non_nullable
              as String?,
      calculations: null == calculations
          ? _value._calculations
          : calculations // ignore: cast_nullable_to_non_nullable
              as List<ShortBowCalculation>,
      stats: freezed == stats
          ? _value.stats
          : stats // ignore: cast_nullable_to_non_nullable
              as ShortBowStats?,
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      isNavigating: null == isNavigating
          ? _value.isNavigating
          : isNavigating // ignore: cast_nullable_to_non_nullable
              as bool,
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

class _$ShortBowStateImpl implements _ShortBowState {
  const _$ShortBowStateImpl(
      {final List<ShortBowSymptom> symptoms = const [],
      final List<ShortBowSymptomLink> topSymptoms = const [],
      final List<ShortBowSymptomLink> currentLinkedSymptoms = const [],
      final List<String> selectedSymptoms = const [],
      final List<String> navigationHistory = const [],
      this.currentSymptom,
      final List<ShortBowCalculation> calculations = const [],
      this.stats,
      this.isLoading = false,
      this.isNavigating = false,
      this.isCalculating = false,
      this.error})
      : _symptoms = symptoms,
        _topSymptoms = topSymptoms,
        _currentLinkedSymptoms = currentLinkedSymptoms,
        _selectedSymptoms = selectedSymptoms,
        _navigationHistory = navigationHistory,
        _calculations = calculations;

  final List<ShortBowSymptom> _symptoms;
  @override
  @JsonKey()
  List<ShortBowSymptom> get symptoms {
    if (_symptoms is EqualUnmodifiableListView) return _symptoms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_symptoms);
  }

  final List<ShortBowSymptomLink> _topSymptoms;
  @override
  @JsonKey()
  List<ShortBowSymptomLink> get topSymptoms {
    if (_topSymptoms is EqualUnmodifiableListView) return _topSymptoms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_topSymptoms);
  }

  final List<ShortBowSymptomLink> _currentLinkedSymptoms;
  @override
  @JsonKey()
  List<ShortBowSymptomLink> get currentLinkedSymptoms {
    if (_currentLinkedSymptoms is EqualUnmodifiableListView)
      return _currentLinkedSymptoms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_currentLinkedSymptoms);
  }

  final List<String> _selectedSymptoms;
  @override
  @JsonKey()
  List<String> get selectedSymptoms {
    if (_selectedSymptoms is EqualUnmodifiableListView)
      return _selectedSymptoms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_selectedSymptoms);
  }

  final List<String> _navigationHistory;
  @override
  @JsonKey()
  List<String> get navigationHistory {
    if (_navigationHistory is EqualUnmodifiableListView)
      return _navigationHistory;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_navigationHistory);
  }

  @override
  final String? currentSymptom;
  final List<ShortBowCalculation> _calculations;
  @override
  @JsonKey()
  List<ShortBowCalculation> get calculations {
    if (_calculations is EqualUnmodifiableListView) return _calculations;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_calculations);
  }

  @override
  final ShortBowStats? stats;
  @override
  @JsonKey()
  final bool isLoading;
  @override
  @JsonKey()
  final bool isNavigating;
  @override
  @JsonKey()
  final bool isCalculating;
  @override
  final String? error;

  @override
  String toString() {
    return 'ShortBowState(symptoms: $symptoms, topSymptoms: $topSymptoms, currentLinkedSymptoms: $currentLinkedSymptoms, selectedSymptoms: $selectedSymptoms, navigationHistory: $navigationHistory, currentSymptom: $currentSymptom, calculations: $calculations, stats: $stats, isLoading: $isLoading, isNavigating: $isNavigating, isCalculating: $isCalculating, error: $error)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ShortBowStateImpl &&
            const DeepCollectionEquality().equals(other._symptoms, _symptoms) &&
            const DeepCollectionEquality()
                .equals(other._topSymptoms, _topSymptoms) &&
            const DeepCollectionEquality()
                .equals(other._currentLinkedSymptoms, _currentLinkedSymptoms) &&
            const DeepCollectionEquality()
                .equals(other._selectedSymptoms, _selectedSymptoms) &&
            const DeepCollectionEquality()
                .equals(other._navigationHistory, _navigationHistory) &&
            (identical(other.currentSymptom, currentSymptom) ||
                other.currentSymptom == currentSymptom) &&
            const DeepCollectionEquality()
                .equals(other._calculations, _calculations) &&
            (identical(other.stats, stats) || other.stats == stats) &&
            (identical(other.isLoading, isLoading) ||
                other.isLoading == isLoading) &&
            (identical(other.isNavigating, isNavigating) ||
                other.isNavigating == isNavigating) &&
            (identical(other.isCalculating, isCalculating) ||
                other.isCalculating == isCalculating) &&
            (identical(other.error, error) || other.error == error));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(_symptoms),
      const DeepCollectionEquality().hash(_topSymptoms),
      const DeepCollectionEquality().hash(_currentLinkedSymptoms),
      const DeepCollectionEquality().hash(_selectedSymptoms),
      const DeepCollectionEquality().hash(_navigationHistory),
      currentSymptom,
      const DeepCollectionEquality().hash(_calculations),
      stats,
      isLoading,
      isNavigating,
      isCalculating,
      error);

  /// Create a copy of ShortBowState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ShortBowStateImplCopyWith<_$ShortBowStateImpl> get copyWith =>
      __$$ShortBowStateImplCopyWithImpl<_$ShortBowStateImpl>(this, _$identity);
}

abstract class _ShortBowState implements ShortBowState {
  const factory _ShortBowState(
      {final List<ShortBowSymptom> symptoms,
      final List<ShortBowSymptomLink> topSymptoms,
      final List<ShortBowSymptomLink> currentLinkedSymptoms,
      final List<String> selectedSymptoms,
      final List<String> navigationHistory,
      final String? currentSymptom,
      final List<ShortBowCalculation> calculations,
      final ShortBowStats? stats,
      final bool isLoading,
      final bool isNavigating,
      final bool isCalculating,
      final String? error}) = _$ShortBowStateImpl;

  @override
  List<ShortBowSymptom> get symptoms;
  @override
  List<ShortBowSymptomLink> get topSymptoms;
  @override
  List<ShortBowSymptomLink> get currentLinkedSymptoms;
  @override
  List<String> get selectedSymptoms;
  @override
  List<String> get navigationHistory;
  @override
  String? get currentSymptom;
  @override
  List<ShortBowCalculation> get calculations;
  @override
  ShortBowStats? get stats;
  @override
  bool get isLoading;
  @override
  bool get isNavigating;
  @override
  bool get isCalculating;
  @override
  String? get error;

  /// Create a copy of ShortBowState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ShortBowStateImplCopyWith<_$ShortBowStateImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
