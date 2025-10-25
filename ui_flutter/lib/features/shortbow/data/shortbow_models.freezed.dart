// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'shortbow_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

ShortBowSymptom _$ShortBowSymptomFromJson(Map<String, dynamic> json) {
  return _ShortBowSymptom.fromJson(json);
}

/// @nodoc
mixin _$ShortBowSymptom {
  int get id => throw _privateConstructorUsedError;
  @JsonKey(name: 'symptom_name')
  String get symptomName => throw _privateConstructorUsedError;
  @JsonKey(name: 'created_at')
  String get createdAt => throw _privateConstructorUsedError;
  @JsonKey(name: 'updated_at')
  String get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this ShortBowSymptom to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ShortBowSymptom
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ShortBowSymptomCopyWith<ShortBowSymptom> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ShortBowSymptomCopyWith<$Res> {
  factory $ShortBowSymptomCopyWith(
          ShortBowSymptom value, $Res Function(ShortBowSymptom) then) =
      _$ShortBowSymptomCopyWithImpl<$Res, ShortBowSymptom>;
  @useResult
  $Res call(
      {int id,
      @JsonKey(name: 'symptom_name') String symptomName,
      @JsonKey(name: 'created_at') String createdAt,
      @JsonKey(name: 'updated_at') String updatedAt});
}

/// @nodoc
class _$ShortBowSymptomCopyWithImpl<$Res, $Val extends ShortBowSymptom>
    implements $ShortBowSymptomCopyWith<$Res> {
  _$ShortBowSymptomCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ShortBowSymptom
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? symptomName = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      symptomName: null == symptomName
          ? _value.symptomName
          : symptomName // ignore: cast_nullable_to_non_nullable
              as String,
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
abstract class _$$ShortBowSymptomImplCopyWith<$Res>
    implements $ShortBowSymptomCopyWith<$Res> {
  factory _$$ShortBowSymptomImplCopyWith(_$ShortBowSymptomImpl value,
          $Res Function(_$ShortBowSymptomImpl) then) =
      __$$ShortBowSymptomImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int id,
      @JsonKey(name: 'symptom_name') String symptomName,
      @JsonKey(name: 'created_at') String createdAt,
      @JsonKey(name: 'updated_at') String updatedAt});
}

/// @nodoc
class __$$ShortBowSymptomImplCopyWithImpl<$Res>
    extends _$ShortBowSymptomCopyWithImpl<$Res, _$ShortBowSymptomImpl>
    implements _$$ShortBowSymptomImplCopyWith<$Res> {
  __$$ShortBowSymptomImplCopyWithImpl(
      _$ShortBowSymptomImpl _value, $Res Function(_$ShortBowSymptomImpl) _then)
      : super(_value, _then);

  /// Create a copy of ShortBowSymptom
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? symptomName = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_$ShortBowSymptomImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      symptomName: null == symptomName
          ? _value.symptomName
          : symptomName // ignore: cast_nullable_to_non_nullable
              as String,
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
class _$ShortBowSymptomImpl implements _ShortBowSymptom {
  const _$ShortBowSymptomImpl(
      {required this.id,
      @JsonKey(name: 'symptom_name') required this.symptomName,
      @JsonKey(name: 'created_at') required this.createdAt,
      @JsonKey(name: 'updated_at') required this.updatedAt});

  factory _$ShortBowSymptomImpl.fromJson(Map<String, dynamic> json) =>
      _$$ShortBowSymptomImplFromJson(json);

  @override
  final int id;
  @override
  @JsonKey(name: 'symptom_name')
  final String symptomName;
  @override
  @JsonKey(name: 'created_at')
  final String createdAt;
  @override
  @JsonKey(name: 'updated_at')
  final String updatedAt;

  @override
  String toString() {
    return 'ShortBowSymptom(id: $id, symptomName: $symptomName, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ShortBowSymptomImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.symptomName, symptomName) ||
                other.symptomName == symptomName) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, id, symptomName, createdAt, updatedAt);

  /// Create a copy of ShortBowSymptom
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ShortBowSymptomImplCopyWith<_$ShortBowSymptomImpl> get copyWith =>
      __$$ShortBowSymptomImplCopyWithImpl<_$ShortBowSymptomImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ShortBowSymptomImplToJson(
      this,
    );
  }
}

abstract class _ShortBowSymptom implements ShortBowSymptom {
  const factory _ShortBowSymptom(
          {required final int id,
          @JsonKey(name: 'symptom_name') required final String symptomName,
          @JsonKey(name: 'created_at') required final String createdAt,
          @JsonKey(name: 'updated_at') required final String updatedAt}) =
      _$ShortBowSymptomImpl;

  factory _ShortBowSymptom.fromJson(Map<String, dynamic> json) =
      _$ShortBowSymptomImpl.fromJson;

  @override
  int get id;
  @override
  @JsonKey(name: 'symptom_name')
  String get symptomName;
  @override
  @JsonKey(name: 'created_at')
  String get createdAt;
  @override
  @JsonKey(name: 'updated_at')
  String get updatedAt;

