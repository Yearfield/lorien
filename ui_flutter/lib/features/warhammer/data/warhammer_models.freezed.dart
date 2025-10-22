// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'warhammer_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

Symptom _$SymptomFromJson(Map<String, dynamic> json) {
  return _Symptom.fromJson(json);
}

/// @nodoc
mixin _$Symptom {
  int get id => throw _privateConstructorUsedError;
  @JsonKey(name: 'symptom_name')
  String get symptomName => throw _privateConstructorUsedError;
  double get probability => throw _privateConstructorUsedError;
  @JsonKey(name: 'created_at')
  String get createdAt => throw _privateConstructorUsedError;
  @JsonKey(name: 'updated_at')
  String get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this Symptom to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Symptom
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SymptomCopyWith<Symptom> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SymptomCopyWith<$Res> {
  factory $SymptomCopyWith(Symptom value, $Res Function(Symptom) then) =
      _$SymptomCopyWithImpl<$Res, Symptom>;
  @useResult
  $Res call(
      {int id,
      @JsonKey(name: 'symptom_name') String symptomName,
      double probability,
      @JsonKey(name: 'created_at') String createdAt,
      @JsonKey(name: 'updated_at') String updatedAt});
}

/// @nodoc
class _$SymptomCopyWithImpl<$Res, $Val extends Symptom>
    implements $SymptomCopyWith<$Res> {
  _$SymptomCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Symptom
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? symptomName = null,
    Object? probability = null,
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
      probability: null == probability
          ? _value.probability
          : probability // ignore: cast_nullable_to_non_nullable
              as double,
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
abstract class _$$SymptomImplCopyWith<$Res> implements $SymptomCopyWith<$Res> {
  factory _$$SymptomImplCopyWith(
          _$SymptomImpl value, $Res Function(_$SymptomImpl) then) =
      __$$SymptomImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int id,
      @JsonKey(name: 'symptom_name') String symptomName,
      double probability,
      @JsonKey(name: 'created_at') String createdAt,
      @JsonKey(name: 'updated_at') String updatedAt});
}

/// @nodoc
class __$$SymptomImplCopyWithImpl<$Res>
    extends _$SymptomCopyWithImpl<$Res, _$SymptomImpl>
    implements _$$SymptomImplCopyWith<$Res> {
  __$$SymptomImplCopyWithImpl(
      _$SymptomImpl _value, $Res Function(_$SymptomImpl) _then)
      : super(_value, _then);

  /// Create a copy of Symptom
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? symptomName = null,
    Object? probability = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_$SymptomImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      symptomName: null == symptomName
          ? _value.symptomName
          : symptomName // ignore: cast_nullable_to_non_nullable
              as String,
      probability: null == probability
          ? _value.probability
          : probability // ignore: cast_nullable_to_non_nullable
              as double,
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
class _$SymptomImpl implements _Symptom {
  const _$SymptomImpl(
      {required this.id,
      @JsonKey(name: 'symptom_name') required this.symptomName,
      required this.probability,
      @JsonKey(name: 'created_at') required this.createdAt,
      @JsonKey(name: 'updated_at') required this.updatedAt});

  factory _$SymptomImpl.fromJson(Map<String, dynamic> json) =>
      _$$SymptomImplFromJson(json);

  @override
  final int id;
  @override
  @JsonKey(name: 'symptom_name')
  final String symptomName;
  @override
  final double probability;
  @override
  @JsonKey(name: 'created_at')
  final String createdAt;
  @override
  @JsonKey(name: 'updated_at')
  final String updatedAt;

  @override
  String toString() {
    return 'Symptom(id: $id, symptomName: $symptomName, probability: $probability, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SymptomImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.symptomName, symptomName) ||
                other.symptomName == symptomName) &&
            (identical(other.probability, probability) ||
                other.probability == probability) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType, id, symptomName, probability, createdAt, updatedAt);

  /// Create a copy of Symptom
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SymptomImplCopyWith<_$SymptomImpl> get copyWith =>
      __$$SymptomImplCopyWithImpl<_$SymptomImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SymptomImplToJson(
      this,
    );
  }
}

abstract class _Symptom implements Symptom {
  const factory _Symptom(
          {required final int id,
          @JsonKey(name: 'symptom_name') required final String symptomName,
          required final double probability,
          @JsonKey(name: 'created_at') required final String createdAt,
          @JsonKey(name: 'updated_at') required final String updatedAt}) =
      _$SymptomImpl;

  factory _Symptom.fromJson(Map<String, dynamic> json) = _$SymptomImpl.fromJson;

  @override
  int get id;
  @override
  @JsonKey(name: 'symptom_name')
  String get symptomName;
  @override
  double get probability;
  @override
  @JsonKey(name: 'created_at')
  String get createdAt;
  @override
  @JsonKey(name: 'updated_at')
  String get updatedAt;

  /// Create a copy of Symptom
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SymptomImplCopyWith<_$SymptomImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

Disease _$DiseaseFromJson(Map<String, dynamic> json) {
  return _Disease.fromJson(json);
}

/// @nodoc
mixin _$Disease {
  int get id => throw _privateConstructorUsedError;
  @JsonKey(name: 'disease_name')
  String get diseaseName => throw _privateConstructorUsedError;
  @JsonKey(name: 'estimated_lifetime_risk')
  double get estimatedLifetimeRisk => throw _privateConstructorUsedError;
  @JsonKey(name: 'created_at')
  String get createdAt => throw _privateConstructorUsedError;
  @JsonKey(name: 'updated_at')
  String get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this Disease to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Disease
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DiseaseCopyWith<Disease> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DiseaseCopyWith<$Res> {
  factory $DiseaseCopyWith(Disease value, $Res Function(Disease) then) =
      _$DiseaseCopyWithImpl<$Res, Disease>;
  @useResult
  $Res call(
      {int id,
      @JsonKey(name: 'disease_name') String diseaseName,
      @JsonKey(name: 'estimated_lifetime_risk') double estimatedLifetimeRisk,
      @JsonKey(name: 'created_at') String createdAt,
      @JsonKey(name: 'updated_at') String updatedAt});
}

/// @nodoc
class _$DiseaseCopyWithImpl<$Res, $Val extends Disease>
    implements $DiseaseCopyWith<$Res> {
  _$DiseaseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Disease
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? diseaseName = null,
    Object? estimatedLifetimeRisk = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      diseaseName: null == diseaseName
          ? _value.diseaseName
          : diseaseName // ignore: cast_nullable_to_non_nullable
              as String,
      estimatedLifetimeRisk: null == estimatedLifetimeRisk
          ? _value.estimatedLifetimeRisk
          : estimatedLifetimeRisk // ignore: cast_nullable_to_non_nullable
              as double,
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
abstract class _$$DiseaseImplCopyWith<$Res> implements $DiseaseCopyWith<$Res> {
  factory _$$DiseaseImplCopyWith(
          _$DiseaseImpl value, $Res Function(_$DiseaseImpl) then) =
      __$$DiseaseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int id,
      @JsonKey(name: 'disease_name') String diseaseName,
      @JsonKey(name: 'estimated_lifetime_risk') double estimatedLifetimeRisk,
      @JsonKey(name: 'created_at') String createdAt,
      @JsonKey(name: 'updated_at') String updatedAt});
}

/// @nodoc
class __$$DiseaseImplCopyWithImpl<$Res>
    extends _$DiseaseCopyWithImpl<$Res, _$DiseaseImpl>
    implements _$$DiseaseImplCopyWith<$Res> {
  __$$DiseaseImplCopyWithImpl(
      _$DiseaseImpl _value, $Res Function(_$DiseaseImpl) _then)
      : super(_value, _then);

  /// Create a copy of Disease
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? diseaseName = null,
    Object? estimatedLifetimeRisk = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_$DiseaseImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      diseaseName: null == diseaseName
          ? _value.diseaseName
          : diseaseName // ignore: cast_nullable_to_non_nullable
              as String,
      estimatedLifetimeRisk: null == estimatedLifetimeRisk
          ? _value.estimatedLifetimeRisk
          : estimatedLifetimeRisk // ignore: cast_nullable_to_non_nullable
              as double,
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
class _$DiseaseImpl implements _Disease {
  const _$DiseaseImpl(
      {required this.id,
      @JsonKey(name: 'disease_name') required this.diseaseName,
      @JsonKey(name: 'estimated_lifetime_risk')
      required this.estimatedLifetimeRisk,
      @JsonKey(name: 'created_at') required this.createdAt,
      @JsonKey(name: 'updated_at') required this.updatedAt});

  factory _$DiseaseImpl.fromJson(Map<String, dynamic> json) =>
      _$$DiseaseImplFromJson(json);

  @override
  final int id;
  @override
  @JsonKey(name: 'disease_name')
  final String diseaseName;
  @override
  @JsonKey(name: 'estimated_lifetime_risk')
  final double estimatedLifetimeRisk;
  @override
  @JsonKey(name: 'created_at')
  final String createdAt;
  @override
  @JsonKey(name: 'updated_at')
  final String updatedAt;

  @override
  String toString() {
    return 'Disease(id: $id, diseaseName: $diseaseName, estimatedLifetimeRisk: $estimatedLifetimeRisk, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DiseaseImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.diseaseName, diseaseName) ||
                other.diseaseName == diseaseName) &&
            (identical(other.estimatedLifetimeRisk, estimatedLifetimeRisk) ||
                other.estimatedLifetimeRisk == estimatedLifetimeRisk) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, diseaseName,
      estimatedLifetimeRisk, createdAt, updatedAt);

  /// Create a copy of Disease
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DiseaseImplCopyWith<_$DiseaseImpl> get copyWith =>
      __$$DiseaseImplCopyWithImpl<_$DiseaseImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DiseaseImplToJson(
      this,
    );
  }
}

abstract class _Disease implements Disease {
  const factory _Disease(
          {required final int id,
          @JsonKey(name: 'disease_name') required final String diseaseName,
          @JsonKey(name: 'estimated_lifetime_risk')
          required final double estimatedLifetimeRisk,
          @JsonKey(name: 'created_at') required final String createdAt,
          @JsonKey(name: 'updated_at') required final String updatedAt}) =
      _$DiseaseImpl;

  factory _Disease.fromJson(Map<String, dynamic> json) = _$DiseaseImpl.fromJson;

  @override
  int get id;
  @override
  @JsonKey(name: 'disease_name')
  String get diseaseName;
  @override
  @JsonKey(name: 'estimated_lifetime_risk')
  double get estimatedLifetimeRisk;
  @override
  @JsonKey(name: 'created_at')
  String get createdAt;
  @override
  @JsonKey(name: 'updated_at')
  String get updatedAt;

