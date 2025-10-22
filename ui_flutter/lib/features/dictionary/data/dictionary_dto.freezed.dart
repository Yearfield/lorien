// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'dictionary_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

DictionaryTerm _$DictionaryTermFromJson(Map<String, dynamic> json) {
  return _DictionaryTerm.fromJson(json);
}

/// @nodoc
mixin _$DictionaryTerm {
  int get id => throw _privateConstructorUsedError;
  String get term => throw _privateConstructorUsedError;
  String? get definition => throw _privateConstructorUsedError;
  List<String> get synonyms => throw _privateConstructorUsedError;
  bool get isRedFlag => throw _privateConstructorUsedError;
  int get avgChildrenCount => throw _privateConstructorUsedError;
  int get conflictsCount => throw _privateConstructorUsedError;
  String get createdAt => throw _privateConstructorUsedError;
  String get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this DictionaryTerm to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DictionaryTerm
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DictionaryTermCopyWith<DictionaryTerm> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DictionaryTermCopyWith<$Res> {
  factory $DictionaryTermCopyWith(
          DictionaryTerm value, $Res Function(DictionaryTerm) then) =
      _$DictionaryTermCopyWithImpl<$Res, DictionaryTerm>;
  @useResult
  $Res call(
      {int id,
      String term,
      String? definition,
      List<String> synonyms,
      bool isRedFlag,
      int avgChildrenCount,
      int conflictsCount,
      String createdAt,
      String updatedAt});
}

/// @nodoc
class _$DictionaryTermCopyWithImpl<$Res, $Val extends DictionaryTerm>
    implements $DictionaryTermCopyWith<$Res> {
  _$DictionaryTermCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DictionaryTerm
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? term = null,
    Object? definition = freezed,
    Object? synonyms = null,
    Object? isRedFlag = null,
    Object? avgChildrenCount = null,
    Object? conflictsCount = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      term: null == term
          ? _value.term
          : term // ignore: cast_nullable_to_non_nullable
              as String,
      definition: freezed == definition
          ? _value.definition
          : definition // ignore: cast_nullable_to_non_nullable
              as String?,
      synonyms: null == synonyms
          ? _value.synonyms
          : synonyms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      isRedFlag: null == isRedFlag
          ? _value.isRedFlag
          : isRedFlag // ignore: cast_nullable_to_non_nullable
              as bool,
      avgChildrenCount: null == avgChildrenCount
          ? _value.avgChildrenCount
          : avgChildrenCount // ignore: cast_nullable_to_non_nullable
              as int,
      conflictsCount: null == conflictsCount
          ? _value.conflictsCount
          : conflictsCount // ignore: cast_nullable_to_non_nullable
              as int,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DictionaryTermImplCopyWith<$Res>
    implements $DictionaryTermCopyWith<$Res> {
  factory _$$DictionaryTermImplCopyWith(_$DictionaryTermImpl value,
          $Res Function(_$DictionaryTermImpl) then) =
      __$$DictionaryTermImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int id,
      String term,
      String? definition,
      List<String> synonyms,
      bool isRedFlag,
      int avgChildrenCount,
      int conflictsCount,
      String createdAt,
      String updatedAt});
}

/// @nodoc
class __$$DictionaryTermImplCopyWithImpl<$Res>
    extends _$DictionaryTermCopyWithImpl<$Res, _$DictionaryTermImpl>
    implements _$$DictionaryTermImplCopyWith<$Res> {
  __$$DictionaryTermImplCopyWithImpl(
      _$DictionaryTermImpl _value, $Res Function(_$DictionaryTermImpl) _then)
      : super(_value, _then);

  /// Create a copy of DictionaryTerm
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? term = null,
    Object? definition = freezed,
    Object? synonyms = null,
    Object? isRedFlag = null,
    Object? avgChildrenCount = null,
    Object? conflictsCount = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_$DictionaryTermImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      term: null == term
          ? _value.term
          : term // ignore: cast_nullable_to_non_nullable
              as String,
      definition: freezed == definition
          ? _value.definition
          : definition // ignore: cast_nullable_to_non_nullable
              as String?,
      synonyms: null == synonyms
          ? _value._synonyms
          : synonyms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      isRedFlag: null == isRedFlag
          ? _value.isRedFlag
          : isRedFlag // ignore: cast_nullable_to_non_nullable
              as bool,
      avgChildrenCount: null == avgChildrenCount
          ? _value.avgChildrenCount
          : avgChildrenCount // ignore: cast_nullable_to_non_nullable
              as int,
      conflictsCount: null == conflictsCount
          ? _value.conflictsCount
          : conflictsCount // ignore: cast_nullable_to_non_nullable
              as int,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DictionaryTermImpl implements _DictionaryTerm {
  const _$DictionaryTermImpl(
      {required this.id,
      required this.term,
      this.definition,
      final List<String> synonyms = const [],
      this.isRedFlag = false,
      this.avgChildrenCount = 0,
      this.conflictsCount = 0,
      required this.createdAt,
      required this.updatedAt})
      : _synonyms = synonyms;

  factory _$DictionaryTermImpl.fromJson(Map<String, dynamic> json) =>
      _$$DictionaryTermImplFromJson(json);

  @override
  final int id;
  @override
  final String term;
  @override
  final String? definition;
  final List<String> _synonyms;
  @override
  @JsonKey()
  List<String> get synonyms {
    if (_synonyms is EqualUnmodifiableListView) return _synonyms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_synonyms);
  }

  @override
  @JsonKey()
  final bool isRedFlag;
  @override
  @JsonKey()
  final int avgChildrenCount;
  @override
  @JsonKey()
  final int conflictsCount;
  @override
  final String createdAt;
  @override
  final String updatedAt;

  @override
  String toString() {
    return 'DictionaryTerm(id: $id, term: $term, definition: $definition, synonyms: $synonyms, isRedFlag: $isRedFlag, avgChildrenCount: $avgChildrenCount, conflictsCount: $conflictsCount, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DictionaryTermImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.term, term) || other.term == term) &&
            (identical(other.definition, definition) ||
                other.definition == definition) &&
            const DeepCollectionEquality().equals(other._synonyms, _synonyms) &&
            (identical(other.isRedFlag, isRedFlag) ||
                other.isRedFlag == isRedFlag) &&
            (identical(other.avgChildrenCount, avgChildrenCount) ||
                other.avgChildrenCount == avgChildrenCount) &&
            (identical(other.conflictsCount, conflictsCount) ||
                other.conflictsCount == conflictsCount) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      term,
      definition,
      const DeepCollectionEquality().hash(_synonyms),
      isRedFlag,
      avgChildrenCount,
      conflictsCount,
      createdAt,
      updatedAt);

  /// Create a copy of DictionaryTerm
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DictionaryTermImplCopyWith<_$DictionaryTermImpl> get copyWith =>
      __$$DictionaryTermImplCopyWithImpl<_$DictionaryTermImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DictionaryTermImplToJson(
      this,
    );
  }
}

