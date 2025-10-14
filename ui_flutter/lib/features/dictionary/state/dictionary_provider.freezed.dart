// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'dictionary_provider.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

/// @nodoc
mixin _$DictionarySearchState {
  List<DictionaryTerm> get items => throw _privateConstructorUsedError;
  int get total => throw _privateConstructorUsedError;
  String get query => throw _privateConstructorUsedError;
  bool get isLoading => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;

  /// Create a copy of DictionarySearchState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DictionarySearchStateCopyWith<DictionarySearchState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DictionarySearchStateCopyWith<$Res> {
  factory $DictionarySearchStateCopyWith(DictionarySearchState value,
          $Res Function(DictionarySearchState) then) =
      _$DictionarySearchStateCopyWithImpl<$Res, DictionarySearchState>;
  @useResult
  $Res call(
      {List<DictionaryTerm> items,
      int total,
      String query,
      bool isLoading,
      String? error});
}

/// @nodoc
class _$DictionarySearchStateCopyWithImpl<$Res,
        $Val extends DictionarySearchState>
    implements $DictionarySearchStateCopyWith<$Res> {
  _$DictionarySearchStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DictionarySearchState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? items = null,
    Object? total = null,
    Object? query = null,
    Object? isLoading = null,
    Object? error = freezed,
  }) {
    return _then(_value.copyWith(
      items: null == items
          ? _value.items
          : items // ignore: cast_nullable_to_non_nullable
              as List<DictionaryTerm>,
      total: null == total
          ? _value.total
          : total // ignore: cast_nullable_to_non_nullable
              as int,
      query: null == query
          ? _value.query
          : query // ignore: cast_nullable_to_non_nullable
              as String,
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DictionarySearchStateImplCopyWith<$Res>
    implements $DictionarySearchStateCopyWith<$Res> {
  factory _$$DictionarySearchStateImplCopyWith(
          _$DictionarySearchStateImpl value,
          $Res Function(_$DictionarySearchStateImpl) then) =
      __$$DictionarySearchStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {List<DictionaryTerm> items,
      int total,
      String query,
      bool isLoading,
      String? error});
}

/// @nodoc
class __$$DictionarySearchStateImplCopyWithImpl<$Res>
    extends _$DictionarySearchStateCopyWithImpl<$Res,
        _$DictionarySearchStateImpl>
    implements _$$DictionarySearchStateImplCopyWith<$Res> {
  __$$DictionarySearchStateImplCopyWithImpl(_$DictionarySearchStateImpl _value,
      $Res Function(_$DictionarySearchStateImpl) _then)
      : super(_value, _then);

  /// Create a copy of DictionarySearchState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? items = null,
    Object? total = null,
    Object? query = null,
    Object? isLoading = null,
    Object? error = freezed,
  }) {
    return _then(_$DictionarySearchStateImpl(
      items: null == items
          ? _value._items
          : items // ignore: cast_nullable_to_non_nullable
              as List<DictionaryTerm>,
      total: null == total
          ? _value.total
          : total // ignore: cast_nullable_to_non_nullable
              as int,
      query: null == query
          ? _value.query
          : query // ignore: cast_nullable_to_non_nullable
              as String,
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc

class _$DictionarySearchStateImpl implements _DictionarySearchState {
  const _$DictionarySearchStateImpl(
      {final List<DictionaryTerm> items = const [],
      this.total = 0,
      this.query = '',
      this.isLoading = false,
      this.error})
      : _items = items;

  final List<DictionaryTerm> _items;
  @override
  @JsonKey()
  List<DictionaryTerm> get items {
    if (_items is EqualUnmodifiableListView) return _items;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_items);
  }

  @override
  @JsonKey()
  final int total;
  @override
  @JsonKey()
  final String query;
  @override
  @JsonKey()
  final bool isLoading;
  @override
  final String? error;

  @override
  String toString() {
    return 'DictionarySearchState(items: $items, total: $total, query: $query, isLoading: $isLoading, error: $error)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DictionarySearchStateImpl &&
            const DeepCollectionEquality().equals(other._items, _items) &&
            (identical(other.total, total) || other.total == total) &&
            (identical(other.query, query) || other.query == query) &&
            (identical(other.isLoading, isLoading) ||
                other.isLoading == isLoading) &&
            (identical(other.error, error) || other.error == error));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(_items),
      total,
      query,
      isLoading,
      error);

  /// Create a copy of DictionarySearchState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DictionarySearchStateImplCopyWith<_$DictionarySearchStateImpl>
      get copyWith => __$$DictionarySearchStateImplCopyWithImpl<
          _$DictionarySearchStateImpl>(this, _$identity);
}

abstract class _DictionarySearchState implements DictionarySearchState {
  const factory _DictionarySearchState(
      {final List<DictionaryTerm> items,
      final int total,
      final String query,
      final bool isLoading,
      final String? error}) = _$DictionarySearchStateImpl;

  @override
  List<DictionaryTerm> get items;
  @override
  int get total;
  @override
  String get query;
  @override
  bool get isLoading;
  @override
  String? get error;

  /// Create a copy of DictionarySearchState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DictionarySearchStateImplCopyWith<_$DictionarySearchStateImpl>
      get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
mixin _$TermDetailsState {
  DictionaryTerm? get term => throw _privateConstructorUsedError;
  DictionaryTreeRelationships? get relationships =>
      throw _privateConstructorUsedError;
  bool get isLoading => throw _privateConstructorUsedError;
  bool get isUpdating => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;

  /// Create a copy of TermDetailsState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $TermDetailsStateCopyWith<TermDetailsState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $TermDetailsStateCopyWith<$Res> {
  factory $TermDetailsStateCopyWith(
          TermDetailsState value, $Res Function(TermDetailsState) then) =
      _$TermDetailsStateCopyWithImpl<$Res, TermDetailsState>;
  @useResult
  $Res call(
      {DictionaryTerm? term,
      DictionaryTreeRelationships? relationships,
      bool isLoading,
      bool isUpdating,
      String? error});

  $DictionaryTermCopyWith<$Res>? get term;
  $DictionaryTreeRelationshipsCopyWith<$Res>? get relationships;
}

/// @nodoc
class _$TermDetailsStateCopyWithImpl<$Res, $Val extends TermDetailsState>
    implements $TermDetailsStateCopyWith<$Res> {
  _$TermDetailsStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of TermDetailsState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? term = freezed,
    Object? relationships = freezed,
    Object? isLoading = null,
    Object? isUpdating = null,
    Object? error = freezed,
  }) {
    return _then(_value.copyWith(
      term: freezed == term
          ? _value.term
          : term // ignore: cast_nullable_to_non_nullable
              as DictionaryTerm?,
      relationships: freezed == relationships
          ? _value.relationships
          : relationships // ignore: cast_nullable_to_non_nullable
              as DictionaryTreeRelationships?,
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      isUpdating: null == isUpdating
          ? _value.isUpdating
          : isUpdating // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }

  /// Create a copy of TermDetailsState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $DictionaryTermCopyWith<$Res>? get term {
    if (_value.term == null) {
      return null;
    }

    return $DictionaryTermCopyWith<$Res>(_value.term!, (value) {
      return _then(_value.copyWith(term: value) as $Val);
    });
  }

  /// Create a copy of TermDetailsState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $DictionaryTreeRelationshipsCopyWith<$Res>? get relationships {
    if (_value.relationships == null) {
      return null;
    }

    return $DictionaryTreeRelationshipsCopyWith<$Res>(_value.relationships!,
        (value) {
      return _then(_value.copyWith(relationships: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$TermDetailsStateImplCopyWith<$Res>
    implements $TermDetailsStateCopyWith<$Res> {
  factory _$$TermDetailsStateImplCopyWith(_$TermDetailsStateImpl value,
          $Res Function(_$TermDetailsStateImpl) then) =
      __$$TermDetailsStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {DictionaryTerm? term,
      DictionaryTreeRelationships? relationships,
      bool isLoading,
      bool isUpdating,
      String? error});

  @override
  $DictionaryTermCopyWith<$Res>? get term;
  @override
  $DictionaryTreeRelationshipsCopyWith<$Res>? get relationships;
}

/// @nodoc
class __$$TermDetailsStateImplCopyWithImpl<$Res>
    extends _$TermDetailsStateCopyWithImpl<$Res, _$TermDetailsStateImpl>
    implements _$$TermDetailsStateImplCopyWith<$Res> {
  __$$TermDetailsStateImplCopyWithImpl(_$TermDetailsStateImpl _value,
      $Res Function(_$TermDetailsStateImpl) _then)
      : super(_value, _then);

  /// Create a copy of TermDetailsState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? term = freezed,
    Object? relationships = freezed,
    Object? isLoading = null,
    Object? isUpdating = null,
    Object? error = freezed,
  }) {
    return _then(_$TermDetailsStateImpl(
      term: freezed == term
          ? _value.term
          : term // ignore: cast_nullable_to_non_nullable
              as DictionaryTerm?,
      relationships: freezed == relationships
          ? _value.relationships
          : relationships // ignore: cast_nullable_to_non_nullable
              as DictionaryTreeRelationships?,
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      isUpdating: null == isUpdating
          ? _value.isUpdating
          : isUpdating // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc

class _$TermDetailsStateImpl implements _TermDetailsState {
  const _$TermDetailsStateImpl(
      {this.term,
      this.relationships,
      this.isLoading = false,
      this.isUpdating = false,
      this.error});

  @override
  final DictionaryTerm? term;
  @override
  final DictionaryTreeRelationships? relationships;
  @override
  @JsonKey()
  final bool isLoading;
  @override
  @JsonKey()
  final bool isUpdating;
  @override
  final String? error;

  @override
  String toString() {
    return 'TermDetailsState(term: $term, relationships: $relationships, isLoading: $isLoading, isUpdating: $isUpdating, error: $error)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$TermDetailsStateImpl &&
            (identical(other.term, term) || other.term == term) &&
            (identical(other.relationships, relationships) ||
                other.relationships == relationships) &&
            (identical(other.isLoading, isLoading) ||
                other.isLoading == isLoading) &&
            (identical(other.isUpdating, isUpdating) ||
                other.isUpdating == isUpdating) &&
            (identical(other.error, error) || other.error == error));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType, term, relationships, isLoading, isUpdating, error);

  /// Create a copy of TermDetailsState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$TermDetailsStateImplCopyWith<_$TermDetailsStateImpl> get copyWith =>
      __$$TermDetailsStateImplCopyWithImpl<_$TermDetailsStateImpl>(
          this, _$identity);
}

abstract class _TermDetailsState implements TermDetailsState {
  const factory _TermDetailsState(
      {final DictionaryTerm? term,
      final DictionaryTreeRelationships? relationships,
      final bool isLoading,
      final bool isUpdating,
      final String? error}) = _$TermDetailsStateImpl;

  @override
  DictionaryTerm? get term;
  @override
  DictionaryTreeRelationships? get relationships;
  @override
  bool get isLoading;
  @override
  bool get isUpdating;
  @override
  String? get error;

  /// Create a copy of TermDetailsState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$TermDetailsStateImplCopyWith<_$TermDetailsStateImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
mixin _$DictionaryStatsState {
  DictionaryStats? get stats => throw _privateConstructorUsedError;
  bool get isLoading => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;

  /// Create a copy of DictionaryStatsState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DictionaryStatsStateCopyWith<DictionaryStatsState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DictionaryStatsStateCopyWith<$Res> {
  factory $DictionaryStatsStateCopyWith(DictionaryStatsState value,
          $Res Function(DictionaryStatsState) then) =
      _$DictionaryStatsStateCopyWithImpl<$Res, DictionaryStatsState>;
  @useResult
  $Res call({DictionaryStats? stats, bool isLoading, String? error});

  $DictionaryStatsCopyWith<$Res>? get stats;
}

/// @nodoc
class _$DictionaryStatsStateCopyWithImpl<$Res,
        $Val extends DictionaryStatsState>
    implements $DictionaryStatsStateCopyWith<$Res> {
  _$DictionaryStatsStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DictionaryStatsState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? stats = freezed,
    Object? isLoading = null,
    Object? error = freezed,
  }) {
    return _then(_value.copyWith(
      stats: freezed == stats
          ? _value.stats
          : stats // ignore: cast_nullable_to_non_nullable
              as DictionaryStats?,
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }

  /// Create a copy of DictionaryStatsState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $DictionaryStatsCopyWith<$Res>? get stats {
    if (_value.stats == null) {
      return null;
    }

    return $DictionaryStatsCopyWith<$Res>(_value.stats!, (value) {
      return _then(_value.copyWith(stats: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$DictionaryStatsStateImplCopyWith<$Res>
    implements $DictionaryStatsStateCopyWith<$Res> {
  factory _$$DictionaryStatsStateImplCopyWith(_$DictionaryStatsStateImpl value,
          $Res Function(_$DictionaryStatsStateImpl) then) =
      __$$DictionaryStatsStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({DictionaryStats? stats, bool isLoading, String? error});

  @override
  $DictionaryStatsCopyWith<$Res>? get stats;
}

/// @nodoc
class __$$DictionaryStatsStateImplCopyWithImpl<$Res>
    extends _$DictionaryStatsStateCopyWithImpl<$Res, _$DictionaryStatsStateImpl>
    implements _$$DictionaryStatsStateImplCopyWith<$Res> {
  __$$DictionaryStatsStateImplCopyWithImpl(_$DictionaryStatsStateImpl _value,
      $Res Function(_$DictionaryStatsStateImpl) _then)
      : super(_value, _then);

  /// Create a copy of DictionaryStatsState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? stats = freezed,
    Object? isLoading = null,
    Object? error = freezed,
  }) {
    return _then(_$DictionaryStatsStateImpl(
      stats: freezed == stats
          ? _value.stats
          : stats // ignore: cast_nullable_to_non_nullable
              as DictionaryStats?,
      isLoading: null == isLoading
          ? _value.isLoading
          : isLoading // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc

class _$DictionaryStatsStateImpl implements _DictionaryStatsState {
  const _$DictionaryStatsStateImpl(
      {this.stats, this.isLoading = false, this.error});

  @override
  final DictionaryStats? stats;
  @override
  @JsonKey()
  final bool isLoading;
  @override
  final String? error;

  @override
  String toString() {
    return 'DictionaryStatsState(stats: $stats, isLoading: $isLoading, error: $error)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DictionaryStatsStateImpl &&
            (identical(other.stats, stats) || other.stats == stats) &&
            (identical(other.isLoading, isLoading) ||
                other.isLoading == isLoading) &&
            (identical(other.error, error) || other.error == error));
  }

  @override
  int get hashCode => Object.hash(runtimeType, stats, isLoading, error);

  /// Create a copy of DictionaryStatsState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DictionaryStatsStateImplCopyWith<_$DictionaryStatsStateImpl>
      get copyWith =>
          __$$DictionaryStatsStateImplCopyWithImpl<_$DictionaryStatsStateImpl>(
              this, _$identity);
}

abstract class _DictionaryStatsState implements DictionaryStatsState {
  const factory _DictionaryStatsState(
      {final DictionaryStats? stats,
      final bool isLoading,
      final String? error}) = _$DictionaryStatsStateImpl;

  @override
  DictionaryStats? get stats;
  @override
  bool get isLoading;
  @override
  String? get error;

  /// Create a copy of DictionaryStatsState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DictionaryStatsStateImplCopyWith<_$DictionaryStatsStateImpl>
      get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
mixin _$DictionaryExportState {
  bool get isExporting => throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;

  /// Create a copy of DictionaryExportState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DictionaryExportStateCopyWith<DictionaryExportState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DictionaryExportStateCopyWith<$Res> {
  factory $DictionaryExportStateCopyWith(DictionaryExportState value,
          $Res Function(DictionaryExportState) then) =
      _$DictionaryExportStateCopyWithImpl<$Res, DictionaryExportState>;
  @useResult
  $Res call({bool isExporting, String? error});
}

/// @nodoc
class _$DictionaryExportStateCopyWithImpl<$Res,
        $Val extends DictionaryExportState>
    implements $DictionaryExportStateCopyWith<$Res> {
  _$DictionaryExportStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DictionaryExportState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? isExporting = null,
    Object? error = freezed,
  }) {
    return _then(_value.copyWith(
      isExporting: null == isExporting
          ? _value.isExporting
          : isExporting // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DictionaryExportStateImplCopyWith<$Res>
    implements $DictionaryExportStateCopyWith<$Res> {
  factory _$$DictionaryExportStateImplCopyWith(
          _$DictionaryExportStateImpl value,
          $Res Function(_$DictionaryExportStateImpl) then) =
      __$$DictionaryExportStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({bool isExporting, String? error});
}

/// @nodoc
class __$$DictionaryExportStateImplCopyWithImpl<$Res>
    extends _$DictionaryExportStateCopyWithImpl<$Res,
        _$DictionaryExportStateImpl>
    implements _$$DictionaryExportStateImplCopyWith<$Res> {
  __$$DictionaryExportStateImplCopyWithImpl(_$DictionaryExportStateImpl _value,
      $Res Function(_$DictionaryExportStateImpl) _then)
      : super(_value, _then);

  /// Create a copy of DictionaryExportState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? isExporting = null,
    Object? error = freezed,
  }) {
    return _then(_$DictionaryExportStateImpl(
      isExporting: null == isExporting
          ? _value.isExporting
          : isExporting // ignore: cast_nullable_to_non_nullable
              as bool,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc

class _$DictionaryExportStateImpl implements _DictionaryExportState {
  const _$DictionaryExportStateImpl({this.isExporting = false, this.error});

  @override
  @JsonKey()
  final bool isExporting;
  @override
  final String? error;

  @override
  String toString() {
    return 'DictionaryExportState(isExporting: $isExporting, error: $error)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DictionaryExportStateImpl &&
            (identical(other.isExporting, isExporting) ||
                other.isExporting == isExporting) &&
            (identical(other.error, error) || other.error == error));
  }

  @override
  int get hashCode => Object.hash(runtimeType, isExporting, error);

  /// Create a copy of DictionaryExportState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DictionaryExportStateImplCopyWith<_$DictionaryExportStateImpl>
      get copyWith => __$$DictionaryExportStateImplCopyWithImpl<
          _$DictionaryExportStateImpl>(this, _$identity);
}

abstract class _DictionaryExportState implements DictionaryExportState {
  const factory _DictionaryExportState(
      {final bool isExporting,
      final String? error}) = _$DictionaryExportStateImpl;

  @override
  bool get isExporting;
  @override
  String? get error;

  /// Create a copy of DictionaryExportState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DictionaryExportStateImplCopyWith<_$DictionaryExportStateImpl>
      get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
mixin _$DictionaryUploadState {
  bool get isUploading => throw _privateConstructorUsedError;
  bool get isValidating => throw _privateConstructorUsedError;
  Map<String, dynamic>? get uploadResult => throw _privateConstructorUsedError;
  Map<String, dynamic>? get validationResult =>
      throw _privateConstructorUsedError;
  String? get error => throw _privateConstructorUsedError;

  /// Create a copy of DictionaryUploadState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DictionaryUploadStateCopyWith<DictionaryUploadState> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DictionaryUploadStateCopyWith<$Res> {
  factory $DictionaryUploadStateCopyWith(DictionaryUploadState value,
          $Res Function(DictionaryUploadState) then) =
      _$DictionaryUploadStateCopyWithImpl<$Res, DictionaryUploadState>;
  @useResult
  $Res call(
      {bool isUploading,
      bool isValidating,
      Map<String, dynamic>? uploadResult,
      Map<String, dynamic>? validationResult,
      String? error});
}

/// @nodoc
class _$DictionaryUploadStateCopyWithImpl<$Res,
        $Val extends DictionaryUploadState>
    implements $DictionaryUploadStateCopyWith<$Res> {
  _$DictionaryUploadStateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DictionaryUploadState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? isUploading = null,
    Object? isValidating = null,
    Object? uploadResult = freezed,
    Object? validationResult = freezed,
    Object? error = freezed,
  }) {
    return _then(_value.copyWith(
      isUploading: null == isUploading
          ? _value.isUploading
          : isUploading // ignore: cast_nullable_to_non_nullable
              as bool,
      isValidating: null == isValidating
          ? _value.isValidating
          : isValidating // ignore: cast_nullable_to_non_nullable
              as bool,
      uploadResult: freezed == uploadResult
          ? _value.uploadResult
          : uploadResult // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      validationResult: freezed == validationResult
          ? _value.validationResult
          : validationResult // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DictionaryUploadStateImplCopyWith<$Res>
    implements $DictionaryUploadStateCopyWith<$Res> {
  factory _$$DictionaryUploadStateImplCopyWith(
          _$DictionaryUploadStateImpl value,
          $Res Function(_$DictionaryUploadStateImpl) then) =
      __$$DictionaryUploadStateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool isUploading,
      bool isValidating,
      Map<String, dynamic>? uploadResult,
      Map<String, dynamic>? validationResult,
      String? error});
}

/// @nodoc
class __$$DictionaryUploadStateImplCopyWithImpl<$Res>
    extends _$DictionaryUploadStateCopyWithImpl<$Res,
        _$DictionaryUploadStateImpl>
    implements _$$DictionaryUploadStateImplCopyWith<$Res> {
  __$$DictionaryUploadStateImplCopyWithImpl(_$DictionaryUploadStateImpl _value,
      $Res Function(_$DictionaryUploadStateImpl) _then)
      : super(_value, _then);

  /// Create a copy of DictionaryUploadState
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? isUploading = null,
    Object? isValidating = null,
    Object? uploadResult = freezed,
    Object? validationResult = freezed,
    Object? error = freezed,
  }) {
    return _then(_$DictionaryUploadStateImpl(
      isUploading: null == isUploading
          ? _value.isUploading
          : isUploading // ignore: cast_nullable_to_non_nullable
              as bool,
      isValidating: null == isValidating
          ? _value.isValidating
          : isValidating // ignore: cast_nullable_to_non_nullable
              as bool,
      uploadResult: freezed == uploadResult
          ? _value._uploadResult
          : uploadResult // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      validationResult: freezed == validationResult
          ? _value._validationResult
          : validationResult // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      error: freezed == error
          ? _value.error
          : error // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc

class _$DictionaryUploadStateImpl implements _DictionaryUploadState {
  const _$DictionaryUploadStateImpl(
      {this.isUploading = false,
      this.isValidating = false,
      final Map<String, dynamic>? uploadResult,
      final Map<String, dynamic>? validationResult,
      this.error})
      : _uploadResult = uploadResult,
        _validationResult = validationResult;

  @override
  @JsonKey()
  final bool isUploading;
  @override
  @JsonKey()
  final bool isValidating;
  final Map<String, dynamic>? _uploadResult;
  @override
  Map<String, dynamic>? get uploadResult {
    final value = _uploadResult;
    if (value == null) return null;
    if (_uploadResult is EqualUnmodifiableMapView) return _uploadResult;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  final Map<String, dynamic>? _validationResult;
  @override
  Map<String, dynamic>? get validationResult {
    final value = _validationResult;
    if (value == null) return null;
    if (_validationResult is EqualUnmodifiableMapView) return _validationResult;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  final String? error;

  @override
  String toString() {
    return 'DictionaryUploadState(isUploading: $isUploading, isValidating: $isValidating, uploadResult: $uploadResult, validationResult: $validationResult, error: $error)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DictionaryUploadStateImpl &&
            (identical(other.isUploading, isUploading) ||
                other.isUploading == isUploading) &&
            (identical(other.isValidating, isValidating) ||
                other.isValidating == isValidating) &&
            const DeepCollectionEquality()
                .equals(other._uploadResult, _uploadResult) &&
            const DeepCollectionEquality()
                .equals(other._validationResult, _validationResult) &&
            (identical(other.error, error) || other.error == error));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      isUploading,
      isValidating,
      const DeepCollectionEquality().hash(_uploadResult),
      const DeepCollectionEquality().hash(_validationResult),
      error);

  /// Create a copy of DictionaryUploadState
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DictionaryUploadStateImplCopyWith<_$DictionaryUploadStateImpl>
      get copyWith => __$$DictionaryUploadStateImplCopyWithImpl<
          _$DictionaryUploadStateImpl>(this, _$identity);
}

abstract class _DictionaryUploadState implements DictionaryUploadState {
  const factory _DictionaryUploadState(
      {final bool isUploading,
      final bool isValidating,
      final Map<String, dynamic>? uploadResult,
      final Map<String, dynamic>? validationResult,
      final String? error}) = _$DictionaryUploadStateImpl;

  @override
  bool get isUploading;
  @override
  bool get isValidating;
  @override
  Map<String, dynamic>? get uploadResult;
  @override
  Map<String, dynamic>? get validationResult;
  @override
  String? get error;

  /// Create a copy of DictionaryUploadState
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DictionaryUploadStateImplCopyWith<_$DictionaryUploadStateImpl>
      get copyWith => throw _privateConstructorUsedError;
}