  /// Create a copy of ShortBowSymptom
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ShortBowSymptomImplCopyWith<_$ShortBowSymptomImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ShortBowSymptomLink _$ShortBowSymptomLinkFromJson(Map<String, dynamic> json) {
  return _ShortBowSymptomLink.fromJson(json);
}

/// @nodoc
mixin _$ShortBowSymptomLink {
  @JsonKey(name: 'from_symptom')
  String get fromSymptom => throw _privateConstructorUsedError;
  @JsonKey(name: 'to_symptom')
  String get toSymptom => throw _privateConstructorUsedError;
  double get probability => throw _privateConstructorUsedError;

  /// Serializes this ShortBowSymptomLink to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ShortBowSymptomLink
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ShortBowSymptomLinkCopyWith<ShortBowSymptomLink> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ShortBowSymptomLinkCopyWith<$Res> {
  factory $ShortBowSymptomLinkCopyWith(
          ShortBowSymptomLink value, $Res Function(ShortBowSymptomLink) then) =
      _$ShortBowSymptomLinkCopyWithImpl<$Res, ShortBowSymptomLink>;
  @useResult
  $Res call(
      {@JsonKey(name: 'from_symptom') String fromSymptom,
      @JsonKey(name: 'to_symptom') String toSymptom,
      double probability});
}

/// @nodoc
class _$ShortBowSymptomLinkCopyWithImpl<$Res, $Val extends ShortBowSymptomLink>
    implements $ShortBowSymptomLinkCopyWith<$Res> {
  _$ShortBowSymptomLinkCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ShortBowSymptomLink
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? fromSymptom = null,
    Object? toSymptom = null,
    Object? probability = null,
  }) {
    return _then(_value.copyWith(
      fromSymptom: null == fromSymptom
          ? _value.fromSymptom
          : fromSymptom // ignore: cast_nullable_to_non_nullable
              as String,
      toSymptom: null == toSymptom
          ? _value.toSymptom
          : toSymptom // ignore: cast_nullable_to_non_nullable
              as String,
      probability: null == probability
          ? _value.probability
          : probability // ignore: cast_nullable_to_non_nullable
              as double,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ShortBowSymptomLinkImplCopyWith<$Res>
    implements $ShortBowSymptomLinkCopyWith<$Res> {
  factory _$$ShortBowSymptomLinkImplCopyWith(_$ShortBowSymptomLinkImpl value,
          $Res Function(_$ShortBowSymptomLinkImpl) then) =
      __$$ShortBowSymptomLinkImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'from_symptom') String fromSymptom,
      @JsonKey(name: 'to_symptom') String toSymptom,
      double probability});
}

/// @nodoc
class __$$ShortBowSymptomLinkImplCopyWithImpl<$Res>
    extends _$ShortBowSymptomLinkCopyWithImpl<$Res, _$ShortBowSymptomLinkImpl>
    implements _$$ShortBowSymptomLinkImplCopyWith<$Res> {
  __$$ShortBowSymptomLinkImplCopyWithImpl(_$ShortBowSymptomLinkImpl _value,
      $Res Function(_$ShortBowSymptomLinkImpl) _then)
      : super(_value, _then);

  /// Create a copy of ShortBowSymptomLink
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? fromSymptom = null,
    Object? toSymptom = null,
    Object? probability = null,
  }) {
    return _then(_$ShortBowSymptomLinkImpl(
      fromSymptom: null == fromSymptom
          ? _value.fromSymptom
          : fromSymptom // ignore: cast_nullable_to_non_nullable
              as String,
      toSymptom: null == toSymptom
          ? _value.toSymptom
          : toSymptom // ignore: cast_nullable_to_non_nullable
              as String,
      probability: null == probability
          ? _value.probability
          : probability // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ShortBowSymptomLinkImpl implements _ShortBowSymptomLink {
  const _$ShortBowSymptomLinkImpl(
      {@JsonKey(name: 'from_symptom') required this.fromSymptom,
      @JsonKey(name: 'to_symptom') required this.toSymptom,
      required this.probability});

  factory _$ShortBowSymptomLinkImpl.fromJson(Map<String, dynamic> json) =>
      _$$ShortBowSymptomLinkImplFromJson(json);

  @override
  @JsonKey(name: 'from_symptom')
  final String fromSymptom;
  @override
  @JsonKey(name: 'to_symptom')
  final String toSymptom;
  @override
  final double probability;

  @override
  String toString() {
    return 'ShortBowSymptomLink(fromSymptom: $fromSymptom, toSymptom: $toSymptom, probability: $probability)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ShortBowSymptomLinkImpl &&
            (identical(other.fromSymptom, fromSymptom) ||
                other.fromSymptom == fromSymptom) &&
            (identical(other.toSymptom, toSymptom) ||
                other.toSymptom == toSymptom) &&
            (identical(other.probability, probability) ||
                other.probability == probability));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, fromSymptom, toSymptom, probability);

  /// Create a copy of ShortBowSymptomLink
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ShortBowSymptomLinkImplCopyWith<_$ShortBowSymptomLinkImpl> get copyWith =>
      __$$ShortBowSymptomLinkImplCopyWithImpl<_$ShortBowSymptomLinkImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ShortBowSymptomLinkImplToJson(
      this,
    );
  }
}

abstract class _ShortBowSymptomLink implements ShortBowSymptomLink {
  const factory _ShortBowSymptomLink(
      {@JsonKey(name: 'from_symptom') required final String fromSymptom,
      @JsonKey(name: 'to_symptom') required final String toSymptom,
      required final double probability}) = _$ShortBowSymptomLinkImpl;

  factory _ShortBowSymptomLink.fromJson(Map<String, dynamic> json) =
      _$ShortBowSymptomLinkImpl.fromJson;

  @override
  @JsonKey(name: 'from_symptom')
  String get fromSymptom;
  @override
  @JsonKey(name: 'to_symptom')
  String get toSymptom;
  @override
  double get probability;

  /// Create a copy of ShortBowSymptomLink
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ShortBowSymptomLinkImplCopyWith<_$ShortBowSymptomLinkImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ShortBowNavigationRequest _$ShortBowNavigationRequestFromJson(
    Map<String, dynamic> json) {
  return _ShortBowNavigationRequest.fromJson(json);
}

/// @nodoc
mixin _$ShortBowNavigationRequest {
  @JsonKey(name: 'current_symptom')
  String get currentSymptom => throw _privateConstructorUsedError;
  List<String> get exclude => throw _privateConstructorUsedError;

  /// Serializes this ShortBowNavigationRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ShortBowNavigationRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ShortBowNavigationRequestCopyWith<ShortBowNavigationRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ShortBowNavigationRequestCopyWith<$Res> {
  factory $ShortBowNavigationRequestCopyWith(ShortBowNavigationRequest value,
          $Res Function(ShortBowNavigationRequest) then) =
      _$ShortBowNavigationRequestCopyWithImpl<$Res, ShortBowNavigationRequest>;
  @useResult
  $Res call(
      {@JsonKey(name: 'current_symptom') String currentSymptom,
      List<String> exclude});
}

/// @nodoc
class _$ShortBowNavigationRequestCopyWithImpl<$Res,
        $Val extends ShortBowNavigationRequest>
    implements $ShortBowNavigationRequestCopyWith<$Res> {
  _$ShortBowNavigationRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ShortBowNavigationRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? currentSymptom = null,
    Object? exclude = null,
  }) {
    return _then(_value.copyWith(
      currentSymptom: null == currentSymptom
          ? _value.currentSymptom
          : currentSymptom // ignore: cast_nullable_to_non_nullable
              as String,
      exclude: null == exclude
          ? _value.exclude
          : exclude // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ShortBowNavigationRequestImplCopyWith<$Res>
    implements $ShortBowNavigationRequestCopyWith<$Res> {
  factory _$$ShortBowNavigationRequestImplCopyWith(
          _$ShortBowNavigationRequestImpl value,
          $Res Function(_$ShortBowNavigationRequestImpl) then) =
      __$$ShortBowNavigationRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'current_symptom') String currentSymptom,
      List<String> exclude});
}