  /// Create a copy of Disease
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DiseaseImplCopyWith<_$DiseaseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

DiseaseResult _$DiseaseResultFromJson(Map<String, dynamic> json) {
  return _DiseaseResult.fromJson(json);
}

/// @nodoc
mixin _$DiseaseResult {
  String get disease => throw _privateConstructorUsedError;
  double get probability => throw _privateConstructorUsedError;

  /// Serializes this DiseaseResult to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DiseaseResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DiseaseResultCopyWith<DiseaseResult> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DiseaseResultCopyWith<$Res> {
  factory $DiseaseResultCopyWith(
          DiseaseResult value, $Res Function(DiseaseResult) then) =
      _$DiseaseResultCopyWithImpl<$Res, DiseaseResult>;
  @useResult
  $Res call({String disease, double probability});
}

/// @nodoc
class _$DiseaseResultCopyWithImpl<$Res, $Val extends DiseaseResult>
    implements $DiseaseResultCopyWith<$Res> {
  _$DiseaseResultCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DiseaseResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? disease = null,
    Object? probability = null,
  }) {
    return _then(_value.copyWith(
      disease: null == disease
          ? _value.disease
          : disease // ignore: cast_nullable_to_non_nullable
              as String,
      probability: null == probability
          ? _value.probability
          : probability // ignore: cast_nullable_to_non_nullable
              as double,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DiseaseResultImplCopyWith<$Res>
    implements $DiseaseResultCopyWith<$Res> {
  factory _$$DiseaseResultImplCopyWith(
          _$DiseaseResultImpl value, $Res Function(_$DiseaseResultImpl) then) =
      __$$DiseaseResultImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String disease, double probability});
}

/// @nodoc
class __$$DiseaseResultImplCopyWithImpl<$Res>
    extends _$DiseaseResultCopyWithImpl<$Res, _$DiseaseResultImpl>
    implements _$$DiseaseResultImplCopyWith<$Res> {
  __$$DiseaseResultImplCopyWithImpl(
      _$DiseaseResultImpl _value, $Res Function(_$DiseaseResultImpl) _then)
      : super(_value, _then);

  /// Create a copy of DiseaseResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? disease = null,
    Object? probability = null,
  }) {
    return _then(_$DiseaseResultImpl(
      disease: null == disease
          ? _value.disease
          : disease // ignore: cast_nullable_to_non_nullable
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
class _$DiseaseResultImpl implements _DiseaseResult {
  const _$DiseaseResultImpl({required this.disease, required this.probability});

  factory _$DiseaseResultImpl.fromJson(Map<String, dynamic> json) =>
      _$$DiseaseResultImplFromJson(json);

  @override
  final String disease;
  @override
  final double probability;

  @override
  String toString() {
    return 'DiseaseResult(disease: $disease, probability: $probability)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DiseaseResultImpl &&
            (identical(other.disease, disease) || other.disease == disease) &&
            (identical(other.probability, probability) ||
                other.probability == probability));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, disease, probability);

  /// Create a copy of DiseaseResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DiseaseResultImplCopyWith<_$DiseaseResultImpl> get copyWith =>
      __$$DiseaseResultImplCopyWithImpl<_$DiseaseResultImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DiseaseResultImplToJson(
      this,
    );
  }
}

abstract class _DiseaseResult implements DiseaseResult {
  const factory _DiseaseResult(
      {required final String disease,
      required final double probability}) = _$DiseaseResultImpl;

  factory _DiseaseResult.fromJson(Map<String, dynamic> json) =
      _$DiseaseResultImpl.fromJson;

  @override
  String get disease;
  @override
  double get probability;

  /// Create a copy of DiseaseResult
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DiseaseResultImplCopyWith<_$DiseaseResultImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CalculationRequest _$CalculationRequestFromJson(Map<String, dynamic> json) {
  return _CalculationRequest.fromJson(json);
}

/// @nodoc
mixin _$CalculationRequest {
  List<String> get symptoms => throw _privateConstructorUsedError;

  /// Serializes this CalculationRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CalculationRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CalculationRequestCopyWith<CalculationRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CalculationRequestCopyWith<$Res> {
  factory $CalculationRequestCopyWith(
          CalculationRequest value, $Res Function(CalculationRequest) then) =
      _$CalculationRequestCopyWithImpl<$Res, CalculationRequest>;
  @useResult
  $Res call({List<String> symptoms});
}

/// @nodoc
class _$CalculationRequestCopyWithImpl<$Res, $Val extends CalculationRequest>
    implements $CalculationRequestCopyWith<$Res> {
  _$CalculationRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CalculationRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? symptoms = null,
  }) {
    return _then(_value.copyWith(
      symptoms: null == symptoms
          ? _value.symptoms
          : symptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CalculationRequestImplCopyWith<$Res>
    implements $CalculationRequestCopyWith<$Res> {
  factory _$$CalculationRequestImplCopyWith(_$CalculationRequestImpl value,
          $Res Function(_$CalculationRequestImpl) then) =
      __$$CalculationRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({List<String> symptoms});
}

/// @nodoc
class __$$CalculationRequestImplCopyWithImpl<$Res>
    extends _$CalculationRequestCopyWithImpl<$Res, _$CalculationRequestImpl>
    implements _$$CalculationRequestImplCopyWith<$Res> {
  __$$CalculationRequestImplCopyWithImpl(_$CalculationRequestImpl _value,
      $Res Function(_$CalculationRequestImpl) _then)
      : super(_value, _then);

  /// Create a copy of CalculationRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? symptoms = null,
  }) {
    return _then(_$CalculationRequestImpl(
      symptoms: null == symptoms
          ? _value._symptoms
          : symptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CalculationRequestImpl implements _CalculationRequest {
  const _$CalculationRequestImpl({required final List<String> symptoms})
      : _symptoms = symptoms;

  factory _$CalculationRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$CalculationRequestImplFromJson(json);

  final List<String> _symptoms;
  @override
  List<String> get symptoms {
    if (_symptoms is EqualUnmodifiableListView) return _symptoms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_symptoms);
  }

  @override
  String toString() {
    return 'CalculationRequest(symptoms: $symptoms)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CalculationRequestImpl &&
            const DeepCollectionEquality().equals(other._symptoms, _symptoms));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, const DeepCollectionEquality().hash(_symptoms));

  /// Create a copy of CalculationRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CalculationRequestImplCopyWith<_$CalculationRequestImpl> get copyWith =>
      __$$CalculationRequestImplCopyWithImpl<_$CalculationRequestImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CalculationRequestImplToJson(
      this,
    );
  }
}

abstract class _CalculationRequest implements CalculationRequest {
  const factory _CalculationRequest({required final List<String> symptoms}) =
      _$CalculationRequestImpl;

  factory _CalculationRequest.fromJson(Map<String, dynamic> json) =
      _$CalculationRequestImpl.fromJson;

  @override
  List<String> get symptoms;

  /// Create a copy of CalculationRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CalculationRequestImplCopyWith<_$CalculationRequestImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CalculationResponse _$CalculationResponseFromJson(Map<String, dynamic> json) {
  return _CalculationResponse.fromJson(json);
}

/// @nodoc
mixin _$CalculationResponse {
  @JsonKey(name: 'calculation_id')
  int? get calculationId => throw _privateConstructorUsedError;
  @JsonKey(name: 'input_symptoms')
  List<String> get inputSymptoms => throw _privateConstructorUsedError;
  @JsonKey(name: 'results')
  List<DiseaseResult> get results => throw _privateConstructorUsedError;
  @JsonKey(name: 'timestamp')
  String get timestamp => throw _privateConstructorUsedError;
  @JsonKey(name: 'errors')
  List<String> get errors => throw _privateConstructorUsedError;
  @JsonKey(name: 'synonym_resolutions')
  List<Map<String, dynamic>> get synonymResolutions =>
      throw _privateConstructorUsedError;

  /// Serializes this CalculationResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CalculationResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CalculationResponseCopyWith<CalculationResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CalculationResponseCopyWith<$Res> {
  factory $CalculationResponseCopyWith(
          CalculationResponse value, $Res Function(CalculationResponse) then) =
      _$CalculationResponseCopyWithImpl<$Res, CalculationResponse>;
  @useResult
  $Res call(
      {@JsonKey(name: 'calculation_id') int? calculationId,
      @JsonKey(name: 'input_symptoms') List<String> inputSymptoms,
      @JsonKey(name: 'results') List<DiseaseResult> results,
      @JsonKey(name: 'timestamp') String timestamp,
      @JsonKey(name: 'errors') List<String> errors,
      @JsonKey(name: 'synonym_resolutions')
      List<Map<String, dynamic>> synonymResolutions});
}

/// @nodoc
class _$CalculationResponseCopyWithImpl<$Res, $Val extends CalculationResponse>
    implements $CalculationResponseCopyWith<$Res> {
  _$CalculationResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CalculationResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? calculationId = freezed,
    Object? inputSymptoms = null,
    Object? results = null,
    Object? timestamp = null,
    Object? errors = null,
    Object? synonymResolutions = null,
  }) {
    return _then(_value.copyWith(
      calculationId: freezed == calculationId
          ? _value.calculationId
          : calculationId // ignore: cast_nullable_to_non_nullable
              as int?,
      inputSymptoms: null == inputSymptoms
          ? _value.inputSymptoms
          : inputSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      results: null == results
          ? _value.results
          : results // ignore: cast_nullable_to_non_nullable
              as List<DiseaseResult>,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as String,
      errors: null == errors
          ? _value.errors
          : errors // ignore: cast_nullable_to_non_nullable
              as List<String>,
      synonymResolutions: null == synonymResolutions
          ? _value.synonymResolutions
          : synonymResolutions // ignore: cast_nullable_to_non_nullable
              as List<Map<String, dynamic>>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CalculationResponseImplCopyWith<$Res>
    implements $CalculationResponseCopyWith<$Res> {
  factory _$$CalculationResponseImplCopyWith(_$CalculationResponseImpl value,
          $Res Function(_$CalculationResponseImpl) then) =
      __$$CalculationResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'calculation_id') int? calculationId,
      @JsonKey(name: 'input_symptoms') List<String> inputSymptoms,
      @JsonKey(name: 'results') List<DiseaseResult> results,
      @JsonKey(name: 'timestamp') String timestamp,
      @JsonKey(name: 'errors') List<String> errors,
      @JsonKey(name: 'synonym_resolutions')
      List<Map<String, dynamic>> synonymResolutions});
}

/// @nodoc
class __$$CalculationResponseImplCopyWithImpl<$Res>
    extends _$CalculationResponseCopyWithImpl<$Res, _$CalculationResponseImpl>
    implements _$$CalculationResponseImplCopyWith<$Res> {
  __$$CalculationResponseImplCopyWithImpl(_$CalculationResponseImpl _value,
      $Res Function(_$CalculationResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of CalculationResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? calculationId = freezed,
    Object? inputSymptoms = null,
    Object? results = null,
    Object? timestamp = null,
    Object? errors = null,
    Object? synonymResolutions = null,
  }) {
    return _then(_$CalculationResponseImpl(
      calculationId: freezed == calculationId
          ? _value.calculationId
          : calculationId // ignore: cast_nullable_to_non_nullable
              as int?,
      inputSymptoms: null == inputSymptoms
          ? _value._inputSymptoms
          : inputSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      results: null == results
          ? _value._results
          : results // ignore: cast_nullable_to_non_nullable
              as List<DiseaseResult>,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as String,
      errors: null == errors
          ? _value._errors
          : errors // ignore: cast_nullable_to_non_nullable
              as List<String>,
      synonymResolutions: null == synonymResolutions
          ? _value._synonymResolutions
          : synonymResolutions // ignore: cast_nullable_to_non_nullable
              as List<Map<String, dynamic>>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CalculationResponseImpl implements _CalculationResponse {
  const _$CalculationResponseImpl(
      {@JsonKey(name: 'calculation_id') this.calculationId,
      @JsonKey(name: 'input_symptoms')
      final List<String> inputSymptoms = const [],
      @JsonKey(name: 'results') final List<DiseaseResult> results = const [],
      @JsonKey(name: 'timestamp') required this.timestamp,
      @JsonKey(name: 'errors') final List<String> errors = const [],
      @JsonKey(name: 'synonym_resolutions')
      final List<Map<String, dynamic>> synonymResolutions = const []})
      : _inputSymptoms = inputSymptoms,
        _results = results,
        _errors = errors,
        _synonymResolutions = synonymResolutions;

  factory _$CalculationResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$CalculationResponseImplFromJson(json);

  @override
  @JsonKey(name: 'calculation_id')
  final int? calculationId;
  final List<String> _inputSymptoms;
  @override
  @JsonKey(name: 'input_symptoms')
  List<String> get inputSymptoms {
    if (_inputSymptoms is EqualUnmodifiableListView) return _inputSymptoms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_inputSymptoms);
  }

  final List<DiseaseResult> _results;
  @override
  @JsonKey(name: 'results')
  List<DiseaseResult> get results {
    if (_results is EqualUnmodifiableListView) return _results;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_results);
  }

  @override
  @JsonKey(name: 'timestamp')
  final String timestamp;
  final List<String> _errors;
  @override
  @JsonKey(name: 'errors')
  List<String> get errors {
    if (_errors is EqualUnmodifiableListView) return _errors;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_errors);
  }

  final List<Map<String, dynamic>> _synonymResolutions;
  @override
  @JsonKey(name: 'synonym_resolutions')
  List<Map<String, dynamic>> get synonymResolutions {
    if (_synonymResolutions is EqualUnmodifiableListView)
      return _synonymResolutions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_synonymResolutions);
  }

  @override
  String toString() {
    return 'CalculationResponse(calculationId: $calculationId, inputSymptoms: $inputSymptoms, results: $results, timestamp: $timestamp, errors: $errors, synonymResolutions: $synonymResolutions)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CalculationResponseImpl &&
            (identical(other.calculationId, calculationId) ||
                other.calculationId == calculationId) &&
            const DeepCollectionEquality()
                .equals(other._inputSymptoms, _inputSymptoms) &&
            const DeepCollectionEquality().equals(other._results, _results) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            const DeepCollectionEquality().equals(other._errors, _errors) &&
            const DeepCollectionEquality()
                .equals(other._synonymResolutions, _synonymResolutions));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      calculationId,
      const DeepCollectionEquality().hash(_inputSymptoms),
      const DeepCollectionEquality().hash(_results),
      timestamp,
      const DeepCollectionEquality().hash(_errors),
      const DeepCollectionEquality().hash(_synonymResolutions));

  /// Create a copy of CalculationResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CalculationResponseImplCopyWith<_$CalculationResponseImpl> get copyWith =>
      __$$CalculationResponseImplCopyWithImpl<_$CalculationResponseImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CalculationResponseImplToJson(
      this,
    );
  }
}

