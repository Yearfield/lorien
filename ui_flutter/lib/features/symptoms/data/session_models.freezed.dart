// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'session_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

SessionContext _$SessionContextFromJson(Map<String, dynamic> json) {
  return _SessionContext.fromJson(json);
}

/// @nodoc
mixin _$SessionContext {
  DateTime get timestamp => throw _privateConstructorUsedError;
  Map<String, dynamic> get uiState => throw _privateConstructorUsedError;
  Map<String, dynamic> get filters => throw _privateConstructorUsedError;
  List<String> get recentSheets => throw _privateConstructorUsedError;
  String? get lastEditedSheet => throw _privateConstructorUsedError;
  Map<String, dynamic>? get userPreferences =>
      throw _privateConstructorUsedError;

  /// Serializes this SessionContext to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SessionContext
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SessionContextCopyWith<SessionContext> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SessionContextCopyWith<$Res> {
  factory $SessionContextCopyWith(
          SessionContext value, $Res Function(SessionContext) then) =
      _$SessionContextCopyWithImpl<$Res, SessionContext>;
  @useResult
  $Res call(
      {DateTime timestamp,
      Map<String, dynamic> uiState,
      Map<String, dynamic> filters,
      List<String> recentSheets,
      String? lastEditedSheet,
      Map<String, dynamic>? userPreferences});
}

/// @nodoc
class _$SessionContextCopyWithImpl<$Res, $Val extends SessionContext>
    implements $SessionContextCopyWith<$Res> {
  _$SessionContextCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SessionContext
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? timestamp = null,
    Object? uiState = null,
    Object? filters = null,
    Object? recentSheets = null,
    Object? lastEditedSheet = freezed,
    Object? userPreferences = freezed,
  }) {
    return _then(_value.copyWith(
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      uiState: null == uiState
          ? _value.uiState
          : uiState // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      filters: null == filters
          ? _value.filters
          : filters // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      recentSheets: null == recentSheets
          ? _value.recentSheets
          : recentSheets // ignore: cast_nullable_to_non_nullable
              as List<String>,
      lastEditedSheet: freezed == lastEditedSheet
          ? _value.lastEditedSheet
          : lastEditedSheet // ignore: cast_nullable_to_non_nullable
              as String?,
      userPreferences: freezed == userPreferences
          ? _value.userPreferences
          : userPreferences // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SessionContextImplCopyWith<$Res>
    implements $SessionContextCopyWith<$Res> {
  factory _$$SessionContextImplCopyWith(_$SessionContextImpl value,
          $Res Function(_$SessionContextImpl) then) =
      __$$SessionContextImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {DateTime timestamp,
      Map<String, dynamic> uiState,
      Map<String, dynamic> filters,
      List<String> recentSheets,
      String? lastEditedSheet,
      Map<String, dynamic>? userPreferences});
}

/// @nodoc
class __$$SessionContextImplCopyWithImpl<$Res>
    extends _$SessionContextCopyWithImpl<$Res, _$SessionContextImpl>
    implements _$$SessionContextImplCopyWith<$Res> {
  __$$SessionContextImplCopyWithImpl(
      _$SessionContextImpl _value, $Res Function(_$SessionContextImpl) _then)
      : super(_value, _then);

  /// Create a copy of SessionContext
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? timestamp = null,
    Object? uiState = null,
    Object? filters = null,
    Object? recentSheets = null,
    Object? lastEditedSheet = freezed,
    Object? userPreferences = freezed,
  }) {
    return _then(_$SessionContextImpl(
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      uiState: null == uiState
          ? _value._uiState
          : uiState // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      filters: null == filters
          ? _value._filters
          : filters // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      recentSheets: null == recentSheets
          ? _value._recentSheets
          : recentSheets // ignore: cast_nullable_to_non_nullable
              as List<String>,
      lastEditedSheet: freezed == lastEditedSheet
          ? _value.lastEditedSheet
          : lastEditedSheet // ignore: cast_nullable_to_non_nullable
              as String?,
      userPreferences: freezed == userPreferences
          ? _value._userPreferences
          : userPreferences // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SessionContextImpl implements _SessionContext {
  const _$SessionContextImpl(
      {required this.timestamp,
      required final Map<String, dynamic> uiState,
      required final Map<String, dynamic> filters,
      required final List<String> recentSheets,
      this.lastEditedSheet,
      final Map<String, dynamic>? userPreferences})
      : _uiState = uiState,
        _filters = filters,
        _recentSheets = recentSheets,
        _userPreferences = userPreferences;

  factory _$SessionContextImpl.fromJson(Map<String, dynamic> json) =>
      _$$SessionContextImplFromJson(json);

  @override
  final DateTime timestamp;
  final Map<String, dynamic> _uiState;
  @override
  Map<String, dynamic> get uiState {
    if (_uiState is EqualUnmodifiableMapView) return _uiState;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_uiState);
  }

  final Map<String, dynamic> _filters;
  @override
  Map<String, dynamic> get filters {
    if (_filters is EqualUnmodifiableMapView) return _filters;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_filters);
  }

  final List<String> _recentSheets;
  @override
  List<String> get recentSheets {
    if (_recentSheets is EqualUnmodifiableListView) return _recentSheets;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_recentSheets);
  }

  @override
  final String? lastEditedSheet;
  final Map<String, dynamic>? _userPreferences;
  @override
  Map<String, dynamic>? get userPreferences {
    final value = _userPreferences;
    if (value == null) return null;
    if (_userPreferences is EqualUnmodifiableMapView) return _userPreferences;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'SessionContext(timestamp: $timestamp, uiState: $uiState, filters: $filters, recentSheets: $recentSheets, lastEditedSheet: $lastEditedSheet, userPreferences: $userPreferences)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SessionContextImpl &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            const DeepCollectionEquality().equals(other._uiState, _uiState) &&
            const DeepCollectionEquality().equals(other._filters, _filters) &&
            const DeepCollectionEquality()
                .equals(other._recentSheets, _recentSheets) &&
            (identical(other.lastEditedSheet, lastEditedSheet) ||
                other.lastEditedSheet == lastEditedSheet) &&
            const DeepCollectionEquality()
                .equals(other._userPreferences, _userPreferences));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      timestamp,
      const DeepCollectionEquality().hash(_uiState),
      const DeepCollectionEquality().hash(_filters),
      const DeepCollectionEquality().hash(_recentSheets),
      lastEditedSheet,
      const DeepCollectionEquality().hash(_userPreferences));

  /// Create a copy of SessionContext
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SessionContextImplCopyWith<_$SessionContextImpl> get copyWith =>
      __$$SessionContextImplCopyWithImpl<_$SessionContextImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SessionContextImplToJson(
      this,
    );
  }
}

abstract class _SessionContext implements SessionContext {
  const factory _SessionContext(
      {required final DateTime timestamp,
      required final Map<String, dynamic> uiState,
      required final Map<String, dynamic> filters,
      required final List<String> recentSheets,
      final String? lastEditedSheet,
      final Map<String, dynamic>? userPreferences}) = _$SessionContextImpl;

  factory _SessionContext.fromJson(Map<String, dynamic> json) =
      _$SessionContextImpl.fromJson;

  @override
  DateTime get timestamp;
  @override
  Map<String, dynamic> get uiState;
  @override
  Map<String, dynamic> get filters;
  @override
  List<String> get recentSheets;
  @override
  String? get lastEditedSheet;
  @override
  Map<String, dynamic>? get userPreferences;