/// @nodoc
class __$$ShortBowNavigationRequestImplCopyWithImpl<$Res>
    extends _$ShortBowNavigationRequestCopyWithImpl<$Res,
        _$ShortBowNavigationRequestImpl>
    implements _$$ShortBowNavigationRequestImplCopyWith<$Res> {
  __$$ShortBowNavigationRequestImplCopyWithImpl(
      _$ShortBowNavigationRequestImpl _value,
      $Res Function(_$ShortBowNavigationRequestImpl) _then)
      : super(_value, _then);

  /// Create a copy of ShortBowNavigationRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? currentSymptom = null,
    Object? exclude = null,
  }) {
    return _then(_$ShortBowNavigationRequestImpl(
      currentSymptom: null == currentSymptom
          ? _value.currentSymptom
          : currentSymptom // ignore: cast_nullable_to_non_nullable
              as String,
      exclude: null == exclude
          ? _value._exclude
          : exclude // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ShortBowNavigationRequestImpl implements _ShortBowNavigationRequest {
  const _$ShortBowNavigationRequestImpl(
      {@JsonKey(name: 'current_symptom') required this.currentSymptom,
      final List<String> exclude = const []})
      : _exclude = exclude;

  factory _$ShortBowNavigationRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$ShortBowNavigationRequestImplFromJson(json);

  @override
  @JsonKey(name: 'current_symptom')
  final String currentSymptom;
  final List<String> _exclude;
  @override
  @JsonKey()
  List<String> get exclude {
    if (_exclude is EqualUnmodifiableListView) return _exclude;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_exclude);
  }

  @override
  String toString() {
    return 'ShortBowNavigationRequest(currentSymptom: $currentSymptom, exclude: $exclude)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ShortBowNavigationRequestImpl &&
            (identical(other.currentSymptom, currentSymptom) ||
                other.currentSymptom == currentSymptom) &&
            const DeepCollectionEquality().equals(other._exclude, _exclude));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, currentSymptom,
      const DeepCollectionEquality().hash(_exclude));

  /// Create a copy of ShortBowNavigationRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ShortBowNavigationRequestImplCopyWith<_$ShortBowNavigationRequestImpl>
      get copyWith => __$$ShortBowNavigationRequestImplCopyWithImpl<
          _$ShortBowNavigationRequestImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ShortBowNavigationRequestImplToJson(
      this,
    );
  }
}

abstract class _ShortBowNavigationRequest implements ShortBowNavigationRequest {
  const factory _ShortBowNavigationRequest(
      {@JsonKey(name: 'current_symptom') required final String currentSymptom,
      final List<String> exclude}) = _$ShortBowNavigationRequestImpl;

  factory _ShortBowNavigationRequest.fromJson(Map<String, dynamic> json) =
      _$ShortBowNavigationRequestImpl.fromJson;

  @override
  @JsonKey(name: 'current_symptom')
  String get currentSymptom;
  @override
  List<String> get exclude;

  /// Create a copy of ShortBowNavigationRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ShortBowNavigationRequestImplCopyWith<_$ShortBowNavigationRequestImpl>
      get copyWith => throw _privateConstructorUsedError;
}

ShortBowNavigationResponse _$ShortBowNavigationResponseFromJson(
    Map<String, dynamic> json) {
  return _ShortBowNavigationResponse.fromJson(json);
}

/// @nodoc
mixin _$ShortBowNavigationResponse {
  @JsonKey(name: 'current_symptom')
  String get currentSymptom => throw _privateConstructorUsedError;
  @JsonKey(name: 'top_linked')
  List<ShortBowSymptomLink> get topLinked => throw _privateConstructorUsedError;
  @JsonKey(name: 'excluded_symptoms')
  List<String> get excludedSymptoms => throw _privateConstructorUsedError;
  @JsonKey(name: 'total_available')
  int get totalAvailable => throw _privateConstructorUsedError;

  /// Serializes this ShortBowNavigationResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ShortBowNavigationResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ShortBowNavigationResponseCopyWith<ShortBowNavigationResponse>
      get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ShortBowNavigationResponseCopyWith<$Res> {
  factory $ShortBowNavigationResponseCopyWith(ShortBowNavigationResponse value,
          $Res Function(ShortBowNavigationResponse) then) =
      _$ShortBowNavigationResponseCopyWithImpl<$Res,
          ShortBowNavigationResponse>;
  @useResult
  $Res call(
      {@JsonKey(name: 'current_symptom') String currentSymptom,
      @JsonKey(name: 'top_linked') List<ShortBowSymptomLink> topLinked,
      @JsonKey(name: 'excluded_symptoms') List<String> excludedSymptoms,
      @JsonKey(name: 'total_available') int totalAvailable});
}

/// @nodoc
class _$ShortBowNavigationResponseCopyWithImpl<$Res,
        $Val extends ShortBowNavigationResponse>
    implements $ShortBowNavigationResponseCopyWith<$Res> {
  _$ShortBowNavigationResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ShortBowNavigationResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? currentSymptom = null,
    Object? topLinked = null,
    Object? excludedSymptoms = null,
    Object? totalAvailable = null,
  }) {
    return _then(_value.copyWith(
      currentSymptom: null == currentSymptom
          ? _value.currentSymptom
          : currentSymptom // ignore: cast_nullable_to_non_nullable
              as String,
      topLinked: null == topLinked
          ? _value.topLinked
          : topLinked // ignore: cast_nullable_to_non_nullable
              as List<ShortBowSymptomLink>,
      excludedSymptoms: null == excludedSymptoms
          ? _value.excludedSymptoms
          : excludedSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      totalAvailable: null == totalAvailable
          ? _value.totalAvailable
          : totalAvailable // ignore: cast_nullable_to_non_nullable
              as int,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ShortBowNavigationResponseImplCopyWith<$Res>
    implements $ShortBowNavigationResponseCopyWith<$Res> {
  factory _$$ShortBowNavigationResponseImplCopyWith(
          _$ShortBowNavigationResponseImpl value,
          $Res Function(_$ShortBowNavigationResponseImpl) then) =
      __$$ShortBowNavigationResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'current_symptom') String currentSymptom,
      @JsonKey(name: 'top_linked') List<ShortBowSymptomLink> topLinked,
      @JsonKey(name: 'excluded_symptoms') List<String> excludedSymptoms,
      @JsonKey(name: 'total_available') int totalAvailable});
}