abstract class _CalculationResponse implements CalculationResponse {
  const factory _CalculationResponse(
          {@JsonKey(name: 'calculation_id') final int? calculationId,
          @JsonKey(name: 'input_symptoms') final List<String> inputSymptoms,
          @JsonKey(name: 'results') final List<DiseaseResult> results,
          @JsonKey(name: 'timestamp') required final String timestamp,
          @JsonKey(name: 'errors') final List<String> errors,
          @JsonKey(name: 'synonym_resolutions')
          final List<Map<String, dynamic>> synonymResolutions}) =
      _$CalculationResponseImpl;

  factory _CalculationResponse.fromJson(Map<String, dynamic> json) =
      _$CalculationResponseImpl.fromJson;

  @override
  @JsonKey(name: 'calculation_id')
  int? get calculationId;
  @override
  @JsonKey(name: 'input_symptoms')
  List<String> get inputSymptoms;
  @override
  @JsonKey(name: 'results')
  List<DiseaseResult> get results;
  @override
  @JsonKey(name: 'timestamp')
  String get timestamp;
  @override
  @JsonKey(name: 'errors')
  List<String> get errors;
  @override
  @JsonKey(name: 'synonym_resolutions')
  List<Map<String, dynamic>> get synonymResolutions;

  /// Create a copy of CalculationResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CalculationResponseImplCopyWith<_$CalculationResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ImportResultResponse _$ImportResultResponseFromJson(Map<String, dynamic> json) {
  return _ImportResultResponse.fromJson(json);
}

/// @nodoc
mixin _$ImportResultResponse {
  bool get success => throw _privateConstructorUsedError;
  int get diseasesProcessed => throw _privateConstructorUsedError;
  int get diseasesCreated => throw _privateConstructorUsedError;
  int get diseasesUpdated => throw _privateConstructorUsedError;
  int get symptomsProcessed => throw _privateConstructorUsedError;
  int get symptomsCreated => throw _privateConstructorUsedError;
  int get symptomsUpdated => throw _privateConstructorUsedError;
  int get conditionalsProcessed => throw _privateConstructorUsedError;
  int get conditionalsCreated => throw _privateConstructorUsedError;
  int get conditionalsUpdated => throw _privateConstructorUsedError;
  List<String> get errors => throw _privateConstructorUsedError;
  List<String> get warnings => throw _privateConstructorUsedError;

  /// Serializes this ImportResultResponse to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ImportResultResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ImportResultResponseCopyWith<ImportResultResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ImportResultResponseCopyWith<$Res> {
  factory $ImportResultResponseCopyWith(ImportResultResponse value,
          $Res Function(ImportResultResponse) then) =
      _$ImportResultResponseCopyWithImpl<$Res, ImportResultResponse>;
  @useResult
  $Res call(
      {bool success,
      int diseasesProcessed,
      int diseasesCreated,
      int diseasesUpdated,
      int symptomsProcessed,
      int symptomsCreated,
      int symptomsUpdated,
      int conditionalsProcessed,
      int conditionalsCreated,
      int conditionalsUpdated,
      List<String> errors,
      List<String> warnings});
}

/// @nodoc
class _$ImportResultResponseCopyWithImpl<$Res,
        $Val extends ImportResultResponse>
    implements $ImportResultResponseCopyWith<$Res> {
  _$ImportResultResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ImportResultResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? diseasesProcessed = null,
    Object? diseasesCreated = null,
    Object? diseasesUpdated = null,
    Object? symptomsProcessed = null,
    Object? symptomsCreated = null,
    Object? symptomsUpdated = null,
    Object? conditionalsProcessed = null,
    Object? conditionalsCreated = null,
    Object? conditionalsUpdated = null,
    Object? errors = null,
    Object? warnings = null,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      diseasesProcessed: null == diseasesProcessed
          ? _value.diseasesProcessed
          : diseasesProcessed // ignore: cast_nullable_to_non_nullable
              as int,
      diseasesCreated: null == diseasesCreated
          ? _value.diseasesCreated
          : diseasesCreated // ignore: cast_nullable_to_non_nullable
              as int,
      diseasesUpdated: null == diseasesUpdated
          ? _value.diseasesUpdated
          : diseasesUpdated // ignore: cast_nullable_to_non_nullable
              as int,
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
      conditionalsProcessed: null == conditionalsProcessed
          ? _value.conditionalsProcessed
          : conditionalsProcessed // ignore: cast_nullable_to_non_nullable
              as int,
      conditionalsCreated: null == conditionalsCreated
          ? _value.conditionalsCreated
          : conditionalsCreated // ignore: cast_nullable_to_non_nullable
              as int,
      conditionalsUpdated: null == conditionalsUpdated
          ? _value.conditionalsUpdated
          : conditionalsUpdated // ignore: cast_nullable_to_non_nullable
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
abstract class _$$ImportResultResponseImplCopyWith<$Res>
    implements $ImportResultResponseCopyWith<$Res> {
  factory _$$ImportResultResponseImplCopyWith(_$ImportResultResponseImpl value,
          $Res Function(_$ImportResultResponseImpl) then) =
      __$$ImportResultResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool success,
      int diseasesProcessed,
      int diseasesCreated,
      int diseasesUpdated,
      int symptomsProcessed,
      int symptomsCreated,
      int symptomsUpdated,
      int conditionalsProcessed,
      int conditionalsCreated,
      int conditionalsUpdated,
      List<String> errors,
      List<String> warnings});
}