  /// Create a copy of SessionContext
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SessionContextImplCopyWith<_$SessionContextImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

WorkbookSnapshot _$WorkbookSnapshotFromJson(Map<String, dynamic> json) {
  return _WorkbookSnapshot.fromJson(json);
}

/// @nodoc
mixin _$WorkbookSnapshot {
  String get name => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;
  Map<String, dynamic> get data => throw _privateConstructorUsedError;
  List<SheetSnapshot> get sheets => throw _privateConstructorUsedError;
  Map<String, dynamic>? get metadata => throw _privateConstructorUsedError;

  /// Serializes this WorkbookSnapshot to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of WorkbookSnapshot
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $WorkbookSnapshotCopyWith<WorkbookSnapshot> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $WorkbookSnapshotCopyWith<$Res> {
  factory $WorkbookSnapshotCopyWith(
          WorkbookSnapshot value, $Res Function(WorkbookSnapshot) then) =
      _$WorkbookSnapshotCopyWithImpl<$Res, WorkbookSnapshot>;
  @useResult
  $Res call(
      {String name,
      DateTime createdAt,
      Map<String, dynamic> data,
      List<SheetSnapshot> sheets,
      Map<String, dynamic>? metadata});
}

/// @nodoc
class _$WorkbookSnapshotCopyWithImpl<$Res, $Val extends WorkbookSnapshot>
    implements $WorkbookSnapshotCopyWith<$Res> {
  _$WorkbookSnapshotCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of WorkbookSnapshot
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? createdAt = null,
    Object? data = null,
    Object? sheets = null,
    Object? metadata = freezed,
  }) {
    return _then(_value.copyWith(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      data: null == data
          ? _value.data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      sheets: null == sheets
          ? _value.sheets
          : sheets // ignore: cast_nullable_to_non_nullable
              as List<SheetSnapshot>,
      metadata: freezed == metadata
          ? _value.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$WorkbookSnapshotImplCopyWith<$Res>
    implements $WorkbookSnapshotCopyWith<$Res> {
  factory _$$WorkbookSnapshotImplCopyWith(_$WorkbookSnapshotImpl value,
          $Res Function(_$WorkbookSnapshotImpl) then) =
      __$$WorkbookSnapshotImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String name,
      DateTime createdAt,
      Map<String, dynamic> data,
      List<SheetSnapshot> sheets,
      Map<String, dynamic>? metadata});
}

/// @nodoc
class __$$WorkbookSnapshotImplCopyWithImpl<$Res>
    extends _$WorkbookSnapshotCopyWithImpl<$Res, _$WorkbookSnapshotImpl>
    implements _$$WorkbookSnapshotImplCopyWith<$Res> {
  __$$WorkbookSnapshotImplCopyWithImpl(_$WorkbookSnapshotImpl _value,
      $Res Function(_$WorkbookSnapshotImpl) _then)
      : super(_value, _then);

  /// Create a copy of WorkbookSnapshot
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? createdAt = null,
    Object? data = null,
    Object? sheets = null,
    Object? metadata = freezed,
  }) {
    return _then(_$WorkbookSnapshotImpl(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      data: null == data
          ? _value._data
          : data // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      sheets: null == sheets
          ? _value._sheets
          : sheets // ignore: cast_nullable_to_non_nullable
              as List<SheetSnapshot>,
      metadata: freezed == metadata
          ? _value._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$WorkbookSnapshotImpl implements _WorkbookSnapshot {
  const _$WorkbookSnapshotImpl(
      {required this.name,
      required this.createdAt,
      required final Map<String, dynamic> data,
      required final List<SheetSnapshot> sheets,
      final Map<String, dynamic>? metadata})
      : _data = data,
        _sheets = sheets,
        _metadata = metadata;

  factory _$WorkbookSnapshotImpl.fromJson(Map<String, dynamic> json) =>
      _$$WorkbookSnapshotImplFromJson(json);

  @override
  final String name;
  @override
  final DateTime createdAt;
  final Map<String, dynamic> _data;
  @override
  Map<String, dynamic> get data {
    if (_data is EqualUnmodifiableMapView) return _data;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_data);
  }

  final List<SheetSnapshot> _sheets;
  @override
  List<SheetSnapshot> get sheets {
    if (_sheets is EqualUnmodifiableListView) return _sheets;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_sheets);
  }

  final Map<String, dynamic>? _metadata;
  @override
  Map<String, dynamic>? get metadata {
    final value = _metadata;
    if (value == null) return null;
    if (_metadata is EqualUnmodifiableMapView) return _metadata;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'WorkbookSnapshot(name: $name, createdAt: $createdAt, data: $data, sheets: $sheets, metadata: $metadata)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$WorkbookSnapshotImpl &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            const DeepCollectionEquality().equals(other._data, _data) &&
            const DeepCollectionEquality().equals(other._sheets, _sheets) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      name,
      createdAt,
      const DeepCollectionEquality().hash(_data),
      const DeepCollectionEquality().hash(_sheets),
      const DeepCollectionEquality().hash(_metadata));

  /// Create a copy of WorkbookSnapshot
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$WorkbookSnapshotImplCopyWith<_$WorkbookSnapshotImpl> get copyWith =>
      __$$WorkbookSnapshotImplCopyWithImpl<_$WorkbookSnapshotImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$WorkbookSnapshotImplToJson(
      this,
    );
  }
}

abstract class _WorkbookSnapshot implements WorkbookSnapshot {
  const factory _WorkbookSnapshot(
      {required final String name,
      required final DateTime createdAt,
      required final Map<String, dynamic> data,
      required final List<SheetSnapshot> sheets,
      final Map<String, dynamic>? metadata}) = _$WorkbookSnapshotImpl;

  factory _WorkbookSnapshot.fromJson(Map<String, dynamic> json) =
      _$WorkbookSnapshotImpl.fromJson;

  @override
  String get name;
  @override
  DateTime get createdAt;
  @override
  Map<String, dynamic> get data;
  @override
  List<SheetSnapshot> get sheets;
  @override
  Map<String, dynamic>? get metadata;