abstract class _DictionaryTerm implements DictionaryTerm {
  const factory _DictionaryTerm(
      {required final int id,
      required final String term,
      final String? definition,
      final List<String> synonyms,
      final bool isRedFlag,
      final int avgChildrenCount,
      final int conflictsCount,
      required final String createdAt,
      required final String updatedAt}) = _$DictionaryTermImpl;

  factory _DictionaryTerm.fromJson(Map<String, dynamic> json) =
      _$DictionaryTermImpl.fromJson;

  @override
  int get id;
  @override
  String get term;
  @override
  String? get definition;
  @override
  List<String> get synonyms;
  @override
  bool get isRedFlag;
  @override
  int get avgChildrenCount;
  @override
  int get conflictsCount;
  @override
  String get createdAt;
  @override
  String get updatedAt;

  /// Create a copy of DictionaryTerm
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DictionaryTermImplCopyWith<_$DictionaryTermImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

DictionarySearchResult _$DictionarySearchResultFromJson(
    Map<String, dynamic> json) {
  return _DictionarySearchResult.fromJson(json);
}

/// @nodoc
mixin _$DictionarySearchResult {
  List<DictionaryTerm> get items => throw _privateConstructorUsedError;
  int get total => throw _privateConstructorUsedError;
  String get query => throw _privateConstructorUsedError;

  /// Serializes this DictionarySearchResult to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DictionarySearchResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DictionarySearchResultCopyWith<DictionarySearchResult> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DictionarySearchResultCopyWith<$Res> {
  factory $DictionarySearchResultCopyWith(DictionarySearchResult value,
          $Res Function(DictionarySearchResult) then) =
      _$DictionarySearchResultCopyWithImpl<$Res, DictionarySearchResult>;
  @useResult
  $Res call({List<DictionaryTerm> items, int total, String query});
}

/// @nodoc
class _$DictionarySearchResultCopyWithImpl<$Res,
        $Val extends DictionarySearchResult>
    implements $DictionarySearchResultCopyWith<$Res> {
  _$DictionarySearchResultCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DictionarySearchResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? items = null,
    Object? total = null,
    Object? query = null,
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
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DictionarySearchResultImplCopyWith<$Res>
    implements $DictionarySearchResultCopyWith<$Res> {
  factory _$$DictionarySearchResultImplCopyWith(
          _$DictionarySearchResultImpl value,
          $Res Function(_$DictionarySearchResultImpl) then) =
      __$$DictionarySearchResultImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({List<DictionaryTerm> items, int total, String query});
}

/// @nodoc
class __$$DictionarySearchResultImplCopyWithImpl<$Res>
    extends _$DictionarySearchResultCopyWithImpl<$Res,
        _$DictionarySearchResultImpl>
    implements _$$DictionarySearchResultImplCopyWith<$Res> {
  __$$DictionarySearchResultImplCopyWithImpl(
      _$DictionarySearchResultImpl _value,
      $Res Function(_$DictionarySearchResultImpl) _then)
      : super(_value, _then);

  /// Create a copy of DictionarySearchResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? items = null,
    Object? total = null,
    Object? query = null,
  }) {
    return _then(_$DictionarySearchResultImpl(
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
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DictionarySearchResultImpl implements _DictionarySearchResult {
  const _$DictionarySearchResultImpl(
      {required final List<DictionaryTerm> items,
      required this.total,
      required this.query})
      : _items = items;

  factory _$DictionarySearchResultImpl.fromJson(Map<String, dynamic> json) =>
      _$$DictionarySearchResultImplFromJson(json);

  final List<DictionaryTerm> _items;
  @override
  List<DictionaryTerm> get items {
    if (_items is EqualUnmodifiableListView) return _items;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_items);
  }

  @override
  final int total;
  @override
  final String query;

  @override
  String toString() {
    return 'DictionarySearchResult(items: $items, total: $total, query: $query)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DictionarySearchResultImpl &&
            const DeepCollectionEquality().equals(other._items, _items) &&
            (identical(other.total, total) || other.total == total) &&
            (identical(other.query, query) || other.query == query));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType, const DeepCollectionEquality().hash(_items), total, query);

  /// Create a copy of DictionarySearchResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DictionarySearchResultImplCopyWith<_$DictionarySearchResultImpl>
      get copyWith => __$$DictionarySearchResultImplCopyWithImpl<
          _$DictionarySearchResultImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DictionarySearchResultImplToJson(
      this,
    );
  }
}

abstract class _DictionarySearchResult implements DictionarySearchResult {
  const factory _DictionarySearchResult(
      {required final List<DictionaryTerm> items,
      required final int total,
      required final String query}) = _$DictionarySearchResultImpl;