/// @nodoc
class __$$ImportResultResponseImplCopyWithImpl<$Res>
    extends _$ImportResultResponseCopyWithImpl<$Res, _$ImportResultResponseImpl>
    implements _$$ImportResultResponseImplCopyWith<$Res> {
  __$$ImportResultResponseImplCopyWithImpl(_$ImportResultResponseImpl _value,
      $Res Function(_$ImportResultResponseImpl) _then)
      : super(_value, _then);

  /// Create a copy of ImportResultResponse
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? diseasesProcessed = null,
    Object? diseasesCreated = null,
    Object? diseasesUpdated = null,
    Object? symptomsProcessed = null,
    Object? symptomsCreated = null,
    Object? symptomsUpdated = null,
    Object? conditionalsProcessed = null,
    Object? conditionalsCreated = null,
    Object? conditionalsUpdated = null,
    Object? errors = null,
    Object? warnings = null,
  }) {
    return _then(_$ImportResultResponseImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      diseasesProcessed: null == diseasesProcessed
          ? _value.diseasesProcessed
          : diseasesProcessed // ignore: cast_nullable_to_non_nullable
              as int,
      diseasesCreated: null == diseasesCreated
          ? _value.diseasesCreated
          : diseasesCreated // ignore: cast_nullable_to_non_nullable
              as int,
      diseasesUpdated: null == diseasesUpdated
          ? _value.diseasesUpdated
          : diseasesUpdated // ignore: cast_nullable_to_non_nullable
              as int,
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
      conditionalsProcessed: null == conditionalsProcessed
          ? _value.conditionalsProcessed
          : conditionalsProcessed // ignore: cast_nullable_to_non_nullable
              as int,
      conditionalsCreated: null == conditionalsCreated
          ? _value.conditionalsCreated
          : conditionalsCreated // ignore: cast_nullable_to_non_nullable
              as int,
      conditionalsUpdated: null == conditionalsUpdated
          ? _value.conditionalsUpdated
          : conditionalsUpdated // ignore: cast_nullable_to_non_nullable
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
class _$ImportResultResponseImpl implements _ImportResultResponse {
  const _$ImportResultResponseImpl(
      {required this.success,
      this.diseasesProcessed = 0,
      this.diseasesCreated = 0,
      this.diseasesUpdated = 0,
      this.symptomsProcessed = 0,
      this.symptomsCreated = 0,
      this.symptomsUpdated = 0,
      this.conditionalsProcessed = 0,
      this.conditionalsCreated = 0,
      this.conditionalsUpdated = 0,
      final List<String> errors = const [],
      final List<String> warnings = const []})
      : _errors = errors,
        _warnings = warnings;

  factory _$ImportResultResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$ImportResultResponseImplFromJson(json);

  @override
  final bool success;
  @override
  @JsonKey()
  final int diseasesProcessed;
  @override
  @JsonKey()
  final int diseasesCreated;
  @override
  @JsonKey()
  final int diseasesUpdated;
  @override
  @JsonKey()
  final int symptomsProcessed;
  @override
  @JsonKey()
  final int symptomsCreated;
  @override
  @JsonKey()
  final int symptomsUpdated;
  @override
  @JsonKey()
  final int conditionalsProcessed;
  @override
  @JsonKey()
  final int conditionalsCreated;
  @override
  @JsonKey()
  final int conditionalsUpdated;
  final List<String> _errors;
  @override
  @JsonKey()
  List<String> get errors {
    if (_errors is EqualUnmodifiableListView) return _errors;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_errors);
  }

  final List<String> _warnings;
  @override
  @JsonKey()
  List<String> get warnings {
    if (_warnings is EqualUnmodifiableListView) return _warnings;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_warnings);
  }

  @override
  String toString() {
    return 'ImportResultResponse(success: $success, diseasesProcessed: $diseasesProcessed, diseasesCreated: $diseasesCreated, diseasesUpdated: $diseasesUpdated, symptomsProcessed: $symptomsProcessed, symptomsCreated: $symptomsCreated, symptomsUpdated: $symptomsUpdated, conditionalsProcessed: $conditionalsProcessed, conditionalsCreated: $conditionalsCreated, conditionalsUpdated: $conditionalsUpdated, errors: $errors, warnings: $warnings)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ImportResultResponseImpl &&
            (identical(other.success, success) || other.success == success) &&
            (identical(other.diseasesProcessed, diseasesProcessed) ||
                other.diseasesProcessed == diseasesProcessed) &&
            (identical(other.diseasesCreated, diseasesCreated) ||
                other.diseasesCreated == diseasesCreated) &&
            (identical(other.diseasesUpdated, diseasesUpdated) ||
                other.diseasesUpdated == diseasesUpdated) &&
            (identical(other.symptomsProcessed, symptomsProcessed) ||
                other.symptomsProcessed == symptomsProcessed) &&
            (identical(other.symptomsCreated, symptomsCreated) ||
                other.symptomsCreated == symptomsCreated) &&
            (identical(other.symptomsUpdated, symptomsUpdated) ||
                other.symptomsUpdated == symptomsUpdated) &&
            (identical(other.conditionalsProcessed, conditionalsProcessed) ||
                other.conditionalsProcessed == conditionalsProcessed) &&
            (identical(other.conditionalsCreated, conditionalsCreated) ||
                other.conditionalsCreated == conditionalsCreated) &&
            (identical(other.conditionalsUpdated, conditionalsUpdated) ||
                other.conditionalsUpdated == conditionalsUpdated) &&
            const DeepCollectionEquality().equals(other._errors, _errors) &&
            const DeepCollectionEquality().equals(other._warnings, _warnings));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      success,
      diseasesProcessed,
      diseasesCreated,
      diseasesUpdated,
      symptomsProcessed,
      symptomsCreated,
      symptomsUpdated,
      conditionalsProcessed,
      conditionalsCreated,
      conditionalsUpdated,
      const DeepCollectionEquality().hash(_errors),
      const DeepCollectionEquality().hash(_warnings));

  /// Create a copy of ImportResultResponse
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ImportResultResponseImplCopyWith<_$ImportResultResponseImpl>
      get copyWith =>
          __$$ImportResultResponseImplCopyWithImpl<_$ImportResultResponseImpl>(
              this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ImportResultResponseImplToJson(
      this,
    );
  }
}

abstract class _ImportResultResponse implements ImportResultResponse {
  const factory _ImportResultResponse(
      {required final bool success,
      final int diseasesProcessed,
      final int diseasesCreated,
      final int diseasesUpdated,
      final int symptomsProcessed,
      final int symptomsCreated,
      final int symptomsUpdated,
      final int conditionalsProcessed,
      final int conditionalsCreated,
      final int conditionalsUpdated,
      final List<String> errors,
      final List<String> warnings}) = _$ImportResultResponseImpl;

  factory _ImportResultResponse.fromJson(Map<String, dynamic> json) =
      _$ImportResultResponseImpl.fromJson;

  @override
  bool get success;
  @override
  int get diseasesProcessed;
  @override
  int get diseasesCreated;
  @override
  int get diseasesUpdated;
  @override
  int get symptomsProcessed;
  @override
  int get symptomsCreated;
  @override
  int get symptomsUpdated;
  @override
  int get conditionalsProcessed;
  @override
  int get conditionalsCreated;
  @override
  int get conditionalsUpdated;
  @override
  List<String> get errors;
  @override
  List<String> get warnings;

  /// Create a copy of ImportResultResponse
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ImportResultResponseImplCopyWith<_$ImportResultResponseImpl>
      get copyWith => throw _privateConstructorUsedError;
}

WarhammerStats _$WarhammerStatsFromJson(Map<String, dynamic> json) {
  return _WarhammerStats.fromJson(json);
}

/// @nodoc
mixin _$WarhammerStats {
  @JsonKey(name: 'total_diseases')
  int get totalDiseases => throw _privateConstructorUsedError;
  @JsonKey(name: 'total_symptoms')
  int get totalSymptoms => throw _privateConstructorUsedError;
  @JsonKey(name: 'total_conditionals')
  int get totalConditionals => throw _privateConstructorUsedError;
  @JsonKey(name: 'total_calculations')
  int get totalCalculations => throw _privateConstructorUsedError;
  @JsonKey(name: 'saved_calculations')
  int get savedCalculations => throw _privateConstructorUsedError;

  /// Serializes this WarhammerStats to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of WarhammerStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $WarhammerStatsCopyWith<WarhammerStats> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $WarhammerStatsCopyWith<$Res> {
  factory $WarhammerStatsCopyWith(
          WarhammerStats value, $Res Function(WarhammerStats) then) =
      _$WarhammerStatsCopyWithImpl<$Res, WarhammerStats>;
  @useResult
  $Res call(
      {@JsonKey(name: 'total_diseases') int totalDiseases,
      @JsonKey(name: 'total_symptoms') int totalSymptoms,
      @JsonKey(name: 'total_conditionals') int totalConditionals,
      @JsonKey(name: 'total_calculations') int totalCalculations,
      @JsonKey(name: 'saved_calculations') int savedCalculations});
}

/// @nodoc
class _$WarhammerStatsCopyWithImpl<$Res, $Val extends WarhammerStats>
    implements $WarhammerStatsCopyWith<$Res> {
  _$WarhammerStatsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of WarhammerStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalDiseases = null,
    Object? totalSymptoms = null,
    Object? totalConditionals = null,
    Object? totalCalculations = null,
    Object? savedCalculations = null,
  }) {
    return _then(_value.copyWith(
      totalDiseases: null == totalDiseases
          ? _value.totalDiseases
          : totalDiseases // ignore: cast_nullable_to_non_nullable
              as int,
      totalSymptoms: null == totalSymptoms
          ? _value.totalSymptoms
          : totalSymptoms // ignore: cast_nullable_to_non_nullable
              as int,
      totalConditionals: null == totalConditionals
          ? _value.totalConditionals
          : totalConditionals // ignore: cast_nullable_to_non_nullable
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
abstract class _$$WarhammerStatsImplCopyWith<$Res>
    implements $WarhammerStatsCopyWith<$Res> {
  factory _$$WarhammerStatsImplCopyWith(_$WarhammerStatsImpl value,
          $Res Function(_$WarhammerStatsImpl) then) =
      __$$WarhammerStatsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'total_diseases') int totalDiseases,
      @JsonKey(name: 'total_symptoms') int totalSymptoms,
      @JsonKey(name: 'total_conditionals') int totalConditionals,
      @JsonKey(name: 'total_calculations') int totalCalculations,
      @JsonKey(name: 'saved_calculations') int savedCalculations});
}