  /// Create a copy of WorkbookSnapshot
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$WorkbookSnapshotImplCopyWith<_$WorkbookSnapshotImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

SheetSnapshot _$SheetSnapshotFromJson(Map<String, dynamic> json) {
  return _SheetSnapshot.fromJson(json);
}

/// @nodoc
mixin _$SheetSnapshot {
  String get name => throw _privateConstructorUsedError;
  DateTime get lastModified => throw _privateConstructorUsedError;
  Map<String, dynamic> get treeData => throw _privateConstructorUsedError;
  List<String> get vitalMeasurements => throw _privateConstructorUsedError;
  Map<String, dynamic>? get overrides => throw _privateConstructorUsedError;

  /// Serializes this SheetSnapshot to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SheetSnapshot
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SheetSnapshotCopyWith<SheetSnapshot> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SheetSnapshotCopyWith<$Res> {
  factory $SheetSnapshotCopyWith(
          SheetSnapshot value, $Res Function(SheetSnapshot) then) =
      _$SheetSnapshotCopyWithImpl<$Res, SheetSnapshot>;
  @useResult
  $Res call(
      {String name,
      DateTime lastModified,
      Map<String, dynamic> treeData,
      List<String> vitalMeasurements,
      Map<String, dynamic>? overrides});
}

/// @nodoc
class _$SheetSnapshotCopyWithImpl<$Res, $Val extends SheetSnapshot>
    implements $SheetSnapshotCopyWith<$Res> {
  _$SheetSnapshotCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SheetSnapshot
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? lastModified = null,
    Object? treeData = null,
    Object? vitalMeasurements = null,
    Object? overrides = freezed,
  }) {
    return _then(_value.copyWith(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      lastModified: null == lastModified
          ? _value.lastModified
          : lastModified // ignore: cast_nullable_to_non_nullable
              as DateTime,
      treeData: null == treeData
          ? _value.treeData
          : treeData // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      vitalMeasurements: null == vitalMeasurements
          ? _value.vitalMeasurements
          : vitalMeasurements // ignore: cast_nullable_to_non_nullable
              as List<String>,
      overrides: freezed == overrides
          ? _value.overrides
          : overrides // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SheetSnapshotImplCopyWith<$Res>
    implements $SheetSnapshotCopyWith<$Res> {
  factory _$$SheetSnapshotImplCopyWith(
          _$SheetSnapshotImpl value, $Res Function(_$SheetSnapshotImpl) then) =
      __$$SheetSnapshotImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String name,
      DateTime lastModified,
      Map<String, dynamic> treeData,
      List<String> vitalMeasurements,
      Map<String, dynamic>? overrides});
}

/// @nodoc
class __$$SheetSnapshotImplCopyWithImpl<$Res>
    extends _$SheetSnapshotCopyWithImpl<$Res, _$SheetSnapshotImpl>
    implements _$$SheetSnapshotImplCopyWith<$Res> {
  __$$SheetSnapshotImplCopyWithImpl(
      _$SheetSnapshotImpl _value, $Res Function(_$SheetSnapshotImpl) _then)
      : super(_value, _then);

  /// Create a copy of SheetSnapshot
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? lastModified = null,
    Object? treeData = null,
    Object? vitalMeasurements = null,
    Object? overrides = freezed,
  }) {
    return _then(_$SheetSnapshotImpl(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      lastModified: null == lastModified
          ? _value.lastModified
          : lastModified // ignore: cast_nullable_to_non_nullable
              as DateTime,
      treeData: null == treeData
          ? _value._treeData
          : treeData // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      vitalMeasurements: null == vitalMeasurements
          ? _value._vitalMeasurements
          : vitalMeasurements // ignore: cast_nullable_to_non_nullable
              as List<String>,
      overrides: freezed == overrides
          ? _value._overrides
          : overrides // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SheetSnapshotImpl implements _SheetSnapshot {
  const _$SheetSnapshotImpl(
      {required this.name,
      required this.lastModified,
      required final Map<String, dynamic> treeData,
      required final List<String> vitalMeasurements,
      final Map<String, dynamic>? overrides})
      : _treeData = treeData,
        _vitalMeasurements = vitalMeasurements,
        _overrides = overrides;

  factory _$SheetSnapshotImpl.fromJson(Map<String, dynamic> json) =>
      _$$SheetSnapshotImplFromJson(json);

  @override
  final String name;
  @override
  final DateTime lastModified;
  final Map<String, dynamic> _treeData;
  @override
  Map<String, dynamic> get treeData {
    if (_treeData is EqualUnmodifiableMapView) return _treeData;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_treeData);
  }

  final List<String> _vitalMeasurements;
  @override
  List<String> get vitalMeasurements {
    if (_vitalMeasurements is EqualUnmodifiableListView)
      return _vitalMeasurements;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_vitalMeasurements);
  }

  final Map<String, dynamic>? _overrides;
  @override
  Map<String, dynamic>? get overrides {
    final value = _overrides;
    if (value == null) return null;
    if (_overrides is EqualUnmodifiableMapView) return _overrides;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'SheetSnapshot(name: $name, lastModified: $lastModified, treeData: $treeData, vitalMeasurements: $vitalMeasurements, overrides: $overrides)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SheetSnapshotImpl &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.lastModified, lastModified) ||
                other.lastModified == lastModified) &&
            const DeepCollectionEquality().equals(other._treeData, _treeData) &&
            const DeepCollectionEquality()
                .equals(other._vitalMeasurements, _vitalMeasurements) &&
            const DeepCollectionEquality()
                .equals(other._overrides, _overrides));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      name,
      lastModified,
      const DeepCollectionEquality().hash(_treeData),
      const DeepCollectionEquality().hash(_vitalMeasurements),
      const DeepCollectionEquality().hash(_overrides));

  /// Create a copy of SheetSnapshot
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SheetSnapshotImplCopyWith<_$SheetSnapshotImpl> get copyWith =>
      __$$SheetSnapshotImplCopyWithImpl<_$SheetSnapshotImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SheetSnapshotImplToJson(
      this,
    );
  }
}

abstract class _SheetSnapshot implements SheetSnapshot {
  const factory _SheetSnapshot(
      {required final String name,
      required final DateTime lastModified,
      required final Map<String, dynamic> treeData,
      required final List<String> vitalMeasurements,
      final Map<String, dynamic>? overrides}) = _$SheetSnapshotImpl;

  factory _SheetSnapshot.fromJson(Map<String, dynamic> json) =
      _$SheetSnapshotImpl.fromJson;

  @override
  String get name;
  @override
  DateTime get lastModified;
  @override
  Map<String, dynamic> get treeData;
  @override
  List<String> get vitalMeasurements;
  @override
  Map<String, dynamic>? get overrides;