/// @nodoc
class __$$ShortBowNavigationResponseImplCopyWithImpl<$Res>
    extends _$ShortBowNavigationResponseCopyWithImpl<$Res,
        _$ShortBowNavigationResponseImpl>
    implements _$$ShortBowNavigationResponseImplCopyWith<$Res> {
  __$$ShortBowNavigationResponseImplCopyWithImpl(
      _$ShortBowNavigationResponseImpl _value,
      $Res Function(_$ShortBowNavigationResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of ShortBowNavigationResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? currentSymptom = null,
    Object? topLinked = null,
    Object? excludedSymptoms = null,
    Object? totalAvailable = null,
  }) {
    return _then(_$ShortBowNavigationResponseImpl(
      currentSymptom: null == currentSymptom
          ? _value.currentSymptom
          : currentSymptom // ignore: cast_nullable_to_non_nullable
              as String,
      topLinked: null == topLinked
          ? _value._topLinked
          : topLinked // ignore: cast_nullable_to_non_nullable
              as List<ShortBowSymptomLink>,
      excludedSymptoms: null == excludedSymptoms
          ? _value._excludedSymptoms
          : excludedSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      totalAvailable: null == totalAvailable
          ? _value.totalAvailable
          : totalAvailable // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ShortBowNavigationResponseImpl implements _ShortBowNavigationResponse {
  const _$ShortBowNavigationResponseImpl(
      {@JsonKey(name: 'current_symptom') required this.currentSymptom,
      @JsonKey(name: 'top_linked')
      required final List<ShortBowSymptomLink> topLinked,
      @JsonKey(name: 'excluded_symptoms')
      required final List<String> excludedSymptoms,
      @JsonKey(name: 'total_available') required this.totalAvailable})
      : _topLinked = topLinked,
        _excludedSymptoms = excludedSymptoms;

  factory _$ShortBowNavigationResponseImpl.fromJson(
          Map<String, dynamic> json) =>
      _$$ShortBowNavigationResponseImplFromJson(json);

  @override
  @JsonKey(name: 'current_symptom')
  final String currentSymptom;
  final List<ShortBowSymptomLink> _topLinked;
  @override
  @JsonKey(name: 'top_linked')
  List<ShortBowSymptomLink> get topLinked {
    if (_topLinked is EqualUnmodifiableListView) return _topLinked;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_topLinked);
  }

  final List<String> _excludedSymptoms;
  @override
  @JsonKey(name: 'excluded_symptoms')
  List<String> get excludedSymptoms {
    if (_excludedSymptoms is EqualUnmodifiableListView)
      return _excludedSymptoms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_excludedSymptoms);
  }

  @override
  @JsonKey(name: 'total_available')
  final int totalAvailable;

  @override
  String toString() {
    return 'ShortBowNavigationResponse(currentSymptom: $currentSymptom, topLinked: $topLinked, excludedSymptoms: $excludedSymptoms, totalAvailable: $totalAvailable)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ShortBowNavigationResponseImpl &&
            (identical(other.currentSymptom, currentSymptom) ||
                other.currentSymptom == currentSymptom) &&
            const DeepCollectionEquality()
                .equals(other._topLinked, _topLinked) &&
            const DeepCollectionEquality()
                .equals(other._excludedSymptoms, _excludedSymptoms) &&
            (identical(other.totalAvailable, totalAvailable) ||
                other.totalAvailable == totalAvailable));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      currentSymptom,
      const DeepCollectionEquality().hash(_topLinked),
      const DeepCollectionEquality().hash(_excludedSymptoms),
      totalAvailable);

  /// Create a copy of ShortBowNavigationResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ShortBowNavigationResponseImplCopyWith<_$ShortBowNavigationResponseImpl>
      get copyWith => __$$ShortBowNavigationResponseImplCopyWithImpl<
          _$ShortBowNavigationResponseImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ShortBowNavigationResponseImplToJson(
      this,
    );
  }
}

abstract class _ShortBowNavigationResponse
    implements ShortBowNavigationResponse {
  const factory _ShortBowNavigationResponse(
      {@JsonKey(name: 'current_symptom') required final String currentSymptom,
      @JsonKey(name: 'top_linked')
      required final List<ShortBowSymptomLink> topLinked,
      @JsonKey(name: 'excluded_symptoms')
      required final List<String> excludedSymptoms,
      @JsonKey(name: 'total_available')
      required final int totalAvailable}) = _$ShortBowNavigationResponseImpl;

  factory _ShortBowNavigationResponse.fromJson(Map<String, dynamic> json) =
      _$ShortBowNavigationResponseImpl.fromJson;

  @override
  @JsonKey(name: 'current_symptom')
  String get currentSymptom;
  @override
  @JsonKey(name: 'top_linked')
  List<ShortBowSymptomLink> get topLinked;
  @override
  @JsonKey(name: 'excluded_symptoms')
  List<String> get excludedSymptoms;
  @override
  @JsonKey(name: 'total_available')
  int get totalAvailable;

  /// Create a copy of ShortBowNavigationResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ShortBowNavigationResponseImplCopyWith<_$ShortBowNavigationResponseImpl>
      get copyWith => throw _privateConstructorUsedError;
}

ShortBowCalculation _$ShortBowCalculationFromJson(Map<String, dynamic> json) {
  return _ShortBowCalculation.fromJson(json);
}

/// @nodoc
mixin _$ShortBowCalculation {
  int get id => throw _privateConstructorUsedError;
  @JsonKey(name: 'calculation_date')
  String get calculationDate => throw _privateConstructorUsedError;
  @JsonKey(name: 'initial_symptom')
  String get initialSymptom => throw _privateConstructorUsedError;
  @JsonKey(name: 'selected_symptoms')
  List<String> get selectedSymptoms => throw _privateConstructorUsedError;
  bool get saved => throw _privateConstructorUsedError;
  @JsonKey(name: 'created_at')
  String get createdAt => throw _privateConstructorUsedError;

  /// Serializes this ShortBowCalculation to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ShortBowCalculation
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ShortBowCalculationCopyWith<ShortBowCalculation> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ShortBowCalculationCopyWith<$Res> {
  factory $ShortBowCalculationCopyWith(
          ShortBowCalculation value, $Res Function(ShortBowCalculation) then) =
      _$ShortBowCalculationCopyWithImpl<$Res, ShortBowCalculation>;
  @useResult
  $Res call(
      {int id,
      @JsonKey(name: 'calculation_date') String calculationDate,
      @JsonKey(name: 'initial_symptom') String initialSymptom,
      @JsonKey(name: 'selected_symptoms') List<String> selectedSymptoms,
      bool saved,
      @JsonKey(name: 'created_at') String createdAt});
}

/// @nodoc
class _$ShortBowCalculationCopyWithImpl<$Res, $Val extends ShortBowCalculation>
    implements $ShortBowCalculationCopyWith<$Res> {
  _$ShortBowCalculationCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ShortBowCalculation
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? calculationDate = null,
    Object? initialSymptom = null,
    Object? selectedSymptoms = null,
    Object? saved = null,
    Object? createdAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      calculationDate: null == calculationDate
          ? _value.calculationDate
          : calculationDate // ignore: cast_nullable_to_non_nullable
              as String,
      initialSymptom: null == initialSymptom
          ? _value.initialSymptom
          : initialSymptom // ignore: cast_nullable_to_non_nullable
              as String,
      selectedSymptoms: null == selectedSymptoms
          ? _value.selectedSymptoms
          : selectedSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      saved: null == saved
          ? _value.saved
          : saved // ignore: cast_nullable_to_non_nullable
              as bool,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ShortBowCalculationImplCopyWith<$Res>
    implements $ShortBowCalculationCopyWith<$Res> {
  factory _$$ShortBowCalculationImplCopyWith(_$ShortBowCalculationImpl value,
          $Res Function(_$ShortBowCalculationImpl) then) =
      __$$ShortBowCalculationImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int id,
      @JsonKey(name: 'calculation_date') String calculationDate,
      @JsonKey(name: 'initial_symptom') String initialSymptom,
      @JsonKey(name: 'selected_symptoms') List<String> selectedSymptoms,
      bool saved,
      @JsonKey(name: 'created_at') String createdAt});
}