/// @nodoc
class __$$WarhammerStatsImplCopyWithImpl<$Res>
    extends _$WarhammerStatsCopyWithImpl<$Res, _$WarhammerStatsImpl>
    implements _$$WarhammerStatsImplCopyWith<$Res> {
  __$$WarhammerStatsImplCopyWithImpl(
      _$WarhammerStatsImpl _value, $Res Function(_$WarhammerStatsImpl) _then)
      : super(_value, _then);

  /// Create a copy of WarhammerStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalDiseases = null,
    Object? totalSymptoms = null,
    Object? totalConditionals = null,
    Object? totalCalculations = null,
    Object? savedCalculations = null,
  }) {
    return _then(_$WarhammerStatsImpl(
      totalDiseases: null == totalDiseases
          ? _value.totalDiseases
          : totalDiseases // ignore: cast_nullable_to_non_nullable
              as int,
      totalSymptoms: null == totalSymptoms
          ? _value.totalSymptoms
          : totalSymptoms // ignore: cast_nullable_to_non_nullable
              as int,
      totalConditionals: null == totalConditionals
          ? _value.totalConditionals
          : totalConditionals // ignore: cast_nullable_to_non_nullable
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
class _$WarhammerStatsImpl implements _WarhammerStats {
  const _$WarhammerStatsImpl(
      {@JsonKey(name: 'total_diseases') required this.totalDiseases,
      @JsonKey(name: 'total_symptoms') required this.totalSymptoms,
      @JsonKey(name: 'total_conditionals') required this.totalConditionals,
      @JsonKey(name: 'total_calculations') required this.totalCalculations,
      @JsonKey(name: 'saved_calculations') required this.savedCalculations});

  factory _$WarhammerStatsImpl.fromJson(Map<String, dynamic> json) =>
      _$$WarhammerStatsImplFromJson(json);

  @override
  @JsonKey(name: 'total_diseases')
  final int totalDiseases;
  @override
  @JsonKey(name: 'total_symptoms')
  final int totalSymptoms;
  @override
  @JsonKey(name: 'total_conditionals')
  final int totalConditionals;
  @override
  @JsonKey(name: 'total_calculations')
  final int totalCalculations;
  @override
  @JsonKey(name: 'saved_calculations')
  final int savedCalculations;

  @override
  String toString() {
    return 'WarhammerStats(totalDiseases: $totalDiseases, totalSymptoms: $totalSymptoms, totalConditionals: $totalConditionals, totalCalculations: $totalCalculations, savedCalculations: $savedCalculations)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$WarhammerStatsImpl &&
            (identical(other.totalDiseases, totalDiseases) ||
                other.totalDiseases == totalDiseases) &&
            (identical(other.totalSymptoms, totalSymptoms) ||
                other.totalSymptoms == totalSymptoms) &&
            (identical(other.totalConditionals, totalConditionals) ||
                other.totalConditionals == totalConditionals) &&
            (identical(other.totalCalculations, totalCalculations) ||
                other.totalCalculations == totalCalculations) &&
            (identical(other.savedCalculations, savedCalculations) ||
                other.savedCalculations == savedCalculations));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, totalDiseases, totalSymptoms,
      totalConditionals, totalCalculations, savedCalculations);

  /// Create a copy of WarhammerStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$WarhammerStatsImplCopyWith<_$WarhammerStatsImpl> get copyWith =>
      __$$WarhammerStatsImplCopyWithImpl<_$WarhammerStatsImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$WarhammerStatsImplToJson(
      this,
    );
  }
}

abstract class _WarhammerStats implements WarhammerStats {
  const factory _WarhammerStats(
      {@JsonKey(name: 'total_diseases') required final int totalDiseases,
      @JsonKey(name: 'total_symptoms') required final int totalSymptoms,
      @JsonKey(name: 'total_conditionals') required final int totalConditionals,
      @JsonKey(name: 'total_calculations') required final int totalCalculations,
      @JsonKey(name: 'saved_calculations')
      required final int savedCalculations}) = _$WarhammerStatsImpl;

  factory _WarhammerStats.fromJson(Map<String, dynamic> json) =
      _$WarhammerStatsImpl.fromJson;

  @override
  @JsonKey(name: 'total_diseases')
  int get totalDiseases;
  @override
  @JsonKey(name: 'total_symptoms')
  int get totalSymptoms;
  @override
  @JsonKey(name: 'total_conditionals')
  int get totalConditionals;
  @override
  @JsonKey(name: 'total_calculations')
  int get totalCalculations;
  @override
  @JsonKey(name: 'saved_calculations')
  int get savedCalculations;

  /// Create a copy of WarhammerStats
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$WarhammerStatsImplCopyWith<_$WarhammerStatsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

SavedCalculation _$SavedCalculationFromJson(Map<String, dynamic> json) {
  return _SavedCalculation.fromJson(json);
}

/// @nodoc
mixin _$SavedCalculation {
  int get id => throw _privateConstructorUsedError;
  String get calculationDate => throw _privateConstructorUsedError;
  List<String> get inputSymptoms => throw _privateConstructorUsedError;
  List<DiseaseResult> get results => throw _privateConstructorUsedError;
  bool get saved => throw _privateConstructorUsedError;

  /// Serializes this SavedCalculation to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SavedCalculation
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SavedCalculationCopyWith<SavedCalculation> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SavedCalculationCopyWith<$Res> {
  factory $SavedCalculationCopyWith(
          SavedCalculation value, $Res Function(SavedCalculation) then) =
      _$SavedCalculationCopyWithImpl<$Res, SavedCalculation>;
  @useResult
  $Res call(
      {int id,
      String calculationDate,
      List<String> inputSymptoms,
      List<DiseaseResult> results,
      bool saved});
}

/// @nodoc
class _$SavedCalculationCopyWithImpl<$Res, $Val extends SavedCalculation>
    implements $SavedCalculationCopyWith<$Res> {
  _$SavedCalculationCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SavedCalculation
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? calculationDate = null,
    Object? inputSymptoms = null,
    Object? results = null,
    Object? saved = null,
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
      inputSymptoms: null == inputSymptoms
          ? _value.inputSymptoms
          : inputSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      results: null == results
          ? _value.results
          : results // ignore: cast_nullable_to_non_nullable
              as List<DiseaseResult>,
      saved: null == saved
          ? _value.saved
          : saved // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SavedCalculationImplCopyWith<$Res>
    implements $SavedCalculationCopyWith<$Res> {
  factory _$$SavedCalculationImplCopyWith(_$SavedCalculationImpl value,
          $Res Function(_$SavedCalculationImpl) then) =
      __$$SavedCalculationImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int id,
      String calculationDate,
      List<String> inputSymptoms,
      List<DiseaseResult> results,
      bool saved});
}

/// @nodoc
class __$$SavedCalculationImplCopyWithImpl<$Res>
    extends _$SavedCalculationCopyWithImpl<$Res, _$SavedCalculationImpl>
    implements _$$SavedCalculationImplCopyWith<$Res> {
  __$$SavedCalculationImplCopyWithImpl(_$SavedCalculationImpl _value,
      $Res Function(_$SavedCalculationImpl) _then)
      : super(_value, _then);

  /// Create a copy of SavedCalculation
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? calculationDate = null,
    Object? inputSymptoms = null,
    Object? results = null,
    Object? saved = null,
  }) {
    return _then(_$SavedCalculationImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      calculationDate: null == calculationDate
          ? _value.calculationDate
          : calculationDate // ignore: cast_nullable_to_non_nullable
              as String,
      inputSymptoms: null == inputSymptoms
          ? _value._inputSymptoms
          : inputSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      results: null == results
          ? _value._results
          : results // ignore: cast_nullable_to_non_nullable
              as List<DiseaseResult>,
      saved: null == saved
          ? _value.saved
          : saved // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SavedCalculationImpl implements _SavedCalculation {
  const _$SavedCalculationImpl(
      {required this.id,
      required this.calculationDate,
      required final List<String> inputSymptoms,
      required final List<DiseaseResult> results,
      required this.saved})
      : _inputSymptoms = inputSymptoms,
        _results = results;

  factory _$SavedCalculationImpl.fromJson(Map<String, dynamic> json) =>
      _$$SavedCalculationImplFromJson(json);

  @override
  final int id;
  @override
  final String calculationDate;
  final List<String> _inputSymptoms;
  @override
  List<String> get inputSymptoms {
    if (_inputSymptoms is EqualUnmodifiableListView) return _inputSymptoms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_inputSymptoms);
  }

  final List<DiseaseResult> _results;
  @override
  List<DiseaseResult> get results {
    if (_results is EqualUnmodifiableListView) return _results;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_results);
  }

  @override
  final bool saved;

  @override
  String toString() {
    return 'SavedCalculation(id: $id, calculationDate: $calculationDate, inputSymptoms: $inputSymptoms, results: $results, saved: $saved)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SavedCalculationImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.calculationDate, calculationDate) ||
                other.calculationDate == calculationDate) &&
            const DeepCollectionEquality()
                .equals(other._inputSymptoms, _inputSymptoms) &&
            const DeepCollectionEquality().equals(other._results, _results) &&
            (identical(other.saved, saved) || other.saved == saved));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      calculationDate,
      const DeepCollectionEquality().hash(_inputSymptoms),
      const DeepCollectionEquality().hash(_results),
      saved);

  /// Create a copy of SavedCalculation
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SavedCalculationImplCopyWith<_$SavedCalculationImpl> get copyWith =>
      __$$SavedCalculationImplCopyWithImpl<_$SavedCalculationImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SavedCalculationImplToJson(
      this,
    );
  }
}

abstract class _SavedCalculation implements SavedCalculation {
  const factory _SavedCalculation(
      {required final int id,
      required final String calculationDate,
      required final List<String> inputSymptoms,
      required final List<DiseaseResult> results,
      required final bool saved}) = _$SavedCalculationImpl;

  factory _SavedCalculation.fromJson(Map<String, dynamic> json) =
      _$SavedCalculationImpl.fromJson;

  @override
  int get id;
  @override
  String get calculationDate;
  @override
  List<String> get inputSymptoms;
  @override
  List<DiseaseResult> get results;
  @override
  bool get saved;