  /// Create a copy of SheetSnapshot
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SheetSnapshotImplCopyWith<_$SheetSnapshotImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CsvPreview _$CsvPreviewFromJson(Map<String, dynamic> json) {
  return _CsvPreview.fromJson(json);
}

/// @nodoc
mixin _$CsvPreview {
  List<String> get headers => throw _privateConstructorUsedError;
  List<Map<String, String>> get rows => throw _privateConstructorUsedError;
  Map<String, String> get normalizedHeaders =>
      throw _privateConstructorUsedError;
  List<String> get validationErrors => throw _privateConstructorUsedError;
  Map<String, List<String>> get headerSuggestions =>
      throw _privateConstructorUsedError;
  int? get totalRows => throw _privateConstructorUsedError;

  /// Serializes this CsvPreview to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CsvPreview
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CsvPreviewCopyWith<CsvPreview> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CsvPreviewCopyWith<$Res> {
  factory $CsvPreviewCopyWith(
          CsvPreview value, $Res Function(CsvPreview) then) =
      _$CsvPreviewCopyWithImpl<$Res, CsvPreview>;
  @useResult
  $Res call(
      {List<String> headers,
      List<Map<String, String>> rows,
      Map<String, String> normalizedHeaders,
      List<String> validationErrors,
      Map<String, List<String>> headerSuggestions,
      int? totalRows});
}

/// @nodoc
class _$CsvPreviewCopyWithImpl<$Res, $Val extends CsvPreview>
    implements $CsvPreviewCopyWith<$Res> {
  _$CsvPreviewCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CsvPreview
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? headers = null,
    Object? rows = null,
    Object? normalizedHeaders = null,
    Object? validationErrors = null,
    Object? headerSuggestions = null,
    Object? totalRows = freezed,
  }) {
    return _then(_value.copyWith(
      headers: null == headers
          ? _value.headers
          : headers // ignore: cast_nullable_to_non_nullable
              as List<String>,
      rows: null == rows
          ? _value.rows
          : rows // ignore: cast_nullable_to_non_nullable
              as List<Map<String, String>>,
      normalizedHeaders: null == normalizedHeaders
          ? _value.normalizedHeaders
          : normalizedHeaders // ignore: cast_nullable_to_non_nullable
              as Map<String, String>,
      validationErrors: null == validationErrors
          ? _value.validationErrors
          : validationErrors // ignore: cast_nullable_to_non_nullable
              as List<String>,
      headerSuggestions: null == headerSuggestions
          ? _value.headerSuggestions
          : headerSuggestions // ignore: cast_nullable_to_non_nullable
              as Map<String, List<String>>,
      totalRows: freezed == totalRows
          ? _value.totalRows
          : totalRows // ignore: cast_nullable_to_non_nullable
              as int?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CsvPreviewImplCopyWith<$Res>
    implements $CsvPreviewCopyWith<$Res> {
  factory _$$CsvPreviewImplCopyWith(
          _$CsvPreviewImpl value, $Res Function(_$CsvPreviewImpl) then) =
      __$$CsvPreviewImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {List<String> headers,
      List<Map<String, String>> rows,
      Map<String, String> normalizedHeaders,
      List<String> validationErrors,
      Map<String, List<String>> headerSuggestions,
      int? totalRows});
}

/// @nodoc
class __$$CsvPreviewImplCopyWithImpl<$Res>
    extends _$CsvPreviewCopyWithImpl<$Res, _$CsvPreviewImpl>
    implements _$$CsvPreviewImplCopyWith<$Res> {
  __$$CsvPreviewImplCopyWithImpl(
      _$CsvPreviewImpl _value, $Res Function(_$CsvPreviewImpl) _then)
      : super(_value, _then);

  /// Create a copy of CsvPreview
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? headers = null,
    Object? rows = null,
    Object? normalizedHeaders = null,
    Object? validationErrors = null,
    Object? headerSuggestions = null,
    Object? totalRows = freezed,
  }) {
    return _then(_$CsvPreviewImpl(
      headers: null == headers
          ? _value._headers
          : headers // ignore: cast_nullable_to_non_nullable
              as List<String>,
      rows: null == rows
          ? _value._rows
          : rows // ignore: cast_nullable_to_non_nullable
              as List<Map<String, String>>,
      normalizedHeaders: null == normalizedHeaders
          ? _value._normalizedHeaders
          : normalizedHeaders // ignore: cast_nullable_to_non_nullable
              as Map<String, String>,
      validationErrors: null == validationErrors
          ? _value._validationErrors
          : validationErrors // ignore: cast_nullable_to_non_nullable
              as List<String>,
      headerSuggestions: null == headerSuggestions
          ? _value._headerSuggestions
          : headerSuggestions // ignore: cast_nullable_to_non_nullable
              as Map<String, List<String>>,
      totalRows: freezed == totalRows
          ? _value.totalRows
          : totalRows // ignore: cast_nullable_to_non_nullable
              as int?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CsvPreviewImpl implements _CsvPreview {
  const _$CsvPreviewImpl(
      {required final List<String> headers,
      required final List<Map<String, String>> rows,
      required final Map<String, String> normalizedHeaders,
      required final List<String> validationErrors,
      required final Map<String, List<String>> headerSuggestions,
      this.totalRows})
      : _headers = headers,
        _rows = rows,
        _normalizedHeaders = normalizedHeaders,
        _validationErrors = validationErrors,
        _headerSuggestions = headerSuggestions;

  factory _$CsvPreviewImpl.fromJson(Map<String, dynamic> json) =>
      _$$CsvPreviewImplFromJson(json);

  final List<String> _headers;
  @override
  List<String> get headers {
    if (_headers is EqualUnmodifiableListView) return _headers;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_headers);
  }

  final List<Map<String, String>> _rows;
  @override
  List<Map<String, String>> get rows {
    if (_rows is EqualUnmodifiableListView) return _rows;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_rows);
  }

  final Map<String, String> _normalizedHeaders;
  @override
  Map<String, String> get normalizedHeaders {
    if (_normalizedHeaders is EqualUnmodifiableMapView)
      return _normalizedHeaders;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_normalizedHeaders);
  }

  final List<String> _validationErrors;
  @override
  List<String> get validationErrors {
    if (_validationErrors is EqualUnmodifiableListView)
      return _validationErrors;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_validationErrors);
  }

  final Map<String, List<String>> _headerSuggestions;
  @override
  Map<String, List<String>> get headerSuggestions {
    if (_headerSuggestions is EqualUnmodifiableMapView)
      return _headerSuggestions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_headerSuggestions);
  }

  @override
  final int? totalRows;

  @override
  String toString() {
    return 'CsvPreview(headers: $headers, rows: $rows, normalizedHeaders: $normalizedHeaders, validationErrors: $validationErrors, headerSuggestions: $headerSuggestions, totalRows: $totalRows)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CsvPreviewImpl &&
            const DeepCollectionEquality().equals(other._headers, _headers) &&
            const DeepCollectionEquality().equals(other._rows, _rows) &&
            const DeepCollectionEquality()
                .equals(other._normalizedHeaders, _normalizedHeaders) &&
            const DeepCollectionEquality()
                .equals(other._validationErrors, _validationErrors) &&
            const DeepCollectionEquality()
                .equals(other._headerSuggestions, _headerSuggestions) &&
            (identical(other.totalRows, totalRows) ||
                other.totalRows == totalRows));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(_headers),
      const DeepCollectionEquality().hash(_rows),
      const DeepCollectionEquality().hash(_normalizedHeaders),
      const DeepCollectionEquality().hash(_validationErrors),
      const DeepCollectionEquality().hash(_headerSuggestions),
      totalRows);

  /// Create a copy of CsvPreview
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CsvPreviewImplCopyWith<_$CsvPreviewImpl> get copyWith =>
      __$$CsvPreviewImplCopyWithImpl<_$CsvPreviewImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CsvPreviewImplToJson(
      this,
    );
  }
}

abstract class _CsvPreview implements CsvPreview {
  const factory _CsvPreview(
      {required final List<String> headers,
      required final List<Map<String, String>> rows,
      required final Map<String, String> normalizedHeaders,
      required final List<String> validationErrors,
      required final Map<String, List<String>> headerSuggestions,
      final int? totalRows}) = _$CsvPreviewImpl;

  factory _CsvPreview.fromJson(Map<String, dynamic> json) =
      _$CsvPreviewImpl.fromJson;

  @override
  List<String> get headers;
  @override
  List<Map<String, String>> get rows;
  @override
  Map<String, String> get normalizedHeaders;
  @override
  List<String> get validationErrors;
  @override
  Map<String, List<String>> get headerSuggestions;
  @override
  int? get totalRows;

  /// Create a copy of CsvPreview
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CsvPreviewImplCopyWith<_$CsvPreviewImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CsvImportResult _$CsvImportResultFromJson(Map<String, dynamic> json) {
  return _CsvImportResult.fromJson(json);
}

/// @nodoc
mixin _$CsvImportResult {
  bool get success => throw _privateConstructorUsedError;
  int get rowsProcessed => throw _privateConstructorUsedError;
  int get rowsImported => throw _privateConstructorUsedError;
  List<String> get errors => throw _privateConstructorUsedError;
  List<String> get warnings => throw _privateConstructorUsedError;
  Map<String, dynamic>? get summary => throw _privateConstructorUsedError;

  /// Serializes this CsvImportResult to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CsvImportResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CsvImportResultCopyWith<CsvImportResult> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CsvImportResultCopyWith<$Res> {
  factory $CsvImportResultCopyWith(
          CsvImportResult value, $Res Function(CsvImportResult) then) =
      _$CsvImportResultCopyWithImpl<$Res, CsvImportResult>;
  @useResult
  $Res call(
      {bool success,
      int rowsProcessed,
      int rowsImported,
      List<String> errors,
      List<String> warnings,
      Map<String, dynamic>? summary});
}

/// @nodoc
class _$CsvImportResultCopyWithImpl<$Res, $Val extends CsvImportResult>
    implements $CsvImportResultCopyWith<$Res> {
  _$CsvImportResultCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CsvImportResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? rowsProcessed = null,
    Object? rowsImported = null,
    Object? errors = null,
    Object? warnings = null,
    Object? summary = freezed,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      rowsProcessed: null == rowsProcessed
          ? _value.rowsProcessed
          : rowsProcessed // ignore: cast_nullable_to_non_nullable
              as int,
      rowsImported: null == rowsImported
          ? _value.rowsImported
          : rowsImported // ignore: cast_nullable_to_non_nullable
              as int,
      errors: null == errors
          ? _value.errors
          : errors // ignore: cast_nullable_to_non_nullable
              as List<String>,
      warnings: null == warnings
          ? _value.warnings
          : warnings // ignore: cast_nullable_to_non_nullable
              as List<String>,
      summary: freezed == summary
          ? _value.summary
          : summary // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CsvImportResultImplCopyWith<$Res>
    implements $CsvImportResultCopyWith<$Res> {
  factory _$$CsvImportResultImplCopyWith(_$CsvImportResultImpl value,
          $Res Function(_$CsvImportResultImpl) then) =
      __$$CsvImportResultImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool success,
      int rowsProcessed,
      int rowsImported,
      List<String> errors,
      List<String> warnings,
      Map<String, dynamic>? summary});
}