/// @nodoc
class __$$ShortBowCalculationImplCopyWithImpl<$Res>
    extends _$ShortBowCalculationCopyWithImpl<$Res, _$ShortBowCalculationImpl>
    implements _$$ShortBowCalculationImplCopyWith<$Res> {
  __$$ShortBowCalculationImplCopyWithImpl(_$ShortBowCalculationImpl _value,
      $Res Function(_$ShortBowCalculationImpl) _then)
      : super(_value, _then);

  /// Create a copy of ShortBowCalculation
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? calculationDate = null,
    Object? initialSymptom = null,
    Object? selectedSymptoms = null,
    Object? saved = null,
    Object? createdAt = null,
  }) {
    return _then(_$ShortBowCalculationImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      calculationDate: null == calculationDate
          ? _value.calculationDate
          : calculationDate // ignore: cast_nullable_to_non_nullable
              as String,
      initialSymptom: null == initialSymptom
          ? _value.initialSymptom
          : initialSymptom // ignore: cast_nullable_to_non_nullable
              as String,
      selectedSymptoms: null == selectedSymptoms
          ? _value._selectedSymptoms
          : selectedSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      saved: null == saved
          ? _value.saved
          : saved // ignore: cast_nullable_to_non_nullable
              as bool,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ShortBowCalculationImpl implements _ShortBowCalculation {
  const _$ShortBowCalculationImpl(
      {required this.id,
      @JsonKey(name: 'calculation_date') required this.calculationDate,
      @JsonKey(name: 'initial_symptom') required this.initialSymptom,
      @JsonKey(name: 'selected_symptoms')
      required final List<String> selectedSymptoms,
      required this.saved,
      @JsonKey(name: 'created_at') required this.createdAt})
      : _selectedSymptoms = selectedSymptoms;

  factory _$ShortBowCalculationImpl.fromJson(Map<String, dynamic> json) =>
      _$$ShortBowCalculationImplFromJson(json);

  @override
  final int id;
  @override
  @JsonKey(name: 'calculation_date')
  final String calculationDate;
  @override
  @JsonKey(name: 'initial_symptom')
  final String initialSymptom;
  final List<String> _selectedSymptoms;
  @override
  @JsonKey(name: 'selected_symptoms')
  List<String> get selectedSymptoms {
    if (_selectedSymptoms is EqualUnmodifiableListView)
      return _selectedSymptoms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_selectedSymptoms);
  }

  @override
  final bool saved;
  @override
  @JsonKey(name: 'created_at')
  final String createdAt;

  @override
  String toString() {
    return 'ShortBowCalculation(id: $id, calculationDate: $calculationDate, initialSymptom: $initialSymptom, selectedSymptoms: $selectedSymptoms, saved: $saved, createdAt: $createdAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ShortBowCalculationImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.calculationDate, calculationDate) ||
                other.calculationDate == calculationDate) &&
            (identical(other.initialSymptom, initialSymptom) ||
                other.initialSymptom == initialSymptom) &&
            const DeepCollectionEquality()
                .equals(other._selectedSymptoms, _selectedSymptoms) &&
            (identical(other.saved, saved) || other.saved == saved) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      calculationDate,
      initialSymptom,
      const DeepCollectionEquality().hash(_selectedSymptoms),
      saved,
      createdAt);

  /// Create a copy of ShortBowCalculation
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ShortBowCalculationImplCopyWith<_$ShortBowCalculationImpl> get copyWith =>
      __$$ShortBowCalculationImplCopyWithImpl<_$ShortBowCalculationImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ShortBowCalculationImplToJson(
      this,
    );
  }
}

abstract class _ShortBowCalculation implements ShortBowCalculation {
  const factory _ShortBowCalculation(
      {required final int id,
      @JsonKey(name: 'calculation_date') required final String calculationDate,
      @JsonKey(name: 'initial_symptom') required final String initialSymptom,
      @JsonKey(name: 'selected_symptoms')
      required final List<String> selectedSymptoms,
      required final bool saved,
      @JsonKey(name: 'created_at')
      required final String createdAt}) = _$ShortBowCalculationImpl;

  factory _ShortBowCalculation.fromJson(Map<String, dynamic> json) =
      _$ShortBowCalculationImpl.fromJson;

  @override
  int get id;
  @override
  @JsonKey(name: 'calculation_date')
  String get calculationDate;
  @override
  @JsonKey(name: 'initial_symptom')
  String get initialSymptom;
  @override
  @JsonKey(name: 'selected_symptoms')
  List<String> get selectedSymptoms;
  @override
  bool get saved;
  @override
  @JsonKey(name: 'created_at')
  String get createdAt;

  /// Create a copy of ShortBowCalculation
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ShortBowCalculationImplCopyWith<_$ShortBowCalculationImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ShortBowCalculationRequest _$ShortBowCalculationRequestFromJson(
    Map<String, dynamic> json) {
  return _ShortBowCalculationRequest.fromJson(json);
}

/// @nodoc
mixin _$ShortBowCalculationRequest {
  @JsonKey(name: 'initial_symptom')
  String get initialSymptom => throw _privateConstructorUsedError;
  @JsonKey(name: 'selected_symptoms')
  List<String> get selectedSymptoms => throw _privateConstructorUsedError;

  /// Serializes this ShortBowCalculationRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ShortBowCalculationRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ShortBowCalculationRequestCopyWith<ShortBowCalculationRequest>
      get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ShortBowCalculationRequestCopyWith<$Res> {
  factory $ShortBowCalculationRequestCopyWith(ShortBowCalculationRequest value,
          $Res Function(ShortBowCalculationRequest) then) =
      _$ShortBowCalculationRequestCopyWithImpl<$Res,
          ShortBowCalculationRequest>;
  @useResult
  $Res call(
      {@JsonKey(name: 'initial_symptom') String initialSymptom,
      @JsonKey(name: 'selected_symptoms') List<String> selectedSymptoms});
}

/// @nodoc
class _$ShortBowCalculationRequestCopyWithImpl<$Res,
        $Val extends ShortBowCalculationRequest>
    implements $ShortBowCalculationRequestCopyWith<$Res> {
  _$ShortBowCalculationRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ShortBowCalculationRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? initialSymptom = null,
    Object? selectedSymptoms = null,
  }) {
    return _then(_value.copyWith(
      initialSymptom: null == initialSymptom
          ? _value.initialSymptom
          : initialSymptom // ignore: cast_nullable_to_non_nullable
              as String,
      selectedSymptoms: null == selectedSymptoms
          ? _value.selectedSymptoms
          : selectedSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ShortBowCalculationRequestImplCopyWith<$Res>
    implements $ShortBowCalculationRequestCopyWith<$Res> {
  factory _$$ShortBowCalculationRequestImplCopyWith(
          _$ShortBowCalculationRequestImpl value,
          $Res Function(_$ShortBowCalculationRequestImpl) then) =
      __$$ShortBowCalculationRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'initial_symptom') String initialSymptom,
      @JsonKey(name: 'selected_symptoms') List<String> selectedSymptoms});
}

/// @nodoc
class __$$ShortBowCalculationRequestImplCopyWithImpl<$Res>
    extends _$ShortBowCalculationRequestCopyWithImpl<$Res,
        _$ShortBowCalculationRequestImpl>
    implements _$$ShortBowCalculationRequestImplCopyWith<$Res> {
  __$$ShortBowCalculationRequestImplCopyWithImpl(
      _$ShortBowCalculationRequestImpl _value,
      $Res Function(_$ShortBowCalculationRequestImpl) _then)
      : super(_value, _then);

  /// Create a copy of ShortBowCalculationRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? initialSymptom = null,
    Object? selectedSymptoms = null,
  }) {
    return _then(_$ShortBowCalculationRequestImpl(
      initialSymptom: null == initialSymptom
          ? _value.initialSymptom
          : initialSymptom // ignore: cast_nullable_to_non_nullable
              as String,
      selectedSymptoms: null == selectedSymptoms
          ? _value._selectedSymptoms
          : selectedSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ShortBowCalculationRequestImpl implements _ShortBowCalculationRequest {
  const _$ShortBowCalculationRequestImpl(
      {@JsonKey(name: 'initial_symptom') required this.initialSymptom,
      @JsonKey(name: 'selected_symptoms')
      required final List<String> selectedSymptoms})
      : _selectedSymptoms = selectedSymptoms;

  factory _$ShortBowCalculationRequestImpl.fromJson(
          Map<String, dynamic> json) =>
      _$$ShortBowCalculationRequestImplFromJson(json);

  @override
  @JsonKey(name: 'initial_symptom')
  final String initialSymptom;
  final List<String> _selectedSymptoms;
  @override
  @JsonKey(name: 'selected_symptoms')
  List<String> get selectedSymptoms {
    if (_selectedSymptoms is EqualUnmodifiableListView)
      return _selectedSymptoms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_selectedSymptoms);
  }

  @override
  String toString() {
    return 'ShortBowCalculationRequest(initialSymptom: $initialSymptom, selectedSymptoms: $selectedSymptoms)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ShortBowCalculationRequestImpl &&
            (identical(other.initialSymptom, initialSymptom) ||
                other.initialSymptom == initialSymptom) &&
            const DeepCollectionEquality()
                .equals(other._selectedSymptoms, _selectedSymptoms));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, initialSymptom,
      const DeepCollectionEquality().hash(_selectedSymptoms));

  /// Create a copy of ShortBowCalculationRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ShortBowCalculationRequestImplCopyWith<_$ShortBowCalculationRequestImpl>
      get copyWith => __$$ShortBowCalculationRequestImplCopyWithImpl<
          _$ShortBowCalculationRequestImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ShortBowCalculationRequestImplToJson(
      this,
    );
  }
}