  /// Create a copy of SavedCalculation
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SavedCalculationImplCopyWith<_$SavedCalculationImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

NormalizedMatch _$NormalizedMatchFromJson(Map<String, dynamic> json) {
  return _NormalizedMatch.fromJson(json);
}

/// @nodoc
mixin _$NormalizedMatch {
  @JsonKey(name: 'decision_tree')
  String get decisionTree => throw _privateConstructorUsedError;
  @JsonKey(name: 'warhammer')
  String get warhammer => throw _privateConstructorUsedError;
  @JsonKey(name: 'normalized')
  String get normalized => throw _privateConstructorUsedError;

  /// Serializes this NormalizedMatch to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of NormalizedMatch
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $NormalizedMatchCopyWith<NormalizedMatch> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $NormalizedMatchCopyWith<$Res> {
  factory $NormalizedMatchCopyWith(
          NormalizedMatch value, $Res Function(NormalizedMatch) then) =
      _$NormalizedMatchCopyWithImpl<$Res, NormalizedMatch>;
  @useResult
  $Res call(
      {@JsonKey(name: 'decision_tree') String decisionTree,
      @JsonKey(name: 'warhammer') String warhammer,
      @JsonKey(name: 'normalized') String normalized});
}

/// @nodoc
class _$NormalizedMatchCopyWithImpl<$Res, $Val extends NormalizedMatch>
    implements $NormalizedMatchCopyWith<$Res> {
  _$NormalizedMatchCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of NormalizedMatch
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? decisionTree = null,
    Object? warhammer = null,
    Object? normalized = null,
  }) {
    return _then(_value.copyWith(
      decisionTree: null == decisionTree
          ? _value.decisionTree
          : decisionTree // ignore: cast_nullable_to_non_nullable
              as String,
      warhammer: null == warhammer
          ? _value.warhammer
          : warhammer // ignore: cast_nullable_to_non_nullable
              as String,
      normalized: null == normalized
          ? _value.normalized
          : normalized // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$NormalizedMatchImplCopyWith<$Res>
    implements $NormalizedMatchCopyWith<$Res> {
  factory _$$NormalizedMatchImplCopyWith(_$NormalizedMatchImpl value,
          $Res Function(_$NormalizedMatchImpl) then) =
      __$$NormalizedMatchImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'decision_tree') String decisionTree,
      @JsonKey(name: 'warhammer') String warhammer,
      @JsonKey(name: 'normalized') String normalized});
}

/// @nodoc
class __$$NormalizedMatchImplCopyWithImpl<$Res>
    extends _$NormalizedMatchCopyWithImpl<$Res, _$NormalizedMatchImpl>
    implements _$$NormalizedMatchImplCopyWith<$Res> {
  __$$NormalizedMatchImplCopyWithImpl(
      _$NormalizedMatchImpl _value, $Res Function(_$NormalizedMatchImpl) _then)
      : super(_value, _then);

  /// Create a copy of NormalizedMatch
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? decisionTree = null,
    Object? warhammer = null,
    Object? normalized = null,
  }) {
    return _then(_$NormalizedMatchImpl(
      decisionTree: null == decisionTree
          ? _value.decisionTree
          : decisionTree // ignore: cast_nullable_to_non_nullable
              as String,
      warhammer: null == warhammer
          ? _value.warhammer
          : warhammer // ignore: cast_nullable_to_non_nullable
              as String,
      normalized: null == normalized
          ? _value.normalized
          : normalized // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$NormalizedMatchImpl implements _NormalizedMatch {
  const _$NormalizedMatchImpl(
      {@JsonKey(name: 'decision_tree') required this.decisionTree,
      @JsonKey(name: 'warhammer') required this.warhammer,
      @JsonKey(name: 'normalized') required this.normalized});

  factory _$NormalizedMatchImpl.fromJson(Map<String, dynamic> json) =>
      _$$NormalizedMatchImplFromJson(json);

  @override
  @JsonKey(name: 'decision_tree')
  final String decisionTree;
  @override
  @JsonKey(name: 'warhammer')
  final String warhammer;
  @override
  @JsonKey(name: 'normalized')
  final String normalized;

  @override
  String toString() {
    return 'NormalizedMatch(decisionTree: $decisionTree, warhammer: $warhammer, normalized: $normalized)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$NormalizedMatchImpl &&
            (identical(other.decisionTree, decisionTree) ||
                other.decisionTree == decisionTree) &&
            (identical(other.warhammer, warhammer) ||
                other.warhammer == warhammer) &&
            (identical(other.normalized, normalized) ||
                other.normalized == normalized));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, decisionTree, warhammer, normalized);

  /// Create a copy of NormalizedMatch
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$NormalizedMatchImplCopyWith<_$NormalizedMatchImpl> get copyWith =>
      __$$NormalizedMatchImplCopyWithImpl<_$NormalizedMatchImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$NormalizedMatchImplToJson(
      this,
    );
  }
}

abstract class _NormalizedMatch implements NormalizedMatch {
  const factory _NormalizedMatch(
          {@JsonKey(name: 'decision_tree') required final String decisionTree,
          @JsonKey(name: 'warhammer') required final String warhammer,
          @JsonKey(name: 'normalized') required final String normalized}) =
      _$NormalizedMatchImpl;

  factory _NormalizedMatch.fromJson(Map<String, dynamic> json) =
      _$NormalizedMatchImpl.fromJson;

  @override
  @JsonKey(name: 'decision_tree')
  String get decisionTree;
  @override
  @JsonKey(name: 'warhammer')
  String get warhammer;
  @override
  @JsonKey(name: 'normalized')
  String get normalized;

  /// Create a copy of NormalizedMatch
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$NormalizedMatchImplCopyWith<_$NormalizedMatchImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

SymptomSynonym _$SymptomSynonymFromJson(Map<String, dynamic> json) {
  return _SymptomSynonym.fromJson(json);
}

/// @nodoc
mixin _$SymptomSynonym {
  int get id => throw _privateConstructorUsedError;
  @JsonKey(name: 'warhammer_symptom')
  String get warhammerSymptom => throw _privateConstructorUsedError;
  @JsonKey(name: 'decision_tree_symptom')
  String get decisionTreeSymptom => throw _privateConstructorUsedError;
  @JsonKey(name: 'created_at')
  String get createdAt => throw _privateConstructorUsedError;
  @JsonKey(name: 'updated_at')
  String get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this SymptomSynonym to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SymptomSynonym
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SymptomSynonymCopyWith<SymptomSynonym> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SymptomSynonymCopyWith<$Res> {
  factory $SymptomSynonymCopyWith(
          SymptomSynonym value, $Res Function(SymptomSynonym) then) =
      _$SymptomSynonymCopyWithImpl<$Res, SymptomSynonym>;
  @useResult
  $Res call(
      {int id,
      @JsonKey(name: 'warhammer_symptom') String warhammerSymptom,
      @JsonKey(name: 'decision_tree_symptom') String decisionTreeSymptom,
      @JsonKey(name: 'created_at') String createdAt,
      @JsonKey(name: 'updated_at') String updatedAt});
}

/// @nodoc
class _$SymptomSynonymCopyWithImpl<$Res, $Val extends SymptomSynonym>
    implements $SymptomSynonymCopyWith<$Res> {
  _$SymptomSynonymCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SymptomSynonym
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? warhammerSymptom = null,
    Object? decisionTreeSymptom = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      warhammerSymptom: null == warhammerSymptom
          ? _value.warhammerSymptom
          : warhammerSymptom // ignore: cast_nullable_to_non_nullable
              as String,
      decisionTreeSymptom: null == decisionTreeSymptom
          ? _value.decisionTreeSymptom
          : decisionTreeSymptom // ignore: cast_nullable_to_non_nullable
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
abstract class _$$SymptomSynonymImplCopyWith<$Res>
    implements $SymptomSynonymCopyWith<$Res> {
  factory _$$SymptomSynonymImplCopyWith(_$SymptomSynonymImpl value,
          $Res Function(_$SymptomSynonymImpl) then) =
      __$$SymptomSynonymImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int id,
      @JsonKey(name: 'warhammer_symptom') String warhammerSymptom,
      @JsonKey(name: 'decision_tree_symptom') String decisionTreeSymptom,
      @JsonKey(name: 'created_at') String createdAt,
      @JsonKey(name: 'updated_at') String updatedAt});
}

/// @nodoc
class __$$SymptomSynonymImplCopyWithImpl<$Res>
    extends _$SymptomSynonymCopyWithImpl<$Res, _$SymptomSynonymImpl>
    implements _$$SymptomSynonymImplCopyWith<$Res> {
  __$$SymptomSynonymImplCopyWithImpl(
      _$SymptomSynonymImpl _value, $Res Function(_$SymptomSynonymImpl) _then)
      : super(_value, _then);

  /// Create a copy of SymptomSynonym
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? warhammerSymptom = null,
    Object? decisionTreeSymptom = null,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_$SymptomSynonymImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      warhammerSymptom: null == warhammerSymptom
          ? _value.warhammerSymptom
          : warhammerSymptom // ignore: cast_nullable_to_non_nullable
              as String,
      decisionTreeSymptom: null == decisionTreeSymptom
          ? _value.decisionTreeSymptom
          : decisionTreeSymptom // ignore: cast_nullable_to_non_nullable
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
class _$SymptomSynonymImpl implements _SymptomSynonym {
  const _$SymptomSynonymImpl(
      {required this.id,
      @JsonKey(name: 'warhammer_symptom') required this.warhammerSymptom,
      @JsonKey(name: 'decision_tree_symptom') required this.decisionTreeSymptom,
      @JsonKey(name: 'created_at') required this.createdAt,
      @JsonKey(name: 'updated_at') required this.updatedAt});

  factory _$SymptomSynonymImpl.fromJson(Map<String, dynamic> json) =>
      _$$SymptomSynonymImplFromJson(json);

  @override
  final int id;
  @override
  @JsonKey(name: 'warhammer_symptom')
  final String warhammerSymptom;
  @override
  @JsonKey(name: 'decision_tree_symptom')
  final String decisionTreeSymptom;
  @override
  @JsonKey(name: 'created_at')
  final String createdAt;
  @override
  @JsonKey(name: 'updated_at')
  final String updatedAt;

  @override
  String toString() {
    return 'SymptomSynonym(id: $id, warhammerSymptom: $warhammerSymptom, decisionTreeSymptom: $decisionTreeSymptom, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SymptomSynonymImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.warhammerSymptom, warhammerSymptom) ||
                other.warhammerSymptom == warhammerSymptom) &&
            (identical(other.decisionTreeSymptom, decisionTreeSymptom) ||
                other.decisionTreeSymptom == decisionTreeSymptom) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, warhammerSymptom,
      decisionTreeSymptom, createdAt, updatedAt);

  /// Create a copy of SymptomSynonym
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SymptomSynonymImplCopyWith<_$SymptomSynonymImpl> get copyWith =>
      __$$SymptomSynonymImplCopyWithImpl<_$SymptomSynonymImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SymptomSynonymImplToJson(
      this,
    );
  }
}

abstract class _SymptomSynonym implements SymptomSynonym {
  const factory _SymptomSynonym(
          {required final int id,
          @JsonKey(name: 'warhammer_symptom')
          required final String warhammerSymptom,
          @JsonKey(name: 'decision_tree_symptom')
          required final String decisionTreeSymptom,
          @JsonKey(name: 'created_at') required final String createdAt,
          @JsonKey(name: 'updated_at') required final String updatedAt}) =
      _$SymptomSynonymImpl;

  factory _SymptomSynonym.fromJson(Map<String, dynamic> json) =
      _$SymptomSynonymImpl.fromJson;

  @override
  int get id;
  @override
  @JsonKey(name: 'warhammer_symptom')
  String get warhammerSymptom;
  @override
  @JsonKey(name: 'decision_tree_symptom')
  String get decisionTreeSymptom;
  @override
  @JsonKey(name: 'created_at')
  String get createdAt;
  @override
  @JsonKey(name: 'updated_at')
  String get updatedAt;