/// @nodoc
class __$$CsvImportResultImplCopyWithImpl<$Res>
    extends _$CsvImportResultCopyWithImpl<$Res, _$CsvImportResultImpl>
    implements _$$CsvImportResultImplCopyWith<$Res> {
  __$$CsvImportResultImplCopyWithImpl(
      _$CsvImportResultImpl _value, $Res Function(_$CsvImportResultImpl) _then)
      : super(_value, _then);

  /// Create a copy of CsvImportResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? rowsProcessed = null,
    Object? rowsImported = null,
    Object? errors = null,
    Object? warnings = null,
    Object? summary = freezed,
  }) {
    return _then(_$CsvImportResultImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      rowsProcessed: null == rowsProcessed
          ? _value.rowsProcessed
          : rowsProcessed // ignore: cast_nullable_to_non_nullable
              as int,
      rowsImported: null == rowsImported
          ? _value.rowsImported
          : rowsImported // ignore: cast_nullable_to_non_nullable
              as int,
      errors: null == errors
          ? _value._errors
          : errors // ignore: cast_nullable_to_non_nullable
              as List<String>,
      warnings: null == warnings
          ? _value._warnings
          : warnings // ignore: cast_nullable_to_non_nullable
              as List<String>,
      summary: freezed == summary
          ? _value._summary
          : summary // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CsvImportResultImpl implements _CsvImportResult {
  const _$CsvImportResultImpl(
      {required this.success,
      required this.rowsProcessed,
      required this.rowsImported,
      required final List<String> errors,
      required final List<String> warnings,
      final Map<String, dynamic>? summary})
      : _errors = errors,
        _warnings = warnings,
        _summary = summary;

  factory _$CsvImportResultImpl.fromJson(Map<String, dynamic> json) =>
      _$$CsvImportResultImplFromJson(json);

  @override
  final bool success;
  @override
  final int rowsProcessed;
  @override
  final int rowsImported;
  final List<String> _errors;
  @override
  List<String> get errors {
    if (_errors is EqualUnmodifiableListView) return _errors;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_errors);
  }

  final List<String> _warnings;
  @override
  List<String> get warnings {
    if (_warnings is EqualUnmodifiableListView) return _warnings;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_warnings);
  }

  final Map<String, dynamic>? _summary;
  @override
  Map<String, dynamic>? get summary {
    final value = _summary;
    if (value == null) return null;
    if (_summary is EqualUnmodifiableMapView) return _summary;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'CsvImportResult(success: $success, rowsProcessed: $rowsProcessed, rowsImported: $rowsImported, errors: $errors, warnings: $warnings, summary: $summary)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CsvImportResultImpl &&
            (identical(other.success, success) || other.success == success) &&
            (identical(other.rowsProcessed, rowsProcessed) ||
                other.rowsProcessed == rowsProcessed) &&
            (identical(other.rowsImported, rowsImported) ||
                other.rowsImported == rowsImported) &&
            const DeepCollectionEquality().equals(other._errors, _errors) &&
            const DeepCollectionEquality().equals(other._warnings, _warnings) &&
            const DeepCollectionEquality().equals(other._summary, _summary));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      success,
      rowsProcessed,
      rowsImported,
      const DeepCollectionEquality().hash(_errors),
      const DeepCollectionEquality().hash(_warnings),
      const DeepCollectionEquality().hash(_summary));

  /// Create a copy of CsvImportResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CsvImportResultImplCopyWith<_$CsvImportResultImpl> get copyWith =>
      __$$CsvImportResultImplCopyWithImpl<_$CsvImportResultImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CsvImportResultImplToJson(
      this,
    );
  }
}

abstract class _CsvImportResult implements CsvImportResult {
  const factory _CsvImportResult(
      {required final bool success,
      required final int rowsProcessed,
      required final int rowsImported,
      required final List<String> errors,
      required final List<String> warnings,
      final Map<String, dynamic>? summary}) = _$CsvImportResultImpl;

  factory _CsvImportResult.fromJson(Map<String, dynamic> json) =
      _$CsvImportResultImpl.fromJson;

  @override
  bool get success;
  @override
  int get rowsProcessed;
  @override
  int get rowsImported;
  @override
  List<String> get errors;
  @override
  List<String> get warnings;
  @override
  Map<String, dynamic>? get summary;