abstract class _ShortBowCalculationRequest
    implements ShortBowCalculationRequest {
  const factory _ShortBowCalculationRequest(
      {@JsonKey(name: 'initial_symptom') required final String initialSymptom,
      @JsonKey(name: 'selected_symptoms')
      required final List<String>
          selectedSymptoms}) = _$ShortBowCalculationRequestImpl;

  factory _ShortBowCalculationRequest.fromJson(Map<String, dynamic> json) =
      _$ShortBowCalculationRequestImpl.fromJson;

  @override
  @JsonKey(name: 'initial_symptom')
  String get initialSymptom;
  @override
  @JsonKey(name: 'selected_symptoms')
  List<String> get selectedSymptoms;

  /// Create a copy of ShortBowCalculationRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ShortBowCalculationRequestImplCopyWith<_$ShortBowCalculationRequestImpl>
      get copyWith => throw _privateConstructorUsedError;
}

ShortBowStats _$ShortBowStatsFromJson(Map<String, dynamic> json) {
  return _ShortBowStats.fromJson(json);
}

/// @nodoc
mixin _$ShortBowStats {
  @JsonKey(name: 'total_symptoms')
  int get totalSymptoms => throw _privateConstructorUsedError;
  @JsonKey(name: 'total_links')
  int get totalLinks => throw _privateConstructorUsedError;
  @JsonKey(name: 'total_calculations')
  int get totalCalculations => throw _privateConstructorUsedError;
  @JsonKey(name: 'saved_calculations')
  int get savedCalculations => throw _privateConstructorUsedError;

  /// Serializes this ShortBowStats to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ShortBowStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ShortBowStatsCopyWith<ShortBowStats> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ShortBowStatsCopyWith<$Res> {
  factory $ShortBowStatsCopyWith(
          ShortBowStats value, $Res Function(ShortBowStats) then) =
      _$ShortBowStatsCopyWithImpl<$Res, ShortBowStats>;
  @useResult
  $Res call(
      {@JsonKey(name: 'total_symptoms') int totalSymptoms,
      @JsonKey(name: 'total_links') int totalLinks,
      @JsonKey(name: 'total_calculations') int totalCalculations,
      @JsonKey(name: 'saved_calculations') int savedCalculations});
}

/// @nodoc
class _$ShortBowStatsCopyWithImpl<$Res, $Val extends ShortBowStats>
    implements $ShortBowStatsCopyWith<$Res> {
  _$ShortBowStatsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ShortBowStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalSymptoms = null,
    Object? totalLinks = null,
    Object? totalCalculations = null,
    Object? savedCalculations = null,
  }) {
    return _then(_value.copyWith(
      totalSymptoms: null == totalSymptoms
          ? _value.totalSymptoms
          : totalSymptoms // ignore: cast_nullable_to_non_nullable
              as int,
      totalLinks: null == totalLinks
          ? _value.totalLinks
          : totalLinks // ignore: cast_nullable_to_non_nullable
              as int,
      totalCalculations: null == totalCalculations
          ? _value.totalCalculations
          : totalCalculations // ignore: cast_nullable_to_non_nullable
              as int,
      savedCalculations: null == savedCalculations
          ? _value.savedCalculations
          : savedCalculations // ignore: cast_nullable_to_non_nullable
              as int,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ShortBowStatsImplCopyWith<$Res>
    implements $ShortBowStatsCopyWith<$Res> {
  factory _$$ShortBowStatsImplCopyWith(
          _$ShortBowStatsImpl value, $Res Function(_$ShortBowStatsImpl) then) =
      __$$ShortBowStatsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'total_symptoms') int totalSymptoms,
      @JsonKey(name: 'total_links') int totalLinks,
      @JsonKey(name: 'total_calculations') int totalCalculations,
      @JsonKey(name: 'saved_calculations') int savedCalculations});
}