  /// Create a copy of SymptomSynonym
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SymptomSynonymImplCopyWith<_$SymptomSynonymImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CreateSynonymRequest _$CreateSynonymRequestFromJson(Map<String, dynamic> json) {
  return _CreateSynonymRequest.fromJson(json);
}

/// @nodoc
mixin _$CreateSynonymRequest {
  @JsonKey(name: 'warhammer_symptom')
  String get warhammerSymptom => throw _privateConstructorUsedError;
  @JsonKey(name: 'decision_tree_symptom')
  String get decisionTreeSymptom => throw _privateConstructorUsedError;

  /// Serializes this CreateSynonymRequest to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CreateSynonymRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CreateSynonymRequestCopyWith<CreateSynonymRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CreateSynonymRequestCopyWith<$Res> {
  factory $CreateSynonymRequestCopyWith(CreateSynonymRequest value,
          $Res Function(CreateSynonymRequest) then) =
      _$CreateSynonymRequestCopyWithImpl<$Res, CreateSynonymRequest>;
  @useResult
  $Res call(
      {@JsonKey(name: 'warhammer_symptom') String warhammerSymptom,
      @JsonKey(name: 'decision_tree_symptom') String decisionTreeSymptom});
}

/// @nodoc
class _$CreateSynonymRequestCopyWithImpl<$Res,
        $Val extends CreateSynonymRequest>
    implements $CreateSynonymRequestCopyWith<$Res> {
  _$CreateSynonymRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CreateSynonymRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? warhammerSymptom = null,
    Object? decisionTreeSymptom = null,
  }) {
    return _then(_value.copyWith(
      warhammerSymptom: null == warhammerSymptom
          ? _value.warhammerSymptom
          : warhammerSymptom // ignore: cast_nullable_to_non_nullable
              as String,
      decisionTreeSymptom: null == decisionTreeSymptom
          ? _value.decisionTreeSymptom
          : decisionTreeSymptom // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CreateSynonymRequestImplCopyWith<$Res>
    implements $CreateSynonymRequestCopyWith<$Res> {
  factory _$$CreateSynonymRequestImplCopyWith(_$CreateSynonymRequestImpl value,
          $Res Function(_$CreateSynonymRequestImpl) then) =
      __$$CreateSynonymRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'warhammer_symptom') String warhammerSymptom,
      @JsonKey(name: 'decision_tree_symptom') String decisionTreeSymptom});
}