  /// Create a copy of CsvImportResult
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CsvImportResultImplCopyWith<_$CsvImportResultImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

PushLogEntry _$PushLogEntryFromJson(Map<String, dynamic> json) {
  return _PushLogEntry.fromJson(json);
}

/// @nodoc
mixin _$PushLogEntry {
  int get id => throw _privateConstructorUsedError;
  DateTime get timestamp => throw _privateConstructorUsedError;
  String get operation => throw _privateConstructorUsedError;
  String get description => throw _privateConstructorUsedError;
  Map<String, dynamic>? get metadata => throw _privateConstructorUsedError;
  String? get user => throw _privateConstructorUsedError;
  bool? get success => throw _privateConstructorUsedError;

  /// Serializes this PushLogEntry to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PushLogEntry
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PushLogEntryCopyWith<PushLogEntry> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PushLogEntryCopyWith<$Res> {
  factory $PushLogEntryCopyWith(
          PushLogEntry value, $Res Function(PushLogEntry) then) =
      _$PushLogEntryCopyWithImpl<$Res, PushLogEntry>;
  @useResult
  $Res call(
      {int id,
      DateTime timestamp,
      String operation,
      String description,
      Map<String, dynamic>? metadata,
      String? user,
      bool? success});
}

/// @nodoc
class _$PushLogEntryCopyWithImpl<$Res, $Val extends PushLogEntry>
    implements $PushLogEntryCopyWith<$Res> {
  _$PushLogEntryCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PushLogEntry
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? timestamp = null,
    Object? operation = null,
    Object? description = null,
    Object? metadata = freezed,
    Object? user = freezed,
    Object? success = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      operation: null == operation
          ? _value.operation
          : operation // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      metadata: freezed == metadata
          ? _value.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      user: freezed == user
          ? _value.user
          : user // ignore: cast_nullable_to_non_nullable
              as String?,
      success: freezed == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$PushLogEntryImplCopyWith<$Res>
    implements $PushLogEntryCopyWith<$Res> {
  factory _$$PushLogEntryImplCopyWith(
          _$PushLogEntryImpl value, $Res Function(_$PushLogEntryImpl) then) =
      __$$PushLogEntryImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int id,
      DateTime timestamp,
      String operation,
      String description,
      Map<String, dynamic>? metadata,
      String? user,
      bool? success});
}

/// @nodoc
class __$$PushLogEntryImplCopyWithImpl<$Res>
    extends _$PushLogEntryCopyWithImpl<$Res, _$PushLogEntryImpl>
    implements _$$PushLogEntryImplCopyWith<$Res> {
  __$$PushLogEntryImplCopyWithImpl(
      _$PushLogEntryImpl _value, $Res Function(_$PushLogEntryImpl) _then)
      : super(_value, _then);

  /// Create a copy of PushLogEntry
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? timestamp = null,
    Object? operation = null,
    Object? description = null,
    Object? metadata = freezed,
    Object? user = freezed,
    Object? success = freezed,
  }) {
    return _then(_$PushLogEntryImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      operation: null == operation
          ? _value.operation
          : operation // ignore: cast_nullable_to_non_nullable
              as String,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      metadata: freezed == metadata
          ? _value._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      user: freezed == user
          ? _value.user
          : user // ignore: cast_nullable_to_non_nullable
              as String?,
      success: freezed == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$PushLogEntryImpl implements _PushLogEntry {
  const _$PushLogEntryImpl(
      {required this.id,
      required this.timestamp,
      required this.operation,
      required this.description,
      final Map<String, dynamic>? metadata,
      this.user,
      this.success})
      : _metadata = metadata;

  factory _$PushLogEntryImpl.fromJson(Map<String, dynamic> json) =>
      _$$PushLogEntryImplFromJson(json);

  @override
  final int id;
  @override
  final DateTime timestamp;
  @override
  final String operation;
  @override
  final String description;
  final Map<String, dynamic>? _metadata;
  @override
  Map<String, dynamic>? get metadata {
    final value = _metadata;
    if (value == null) return null;
    if (_metadata is EqualUnmodifiableMapView) return _metadata;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  final String? user;
  @override
  final bool? success;

  @override
  String toString() {
    return 'PushLogEntry(id: $id, timestamp: $timestamp, operation: $operation, description: $description, metadata: $metadata, user: $user, success: $success)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PushLogEntryImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            (identical(other.operation, operation) ||
                other.operation == operation) &&
            (identical(other.description, description) ||
                other.description == description) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata) &&
            (identical(other.user, user) || other.user == user) &&
            (identical(other.success, success) || other.success == success));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      timestamp,
      operation,
      description,
      const DeepCollectionEquality().hash(_metadata),
      user,
      success);

  /// Create a copy of PushLogEntry
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PushLogEntryImplCopyWith<_$PushLogEntryImpl> get copyWith =>
      __$$PushLogEntryImplCopyWithImpl<_$PushLogEntryImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PushLogEntryImplToJson(
      this,
    );
  }
}

abstract class _PushLogEntry implements PushLogEntry {
  const factory _PushLogEntry(
      {required final int id,
      required final DateTime timestamp,
      required final String operation,
      required final String description,
      final Map<String, dynamic>? metadata,
      final String? user,
      final bool? success}) = _$PushLogEntryImpl;

  factory _PushLogEntry.fromJson(Map<String, dynamic> json) =
      _$PushLogEntryImpl.fromJson;

  @override
  int get id;
  @override
  DateTime get timestamp;
  @override
  String get operation;
  @override
  String get description;
  @override
  Map<String, dynamic>? get metadata;
  @override
  String? get user;
  @override
  bool? get success;