/// @nodoc
class __$$ShortBowStatsImplCopyWithImpl<$Res>
    extends _$ShortBowStatsCopyWithImpl<$Res, _$ShortBowStatsImpl>
    implements _$$ShortBowStatsImplCopyWith<$Res> {
  __$$ShortBowStatsImplCopyWithImpl(
      _$ShortBowStatsImpl _value, $Res Function(_$ShortBowStatsImpl) _then)
      : super(_value, _then);

  /// Create a copy of ShortBowStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalSymptoms = null,
    Object? totalLinks = null,
    Object? totalCalculations = null,
    Object? savedCalculations = null,
  }) {
    return _then(_$ShortBowStatsImpl(
      totalSymptoms: null == totalSymptoms
          ? _value.totalSymptoms
          : totalSymptoms // ignore: cast_nullable_to_non_nullable
              as int,
      totalLinks: null == totalLinks
          ? _value.totalLinks
          : totalLinks // ignore: cast_nullable_to_non_nullable
              as int,
      totalCalculations: null == totalCalculations
          ? _value.totalCalculations
          : totalCalculations // ignore: cast_nullable_to_non_nullable
              as int,
      savedCalculations: null == savedCalculations
          ? _value.savedCalculations
          : savedCalculations // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ShortBowStatsImpl implements _ShortBowStats {
  const _$ShortBowStatsImpl(
      {@JsonKey(name: 'total_symptoms') required this.totalSymptoms,
      @JsonKey(name: 'total_links') required this.totalLinks,
      @JsonKey(name: 'total_calculations') required this.totalCalculations,
      @JsonKey(name: 'saved_calculations') required this.savedCalculations});

  factory _$ShortBowStatsImpl.fromJson(Map<String, dynamic> json) =>
      _$$ShortBowStatsImplFromJson(json);

  @override
  @JsonKey(name: 'total_symptoms')
  final int totalSymptoms;
  @override
  @JsonKey(name: 'total_links')
  final int totalLinks;
  @override
  @JsonKey(name: 'total_calculations')
  final int totalCalculations;
  @override
  @JsonKey(name: 'saved_calculations')
  final int savedCalculations;

  @override
  String toString() {
    return 'ShortBowStats(totalSymptoms: $totalSymptoms, totalLinks: $totalLinks, totalCalculations: $totalCalculations, savedCalculations: $savedCalculations)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ShortBowStatsImpl &&
            (identical(other.totalSymptoms, totalSymptoms) ||
                other.totalSymptoms == totalSymptoms) &&
            (identical(other.totalLinks, totalLinks) ||
                other.totalLinks == totalLinks) &&
            (identical(other.totalCalculations, totalCalculations) ||
                other.totalCalculations == totalCalculations) &&
            (identical(other.savedCalculations, savedCalculations) ||
                other.savedCalculations == savedCalculations));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, totalSymptoms, totalLinks,
      totalCalculations, savedCalculations);

  /// Create a copy of ShortBowStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ShortBowStatsImplCopyWith<_$ShortBowStatsImpl> get copyWith =>
      __$$ShortBowStatsImplCopyWithImpl<_$ShortBowStatsImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ShortBowStatsImplToJson(
      this,
    );
  }
}

abstract class _ShortBowStats implements ShortBowStats {
  const factory _ShortBowStats(
      {@JsonKey(name: 'total_symptoms') required final int totalSymptoms,
      @JsonKey(name: 'total_links') required final int totalLinks,
      @JsonKey(name: 'total_calculations') required final int totalCalculations,
      @JsonKey(name: 'saved_calculations')
      required final int savedCalculations}) = _$ShortBowStatsImpl;

  factory _ShortBowStats.fromJson(Map<String, dynamic> json) =
      _$ShortBowStatsImpl.fromJson;

  @override
  @JsonKey(name: 'total_symptoms')
  int get totalSymptoms;
  @override
  @JsonKey(name: 'total_links')
  int get totalLinks;
  @override
  @JsonKey(name: 'total_calculations')
  int get totalCalculations;
  @override
  @JsonKey(name: 'saved_calculations')
  int get savedCalculations;

  /// Create a copy of ShortBowStats
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ShortBowStatsImplCopyWith<_$ShortBowStatsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ShortBowImportResult _$ShortBowImportResultFromJson(Map<String, dynamic> json) {
  return _ShortBowImportResult.fromJson(json);
}

/// @nodoc
mixin _$ShortBowImportResult {
  bool get success => throw _privateConstructorUsedError;
  @JsonKey(name: 'symptoms_processed')
  int get symptomsProcessed => throw _privateConstructorUsedError;
  @JsonKey(name: 'symptoms_created')
  int get symptomsCreated => throw _privateConstructorUsedError;
  @JsonKey(name: 'symptoms_updated')
  int get symptomsUpdated => throw _privateConstructorUsedError;
  @JsonKey(name: 'links_processed')
  int get linksProcessed => throw _privateConstructorUsedError;
  @JsonKey(name: 'links_created')
  int get linksCreated => throw _privateConstructorUsedError;
  @JsonKey(name: 'links_updated')
  int get linksUpdated => throw _privateConstructorUsedError;
  List<String> get errors => throw _privateConstructorUsedError;
  List<String> get warnings => throw _privateConstructorUsedError;

  /// Serializes this ShortBowImportResult to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ShortBowImportResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ShortBowImportResultCopyWith<ShortBowImportResult> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ShortBowImportResultCopyWith<$Res> {
  factory $ShortBowImportResultCopyWith(ShortBowImportResult value,
          $Res Function(ShortBowImportResult) then) =
      _$ShortBowImportResultCopyWithImpl<$Res, ShortBowImportResult>;
  @useResult
  $Res call(
      {bool success,
      @JsonKey(name: 'symptoms_processed') int symptomsProcessed,
      @JsonKey(name: 'symptoms_created') int symptomsCreated,
      @JsonKey(name: 'symptoms_updated') int symptomsUpdated,
      @JsonKey(name: 'links_processed') int linksProcessed,
      @JsonKey(name: 'links_created') int linksCreated,
      @JsonKey(name: 'links_updated') int linksUpdated,
      List<String> errors,
      List<String> warnings});
}

/// @nodoc
class _$ShortBowImportResultCopyWithImpl<$Res,
        $Val extends ShortBowImportResult>
    implements $ShortBowImportResultCopyWith<$Res> {
  _$ShortBowImportResultCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ShortBowImportResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? symptomsProcessed = null,
    Object? symptomsCreated = null,
    Object? symptomsUpdated = null,
    Object? linksProcessed = null,
    Object? linksCreated = null,
    Object? linksUpdated = null,
    Object? errors = null,
    Object? warnings = null,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      symptomsProcessed: null == symptomsProcessed
          ? _value.symptomsProcessed
          : symptomsProcessed // ignore: cast_nullable_to_non_nullable
              as int,
      symptomsCreated: null == symptomsCreated
          ? _value.symptomsCreated
          : symptomsCreated // ignore: cast_nullable_to_non_nullable
              as int,
      symptomsUpdated: null == symptomsUpdated
          ? _value.symptomsUpdated
          : symptomsUpdated // ignore: cast_nullable_to_non_nullable
              as int,
      linksProcessed: null == linksProcessed
          ? _value.linksProcessed
          : linksProcessed // ignore: cast_nullable_to_non_nullable
              as int,
      linksCreated: null == linksCreated
          ? _value.linksCreated
          : linksCreated // ignore: cast_nullable_to_non_nullable
              as int,
      linksUpdated: null == linksUpdated
          ? _value.linksUpdated
          : linksUpdated // ignore: cast_nullable_to_non_nullable
              as int,
      errors: null == errors
          ? _value.errors
          : errors // ignore: cast_nullable_to_non_nullable
              as List<String>,
      warnings: null == warnings
          ? _value.warnings
          : warnings // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ShortBowImportResultImplCopyWith<$Res>
    implements $ShortBowImportResultCopyWith<$Res> {
  factory _$$ShortBowImportResultImplCopyWith(_$ShortBowImportResultImpl value,
          $Res Function(_$ShortBowImportResultImpl) then) =
      __$$ShortBowImportResultImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool success,
      @JsonKey(name: 'symptoms_processed') int symptomsProcessed,
      @JsonKey(name: 'symptoms_created') int symptomsCreated,
      @JsonKey(name: 'symptoms_updated') int symptomsUpdated,
      @JsonKey(name: 'links_processed') int linksProcessed,
      @JsonKey(name: 'links_created') int linksCreated,
      @JsonKey(name: 'links_updated') int linksUpdated,
      List<String> errors,
      List<String> warnings});
}