/// @nodoc
class __$$CreateSynonymRequestImplCopyWithImpl<$Res>
    extends _$CreateSynonymRequestCopyWithImpl<$Res, _$CreateSynonymRequestImpl>
    implements _$$CreateSynonymRequestImplCopyWith<$Res> {
  __$$CreateSynonymRequestImplCopyWithImpl(_$CreateSynonymRequestImpl _value,
      $Res Function(_$CreateSynonymRequestImpl) _then)
      : super(_value, _then);

  /// Create a copy of CreateSynonymRequest
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? warhammerSymptom = null,
    Object? decisionTreeSymptom = null,
  }) {
    return _then(_$CreateSynonymRequestImpl(
      warhammerSymptom: null == warhammerSymptom
          ? _value.warhammerSymptom
          : warhammerSymptom // ignore: cast_nullable_to_non_nullable
              as String,
      decisionTreeSymptom: null == decisionTreeSymptom
          ? _value.decisionTreeSymptom
          : decisionTreeSymptom // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CreateSynonymRequestImpl implements _CreateSynonymRequest {
  const _$CreateSynonymRequestImpl(
      {@JsonKey(name: 'warhammer_symptom') required this.warhammerSymptom,
      @JsonKey(name: 'decision_tree_symptom')
      required this.decisionTreeSymptom});

  factory _$CreateSynonymRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$CreateSynonymRequestImplFromJson(json);

  @override
  @JsonKey(name: 'warhammer_symptom')
  final String warhammerSymptom;
  @override
  @JsonKey(name: 'decision_tree_symptom')
  final String decisionTreeSymptom;

  @override
  String toString() {
    return 'CreateSynonymRequest(warhammerSymptom: $warhammerSymptom, decisionTreeSymptom: $decisionTreeSymptom)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CreateSynonymRequestImpl &&
            (identical(other.warhammerSymptom, warhammerSymptom) ||
                other.warhammerSymptom == warhammerSymptom) &&
            (identical(other.decisionTreeSymptom, decisionTreeSymptom) ||
                other.decisionTreeSymptom == decisionTreeSymptom));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, warhammerSymptom, decisionTreeSymptom);

  /// Create a copy of CreateSynonymRequest
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CreateSynonymRequestImplCopyWith<_$CreateSynonymRequestImpl>
      get copyWith =>
          __$$CreateSynonymRequestImplCopyWithImpl<_$CreateSynonymRequestImpl>(
              this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CreateSynonymRequestImplToJson(
      this,
    );
  }
}

abstract class _CreateSynonymRequest implements CreateSynonymRequest {
  const factory _CreateSynonymRequest(
      {@JsonKey(name: 'warhammer_symptom')
      required final String warhammerSymptom,
      @JsonKey(name: 'decision_tree_symptom')
      required final String decisionTreeSymptom}) = _$CreateSynonymRequestImpl;

  factory _CreateSynonymRequest.fromJson(Map<String, dynamic> json) =
      _$CreateSynonymRequestImpl.fromJson;

  @override
  @JsonKey(name: 'warhammer_symptom')
  String get warhammerSymptom;
  @override
  @JsonKey(name: 'decision_tree_symptom')
  String get decisionTreeSymptom;

  /// Create a copy of CreateSynonymRequest
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CreateSynonymRequestImplCopyWith<_$CreateSynonymRequestImpl>
      get copyWith => throw _privateConstructorUsedError;
}

SymptomComparison _$SymptomComparisonFromJson(Map<String, dynamic> json) {
  return _SymptomComparison.fromJson(json);
}

/// @nodoc
mixin _$SymptomComparison {
  @JsonKey(name: 'decision_tree_symptoms')
  List<String> get decisionTreeSymptoms => throw _privateConstructorUsedError;
  @JsonKey(name: 'warhammer_symptoms')
  List<String> get warhammerSymptoms => throw _privateConstructorUsedError;
  @JsonKey(name: 'matching_symptoms')
  List<String> get matchingSymptoms => throw _privateConstructorUsedError;
  @JsonKey(name: 'missing_from_warhammer')
  List<String> get missingFromWarhammer => throw _privateConstructorUsedError;
  @JsonKey(name: 'extra_in_warhammer')
  List<String> get extraInWarhammer => throw _privateConstructorUsedError;
  @JsonKey(name: 'total_decision_tree')
  int get totalDecisionTree => throw _privateConstructorUsedError;
  @JsonKey(name: 'total_warhammer')
  int get totalWarhammer => throw _privateConstructorUsedError;
  @JsonKey(name: 'match_count')
  int get matchCount => throw _privateConstructorUsedError;
  @JsonKey(name: 'normalized_matches')
  List<NormalizedMatch> get normalizedMatches =>
      throw _privateConstructorUsedError;

  /// Serializes this SymptomComparison to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SymptomComparison
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SymptomComparisonCopyWith<SymptomComparison> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SymptomComparisonCopyWith<$Res> {
  factory $SymptomComparisonCopyWith(
          SymptomComparison value, $Res Function(SymptomComparison) then) =
      _$SymptomComparisonCopyWithImpl<$Res, SymptomComparison>;
  @useResult
  $Res call(
      {@JsonKey(name: 'decision_tree_symptoms')
      List<String> decisionTreeSymptoms,
      @JsonKey(name: 'warhammer_symptoms') List<String> warhammerSymptoms,
      @JsonKey(name: 'matching_symptoms') List<String> matchingSymptoms,
      @JsonKey(name: 'missing_from_warhammer')
      List<String> missingFromWarhammer,
      @JsonKey(name: 'extra_in_warhammer') List<String> extraInWarhammer,
      @JsonKey(name: 'total_decision_tree') int totalDecisionTree,
      @JsonKey(name: 'total_warhammer') int totalWarhammer,
      @JsonKey(name: 'match_count') int matchCount,
      @JsonKey(name: 'normalized_matches')
      List<NormalizedMatch> normalizedMatches});
}

/// @nodoc
class _$SymptomComparisonCopyWithImpl<$Res, $Val extends SymptomComparison>
    implements $SymptomComparisonCopyWith<$Res> {
  _$SymptomComparisonCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SymptomComparison
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? decisionTreeSymptoms = null,
    Object? warhammerSymptoms = null,
    Object? matchingSymptoms = null,
    Object? missingFromWarhammer = null,
    Object? extraInWarhammer = null,
    Object? totalDecisionTree = null,
    Object? totalWarhammer = null,
    Object? matchCount = null,
    Object? normalizedMatches = null,
  }) {
    return _then(_value.copyWith(
      decisionTreeSymptoms: null == decisionTreeSymptoms
          ? _value.decisionTreeSymptoms
          : decisionTreeSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      warhammerSymptoms: null == warhammerSymptoms
          ? _value.warhammerSymptoms
          : warhammerSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      matchingSymptoms: null == matchingSymptoms
          ? _value.matchingSymptoms
          : matchingSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      missingFromWarhammer: null == missingFromWarhammer
          ? _value.missingFromWarhammer
          : missingFromWarhammer // ignore: cast_nullable_to_non_nullable
              as List<String>,
      extraInWarhammer: null == extraInWarhammer
          ? _value.extraInWarhammer
          : extraInWarhammer // ignore: cast_nullable_to_non_nullable
              as List<String>,
      totalDecisionTree: null == totalDecisionTree
          ? _value.totalDecisionTree
          : totalDecisionTree // ignore: cast_nullable_to_non_nullable
              as int,
      totalWarhammer: null == totalWarhammer
          ? _value.totalWarhammer
          : totalWarhammer // ignore: cast_nullable_to_non_nullable
              as int,
      matchCount: null == matchCount
          ? _value.matchCount
          : matchCount // ignore: cast_nullable_to_non_nullable
              as int,
      normalizedMatches: null == normalizedMatches
          ? _value.normalizedMatches
          : normalizedMatches // ignore: cast_nullable_to_non_nullable
              as List<NormalizedMatch>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SymptomComparisonImplCopyWith<$Res>
    implements $SymptomComparisonCopyWith<$Res> {
  factory _$$SymptomComparisonImplCopyWith(_$SymptomComparisonImpl value,
          $Res Function(_$SymptomComparisonImpl) then) =
      __$$SymptomComparisonImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'decision_tree_symptoms')
      List<String> decisionTreeSymptoms,
      @JsonKey(name: 'warhammer_symptoms') List<String> warhammerSymptoms,
      @JsonKey(name: 'matching_symptoms') List<String> matchingSymptoms,
      @JsonKey(name: 'missing_from_warhammer')
      List<String> missingFromWarhammer,
      @JsonKey(name: 'extra_in_warhammer') List<String> extraInWarhammer,
      @JsonKey(name: 'total_decision_tree') int totalDecisionTree,
      @JsonKey(name: 'total_warhammer') int totalWarhammer,
      @JsonKey(name: 'match_count') int matchCount,
      @JsonKey(name: 'normalized_matches')
      List<NormalizedMatch> normalizedMatches});
}

/// @nodoc
class __$$SymptomComparisonImplCopyWithImpl<$Res>
    extends _$SymptomComparisonCopyWithImpl<$Res, _$SymptomComparisonImpl>
    implements _$$SymptomComparisonImplCopyWith<$Res> {
  __$$SymptomComparisonImplCopyWithImpl(_$SymptomComparisonImpl _value,
      $Res Function(_$SymptomComparisonImpl) _then)
      : super(_value, _then);

  /// Create a copy of SymptomComparison
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? decisionTreeSymptoms = null,
    Object? warhammerSymptoms = null,
    Object? matchingSymptoms = null,
    Object? missingFromWarhammer = null,
    Object? extraInWarhammer = null,
    Object? totalDecisionTree = null,
    Object? totalWarhammer = null,
    Object? matchCount = null,
    Object? normalizedMatches = null,
  }) {
    return _then(_$SymptomComparisonImpl(
      decisionTreeSymptoms: null == decisionTreeSymptoms
          ? _value._decisionTreeSymptoms
          : decisionTreeSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      warhammerSymptoms: null == warhammerSymptoms
          ? _value._warhammerSymptoms
          : warhammerSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      matchingSymptoms: null == matchingSymptoms
          ? _value._matchingSymptoms
          : matchingSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      missingFromWarhammer: null == missingFromWarhammer
          ? _value._missingFromWarhammer
          : missingFromWarhammer // ignore: cast_nullable_to_non_nullable
              as List<String>,
      extraInWarhammer: null == extraInWarhammer
          ? _value._extraInWarhammer
          : extraInWarhammer // ignore: cast_nullable_to_non_nullable
              as List<String>,
      totalDecisionTree: null == totalDecisionTree
          ? _value.totalDecisionTree
          : totalDecisionTree // ignore: cast_nullable_to_non_nullable
              as int,
      totalWarhammer: null == totalWarhammer
          ? _value.totalWarhammer
          : totalWarhammer // ignore: cast_nullable_to_non_nullable
              as int,
      matchCount: null == matchCount
          ? _value.matchCount
          : matchCount // ignore: cast_nullable_to_non_nullable
              as int,
      normalizedMatches: null == normalizedMatches
          ? _value._normalizedMatches
          : normalizedMatches // ignore: cast_nullable_to_non_nullable
              as List<NormalizedMatch>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SymptomComparisonImpl implements _SymptomComparison {
  const _$SymptomComparisonImpl(
      {@JsonKey(name: 'decision_tree_symptoms')
      final List<String> decisionTreeSymptoms = const [],
      @JsonKey(name: 'warhammer_symptoms')
      final List<String> warhammerSymptoms = const [],
      @JsonKey(name: 'matching_symptoms')
      final List<String> matchingSymptoms = const [],
      @JsonKey(name: 'missing_from_warhammer')
      final List<String> missingFromWarhammer = const [],
      @JsonKey(name: 'extra_in_warhammer')
      final List<String> extraInWarhammer = const [],
      @JsonKey(name: 'total_decision_tree') this.totalDecisionTree = 0,
      @JsonKey(name: 'total_warhammer') this.totalWarhammer = 0,
      @JsonKey(name: 'match_count') this.matchCount = 0,
      @JsonKey(name: 'normalized_matches')
      final List<NormalizedMatch> normalizedMatches = const []})
      : _decisionTreeSymptoms = decisionTreeSymptoms,
        _warhammerSymptoms = warhammerSymptoms,
        _matchingSymptoms = matchingSymptoms,
        _missingFromWarhammer = missingFromWarhammer,
        _extraInWarhammer = extraInWarhammer,
        _normalizedMatches = normalizedMatches;

  factory _$SymptomComparisonImpl.fromJson(Map<String, dynamic> json) =>
      _$$SymptomComparisonImplFromJson(json);

  final List<String> _decisionTreeSymptoms;
  @override
  @JsonKey(name: 'decision_tree_symptoms')
  List<String> get decisionTreeSymptoms {
    if (_decisionTreeSymptoms is EqualUnmodifiableListView)
      return _decisionTreeSymptoms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_decisionTreeSymptoms);
  }

  final List<String> _warhammerSymptoms;
  @override
  @JsonKey(name: 'warhammer_symptoms')
  List<String> get warhammerSymptoms {
    if (_warhammerSymptoms is EqualUnmodifiableListView)
      return _warhammerSymptoms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_warhammerSymptoms);
  }

  final List<String> _matchingSymptoms;
  @override
  @JsonKey(name: 'matching_symptoms')
  List<String> get matchingSymptoms {
    if (_matchingSymptoms is EqualUnmodifiableListView)
      return _matchingSymptoms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_matchingSymptoms);
  }

  final List<String> _missingFromWarhammer;
  @override
  @JsonKey(name: 'missing_from_warhammer')
  List<String> get missingFromWarhammer {
    if (_missingFromWarhammer is EqualUnmodifiableListView)
      return _missingFromWarhammer;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_missingFromWarhammer);
  }

  final List<String> _extraInWarhammer;
  @override
  @JsonKey(name: 'extra_in_warhammer')
  List<String> get extraInWarhammer {
    if (_extraInWarhammer is EqualUnmodifiableListView)
      return _extraInWarhammer;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_extraInWarhammer);
  }

  @override
  @JsonKey(name: 'total_decision_tree')
  final int totalDecisionTree;
  @override
  @JsonKey(name: 'total_warhammer')
  final int totalWarhammer;
  @override
  @JsonKey(name: 'match_count')
  final int matchCount;
  final List<NormalizedMatch> _normalizedMatches;
  @override
  @JsonKey(name: 'normalized_matches')
  List<NormalizedMatch> get normalizedMatches {
    if (_normalizedMatches is EqualUnmodifiableListView)
      return _normalizedMatches;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_normalizedMatches);
  }

  @override
  String toString() {
    return 'SymptomComparison(decisionTreeSymptoms: $decisionTreeSymptoms, warhammerSymptoms: $warhammerSymptoms, matchingSymptoms: $matchingSymptoms, missingFromWarhammer: $missingFromWarhammer, extraInWarhammer: $extraInWarhammer, totalDecisionTree: $totalDecisionTree, totalWarhammer: $totalWarhammer, matchCount: $matchCount, normalizedMatches: $normalizedMatches)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SymptomComparisonImpl &&
            const DeepCollectionEquality()
                .equals(other._decisionTreeSymptoms, _decisionTreeSymptoms) &&
            const DeepCollectionEquality()
                .equals(other._warhammerSymptoms, _warhammerSymptoms) &&
            const DeepCollectionEquality()
                .equals(other._matchingSymptoms, _matchingSymptoms) &&
            const DeepCollectionEquality()
                .equals(other._missingFromWarhammer, _missingFromWarhammer) &&
            const DeepCollectionEquality()
                .equals(other._extraInWarhammer, _extraInWarhammer) &&
            (identical(other.totalDecisionTree, totalDecisionTree) ||
                other.totalDecisionTree == totalDecisionTree) &&
            (identical(other.totalWarhammer, totalWarhammer) ||
                other.totalWarhammer == totalWarhammer) &&
            (identical(other.matchCount, matchCount) ||
                other.matchCount == matchCount) &&
            const DeepCollectionEquality()
                .equals(other._normalizedMatches, _normalizedMatches));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      const DeepCollectionEquality().hash(_decisionTreeSymptoms),
      const DeepCollectionEquality().hash(_warhammerSymptoms),
      const DeepCollectionEquality().hash(_matchingSymptoms),
      const DeepCollectionEquality().hash(_missingFromWarhammer),
      const DeepCollectionEquality().hash(_extraInWarhammer),
      totalDecisionTree,
      totalWarhammer,
      matchCount,
      const DeepCollectionEquality().hash(_normalizedMatches));

  /// Create a copy of SymptomComparison
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SymptomComparisonImplCopyWith<_$SymptomComparisonImpl> get copyWith =>
      __$$SymptomComparisonImplCopyWithImpl<_$SymptomComparisonImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SymptomComparisonImplToJson(
      this,
    );
  }
}

abstract class _SymptomComparison implements SymptomComparison {
  const factory _SymptomComparison(
      {@JsonKey(name: 'decision_tree_symptoms')
      final List<String> decisionTreeSymptoms,
      @JsonKey(name: 'warhammer_symptoms') final List<String> warhammerSymptoms,
      @JsonKey(name: 'matching_symptoms') final List<String> matchingSymptoms,
      @JsonKey(name: 'missing_from_warhammer')
      final List<String> missingFromWarhammer,
      @JsonKey(name: 'extra_in_warhammer') final List<String> extraInWarhammer,
      @JsonKey(name: 'total_decision_tree') final int totalDecisionTree,
      @JsonKey(name: 'total_warhammer') final int totalWarhammer,
      @JsonKey(name: 'match_count') final int matchCount,
      @JsonKey(name: 'normalized_matches')
      final List<NormalizedMatch> normalizedMatches}) = _$SymptomComparisonImpl;

  factory _SymptomComparison.fromJson(Map<String, dynamic> json) =
      _$SymptomComparisonImpl.fromJson;

  @override
  @JsonKey(name: 'decision_tree_symptoms')
  List<String> get decisionTreeSymptoms;
  @override
  @JsonKey(name: 'warhammer_symptoms')
  List<String> get warhammerSymptoms;
  @override
  @JsonKey(name: 'matching_symptoms')
  List<String> get matchingSymptoms;
  @override
  @JsonKey(name: 'missing_from_warhammer')
  List<String> get missingFromWarhammer;
  @override
  @JsonKey(name: 'extra_in_warhammer')
  List<String> get extraInWarhammer;
  @override
  @JsonKey(name: 'total_decision_tree')
  int get totalDecisionTree;
  @override
  @JsonKey(name: 'total_warhammer')
  int get totalWarhammer;
  @override
  @JsonKey(name: 'match_count')
  int get matchCount;
  @override
  @JsonKey(name: 'normalized_matches')
  List<NormalizedMatch> get normalizedMatches;

  /// Create a copy of SymptomComparison
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SymptomComparisonImplCopyWith<_$SymptomComparisonImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