  /// Create a copy of PushLogEntry
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PushLogEntryImplCopyWith<_$PushLogEntryImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

PushLogSummary _$PushLogSummaryFromJson(Map<String, dynamic> json) {
  return _PushLogSummary.fromJson(json);
}

/// @nodoc
mixin _$PushLogSummary {
  List<PushLogEntry> get entries => throw _privateConstructorUsedError;
  int get totalEntries => throw _privateConstructorUsedError;
  DateTime? get lastSync => throw _privateConstructorUsedError;
  Map<String, int>? get operationsByType => throw _privateConstructorUsedError;

  /// Serializes this PushLogSummary to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PushLogSummary
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PushLogSummaryCopyWith<PushLogSummary> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PushLogSummaryCopyWith<$Res> {
  factory $PushLogSummaryCopyWith(
          PushLogSummary value, $Res Function(PushLogSummary) then) =
      _$PushLogSummaryCopyWithImpl<$Res, PushLogSummary>;
  @useResult
  $Res call(
      {List<PushLogEntry> entries,
      int totalEntries,
      DateTime? lastSync,
      Map<String, int>? operationsByType});
}

/// @nodoc
class _$PushLogSummaryCopyWithImpl<$Res, $Val extends PushLogSummary>
    implements $PushLogSummaryCopyWith<$Res> {
  _$PushLogSummaryCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PushLogSummary
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? entries = null,
    Object? totalEntries = null,
    Object? lastSync = freezed,
    Object? operationsByType = freezed,
  }) {
    return _then(_value.copyWith(
      entries: null == entries
          ? _value.entries
          : entries // ignore: cast_nullable_to_non_nullable
              as List<PushLogEntry>,
      totalEntries: null == totalEntries
          ? _value.totalEntries
          : totalEntries // ignore: cast_nullable_to_non_nullable
              as int,
      lastSync: freezed == lastSync
          ? _value.lastSync
          : lastSync // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      operationsByType: freezed == operationsByType
          ? _value.operationsByType
          : operationsByType // ignore: cast_nullable_to_non_nullable
              as Map<String, int>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$PushLogSummaryImplCopyWith<$Res>
    implements $PushLogSummaryCopyWith<$Res> {
  factory _$$PushLogSummaryImplCopyWith(_$PushLogSummaryImpl value,
          $Res Function(_$PushLogSummaryImpl) then) =
      __$$PushLogSummaryImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {List<PushLogEntry> entries,
      int totalEntries,
      DateTime? lastSync,
      Map<String, int>? operationsByType});
}

/// @nodoc
class __$$PushLogSummaryImplCopyWithImpl<$Res>
    extends _$PushLogSummaryCopyWithImpl<$Res, _$PushLogSummaryImpl>
    implements _$$PushLogSummaryImplCopyWith<$Res> {
  __$$PushLogSummaryImplCopyWithImpl(
      _$PushLogSummaryImpl _value, $Res Function(_$PushLogSummaryImpl) _then)
      : super(_value, _then);

  /// Create a copy of PushLogSummary
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? entries = null,
    Object? totalEntries = null,
    Object? lastSync = freezed,
    Object? operationsByType = freezed,
  }) {
    return _then(_$PushLogSummaryImpl(
      entries: null == entries
          ? _value._entries
          : entries // ignore: cast_nullable_to_non_nullable
              as List<PushLogEntry>,
      totalEntries: null == totalEntries
          ? _value.totalEntries
          : totalEntries // ignore: cast_nullable_to_non_nullable
              as int,
      lastSync: freezed == lastSync
          ? _value.lastSync
          : lastSync // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      operationsByType: freezed == operationsByType
          ? _value._operationsByType
          : operationsByType // ignore: cast_nullable_to_non_nullable
              as Map<String, int>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$PushLogSummaryImpl implements _PushLogSummary {
  const _$PushLogSummaryImpl(
      {required final List<PushLogEntry> entries,
      required this.totalEntries,
      this.lastSync,
      final Map<String, int>? operationsByType})
      : _entries = entries,
        _operationsByType = operationsByType;

  factory _$PushLogSummaryImpl.fromJson(Map<String, dynamic> json) =>
      _$$PushLogSummaryImplFromJson(json);

  final List<PushLogEntry> _entries;
  @override
  List<PushLogEntry> get entries {
    if (_entries is EqualUnmodifiableListView) return _entries;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_entries);
  }

  @override
  final int totalEntries;
  @override
  final DateTime? lastSync;
  final Map<String, int>? _operationsByType;
  @override
  Map<String, int>? get operationsByType {
    final value = _operationsByType;
    if (value == null) return null;
    if (_operationsByType is EqualUnmodifiableMapView) return _operationsByType;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'PushLogSummary(entries: $entries, totalEntries: $totalEntries, lastSync: $lastSync, operationsByType: $operationsByType)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PushLogSummaryImpl &&
            const DeepCollectionEquality().equals(other._entries, _entries) &&
            (identical(other.totalEntries, totalEntries) ||
                other.totalEntries == totalEntries) &&
            (identical(other.lastSync, lastSync) ||
                other.lastSync == lastSync) &&
            const DeepCollectionEquality()
                .equals(other._operationsByType, _operationsByType));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(_entries),
      totalEntries,
      lastSync,
      const DeepCollectionEquality().hash(_operationsByType));

  /// Create a copy of PushLogSummary
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PushLogSummaryImplCopyWith<_$PushLogSummaryImpl> get copyWith =>
      __$$PushLogSummaryImplCopyWithImpl<_$PushLogSummaryImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PushLogSummaryImplToJson(
      this,
    );
  }
}

abstract class _PushLogSummary implements PushLogSummary {
  const factory _PushLogSummary(
      {required final List<PushLogEntry> entries,
      required final int totalEntries,
      final DateTime? lastSync,
      final Map<String, int>? operationsByType}) = _$PushLogSummaryImpl;

  factory _PushLogSummary.fromJson(Map<String, dynamic> json) =
      _$PushLogSummaryImpl.fromJson;

  @override
  List<PushLogEntry> get entries;
  @override
  int get totalEntries;
  @override
  DateTime? get lastSync;
  @override
  Map<String, int>? get operationsByType;

  /// Create a copy of PushLogSummary
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PushLogSummaryImplCopyWith<_$PushLogSummaryImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

SessionExport _$SessionExportFromJson(Map<String, dynamic> json) {
  return _SessionExport.fromJson(json);
}

/// @nodoc
mixin _$SessionExport {
  String get version => throw _privateConstructorUsedError;
  DateTime get exportedAt => throw _privateConstructorUsedError;
  SessionContext get context => throw _privateConstructorUsedError;
  WorkbookSnapshot get workbook => throw _privateConstructorUsedError;
  Map<String, dynamic>? get settings => throw _privateConstructorUsedError;

  /// Serializes this SessionExport to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SessionExport
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SessionExportCopyWith<SessionExport> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SessionExportCopyWith<$Res> {
  factory $SessionExportCopyWith(
          SessionExport value, $Res Function(SessionExport) then) =
      _$SessionExportCopyWithImpl<$Res, SessionExport>;
  @useResult
  $Res call(
      {String version,
      DateTime exportedAt,
      SessionContext context,
      WorkbookSnapshot workbook,
      Map<String, dynamic>? settings});

  $SessionContextCopyWith<$Res> get context;
  $WorkbookSnapshotCopyWith<$Res> get workbook;
}

/// @nodoc
class _$SessionExportCopyWithImpl<$Res, $Val extends SessionExport>
    implements $SessionExportCopyWith<$Res> {
  _$SessionExportCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SessionExport
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? version = null,
    Object? exportedAt = null,
    Object? context = null,
    Object? workbook = null,
    Object? settings = freezed,
  }) {
    return _then(_value.copyWith(
      version: null == version
          ? _value.version
          : version // ignore: cast_nullable_to_non_nullable
              as String,
      exportedAt: null == exportedAt
          ? _value.exportedAt
          : exportedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      context: null == context
          ? _value.context
          : context // ignore: cast_nullable_to_non_nullable
              as SessionContext,
      workbook: null == workbook
          ? _value.workbook
          : workbook // ignore: cast_nullable_to_non_nullable
              as WorkbookSnapshot,
      settings: freezed == settings
          ? _value.settings
          : settings // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }

  /// Create a copy of SessionExport
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $SessionContextCopyWith<$Res> get context {
    return $SessionContextCopyWith<$Res>(_value.context, (value) {
      return _then(_value.copyWith(context: value) as $Val);
    });
  }

  /// Create a copy of SessionExport
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $WorkbookSnapshotCopyWith<$Res> get workbook {
    return $WorkbookSnapshotCopyWith<$Res>(_value.workbook, (value) {
      return _then(_value.copyWith(workbook: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$SessionExportImplCopyWith<$Res>
    implements $SessionExportCopyWith<$Res> {
  factory _$$SessionExportImplCopyWith(
          _$SessionExportImpl value, $Res Function(_$SessionExportImpl) then) =
      __$$SessionExportImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String version,
      DateTime exportedAt,
      SessionContext context,
      WorkbookSnapshot workbook,
      Map<String, dynamic>? settings});

  @override
  $SessionContextCopyWith<$Res> get context;
  @override
  $WorkbookSnapshotCopyWith<$Res> get workbook;
}

/// @nodoc
class __$$SessionExportImplCopyWithImpl<$Res>
    extends _$SessionExportCopyWithImpl<$Res, _$SessionExportImpl>
    implements _$$SessionExportImplCopyWith<$Res> {
  __$$SessionExportImplCopyWithImpl(
      _$SessionExportImpl _value, $Res Function(_$SessionExportImpl) _then)
      : super(_value, _then);

  /// Create a copy of SessionExport
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? version = null,
    Object? exportedAt = null,
    Object? context = null,
    Object? workbook = null,
    Object? settings = freezed,
  }) {
    return _then(_$SessionExportImpl(
      version: null == version
          ? _value.version
          : version // ignore: cast_nullable_to_non_nullable
              as String,
      exportedAt: null == exportedAt
          ? _value.exportedAt
          : exportedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      context: null == context
          ? _value.context
          : context // ignore: cast_nullable_to_non_nullable
              as SessionContext,
      workbook: null == workbook
          ? _value.workbook
          : workbook // ignore: cast_nullable_to_non_nullable
              as WorkbookSnapshot,
      settings: freezed == settings
          ? _value._settings
          : settings // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SessionExportImpl implements _SessionExport {
  const _$SessionExportImpl(
      {required this.version,
      required this.exportedAt,
      required this.context,
      required this.workbook,
      final Map<String, dynamic>? settings})
      : _settings = settings;

  factory _$SessionExportImpl.fromJson(Map<String, dynamic> json) =>
      _$$SessionExportImplFromJson(json);

  @override
  final String version;
  @override
  final DateTime exportedAt;
  @override
  final SessionContext context;
  @override
  final WorkbookSnapshot workbook;
  final Map<String, dynamic>? _settings;
  @override
  Map<String, dynamic>? get settings {
    final value = _settings;
    if (value == null) return null;
    if (_settings is EqualUnmodifiableMapView) return _settings;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'SessionExport(version: $version, exportedAt: $exportedAt, context: $context, workbook: $workbook, settings: $settings)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SessionExportImpl &&
            (identical(other.version, version) || other.version == version) &&
            (identical(other.exportedAt, exportedAt) ||
                other.exportedAt == exportedAt) &&
            (identical(other.context, context) || other.context == context) &&
            (identical(other.workbook, workbook) ||
                other.workbook == workbook) &&
            const DeepCollectionEquality().equals(other._settings, _settings));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, version, exportedAt, context,
      workbook, const DeepCollectionEquality().hash(_settings));

  /// Create a copy of SessionExport
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SessionExportImplCopyWith<_$SessionExportImpl> get copyWith =>
      __$$SessionExportImplCopyWithImpl<_$SessionExportImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SessionExportImplToJson(
      this,
    );
  }
}

abstract class _SessionExport implements SessionExport {
  const factory _SessionExport(
      {required final String version,
      required final DateTime exportedAt,
      required final SessionContext context,
      required final WorkbookSnapshot workbook,
      final Map<String, dynamic>? settings}) = _$SessionExportImpl;

  factory _SessionExport.fromJson(Map<String, dynamic> json) =
      _$SessionExportImpl.fromJson;

  @override
  String get version;
  @override
  DateTime get exportedAt;
  @override
  SessionContext get context;
  @override
  WorkbookSnapshot get workbook;
  @override
  Map<String, dynamic>? get settings;

  /// Create a copy of SessionExport
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SessionExportImplCopyWith<_$SessionExportImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

SessionImportResult _$SessionImportResultFromJson(Map<String, dynamic> json) {
  return _SessionImportResult.fromJson(json);
}

/// @nodoc
mixin _$SessionImportResult {
  bool get success => throw _privateConstructorUsedError;
  List<String> get importedSheets => throw _privateConstructorUsedError;
  List<String> get errors => throw _privateConstructorUsedError;
  List<String> get warnings => throw _privateConstructorUsedError;
  Map<String, dynamic>? get conflicts => throw _privateConstructorUsedError;

  /// Serializes this SessionImportResult to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SessionImportResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SessionImportResultCopyWith<SessionImportResult> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SessionImportResultCopyWith<$Res> {
  factory $SessionImportResultCopyWith(
          SessionImportResult value, $Res Function(SessionImportResult) then) =
      _$SessionImportResultCopyWithImpl<$Res, SessionImportResult>;
  @useResult
  $Res call(
      {bool success,
      List<String> importedSheets,
      List<String> errors,
      List<String> warnings,
      Map<String, dynamic>? conflicts});
}

/// @nodoc
class _$SessionImportResultCopyWithImpl<$Res, $Val extends SessionImportResult>
    implements $SessionImportResultCopyWith<$Res> {
  _$SessionImportResultCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SessionImportResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? importedSheets = null,
    Object? errors = null,
    Object? warnings = null,
    Object? conflicts = freezed,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      importedSheets: null == importedSheets
          ? _value.importedSheets
          : importedSheets // ignore: cast_nullable_to_non_nullable
              as List<String>,
      errors: null == errors
          ? _value.errors
          : errors // ignore: cast_nullable_to_non_nullable
              as List<String>,
      warnings: null == warnings
          ? _value.warnings
          : warnings // ignore: cast_nullable_to_non_nullable
              as List<String>,
      conflicts: freezed == conflicts
          ? _value.conflicts
          : conflicts // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SessionImportResultImplCopyWith<$Res>
    implements $SessionImportResultCopyWith<$Res> {
  factory _$$SessionImportResultImplCopyWith(_$SessionImportResultImpl value,
          $Res Function(_$SessionImportResultImpl) then) =
      __$$SessionImportResultImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool success,
      List<String> importedSheets,
      List<String> errors,
      List<String> warnings,
      Map<String, dynamic>? conflicts});
}

/// @nodoc
class __$$SessionImportResultImplCopyWithImpl<$Res>
    extends _$SessionImportResultCopyWithImpl<$Res, _$SessionImportResultImpl>
    implements _$$SessionImportResultImplCopyWith<$Res> {
  __$$SessionImportResultImplCopyWithImpl(_$SessionImportResultImpl _value,
      $Res Function(_$SessionImportResultImpl) _then)
      : super(_value, _then);

  /// Create a copy of SessionImportResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? importedSheets = null,
    Object? errors = null,
    Object? warnings = null,
    Object? conflicts = freezed,
  }) {
    return _then(_$SessionImportResultImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      importedSheets: null == importedSheets
          ? _value._importedSheets
          : importedSheets // ignore: cast_nullable_to_non_nullable
              as List<String>,
      errors: null == errors
          ? _value._errors
          : errors // ignore: cast_nullable_to_non_nullable
              as List<String>,
      warnings: null == warnings
          ? _value._warnings
          : warnings // ignore: cast_nullable_to_non_nullable
              as List<String>,
      conflicts: freezed == conflicts
          ? _value._conflicts
          : conflicts // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SessionImportResultImpl implements _SessionImportResult {
  const _$SessionImportResultImpl(
      {required this.success,
      required final List<String> importedSheets,
      required final List<String> errors,
      required final List<String> warnings,
      final Map<String, dynamic>? conflicts})
      : _importedSheets = importedSheets,
        _errors = errors,
        _warnings = warnings,
        _conflicts = conflicts;

  factory _$SessionImportResultImpl.fromJson(Map<String, dynamic> json) =>
      _$$SessionImportResultImplFromJson(json);

  @override
  final bool success;
  final List<String> _importedSheets;
  @override
  List<String> get importedSheets {
    if (_importedSheets is EqualUnmodifiableListView) return _importedSheets;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_importedSheets);
  }

  final List<String> _errors;
  @override
  List<String> get errors {
    if (_errors is EqualUnmodifiableListView) return _errors;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_errors);
  }

  final List<String> _warnings;
  @override
  List<String> get warnings {
    if (_warnings is EqualUnmodifiableListView) return _warnings;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_warnings);
  }

  final Map<String, dynamic>? _conflicts;
  @override
  Map<String, dynamic>? get conflicts {
    final value = _conflicts;
    if (value == null) return null;
    if (_conflicts is EqualUnmodifiableMapView) return _conflicts;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'SessionImportResult(success: $success, importedSheets: $importedSheets, errors: $errors, warnings: $warnings, conflicts: $conflicts)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SessionImportResultImpl &&
            (identical(other.success, success) || other.success == success) &&
            const DeepCollectionEquality()
                .equals(other._importedSheets, _importedSheets) &&
            const DeepCollectionEquality().equals(other._errors, _errors) &&
            const DeepCollectionEquality().equals(other._warnings, _warnings) &&
            const DeepCollectionEquality()
                .equals(other._conflicts, _conflicts));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      success,
      const DeepCollectionEquality().hash(_importedSheets),
      const DeepCollectionEquality().hash(_errors),
      const DeepCollectionEquality().hash(_warnings),
      const DeepCollectionEquality().hash(_conflicts));

  /// Create a copy of SessionImportResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SessionImportResultImplCopyWith<_$SessionImportResultImpl> get copyWith =>
      __$$SessionImportResultImplCopyWithImpl<_$SessionImportResultImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SessionImportResultImplToJson(
      this,
    );
  }
}

abstract class _SessionImportResult implements SessionImportResult {
  const factory _SessionImportResult(
      {required final bool success,
      required final List<String> importedSheets,
      required final List<String> errors,
      required final List<String> warnings,
      final Map<String, dynamic>? conflicts}) = _$SessionImportResultImpl;

  factory _SessionImportResult.fromJson(Map<String, dynamic> json) =
      _$SessionImportResultImpl.fromJson;

  @override
  bool get success;
  @override
  List<String> get importedSheets;
  @override
  List<String> get errors;
  @override
  List<String> get warnings;
  @override
  Map<String, dynamic>? get conflicts;

  /// Create a copy of SessionImportResult
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SessionImportResultImplCopyWith<_$SessionImportResultImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