/// @nodoc
class __$$ShortBowImportResultImplCopyWithImpl<$Res>
    extends _$ShortBowImportResultCopyWithImpl<$Res, _$ShortBowImportResultImpl>
    implements _$$ShortBowImportResultImplCopyWith<$Res> {
  __$$ShortBowImportResultImplCopyWithImpl(_$ShortBowImportResultImpl _value,
      $Res Function(_$ShortBowImportResultImpl) _then)
      : super(_value, _then);

  /// Create a copy of ShortBowImportResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? symptomsProcessed = null,
    Object? symptomsCreated = null,
    Object? symptomsUpdated = null,
    Object? linksProcessed = null,
    Object? linksCreated = null,
    Object? linksUpdated = null,
    Object? errors = null,
    Object? warnings = null,
  }) {
    return _then(_$ShortBowImportResultImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      symptomsProcessed: null == symptomsProcessed
          ? _value.symptomsProcessed
          : symptomsProcessed // ignore: cast_nullable_to_non_nullable
              as int,
      symptomsCreated: null == symptomsCreated
          ? _value.symptomsCreated
          : symptomsCreated // ignore: cast_nullable_to_non_nullable
              as int,
      symptomsUpdated: null == symptomsUpdated
          ? _value.symptomsUpdated
          : symptomsUpdated // ignore: cast_nullable_to_non_nullable
              as int,
      linksProcessed: null == linksProcessed
          ? _value.linksProcessed
          : linksProcessed // ignore: cast_nullable_to_non_nullable
              as int,
      linksCreated: null == linksCreated
          ? _value.linksCreated
          : linksCreated // ignore: cast_nullable_to_non_nullable
              as int,
      linksUpdated: null == linksUpdated
          ? _value.linksUpdated
          : linksUpdated // ignore: cast_nullable_to_non_nullable
              as int,
      errors: null == errors
          ? _value._errors
          : errors // ignore: cast_nullable_to_non_nullable
              as List<String>,
      warnings: null == warnings
          ? _value._warnings
          : warnings // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ShortBowImportResultImpl implements _ShortBowImportResult {
  const _$ShortBowImportResultImpl(
      {required this.success,
      @JsonKey(name: 'symptoms_processed') required this.symptomsProcessed,
      @JsonKey(name: 'symptoms_created') required this.symptomsCreated,
      @JsonKey(name: 'symptoms_updated') required this.symptomsUpdated,
      @JsonKey(name: 'links_processed') required this.linksProcessed,
      @JsonKey(name: 'links_created') required this.linksCreated,
      @JsonKey(name: 'links_updated') required this.linksUpdated,
      required final List<String> errors,
      required final List<String> warnings})
      : _errors = errors,
        _warnings = warnings;

  factory _$ShortBowImportResultImpl.fromJson(Map<String, dynamic> json) =>
      _$$ShortBowImportResultImplFromJson(json);

  @override
  final bool success;
  @override
  @JsonKey(name: 'symptoms_processed')
  final int symptomsProcessed;
  @override
  @JsonKey(name: 'symptoms_created')
  final int symptomsCreated;
  @override
  @JsonKey(name: 'symptoms_updated')
  final int symptomsUpdated;
  @override
  @JsonKey(name: 'links_processed')
  final int linksProcessed;
  @override
  @JsonKey(name: 'links_created')
  final int linksCreated;
  @override
  @JsonKey(name: 'links_updated')
  final int linksUpdated;
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

  @override
  String toString() {
    return 'ShortBowImportResult(success: $success, symptomsProcessed: $symptomsProcessed, symptomsCreated: $symptomsCreated, symptomsUpdated: $symptomsUpdated, linksProcessed: $linksProcessed, linksCreated: $linksCreated, linksUpdated: $linksUpdated, errors: $errors, warnings: $warnings)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ShortBowImportResultImpl &&
            (identical(other.success, success) || other.success == success) &&
            (identical(other.symptomsProcessed, symptomsProcessed) ||
                other.symptomsProcessed == symptomsProcessed) &&
            (identical(other.symptomsCreated, symptomsCreated) ||
                other.symptomsCreated == symptomsCreated) &&
            (identical(other.symptomsUpdated, symptomsUpdated) ||
                other.symptomsUpdated == symptomsUpdated) &&
            (identical(other.linksProcessed, linksProcessed) ||
                other.linksProcessed == linksProcessed) &&
            (identical(other.linksCreated, linksCreated) ||
                other.linksCreated == linksCreated) &&
            (identical(other.linksUpdated, linksUpdated) ||
                other.linksUpdated == linksUpdated) &&
            const DeepCollectionEquality().equals(other._errors, _errors) &&
            const DeepCollectionEquality().equals(other._warnings, _warnings));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      success,
      symptomsProcessed,
      symptomsCreated,
      symptomsUpdated,
      linksProcessed,
      linksCreated,
      linksUpdated,
      const DeepCollectionEquality().hash(_errors),
      const DeepCollectionEquality().hash(_warnings));

  /// Create a copy of ShortBowImportResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ShortBowImportResultImplCopyWith<_$ShortBowImportResultImpl>
      get copyWith =>
          __$$ShortBowImportResultImplCopyWithImpl<_$ShortBowImportResultImpl>(
              this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ShortBowImportResultImplToJson(
      this,
    );
  }
}

abstract class _ShortBowImportResult implements ShortBowImportResult {
  const factory _ShortBowImportResult(
      {required final bool success,
      @JsonKey(name: 'symptoms_processed') required final int symptomsProcessed,
      @JsonKey(name: 'symptoms_created') required final int symptomsCreated,
      @JsonKey(name: 'symptoms_updated') required final int symptomsUpdated,
      @JsonKey(name: 'links_processed') required final int linksProcessed,
      @JsonKey(name: 'links_created') required final int linksCreated,
      @JsonKey(name: 'links_updated') required final int linksUpdated,
      required final List<String> errors,
      required final List<String> warnings}) = _$ShortBowImportResultImpl;

  factory _ShortBowImportResult.fromJson(Map<String, dynamic> json) =
      _$ShortBowImportResultImpl.fromJson;

  @override
  bool get success;
  @override
  @JsonKey(name: 'symptoms_processed')
  int get symptomsProcessed;
  @override
  @JsonKey(name: 'symptoms_created')
  int get symptomsCreated;
  @override
  @JsonKey(name: 'symptoms_updated')
  int get symptomsUpdated;
  @override
  @JsonKey(name: 'links_processed')
  int get linksProcessed;
  @override
  @JsonKey(name: 'links_created')
  int get linksCreated;
  @override
  @JsonKey(name: 'links_updated')
  int get linksUpdated;
  @override
  List<String> get errors;
  @override
  List<String> get warnings;

  /// Create a copy of ShortBowImportResult
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ShortBowImportResultImplCopyWith<_$ShortBowImportResultImpl>
      get copyWith => throw _privateConstructorUsedError;
}