  factory _DictionarySearchResult.fromJson(Map<String, dynamic> json) =
      _$DictionarySearchResultImpl.fromJson;

  @override
  List<DictionaryTerm> get items;
  @override
  int get total;
  @override
  String get query;

  /// Create a copy of DictionarySearchResult
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DictionarySearchResultImplCopyWith<_$DictionarySearchResultImpl>
      get copyWith => throw _privateConstructorUsedError;
}

DictionaryUpdateRequest _$DictionaryUpdateRequestFromJson(
    Map<String, dynamic> json) {
  return _DictionaryUpdateRequest.fromJson(json);
}

/// @nodoc
mixin _$DictionaryUpdateRequest {
  String? get definition => throw _privateConstructorUsedError;
  List<String>? get synonyms => throw _privateConstructorUsedError;
  bool? get isRedFlag => throw _privateConstructorUsedError;

  /// Serializes this DictionaryUpdateRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DictionaryUpdateRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DictionaryUpdateRequestCopyWith<DictionaryUpdateRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DictionaryUpdateRequestCopyWith<$Res> {
  factory $DictionaryUpdateRequestCopyWith(DictionaryUpdateRequest value,
          $Res Function(DictionaryUpdateRequest) then) =
      _$DictionaryUpdateRequestCopyWithImpl<$Res, DictionaryUpdateRequest>;
  @useResult
  $Res call({String? definition, List<String>? synonyms, bool? isRedFlag});
}

/// @nodoc
class _$DictionaryUpdateRequestCopyWithImpl<$Res,
        $Val extends DictionaryUpdateRequest>
    implements $DictionaryUpdateRequestCopyWith<$Res> {
  _$DictionaryUpdateRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DictionaryUpdateRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? definition = freezed,
    Object? synonyms = freezed,
    Object? isRedFlag = freezed,
  }) {
    return _then(_value.copyWith(
      definition: freezed == definition
          ? _value.definition
          : definition // ignore: cast_nullable_to_non_nullable
              as String?,
      synonyms: freezed == synonyms
          ? _value.synonyms
          : synonyms // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      isRedFlag: freezed == isRedFlag
          ? _value.isRedFlag
          : isRedFlag // ignore: cast_nullable_to_non_nullable
              as bool?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DictionaryUpdateRequestImplCopyWith<$Res>
    implements $DictionaryUpdateRequestCopyWith<$Res> {
  factory _$$DictionaryUpdateRequestImplCopyWith(
          _$DictionaryUpdateRequestImpl value,
          $Res Function(_$DictionaryUpdateRequestImpl) then) =
      __$$DictionaryUpdateRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String? definition, List<String>? synonyms, bool? isRedFlag});
}

/// @nodoc
class __$$DictionaryUpdateRequestImplCopyWithImpl<$Res>
    extends _$DictionaryUpdateRequestCopyWithImpl<$Res,
        _$DictionaryUpdateRequestImpl>
    implements _$$DictionaryUpdateRequestImplCopyWith<$Res> {
  __$$DictionaryUpdateRequestImplCopyWithImpl(
      _$DictionaryUpdateRequestImpl _value,
      $Res Function(_$DictionaryUpdateRequestImpl) _then)
      : super(_value, _then);

  /// Create a copy of DictionaryUpdateRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? definition = freezed,
    Object? synonyms = freezed,
    Object? isRedFlag = freezed,
  }) {
    return _then(_$DictionaryUpdateRequestImpl(
      definition: freezed == definition
          ? _value.definition
          : definition // ignore: cast_nullable_to_non_nullable
              as String?,
      synonyms: freezed == synonyms
          ? _value._synonyms
          : synonyms // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      isRedFlag: freezed == isRedFlag
          ? _value.isRedFlag
          : isRedFlag // ignore: cast_nullable_to_non_nullable
              as bool?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DictionaryUpdateRequestImpl implements _DictionaryUpdateRequest {
  const _$DictionaryUpdateRequestImpl(
      {this.definition, final List<String>? synonyms, this.isRedFlag})
      : _synonyms = synonyms;

  factory _$DictionaryUpdateRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$DictionaryUpdateRequestImplFromJson(json);

  @override
  final String? definition;
  final List<String>? _synonyms;
  @override
  List<String>? get synonyms {
    final value = _synonyms;
    if (value == null) return null;
    if (_synonyms is EqualUnmodifiableListView) return _synonyms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  @override
  final bool? isRedFlag;

  @override
  String toString() {
    return 'DictionaryUpdateRequest(definition: $definition, synonyms: $synonyms, isRedFlag: $isRedFlag)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DictionaryUpdateRequestImpl &&
            (identical(other.definition, definition) ||
                other.definition == definition) &&
            const DeepCollectionEquality().equals(other._synonyms, _synonyms) &&
            (identical(other.isRedFlag, isRedFlag) ||
                other.isRedFlag == isRedFlag));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, definition,
      const DeepCollectionEquality().hash(_synonyms), isRedFlag);

  /// Create a copy of DictionaryUpdateRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DictionaryUpdateRequestImplCopyWith<_$DictionaryUpdateRequestImpl>
      get copyWith => __$$DictionaryUpdateRequestImplCopyWithImpl<
          _$DictionaryUpdateRequestImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DictionaryUpdateRequestImplToJson(
      this,
    );
  }
}

abstract class _DictionaryUpdateRequest implements DictionaryUpdateRequest {
  const factory _DictionaryUpdateRequest(
      {final String? definition,
      final List<String>? synonyms,
      final bool? isRedFlag}) = _$DictionaryUpdateRequestImpl;

  factory _DictionaryUpdateRequest.fromJson(Map<String, dynamic> json) =
      _$DictionaryUpdateRequestImpl.fromJson;

  @override
  String? get definition;
  @override
  List<String>? get synonyms;
  @override
  bool? get isRedFlag;

  /// Create a copy of DictionaryUpdateRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DictionaryUpdateRequestImplCopyWith<_$DictionaryUpdateRequestImpl>
      get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
mixin _$DictionaryStats {
  int get totalTerms => throw _privateConstructorUsedError;
  int get redFlagTerms => throw _privateConstructorUsedError;
  int get termsWithDefinitions => throw _privateConstructorUsedError;
  int get termsWithSynonyms => throw _privateConstructorUsedError;
  double get avgChildrenPerTerm => throw _privateConstructorUsedError;
  int get totalConflicts => throw _privateConstructorUsedError;
  DictionaryCompletionRate get completionRate =>
      throw _privateConstructorUsedError;

  /// Create a copy of DictionaryStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DictionaryStatsCopyWith<DictionaryStats> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DictionaryStatsCopyWith<$Res> {
  factory $DictionaryStatsCopyWith(
          DictionaryStats value, $Res Function(DictionaryStats) then) =
      _$DictionaryStatsCopyWithImpl<$Res, DictionaryStats>;
  @useResult
  $Res call(
      {int totalTerms,
      int redFlagTerms,
      int termsWithDefinitions,
      int termsWithSynonyms,
      double avgChildrenPerTerm,
      int totalConflicts,
      DictionaryCompletionRate completionRate});

  $DictionaryCompletionRateCopyWith<$Res> get completionRate;
}

/// @nodoc
class _$DictionaryStatsCopyWithImpl<$Res, $Val extends DictionaryStats>
    implements $DictionaryStatsCopyWith<$Res> {
  _$DictionaryStatsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DictionaryStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalTerms = null,
    Object? redFlagTerms = null,
    Object? termsWithDefinitions = null,
    Object? termsWithSynonyms = null,
    Object? avgChildrenPerTerm = null,
    Object? totalConflicts = null,
    Object? completionRate = null,
  }) {
    return _then(_value.copyWith(
      totalTerms: null == totalTerms
          ? _value.totalTerms
          : totalTerms // ignore: cast_nullable_to_non_nullable
              as int,
      redFlagTerms: null == redFlagTerms
          ? _value.redFlagTerms
          : redFlagTerms // ignore: cast_nullable_to_non_nullable
              as int,
      termsWithDefinitions: null == termsWithDefinitions
          ? _value.termsWithDefinitions
          : termsWithDefinitions // ignore: cast_nullable_to_non_nullable
              as int,
      termsWithSynonyms: null == termsWithSynonyms
          ? _value.termsWithSynonyms
          : termsWithSynonyms // ignore: cast_nullable_to_non_nullable
              as int,
      avgChildrenPerTerm: null == avgChildrenPerTerm
          ? _value.avgChildrenPerTerm
          : avgChildrenPerTerm // ignore: cast_nullable_to_non_nullable
              as double,
      totalConflicts: null == totalConflicts
          ? _value.totalConflicts
          : totalConflicts // ignore: cast_nullable_to_non_nullable
              as int,
      completionRate: null == completionRate
          ? _value.completionRate
          : completionRate // ignore: cast_nullable_to_non_nullable
              as DictionaryCompletionRate,
    ) as $Val);
  }

  /// Create a copy of DictionaryStats
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $DictionaryCompletionRateCopyWith<$Res> get completionRate {
    return $DictionaryCompletionRateCopyWith<$Res>(_value.completionRate,
        (value) {
      return _then(_value.copyWith(completionRate: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$DictionaryStatsImplCopyWith<$Res>
    implements $DictionaryStatsCopyWith<$Res> {
  factory _$$DictionaryStatsImplCopyWith(_$DictionaryStatsImpl value,
          $Res Function(_$DictionaryStatsImpl) then) =
      __$$DictionaryStatsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int totalTerms,
      int redFlagTerms,
      int termsWithDefinitions,
      int termsWithSynonyms,
      double avgChildrenPerTerm,
      int totalConflicts,
      DictionaryCompletionRate completionRate});

  @override
  $DictionaryCompletionRateCopyWith<$Res> get completionRate;
}

/// @nodoc
class __$$DictionaryStatsImplCopyWithImpl<$Res>
    extends _$DictionaryStatsCopyWithImpl<$Res, _$DictionaryStatsImpl>
    implements _$$DictionaryStatsImplCopyWith<$Res> {
  __$$DictionaryStatsImplCopyWithImpl(
      _$DictionaryStatsImpl _value, $Res Function(_$DictionaryStatsImpl) _then)
      : super(_value, _then);

  /// Create a copy of DictionaryStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalTerms = null,
    Object? redFlagTerms = null,
    Object? termsWithDefinitions = null,
    Object? termsWithSynonyms = null,
    Object? avgChildrenPerTerm = null,
    Object? totalConflicts = null,
    Object? completionRate = null,
  }) {
    return _then(_$DictionaryStatsImpl(
      totalTerms: null == totalTerms
          ? _value.totalTerms
          : totalTerms // ignore: cast_nullable_to_non_nullable
              as int,
      redFlagTerms: null == redFlagTerms
          ? _value.redFlagTerms
          : redFlagTerms // ignore: cast_nullable_to_non_nullable
              as int,
      termsWithDefinitions: null == termsWithDefinitions
          ? _value.termsWithDefinitions
          : termsWithDefinitions // ignore: cast_nullable_to_non_nullable
              as int,
      termsWithSynonyms: null == termsWithSynonyms
          ? _value.termsWithSynonyms
          : termsWithSynonyms // ignore: cast_nullable_to_non_nullable
              as int,
      avgChildrenPerTerm: null == avgChildrenPerTerm
          ? _value.avgChildrenPerTerm
          : avgChildrenPerTerm // ignore: cast_nullable_to_non_nullable
              as double,
      totalConflicts: null == totalConflicts
          ? _value.totalConflicts
          : totalConflicts // ignore: cast_nullable_to_non_nullable
              as int,
      completionRate: null == completionRate
          ? _value.completionRate
          : completionRate // ignore: cast_nullable_to_non_nullable
              as DictionaryCompletionRate,
    ));
  }
}

/// @nodoc

class _$DictionaryStatsImpl implements _DictionaryStats {
  const _$DictionaryStatsImpl(
      {required this.totalTerms,
      required this.redFlagTerms,
      required this.termsWithDefinitions,
      required this.termsWithSynonyms,
      required this.avgChildrenPerTerm,
      required this.totalConflicts,
      required this.completionRate});

  @override
  final int totalTerms;
  @override
  final int redFlagTerms;
  @override
  final int termsWithDefinitions;
  @override
  final int termsWithSynonyms;
  @override
  final double avgChildrenPerTerm;
  @override
  final int totalConflicts;
  @override
  final DictionaryCompletionRate completionRate;

  @override
  String toString() {
    return 'DictionaryStats(totalTerms: $totalTerms, redFlagTerms: $redFlagTerms, termsWithDefinitions: $termsWithDefinitions, termsWithSynonyms: $termsWithSynonyms, avgChildrenPerTerm: $avgChildrenPerTerm, totalConflicts: $totalConflicts, completionRate: $completionRate)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DictionaryStatsImpl &&
            (identical(other.totalTerms, totalTerms) ||
                other.totalTerms == totalTerms) &&
            (identical(other.redFlagTerms, redFlagTerms) ||
                other.redFlagTerms == redFlagTerms) &&
            (identical(other.termsWithDefinitions, termsWithDefinitions) ||
                other.termsWithDefinitions == termsWithDefinitions) &&
            (identical(other.termsWithSynonyms, termsWithSynonyms) ||
                other.termsWithSynonyms == termsWithSynonyms) &&
            (identical(other.avgChildrenPerTerm, avgChildrenPerTerm) ||
                other.avgChildrenPerTerm == avgChildrenPerTerm) &&
            (identical(other.totalConflicts, totalConflicts) ||
                other.totalConflicts == totalConflicts) &&
            (identical(other.completionRate, completionRate) ||
                other.completionRate == completionRate));
  }

  @override
  int get hashCode => Object.hash(
      runtimeType,
      totalTerms,
      redFlagTerms,
      termsWithDefinitions,
      termsWithSynonyms,
      avgChildrenPerTerm,
      totalConflicts,
      completionRate);

  /// Create a copy of DictionaryStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DictionaryStatsImplCopyWith<_$DictionaryStatsImpl> get copyWith =>
      __$$DictionaryStatsImplCopyWithImpl<_$DictionaryStatsImpl>(
          this, _$identity);
}

abstract class _DictionaryStats implements DictionaryStats {
  const factory _DictionaryStats(
          {required final int totalTerms,
          required final int redFlagTerms,
          required final int termsWithDefinitions,
          required final int termsWithSynonyms,
          required final double avgChildrenPerTerm,
          required final int totalConflicts,
          required final DictionaryCompletionRate completionRate}) =
      _$DictionaryStatsImpl;

  @override
  int get totalTerms;
  @override
  int get redFlagTerms;
  @override
  int get termsWithDefinitions;
  @override
  int get termsWithSynonyms;
  @override
  double get avgChildrenPerTerm;
  @override
  int get totalConflicts;
  @override
  DictionaryCompletionRate get completionRate;

  /// Create a copy of DictionaryStats
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DictionaryStatsImplCopyWith<_$DictionaryStatsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
mixin _$DictionaryCompletionRate {
  double get definitions => throw _privateConstructorUsedError;
  double get synonyms => throw _privateConstructorUsedError;

  /// Create a copy of DictionaryCompletionRate
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DictionaryCompletionRateCopyWith<DictionaryCompletionRate> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DictionaryCompletionRateCopyWith<$Res> {
  factory $DictionaryCompletionRateCopyWith(DictionaryCompletionRate value,
          $Res Function(DictionaryCompletionRate) then) =
      _$DictionaryCompletionRateCopyWithImpl<$Res, DictionaryCompletionRate>;
  @useResult
  $Res call({double definitions, double synonyms});
}

/// @nodoc
class _$DictionaryCompletionRateCopyWithImpl<$Res,
        $Val extends DictionaryCompletionRate>
    implements $DictionaryCompletionRateCopyWith<$Res> {
  _$DictionaryCompletionRateCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DictionaryCompletionRate
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? definitions = null,
    Object? synonyms = null,
  }) {
    return _then(_value.copyWith(
      definitions: null == definitions
          ? _value.definitions
          : definitions // ignore: cast_nullable_to_non_nullable
              as double,
      synonyms: null == synonyms
          ? _value.synonyms
          : synonyms // ignore: cast_nullable_to_non_nullable
              as double,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DictionaryCompletionRateImplCopyWith<$Res>
    implements $DictionaryCompletionRateCopyWith<$Res> {
  factory _$$DictionaryCompletionRateImplCopyWith(
          _$DictionaryCompletionRateImpl value,
          $Res Function(_$DictionaryCompletionRateImpl) then) =
      __$$DictionaryCompletionRateImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({double definitions, double synonyms});
}

/// @nodoc
class __$$DictionaryCompletionRateImplCopyWithImpl<$Res>
    extends _$DictionaryCompletionRateCopyWithImpl<$Res,
        _$DictionaryCompletionRateImpl>
    implements _$$DictionaryCompletionRateImplCopyWith<$Res> {
  __$$DictionaryCompletionRateImplCopyWithImpl(
      _$DictionaryCompletionRateImpl _value,
      $Res Function(_$DictionaryCompletionRateImpl) _then)
      : super(_value, _then);

  /// Create a copy of DictionaryCompletionRate
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? definitions = null,
    Object? synonyms = null,
  }) {
    return _then(_$DictionaryCompletionRateImpl(
      definitions: null == definitions
          ? _value.definitions
          : definitions // ignore: cast_nullable_to_non_nullable
              as double,
      synonyms: null == synonyms
          ? _value.synonyms
          : synonyms // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

/// @nodoc

class _$DictionaryCompletionRateImpl implements _DictionaryCompletionRate {
  const _$DictionaryCompletionRateImpl(
      {required this.definitions, required this.synonyms});

  @override
  final double definitions;
  @override
  final double synonyms;

  @override
  String toString() {
    return 'DictionaryCompletionRate(definitions: $definitions, synonyms: $synonyms)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DictionaryCompletionRateImpl &&
            (identical(other.definitions, definitions) ||
                other.definitions == definitions) &&
            (identical(other.synonyms, synonyms) ||
                other.synonyms == synonyms));
  }

  @override
  int get hashCode => Object.hash(runtimeType, definitions, synonyms);

  /// Create a copy of DictionaryCompletionRate
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DictionaryCompletionRateImplCopyWith<_$DictionaryCompletionRateImpl>
      get copyWith => __$$DictionaryCompletionRateImplCopyWithImpl<
          _$DictionaryCompletionRateImpl>(this, _$identity);
}

abstract class _DictionaryCompletionRate implements DictionaryCompletionRate {
  const factory _DictionaryCompletionRate(
      {required final double definitions,
      required final double synonyms}) = _$DictionaryCompletionRateImpl;

  @override
  double get definitions;
  @override
  double get synonyms;

  /// Create a copy of DictionaryCompletionRate
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DictionaryCompletionRateImplCopyWith<_$DictionaryCompletionRateImpl>
      get copyWith => throw _privateConstructorUsedError;
}

TreeRelationship _$TreeRelationshipFromJson(Map<String, dynamic> json) {
  return _TreeRelationship.fromJson(json);
}

/// @nodoc
mixin _$TreeRelationship {
  int get id => throw _privateConstructorUsedError;
  String? get label => throw _privateConstructorUsedError;
  int get depth => throw _privateConstructorUsedError;
  int? get slot => throw _privateConstructorUsedError;
  @JsonKey(name: 'parent_id')
  int? get parentId => throw _privateConstructorUsedError;

  /// Serializes this TreeRelationship to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of TreeRelationship
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $TreeRelationshipCopyWith<TreeRelationship> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $TreeRelationshipCopyWith<$Res> {
  factory $TreeRelationshipCopyWith(
          TreeRelationship value, $Res Function(TreeRelationship) then) =
      _$TreeRelationshipCopyWithImpl<$Res, TreeRelationship>;
  @useResult
  $Res call(
      {int id,
      String? label,
      int depth,
      int? slot,
      @JsonKey(name: 'parent_id') int? parentId});
}

/// @nodoc
class _$TreeRelationshipCopyWithImpl<$Res, $Val extends TreeRelationship>
    implements $TreeRelationshipCopyWith<$Res> {
  _$TreeRelationshipCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of TreeRelationship
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? label = freezed,
    Object? depth = null,
    Object? slot = freezed,
    Object? parentId = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      label: freezed == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String?,
      depth: null == depth
          ? _value.depth
          : depth // ignore: cast_nullable_to_non_nullable
              as int,
      slot: freezed == slot
          ? _value.slot
          : slot // ignore: cast_nullable_to_non_nullable
              as int?,
      parentId: freezed == parentId
          ? _value.parentId
          : parentId // ignore: cast_nullable_to_non_nullable
              as int?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$TreeRelationshipImplCopyWith<$Res>
    implements $TreeRelationshipCopyWith<$Res> {
  factory _$$TreeRelationshipImplCopyWith(_$TreeRelationshipImpl value,
          $Res Function(_$TreeRelationshipImpl) then) =
      __$$TreeRelationshipImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int id,
      String? label,
      int depth,
      int? slot,
      @JsonKey(name: 'parent_id') int? parentId});
}

/// @nodoc
class __$$TreeRelationshipImplCopyWithImpl<$Res>
    extends _$TreeRelationshipCopyWithImpl<$Res, _$TreeRelationshipImpl>
    implements _$$TreeRelationshipImplCopyWith<$Res> {
  __$$TreeRelationshipImplCopyWithImpl(_$TreeRelationshipImpl _value,
      $Res Function(_$TreeRelationshipImpl) _then)
      : super(_value, _then);

  /// Create a copy of TreeRelationship
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? label = freezed,
    Object? depth = null,
    Object? slot = freezed,
    Object? parentId = freezed,
  }) {
    return _then(_$TreeRelationshipImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      label: freezed == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String?,
      depth: null == depth
          ? _value.depth
          : depth // ignore: cast_nullable_to_non_nullable
              as int,
      slot: freezed == slot
          ? _value.slot
          : slot // ignore: cast_nullable_to_non_nullable
              as int?,
      parentId: freezed == parentId
          ? _value.parentId
          : parentId // ignore: cast_nullable_to_non_nullable
              as int?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$TreeRelationshipImpl implements _TreeRelationship {
  const _$TreeRelationshipImpl(
      {required this.id,
      this.label,
      required this.depth,
      this.slot,
      @JsonKey(name: 'parent_id') this.parentId});

  factory _$TreeRelationshipImpl.fromJson(Map<String, dynamic> json) =>
      _$$TreeRelationshipImplFromJson(json);

  @override
  final int id;
  @override
  final String? label;
  @override
  final int depth;
  @override
  final int? slot;
  @override
  @JsonKey(name: 'parent_id')
  final int? parentId;

  @override
  String toString() {
    return 'TreeRelationship(id: $id, label: $label, depth: $depth, slot: $slot, parentId: $parentId)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$TreeRelationshipImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.label, label) || other.label == label) &&
            (identical(other.depth, depth) || other.depth == depth) &&
            (identical(other.slot, slot) || other.slot == slot) &&
            (identical(other.parentId, parentId) ||
                other.parentId == parentId));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, id, label, depth, slot, parentId);

  /// Create a copy of TreeRelationship
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$TreeRelationshipImplCopyWith<_$TreeRelationshipImpl> get copyWith =>
      __$$TreeRelationshipImplCopyWithImpl<_$TreeRelationshipImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$TreeRelationshipImplToJson(
      this,
    );
  }
}

abstract class _TreeRelationship implements TreeRelationship {
  const factory _TreeRelationship(
          {required final int id,
          final String? label,
          required final int depth,
          final int? slot,
          @JsonKey(name: 'parent_id') final int? parentId}) =
      _$TreeRelationshipImpl;

  factory _TreeRelationship.fromJson(Map<String, dynamic> json) =
      _$TreeRelationshipImpl.fromJson;

  @override
  int get id;
  @override
  String? get label;
  @override
  int get depth;
  @override
  int? get slot;
  @override
  @JsonKey(name: 'parent_id')
  int? get parentId;

  /// Create a copy of TreeRelationship
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$TreeRelationshipImplCopyWith<_$TreeRelationshipImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

DictionaryTreeRelationships _$DictionaryTreeRelationshipsFromJson(
    Map<String, dynamic> json) {
  return _DictionaryTreeRelationships.fromJson(json);
}

/// @nodoc
mixin _$DictionaryTreeRelationships {
  String get term => throw _privateConstructorUsedError;
  List<TreeRelationship> get nodes => throw _privateConstructorUsedError;
  List<TreeRelationship> get parents => throw _privateConstructorUsedError;
  List<TreeRelationship> get children => throw _privateConstructorUsedError;

  /// Serializes this DictionaryTreeRelationships to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DictionaryTreeRelationships
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DictionaryTreeRelationshipsCopyWith<DictionaryTreeRelationships>
      get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DictionaryTreeRelationshipsCopyWith<$Res> {
  factory $DictionaryTreeRelationshipsCopyWith(
          DictionaryTreeRelationships value,
          $Res Function(DictionaryTreeRelationships) then) =
      _$DictionaryTreeRelationshipsCopyWithImpl<$Res,
          DictionaryTreeRelationships>;
  @useResult
  $Res call(
      {String term,
      List<TreeRelationship> nodes,
      List<TreeRelationship> parents,
      List<TreeRelationship> children});
}

/// @nodoc
class _$DictionaryTreeRelationshipsCopyWithImpl<$Res,
        $Val extends DictionaryTreeRelationships>
    implements $DictionaryTreeRelationshipsCopyWith<$Res> {
  _$DictionaryTreeRelationshipsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DictionaryTreeRelationships
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? term = null,
    Object? nodes = null,
    Object? parents = null,
    Object? children = null,
  }) {
    return _then(_value.copyWith(
      term: null == term
          ? _value.term
          : term // ignore: cast_nullable_to_non_nullable
              as String,
      nodes: null == nodes
          ? _value.nodes
          : nodes // ignore: cast_nullable_to_non_nullable
              as List<TreeRelationship>,
      parents: null == parents
          ? _value.parents
          : parents // ignore: cast_nullable_to_non_nullable
              as List<TreeRelationship>,
      children: null == children
          ? _value.children
          : children // ignore: cast_nullable_to_non_nullable
              as List<TreeRelationship>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DictionaryTreeRelationshipsImplCopyWith<$Res>
    implements $DictionaryTreeRelationshipsCopyWith<$Res> {
  factory _$$DictionaryTreeRelationshipsImplCopyWith(
          _$DictionaryTreeRelationshipsImpl value,
          $Res Function(_$DictionaryTreeRelationshipsImpl) then) =
      __$$DictionaryTreeRelationshipsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String term,
      List<TreeRelationship> nodes,
      List<TreeRelationship> parents,
      List<TreeRelationship> children});
}

/// @nodoc
class __$$DictionaryTreeRelationshipsImplCopyWithImpl<$Res>
    extends _$DictionaryTreeRelationshipsCopyWithImpl<$Res,
        _$DictionaryTreeRelationshipsImpl>
    implements _$$DictionaryTreeRelationshipsImplCopyWith<$Res> {
  __$$DictionaryTreeRelationshipsImplCopyWithImpl(
      _$DictionaryTreeRelationshipsImpl _value,
      $Res Function(_$DictionaryTreeRelationshipsImpl) _then)
      : super(_value, _then);

  /// Create a copy of DictionaryTreeRelationships
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? term = null,
    Object? nodes = null,
    Object? parents = null,
    Object? children = null,
  }) {
    return _then(_$DictionaryTreeRelationshipsImpl(
      term: null == term
          ? _value.term
          : term // ignore: cast_nullable_to_non_nullable
              as String,
      nodes: null == nodes
          ? _value._nodes
          : nodes // ignore: cast_nullable_to_non_nullable
              as List<TreeRelationship>,
      parents: null == parents
          ? _value._parents
          : parents // ignore: cast_nullable_to_non_nullable
              as List<TreeRelationship>,
      children: null == children
          ? _value._children
          : children // ignore: cast_nullable_to_non_nullable
              as List<TreeRelationship>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DictionaryTreeRelationshipsImpl
    implements _DictionaryTreeRelationships {
  const _$DictionaryTreeRelationshipsImpl(
      {required this.term,
      required final List<TreeRelationship> nodes,
      required final List<TreeRelationship> parents,
      required final List<TreeRelationship> children})
      : _nodes = nodes,
        _parents = parents,
        _children = children;

  factory _$DictionaryTreeRelationshipsImpl.fromJson(
          Map<String, dynamic> json) =>
      _$$DictionaryTreeRelationshipsImplFromJson(json);

  @override
  final String term;
  final List<TreeRelationship> _nodes;
  @override
  List<TreeRelationship> get nodes {
    if (_nodes is EqualUnmodifiableListView) return _nodes;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_nodes);
  }

  final List<TreeRelationship> _parents;
  @override
  List<TreeRelationship> get parents {
    if (_parents is EqualUnmodifiableListView) return _parents;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_parents);
  }

  final List<TreeRelationship> _children;
  @override
  List<TreeRelationship> get children {
    if (_children is EqualUnmodifiableListView) return _children;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_children);
  }

  @override
  String toString() {
    return 'DictionaryTreeRelationships(term: $term, nodes: $nodes, parents: $parents, children: $children)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DictionaryTreeRelationshipsImpl &&
            (identical(other.term, term) || other.term == term) &&
            const DeepCollectionEquality().equals(other._nodes, _nodes) &&
            const DeepCollectionEquality().equals(other._parents, _parents) &&
            const DeepCollectionEquality().equals(other._children, _children));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      term,
      const DeepCollectionEquality().hash(_nodes),
      const DeepCollectionEquality().hash(_parents),
      const DeepCollectionEquality().hash(_children));

  /// Create a copy of DictionaryTreeRelationships
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DictionaryTreeRelationshipsImplCopyWith<_$DictionaryTreeRelationshipsImpl>
      get copyWith => __$$DictionaryTreeRelationshipsImplCopyWithImpl<
          _$DictionaryTreeRelationshipsImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DictionaryTreeRelationshipsImplToJson(
      this,
    );
  }
}

abstract class _DictionaryTreeRelationships
    implements DictionaryTreeRelationships {
  const factory _DictionaryTreeRelationships(
          {required final String term,
          required final List<TreeRelationship> nodes,
          required final List<TreeRelationship> parents,
          required final List<TreeRelationship> children}) =
      _$DictionaryTreeRelationshipsImpl;

  factory _DictionaryTreeRelationships.fromJson(Map<String, dynamic> json) =
      _$DictionaryTreeRelationshipsImpl.fromJson;

  @override
  String get term;
  @override
  List<TreeRelationship> get nodes;
  @override
  List<TreeRelationship> get parents;
  @override
  List<TreeRelationship> get children;

  /// Create a copy of DictionaryTreeRelationships
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DictionaryTreeRelationshipsImplCopyWith<_$DictionaryTreeRelationshipsImpl>
      get copyWith => throw _privateConstructorUsedError;
}
