// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'pathogen_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

Pathogen _$PathogenFromJson(Map<String, dynamic> json) {
  return _Pathogen.fromJson(json);
}

/// @nodoc
mixin _$Pathogen {
  int get id => throw _privateConstructorUsedError;
  String? get classification => throw _privateConstructorUsedError;
  String? get nt => throw _privateConstructorUsedError;
  @JsonKey(name: 'pathogen_id')
  String? get pathogenId => throw _privateConstructorUsedError;
  @JsonKey(name: 'pathogen_name')
  String get pathogenName => throw _privateConstructorUsedError;
  String? get vaccine => throw _privateConstructorUsedError;
  String? get toxin => throw _privateConstructorUsedError;
  String? get transmission => throw _privateConstructorUsedError;
  @JsonKey(name: 'ab_resistance')
  String? get abResistance => throw _privateConstructorUsedError;
  String? get host => throw _privateConstructorUsedError;
  String? get commensal => throw _privateConstructorUsedError;
  String? get disease => throw _privateConstructorUsedError;
  String? get incubation => throw _privateConstructorUsedError;
  String? get diagnosis => throw _privateConstructorUsedError;
  String? get treatment => throw _privateConstructorUsedError;
  String? get prevention => throw _privateConstructorUsedError;
  String? get notes => throw _privateConstructorUsedError;
  @JsonKey(name: 'created_at')
  String get createdAt => throw _privateConstructorUsedError;
  @JsonKey(name: 'updated_at')
  String get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this Pathogen to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Pathogen
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PathogenCopyWith<Pathogen> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PathogenCopyWith<$Res> {
  factory $PathogenCopyWith(Pathogen value, $Res Function(Pathogen) then) =
      _$PathogenCopyWithImpl<$Res, Pathogen>;
  @useResult
  $Res call(
      {int id,
      String? classification,
      String? nt,
      @JsonKey(name: 'pathogen_id') String? pathogenId,
      @JsonKey(name: 'pathogen_name') String pathogenName,
      String? vaccine,
      String? toxin,
      String? transmission,
      @JsonKey(name: 'ab_resistance') String? abResistance,
      String? host,
      String? commensal,
      String? disease,
      String? incubation,
      String? diagnosis,
      String? treatment,
      String? prevention,
      String? notes,
      @JsonKey(name: 'created_at') String createdAt,
      @JsonKey(name: 'updated_at') String updatedAt});
}

/// @nodoc
class _$PathogenCopyWithImpl<$Res, $Val extends Pathogen>
    implements $PathogenCopyWith<$Res> {
  _$PathogenCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Pathogen
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? classification = freezed,
    Object? nt = freezed,
    Object? pathogenId = freezed,
    Object? pathogenName = null,
    Object? vaccine = freezed,
    Object? toxin = freezed,
    Object? transmission = freezed,
    Object? abResistance = freezed,
    Object? host = freezed,
    Object? commensal = freezed,
    Object? disease = freezed,
    Object? incubation = freezed,
    Object? diagnosis = freezed,
    Object? treatment = freezed,
    Object? prevention = freezed,
    Object? notes = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      classification: freezed == classification
          ? _value.classification
          : classification // ignore: cast_nullable_to_non_nullable
              as String?,
      nt: freezed == nt
          ? _value.nt
          : nt // ignore: cast_nullable_to_non_nullable
              as String?,
      pathogenId: freezed == pathogenId
          ? _value.pathogenId
          : pathogenId // ignore: cast_nullable_to_non_nullable
              as String?,
      pathogenName: null == pathogenName
          ? _value.pathogenName
          : pathogenName // ignore: cast_nullable_to_non_nullable
              as String,
      vaccine: freezed == vaccine
          ? _value.vaccine
          : vaccine // ignore: cast_nullable_to_non_nullable
              as String?,
      toxin: freezed == toxin
          ? _value.toxin
          : toxin // ignore: cast_nullable_to_non_nullable
              as String?,
      transmission: freezed == transmission
          ? _value.transmission
          : transmission // ignore: cast_nullable_to_non_nullable
              as String?,
      abResistance: freezed == abResistance
          ? _value.abResistance
          : abResistance // ignore: cast_nullable_to_non_nullable
              as String?,
      host: freezed == host
          ? _value.host
          : host // ignore: cast_nullable_to_non_nullable
              as String?,
      commensal: freezed == commensal
          ? _value.commensal
          : commensal // ignore: cast_nullable_to_non_nullable
              as String?,
      disease: freezed == disease
          ? _value.disease
          : disease // ignore: cast_nullable_to_non_nullable
              as String?,
      incubation: freezed == incubation
          ? _value.incubation
          : incubation // ignore: cast_nullable_to_non_nullable
              as String?,
      diagnosis: freezed == diagnosis
          ? _value.diagnosis
          : diagnosis // ignore: cast_nullable_to_non_nullable
              as String?,
      treatment: freezed == treatment
          ? _value.treatment
          : treatment // ignore: cast_nullable_to_non_nullable
              as String?,
      prevention: freezed == prevention
          ? _value.prevention
          : prevention // ignore: cast_nullable_to_non_nullable
              as String?,
      notes: freezed == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String?,
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
abstract class _$$PathogenImplCopyWith<$Res>
    implements $PathogenCopyWith<$Res> {
  factory _$$PathogenImplCopyWith(
          _$PathogenImpl value, $Res Function(_$PathogenImpl) then) =
      __$$PathogenImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int id,
      String? classification,
      String? nt,
      @JsonKey(name: 'pathogen_id') String? pathogenId,
      @JsonKey(name: 'pathogen_name') String pathogenName,
      String? vaccine,
      String? toxin,
      String? transmission,
      @JsonKey(name: 'ab_resistance') String? abResistance,
      String? host,
      String? commensal,
      String? disease,
      String? incubation,
      String? diagnosis,
      String? treatment,
      String? prevention,
      String? notes,
      @JsonKey(name: 'created_at') String createdAt,
      @JsonKey(name: 'updated_at') String updatedAt});
}

/// @nodoc
class __$$PathogenImplCopyWithImpl<$Res>
    extends _$PathogenCopyWithImpl<$Res, _$PathogenImpl>
    implements _$$PathogenImplCopyWith<$Res> {
  __$$PathogenImplCopyWithImpl(
      _$PathogenImpl _value, $Res Function(_$PathogenImpl) _then)
      : super(_value, _then);

  /// Create a copy of Pathogen
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? classification = freezed,
    Object? nt = freezed,
    Object? pathogenId = freezed,
    Object? pathogenName = null,
    Object? vaccine = freezed,
    Object? toxin = freezed,
    Object? transmission = freezed,
    Object? abResistance = freezed,
    Object? host = freezed,
    Object? commensal = freezed,
    Object? disease = freezed,
    Object? incubation = freezed,
    Object? diagnosis = freezed,
    Object? treatment = freezed,
    Object? prevention = freezed,
    Object? notes = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
  }) {
    return _then(_$PathogenImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      classification: freezed == classification
          ? _value.classification
          : classification // ignore: cast_nullable_to_non_nullable
              as String?,
      nt: freezed == nt
          ? _value.nt
          : nt // ignore: cast_nullable_to_non_nullable
              as String?,
      pathogenId: freezed == pathogenId
          ? _value.pathogenId
          : pathogenId // ignore: cast_nullable_to_non_nullable
              as String?,
      pathogenName: null == pathogenName
          ? _value.pathogenName
          : pathogenName // ignore: cast_nullable_to_non_nullable
              as String,
      vaccine: freezed == vaccine
          ? _value.vaccine
          : vaccine // ignore: cast_nullable_to_non_nullable
              as String?,
      toxin: freezed == toxin
          ? _value.toxin
          : toxin // ignore: cast_nullable_to_non_nullable
              as String?,
      transmission: freezed == transmission
          ? _value.transmission
          : transmission // ignore: cast_nullable_to_non_nullable
              as String?,
      abResistance: freezed == abResistance
          ? _value.abResistance
          : abResistance // ignore: cast_nullable_to_non_nullable
              as String?,
      host: freezed == host
          ? _value.host
          : host // ignore: cast_nullable_to_non_nullable
              as String?,
      commensal: freezed == commensal
          ? _value.commensal
          : commensal // ignore: cast_nullable_to_non_nullable
              as String?,
      disease: freezed == disease
          ? _value.disease
          : disease // ignore: cast_nullable_to_non_nullable
              as String?,
      incubation: freezed == incubation
          ? _value.incubation
          : incubation // ignore: cast_nullable_to_non_nullable
              as String?,
      diagnosis: freezed == diagnosis
          ? _value.diagnosis
          : diagnosis // ignore: cast_nullable_to_non_nullable
              as String?,
      treatment: freezed == treatment
          ? _value.treatment
          : treatment // ignore: cast_nullable_to_non_nullable
              as String?,
      prevention: freezed == prevention
          ? _value.prevention
          : prevention // ignore: cast_nullable_to_non_nullable
              as String?,
      notes: freezed == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String?,
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
class _$PathogenImpl implements _Pathogen {
  const _$PathogenImpl(
      {required this.id,
      this.classification,
      this.nt,
      @JsonKey(name: 'pathogen_id') this.pathogenId,
      @JsonKey(name: 'pathogen_name') required this.pathogenName,
      this.vaccine,
      this.toxin,
      this.transmission,
      @JsonKey(name: 'ab_resistance') this.abResistance,
      this.host,
      this.commensal,
      this.disease,
      this.incubation,
      this.diagnosis,
      this.treatment,
      this.prevention,
      this.notes,
      @JsonKey(name: 'created_at') required this.createdAt,
      @JsonKey(name: 'updated_at') required this.updatedAt});

  factory _$PathogenImpl.fromJson(Map<String, dynamic> json) =>
      _$$PathogenImplFromJson(json);

  @override
  final int id;
  @override
  final String? classification;
  @override
  final String? nt;
  @override
  @JsonKey(name: 'pathogen_id')
  final String? pathogenId;
  @override
  @JsonKey(name: 'pathogen_name')
  final String pathogenName;
  @override
  final String? vaccine;
  @override
  final String? toxin;
  @override
  final String? transmission;
  @override
  @JsonKey(name: 'ab_resistance')
  final String? abResistance;
  @override
  final String? host;
  @override
  final String? commensal;
  @override
  final String? disease;
  @override
  final String? incubation;
  @override
  final String? diagnosis;
  @override
  final String? treatment;
  @override
  final String? prevention;
  @override
  final String? notes;
  @override
  @JsonKey(name: 'created_at')
  final String createdAt;
  @override
  @JsonKey(name: 'updated_at')
  final String updatedAt;

  @override
  String toString() {
    return 'Pathogen(id: $id, classification: $classification, nt: $nt, pathogenId: $pathogenId, pathogenName: $pathogenName, vaccine: $vaccine, toxin: $toxin, transmission: $transmission, abResistance: $abResistance, host: $host, commensal: $commensal, disease: $disease, incubation: $incubation, diagnosis: $diagnosis, treatment: $treatment, prevention: $prevention, notes: $notes, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PathogenImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.classification, classification) ||
                other.classification == classification) &&
            (identical(other.nt, nt) || other.nt == nt) &&
            (identical(other.pathogenId, pathogenId) ||
                other.pathogenId == pathogenId) &&
            (identical(other.pathogenName, pathogenName) ||
                other.pathogenName == pathogenName) &&
            (identical(other.vaccine, vaccine) || other.vaccine == vaccine) &&
            (identical(other.toxin, toxin) || other.toxin == toxin) &&
            (identical(other.transmission, transmission) ||
                other.transmission == transmission) &&
            (identical(other.abResistance, abResistance) ||
                other.abResistance == abResistance) &&
            (identical(other.host, host) || other.host == host) &&
            (identical(other.commensal, commensal) ||
                other.commensal == commensal) &&
            (identical(other.disease, disease) || other.disease == disease) &&
            (identical(other.incubation, incubation) ||
                other.incubation == incubation) &&
            (identical(other.diagnosis, diagnosis) ||
                other.diagnosis == diagnosis) &&
            (identical(other.treatment, treatment) ||
                other.treatment == treatment) &&
            (identical(other.prevention, prevention) ||
                other.prevention == prevention) &&
            (identical(other.notes, notes) || other.notes == notes) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hashAll([
        runtimeType,
        id,
        classification,
        nt,
        pathogenId,
        pathogenName,
        vaccine,
        toxin,
        transmission,
        abResistance,
        host,
        commensal,
        disease,
        incubation,
        diagnosis,
        treatment,
        prevention,
        notes,
        createdAt,
        updatedAt
      ]);

  /// Create a copy of Pathogen
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PathogenImplCopyWith<_$PathogenImpl> get copyWith =>
      __$$PathogenImplCopyWithImpl<_$PathogenImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PathogenImplToJson(
      this,
    );
  }
}

abstract class _Pathogen implements Pathogen {
  const factory _Pathogen(
          {required final int id,
          final String? classification,
          final String? nt,
          @JsonKey(name: 'pathogen_id') final String? pathogenId,
          @JsonKey(name: 'pathogen_name') required final String pathogenName,
          final String? vaccine,
          final String? toxin,
          final String? transmission,
          @JsonKey(name: 'ab_resistance') final String? abResistance,
          final String? host,
          final String? commensal,
          final String? disease,
          final String? incubation,
          final String? diagnosis,
          final String? treatment,
          final String? prevention,
          final String? notes,
          @JsonKey(name: 'created_at') required final String createdAt,
          @JsonKey(name: 'updated_at') required final String updatedAt}) =
      _$PathogenImpl;

  factory _Pathogen.fromJson(Map<String, dynamic> json) =
      _$PathogenImpl.fromJson;

  @override
  int get id;
  @override
  String? get classification;
  @override
  String? get nt;
  @override
  @JsonKey(name: 'pathogen_id')
  String? get pathogenId;
  @override
  @JsonKey(name: 'pathogen_name')
  String get pathogenName;
  @override
  String? get vaccine;
  @override
  String? get toxin;
  @override
  String? get transmission;
  @override
  @JsonKey(name: 'ab_resistance')
  String? get abResistance;
  @override
  String? get host;
  @override
  String? get commensal;
  @override
  String? get disease;
  @override
  String? get incubation;
  @override
  String? get diagnosis;
  @override
  String? get treatment;
  @override
  String? get prevention;
  @override
  String? get notes;
  @override
  @JsonKey(name: 'created_at')
  String get createdAt;
  @override
  @JsonKey(name: 'updated_at')
  String get updatedAt;

  /// Create a copy of Pathogen
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PathogenImplCopyWith<_$PathogenImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

AssociationType _$AssociationTypeFromJson(Map<String, dynamic> json) {
  return _AssociationType.fromJson(json);
}

/// @nodoc
mixin _$AssociationType {
  int get id => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String? get description => throw _privateConstructorUsedError;
  @JsonKey(name: 'created_at')
  String get createdAt => throw _privateConstructorUsedError;

  /// Serializes this AssociationType to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of AssociationType
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $AssociationTypeCopyWith<AssociationType> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $AssociationTypeCopyWith<$Res> {
  factory $AssociationTypeCopyWith(
          AssociationType value, $Res Function(AssociationType) then) =
      _$AssociationTypeCopyWithImpl<$Res, AssociationType>;
  @useResult
  $Res call(
      {int id,
      String name,
      String? description,
      @JsonKey(name: 'created_at') String createdAt});
}

/// @nodoc
class _$AssociationTypeCopyWithImpl<$Res, $Val extends AssociationType>
    implements $AssociationTypeCopyWith<$Res> {
  _$AssociationTypeCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of AssociationType
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? description = freezed,
    Object? createdAt = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$AssociationTypeImplCopyWith<$Res>
    implements $AssociationTypeCopyWith<$Res> {
  factory _$$AssociationTypeImplCopyWith(_$AssociationTypeImpl value,
          $Res Function(_$AssociationTypeImpl) then) =
      __$$AssociationTypeImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int id,
      String name,
      String? description,
      @JsonKey(name: 'created_at') String createdAt});
}

/// @nodoc
class __$$AssociationTypeImplCopyWithImpl<$Res>
    extends _$AssociationTypeCopyWithImpl<$Res, _$AssociationTypeImpl>
    implements _$$AssociationTypeImplCopyWith<$Res> {
  __$$AssociationTypeImplCopyWithImpl(
      _$AssociationTypeImpl _value, $Res Function(_$AssociationTypeImpl) _then)
      : super(_value, _then);

  /// Create a copy of AssociationType
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? description = freezed,
    Object? createdAt = null,
  }) {
    return _then(_$AssociationTypeImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$AssociationTypeImpl implements _AssociationType {
  const _$AssociationTypeImpl(
      {required this.id,
      required this.name,
      this.description,
      @JsonKey(name: 'created_at') required this.createdAt});

  factory _$AssociationTypeImpl.fromJson(Map<String, dynamic> json) =>
      _$$AssociationTypeImplFromJson(json);

  @override
  final int id;
  @override
  final String name;
  @override
  final String? description;
  @override
  @JsonKey(name: 'created_at')
  final String createdAt;

  @override
  String toString() {
    return 'AssociationType(id: $id, name: $name, description: $description, createdAt: $createdAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$AssociationTypeImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, id, name, description, createdAt);

  /// Create a copy of AssociationType
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$AssociationTypeImplCopyWith<_$AssociationTypeImpl> get copyWith =>
      __$$AssociationTypeImplCopyWithImpl<_$AssociationTypeImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$AssociationTypeImplToJson(
      this,
    );
  }
}

abstract class _AssociationType implements AssociationType {
  const factory _AssociationType(
          {required final int id,
          required final String name,
          final String? description,
          @JsonKey(name: 'created_at') required final String createdAt}) =
      _$AssociationTypeImpl;

  factory _AssociationType.fromJson(Map<String, dynamic> json) =
      _$AssociationTypeImpl.fromJson;

  @override
  int get id;
  @override
  String get name;
  @override
  String? get description;
  @override
  @JsonKey(name: 'created_at')
  String get createdAt;

  /// Create a copy of AssociationType
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$AssociationTypeImplCopyWith<_$AssociationTypeImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

PathogenAssociation _$PathogenAssociationFromJson(Map<String, dynamic> json) {
  return _PathogenAssociation.fromJson(json);
}

/// @nodoc
mixin _$PathogenAssociation {
  @JsonKey(name: 'pathogen_id')
  int get pathogenId => throw _privateConstructorUsedError;
  @JsonKey(name: 'association_type_id')
  int get associationTypeId => throw _privateConstructorUsedError;
  int get value => throw _privateConstructorUsedError;
  @JsonKey(name: 'association_type_name')
  String? get associationTypeName => throw _privateConstructorUsedError;

  /// Serializes this PathogenAssociation to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PathogenAssociation
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PathogenAssociationCopyWith<PathogenAssociation> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PathogenAssociationCopyWith<$Res> {
  factory $PathogenAssociationCopyWith(
          PathogenAssociation value, $Res Function(PathogenAssociation) then) =
      _$PathogenAssociationCopyWithImpl<$Res, PathogenAssociation>;
  @useResult
  $Res call(
      {@JsonKey(name: 'pathogen_id') int pathogenId,
      @JsonKey(name: 'association_type_id') int associationTypeId,
      int value,
      @JsonKey(name: 'association_type_name') String? associationTypeName});
}

/// @nodoc
class _$PathogenAssociationCopyWithImpl<$Res, $Val extends PathogenAssociation>
    implements $PathogenAssociationCopyWith<$Res> {
  _$PathogenAssociationCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PathogenAssociation
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? pathogenId = null,
    Object? associationTypeId = null,
    Object? value = null,
    Object? associationTypeName = freezed,
  }) {
    return _then(_value.copyWith(
      pathogenId: null == pathogenId
          ? _value.pathogenId
          : pathogenId // ignore: cast_nullable_to_non_nullable
              as int,
      associationTypeId: null == associationTypeId
          ? _value.associationTypeId
          : associationTypeId // ignore: cast_nullable_to_non_nullable
              as int,
      value: null == value
          ? _value.value
          : value // ignore: cast_nullable_to_non_nullable
              as int,
      associationTypeName: freezed == associationTypeName
          ? _value.associationTypeName
          : associationTypeName // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$PathogenAssociationImplCopyWith<$Res>
    implements $PathogenAssociationCopyWith<$Res> {
  factory _$$PathogenAssociationImplCopyWith(_$PathogenAssociationImpl value,
          $Res Function(_$PathogenAssociationImpl) then) =
      __$$PathogenAssociationImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'pathogen_id') int pathogenId,
      @JsonKey(name: 'association_type_id') int associationTypeId,
      int value,
      @JsonKey(name: 'association_type_name') String? associationTypeName});
}

/// @nodoc
class __$$PathogenAssociationImplCopyWithImpl<$Res>
    extends _$PathogenAssociationCopyWithImpl<$Res, _$PathogenAssociationImpl>
    implements _$$PathogenAssociationImplCopyWith<$Res> {
  __$$PathogenAssociationImplCopyWithImpl(_$PathogenAssociationImpl _value,
      $Res Function(_$PathogenAssociationImpl) _then)
      : super(_value, _then);

  /// Create a copy of PathogenAssociation
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? pathogenId = null,
    Object? associationTypeId = null,
    Object? value = null,
    Object? associationTypeName = freezed,
  }) {
    return _then(_$PathogenAssociationImpl(
      pathogenId: null == pathogenId
          ? _value.pathogenId
          : pathogenId // ignore: cast_nullable_to_non_nullable
              as int,
      associationTypeId: null == associationTypeId
          ? _value.associationTypeId
          : associationTypeId // ignore: cast_nullable_to_non_nullable
              as int,
      value: null == value
          ? _value.value
          : value // ignore: cast_nullable_to_non_nullable
              as int,
      associationTypeName: freezed == associationTypeName
          ? _value.associationTypeName
          : associationTypeName // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$PathogenAssociationImpl implements _PathogenAssociation {
  const _$PathogenAssociationImpl(
      {@JsonKey(name: 'pathogen_id') required this.pathogenId,
      @JsonKey(name: 'association_type_id') required this.associationTypeId,
      required this.value,
      @JsonKey(name: 'association_type_name') this.associationTypeName});

  factory _$PathogenAssociationImpl.fromJson(Map<String, dynamic> json) =>
      _$$PathogenAssociationImplFromJson(json);

  @override
  @JsonKey(name: 'pathogen_id')
  final int pathogenId;
  @override
  @JsonKey(name: 'association_type_id')
  final int associationTypeId;
  @override
  final int value;
  @override
  @JsonKey(name: 'association_type_name')
  final String? associationTypeName;

  @override
  String toString() {
    return 'PathogenAssociation(pathogenId: $pathogenId, associationTypeId: $associationTypeId, value: $value, associationTypeName: $associationTypeName)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PathogenAssociationImpl &&
            (identical(other.pathogenId, pathogenId) ||
                other.pathogenId == pathogenId) &&
            (identical(other.associationTypeId, associationTypeId) ||
                other.associationTypeId == associationTypeId) &&
            (identical(other.value, value) || other.value == value) &&
            (identical(other.associationTypeName, associationTypeName) ||
                other.associationTypeName == associationTypeName));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType, pathogenId, associationTypeId, value, associationTypeName);

  /// Create a copy of PathogenAssociation
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PathogenAssociationImplCopyWith<_$PathogenAssociationImpl> get copyWith =>
      __$$PathogenAssociationImplCopyWithImpl<_$PathogenAssociationImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PathogenAssociationImplToJson(
      this,
    );
  }
}

abstract class _PathogenAssociation implements PathogenAssociation {
  const factory _PathogenAssociation(
      {@JsonKey(name: 'pathogen_id') required final int pathogenId,
      @JsonKey(name: 'association_type_id')
      required final int associationTypeId,
      required final int value,
      @JsonKey(name: 'association_type_name')
      final String? associationTypeName}) = _$PathogenAssociationImpl;

  factory _PathogenAssociation.fromJson(Map<String, dynamic> json) =
      _$PathogenAssociationImpl.fromJson;

  @override
  @JsonKey(name: 'pathogen_id')
  int get pathogenId;
  @override
  @JsonKey(name: 'association_type_id')
  int get associationTypeId;
  @override
  int get value;
  @override
  @JsonKey(name: 'association_type_name')
  String? get associationTypeName;

  /// Create a copy of PathogenAssociation
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PathogenAssociationImplCopyWith<_$PathogenAssociationImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

PathogenWithAssociations _$PathogenWithAssociationsFromJson(
    Map<String, dynamic> json) {
  return _PathogenWithAssociations.fromJson(json);
}

/// @nodoc
mixin _$PathogenWithAssociations {
  int get id => throw _privateConstructorUsedError;
  String? get classification => throw _privateConstructorUsedError;
  String? get nt => throw _privateConstructorUsedError;
  @JsonKey(name: 'pathogen_id')
  String? get pathogenId => throw _privateConstructorUsedError;
  @JsonKey(name: 'pathogen_name')
  String get pathogenName => throw _privateConstructorUsedError;
  String? get vaccine => throw _privateConstructorUsedError;
  String? get toxin => throw _privateConstructorUsedError;
  String? get transmission => throw _privateConstructorUsedError;
  @JsonKey(name: 'ab_resistance')
  String? get abResistance => throw _privateConstructorUsedError;
  String? get host => throw _privateConstructorUsedError;
  String? get commensal => throw _privateConstructorUsedError;
  String? get disease => throw _privateConstructorUsedError;
  String? get incubation => throw _privateConstructorUsedError;
  String? get diagnosis => throw _privateConstructorUsedError;
  String? get treatment => throw _privateConstructorUsedError;
  String? get prevention => throw _privateConstructorUsedError;
  String? get notes => throw _privateConstructorUsedError;
  @JsonKey(name: 'created_at')
  String get createdAt => throw _privateConstructorUsedError;
  @JsonKey(name: 'updated_at')
  String get updatedAt => throw _privateConstructorUsedError;
  List<PathogenAssociation> get associations =>
      throw _privateConstructorUsedError;

  /// Serializes this PathogenWithAssociations to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PathogenWithAssociations
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PathogenWithAssociationsCopyWith<PathogenWithAssociations> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PathogenWithAssociationsCopyWith<$Res> {
  factory $PathogenWithAssociationsCopyWith(PathogenWithAssociations value,
          $Res Function(PathogenWithAssociations) then) =
      _$PathogenWithAssociationsCopyWithImpl<$Res, PathogenWithAssociations>;
  @useResult
  $Res call(
      {int id,
      String? classification,
      String? nt,
      @JsonKey(name: 'pathogen_id') String? pathogenId,
      @JsonKey(name: 'pathogen_name') String pathogenName,
      String? vaccine,
      String? toxin,
      String? transmission,
      @JsonKey(name: 'ab_resistance') String? abResistance,
      String? host,
      String? commensal,
      String? disease,
      String? incubation,
      String? diagnosis,
      String? treatment,
      String? prevention,
      String? notes,
      @JsonKey(name: 'created_at') String createdAt,
      @JsonKey(name: 'updated_at') String updatedAt,
      List<PathogenAssociation> associations});
}

/// @nodoc
class _$PathogenWithAssociationsCopyWithImpl<$Res,
        $Val extends PathogenWithAssociations>
    implements $PathogenWithAssociationsCopyWith<$Res> {
  _$PathogenWithAssociationsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PathogenWithAssociations
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? classification = freezed,
    Object? nt = freezed,
    Object? pathogenId = freezed,
    Object? pathogenName = null,
    Object? vaccine = freezed,
    Object? toxin = freezed,
    Object? transmission = freezed,
    Object? abResistance = freezed,
    Object? host = freezed,
    Object? commensal = freezed,
    Object? disease = freezed,
    Object? incubation = freezed,
    Object? diagnosis = freezed,
    Object? treatment = freezed,
    Object? prevention = freezed,
    Object? notes = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
    Object? associations = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      classification: freezed == classification
          ? _value.classification
          : classification // ignore: cast_nullable_to_non_nullable
              as String?,
      nt: freezed == nt
          ? _value.nt
          : nt // ignore: cast_nullable_to_non_nullable
              as String?,
      pathogenId: freezed == pathogenId
          ? _value.pathogenId
          : pathogenId // ignore: cast_nullable_to_non_nullable
              as String?,
      pathogenName: null == pathogenName
          ? _value.pathogenName
          : pathogenName // ignore: cast_nullable_to_non_nullable
              as String,
      vaccine: freezed == vaccine
          ? _value.vaccine
          : vaccine // ignore: cast_nullable_to_non_nullable
              as String?,
      toxin: freezed == toxin
          ? _value.toxin
          : toxin // ignore: cast_nullable_to_non_nullable
              as String?,
      transmission: freezed == transmission
          ? _value.transmission
          : transmission // ignore: cast_nullable_to_non_nullable
              as String?,
      abResistance: freezed == abResistance
          ? _value.abResistance
          : abResistance // ignore: cast_nullable_to_non_nullable
              as String?,
      host: freezed == host
          ? _value.host
          : host // ignore: cast_nullable_to_non_nullable
              as String?,
      commensal: freezed == commensal
          ? _value.commensal
          : commensal // ignore: cast_nullable_to_non_nullable
              as String?,
      disease: freezed == disease
          ? _value.disease
          : disease // ignore: cast_nullable_to_non_nullable
              as String?,
      incubation: freezed == incubation
          ? _value.incubation
          : incubation // ignore: cast_nullable_to_non_nullable
              as String?,
      diagnosis: freezed == diagnosis
          ? _value.diagnosis
          : diagnosis // ignore: cast_nullable_to_non_nullable
              as String?,
      treatment: freezed == treatment
          ? _value.treatment
          : treatment // ignore: cast_nullable_to_non_nullable
              as String?,
      prevention: freezed == prevention
          ? _value.prevention
          : prevention // ignore: cast_nullable_to_non_nullable
              as String?,
      notes: freezed == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as String,
      associations: null == associations
          ? _value.associations
          : associations // ignore: cast_nullable_to_non_nullable
              as List<PathogenAssociation>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$PathogenWithAssociationsImplCopyWith<$Res>
    implements $PathogenWithAssociationsCopyWith<$Res> {
  factory _$$PathogenWithAssociationsImplCopyWith(
          _$PathogenWithAssociationsImpl value,
          $Res Function(_$PathogenWithAssociationsImpl) then) =
      __$$PathogenWithAssociationsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int id,
      String? classification,
      String? nt,
      @JsonKey(name: 'pathogen_id') String? pathogenId,
      @JsonKey(name: 'pathogen_name') String pathogenName,
      String? vaccine,
      String? toxin,
      String? transmission,
      @JsonKey(name: 'ab_resistance') String? abResistance,
      String? host,
      String? commensal,
      String? disease,
      String? incubation,
      String? diagnosis,
      String? treatment,
      String? prevention,
      String? notes,
      @JsonKey(name: 'created_at') String createdAt,
      @JsonKey(name: 'updated_at') String updatedAt,
      List<PathogenAssociation> associations});
}

/// @nodoc
class __$$PathogenWithAssociationsImplCopyWithImpl<$Res>
    extends _$PathogenWithAssociationsCopyWithImpl<$Res,
        _$PathogenWithAssociationsImpl>
    implements _$$PathogenWithAssociationsImplCopyWith<$Res> {
  __$$PathogenWithAssociationsImplCopyWithImpl(
      _$PathogenWithAssociationsImpl _value,
      $Res Function(_$PathogenWithAssociationsImpl) _then)
      : super(_value, _then);

  /// Create a copy of PathogenWithAssociations
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? classification = freezed,
    Object? nt = freezed,
    Object? pathogenId = freezed,
    Object? pathogenName = null,
    Object? vaccine = freezed,
    Object? toxin = freezed,
    Object? transmission = freezed,
    Object? abResistance = freezed,
    Object? host = freezed,
    Object? commensal = freezed,
    Object? disease = freezed,
    Object? incubation = freezed,
    Object? diagnosis = freezed,
    Object? treatment = freezed,
    Object? prevention = freezed,
    Object? notes = freezed,
    Object? createdAt = null,
    Object? updatedAt = null,
    Object? associations = null,
  }) {
    return _then(_$PathogenWithAssociationsImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      classification: freezed == classification
          ? _value.classification
          : classification // ignore: cast_nullable_to_non_nullable
              as String?,
      nt: freezed == nt
          ? _value.nt
          : nt // ignore: cast_nullable_to_non_nullable
              as String?,
      pathogenId: freezed == pathogenId
          ? _value.pathogenId
          : pathogenId // ignore: cast_nullable_to_non_nullable
              as String?,
      pathogenName: null == pathogenName
          ? _value.pathogenName
          : pathogenName // ignore: cast_nullable_to_non_nullable
              as String,
      vaccine: freezed == vaccine
          ? _value.vaccine
          : vaccine // ignore: cast_nullable_to_non_nullable
              as String?,
      toxin: freezed == toxin
          ? _value.toxin
          : toxin // ignore: cast_nullable_to_non_nullable
              as String?,
      transmission: freezed == transmission
          ? _value.transmission
          : transmission // ignore: cast_nullable_to_non_nullable
              as String?,
      abResistance: freezed == abResistance
          ? _value.abResistance
          : abResistance // ignore: cast_nullable_to_non_nullable
              as String?,
      host: freezed == host
          ? _value.host
          : host // ignore: cast_nullable_to_non_nullable
              as String?,
      commensal: freezed == commensal
          ? _value.commensal
          : commensal // ignore: cast_nullable_to_non_nullable
              as String?,
      disease: freezed == disease
          ? _value.disease
          : disease // ignore: cast_nullable_to_non_nullable
              as String?,
      incubation: freezed == incubation
          ? _value.incubation
          : incubation // ignore: cast_nullable_to_non_nullable
              as String?,
      diagnosis: freezed == diagnosis
          ? _value.diagnosis
          : diagnosis // ignore: cast_nullable_to_non_nullable
              as String?,
      treatment: freezed == treatment
          ? _value.treatment
          : treatment // ignore: cast_nullable_to_non_nullable
              as String?,
      prevention: freezed == prevention
          ? _value.prevention
          : prevention // ignore: cast_nullable_to_non_nullable
              as String?,
      notes: freezed == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String?,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as String,
      updatedAt: null == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as String,
      associations: null == associations
          ? _value._associations
          : associations // ignore: cast_nullable_to_non_nullable
              as List<PathogenAssociation>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$PathogenWithAssociationsImpl implements _PathogenWithAssociations {
  const _$PathogenWithAssociationsImpl(
      {required this.id,
      this.classification,
      this.nt,
      @JsonKey(name: 'pathogen_id') this.pathogenId,
      @JsonKey(name: 'pathogen_name') required this.pathogenName,
      this.vaccine,
      this.toxin,
      this.transmission,
      @JsonKey(name: 'ab_resistance') this.abResistance,
      this.host,
      this.commensal,
      this.disease,
      this.incubation,
      this.diagnosis,
      this.treatment,
      this.prevention,
      this.notes,
      @JsonKey(name: 'created_at') required this.createdAt,
      @JsonKey(name: 'updated_at') required this.updatedAt,
      required final List<PathogenAssociation> associations})
      : _associations = associations;

  factory _$PathogenWithAssociationsImpl.fromJson(Map<String, dynamic> json) =>
      _$$PathogenWithAssociationsImplFromJson(json);

  @override
  final int id;
  @override
  final String? classification;
  @override
  final String? nt;
  @override
  @JsonKey(name: 'pathogen_id')
  final String? pathogenId;
  @override
  @JsonKey(name: 'pathogen_name')
  final String pathogenName;
  @override
  final String? vaccine;
  @override
  final String? toxin;
  @override
  final String? transmission;
  @override
  @JsonKey(name: 'ab_resistance')
  final String? abResistance;
  @override
  final String? host;
  @override
  final String? commensal;
  @override
  final String? disease;
  @override
  final String? incubation;
  @override
  final String? diagnosis;
  @override
  final String? treatment;
  @override
  final String? prevention;
  @override
  final String? notes;
  @override
  @JsonKey(name: 'created_at')
  final String createdAt;
  @override
  @JsonKey(name: 'updated_at')
  final String updatedAt;
  final List<PathogenAssociation> _associations;
  @override
  List<PathogenAssociation> get associations {
    if (_associations is EqualUnmodifiableListView) return _associations;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_associations);
  }

  @override
  String toString() {
    return 'PathogenWithAssociations(id: $id, classification: $classification, nt: $nt, pathogenId: $pathogenId, pathogenName: $pathogenName, vaccine: $vaccine, toxin: $toxin, transmission: $transmission, abResistance: $abResistance, host: $host, commensal: $commensal, disease: $disease, incubation: $incubation, diagnosis: $diagnosis, treatment: $treatment, prevention: $prevention, notes: $notes, createdAt: $createdAt, updatedAt: $updatedAt, associations: $associations)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PathogenWithAssociationsImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.classification, classification) ||
                other.classification == classification) &&
            (identical(other.nt, nt) || other.nt == nt) &&
            (identical(other.pathogenId, pathogenId) ||
                other.pathogenId == pathogenId) &&
            (identical(other.pathogenName, pathogenName) ||
                other.pathogenName == pathogenName) &&
            (identical(other.vaccine, vaccine) || other.vaccine == vaccine) &&
            (identical(other.toxin, toxin) || other.toxin == toxin) &&
            (identical(other.transmission, transmission) ||
                other.transmission == transmission) &&
            (identical(other.abResistance, abResistance) ||
                other.abResistance == abResistance) &&
            (identical(other.host, host) || other.host == host) &&
            (identical(other.commensal, commensal) ||
                other.commensal == commensal) &&
            (identical(other.disease, disease) || other.disease == disease) &&
            (identical(other.incubation, incubation) ||
                other.incubation == incubation) &&
            (identical(other.diagnosis, diagnosis) ||
                other.diagnosis == diagnosis) &&
            (identical(other.treatment, treatment) ||
                other.treatment == treatment) &&
            (identical(other.prevention, prevention) ||
                other.prevention == prevention) &&
            (identical(other.notes, notes) || other.notes == notes) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt) &&
            const DeepCollectionEquality()
                .equals(other._associations, _associations));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hashAll([
        runtimeType,
        id,
        classification,
        nt,
        pathogenId,
        pathogenName,
        vaccine,
        toxin,
        transmission,
        abResistance,
        host,
        commensal,
        disease,
        incubation,
        diagnosis,
        treatment,
        prevention,
        notes,
        createdAt,
        updatedAt,
        const DeepCollectionEquality().hash(_associations)
      ]);

  /// Create a copy of PathogenWithAssociations
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PathogenWithAssociationsImplCopyWith<_$PathogenWithAssociationsImpl>
      get copyWith => __$$PathogenWithAssociationsImplCopyWithImpl<
          _$PathogenWithAssociationsImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PathogenWithAssociationsImplToJson(
      this,
    );
  }
}

abstract class _PathogenWithAssociations implements PathogenWithAssociations {
  const factory _PathogenWithAssociations(
          {required final int id,
          final String? classification,
          final String? nt,
          @JsonKey(name: 'pathogen_id') final String? pathogenId,
          @JsonKey(name: 'pathogen_name') required final String pathogenName,
          final String? vaccine,
          final String? toxin,
          final String? transmission,
          @JsonKey(name: 'ab_resistance') final String? abResistance,
          final String? host,
          final String? commensal,
          final String? disease,
          final String? incubation,
          final String? diagnosis,
          final String? treatment,
          final String? prevention,
          final String? notes,
          @JsonKey(name: 'created_at') required final String createdAt,
          @JsonKey(name: 'updated_at') required final String updatedAt,
          required final List<PathogenAssociation> associations}) =
      _$PathogenWithAssociationsImpl;

  factory _PathogenWithAssociations.fromJson(Map<String, dynamic> json) =
      _$PathogenWithAssociationsImpl.fromJson;

  @override
  int get id;
  @override
  String? get classification;
  @override
  String? get nt;
  @override
  @JsonKey(name: 'pathogen_id')
  String? get pathogenId;
  @override
  @JsonKey(name: 'pathogen_name')
  String get pathogenName;
  @override
  String? get vaccine;
  @override
  String? get toxin;
  @override
  String? get transmission;
  @override
  @JsonKey(name: 'ab_resistance')
  String? get abResistance;
  @override
  String? get host;
  @override
  String? get commensal;
  @override
  String? get disease;
  @override
  String? get incubation;
  @override
  String? get diagnosis;
  @override
  String? get treatment;
  @override
  String? get prevention;
  @override
  String? get notes;
  @override
  @JsonKey(name: 'created_at')
  String get createdAt;
  @override
  @JsonKey(name: 'updated_at')
  String get updatedAt;
  @override
  List<PathogenAssociation> get associations;

  /// Create a copy of PathogenWithAssociations
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PathogenWithAssociationsImplCopyWith<_$PathogenWithAssociationsImpl>
      get copyWith => throw _privateConstructorUsedError;
}

PathogenStats _$PathogenStatsFromJson(Map<String, dynamic> json) {
  return _PathogenStats.fromJson(json);
}

/// @nodoc
mixin _$PathogenStats {
  @JsonKey(name: 'total_pathogens')
  int get totalPathogens => throw _privateConstructorUsedError;
  @JsonKey(name: 'total_associations')
  int get totalAssociations => throw _privateConstructorUsedError;
  @JsonKey(name: 'pathogens_with_associations')
  int get pathogensWithAssociations => throw _privateConstructorUsedError;
  @JsonKey(name: 'average_associations_per_pathogen')
  double get averageAssociationsPerPathogen =>
      throw _privateConstructorUsedError;

  /// Serializes this PathogenStats to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PathogenStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PathogenStatsCopyWith<PathogenStats> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PathogenStatsCopyWith<$Res> {
  factory $PathogenStatsCopyWith(
          PathogenStats value, $Res Function(PathogenStats) then) =
      _$PathogenStatsCopyWithImpl<$Res, PathogenStats>;
  @useResult
  $Res call(
      {@JsonKey(name: 'total_pathogens') int totalPathogens,
      @JsonKey(name: 'total_associations') int totalAssociations,
      @JsonKey(name: 'pathogens_with_associations')
      int pathogensWithAssociations,
      @JsonKey(name: 'average_associations_per_pathogen')
      double averageAssociationsPerPathogen});
}

/// @nodoc
class _$PathogenStatsCopyWithImpl<$Res, $Val extends PathogenStats>
    implements $PathogenStatsCopyWith<$Res> {
  _$PathogenStatsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PathogenStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalPathogens = null,
    Object? totalAssociations = null,
    Object? pathogensWithAssociations = null,
    Object? averageAssociationsPerPathogen = null,
  }) {
    return _then(_value.copyWith(
      totalPathogens: null == totalPathogens
          ? _value.totalPathogens
          : totalPathogens // ignore: cast_nullable_to_non_nullable
              as int,
      totalAssociations: null == totalAssociations
          ? _value.totalAssociations
          : totalAssociations // ignore: cast_nullable_to_non_nullable
              as int,
      pathogensWithAssociations: null == pathogensWithAssociations
          ? _value.pathogensWithAssociations
          : pathogensWithAssociations // ignore: cast_nullable_to_non_nullable
              as int,
      averageAssociationsPerPathogen: null == averageAssociationsPerPathogen
          ? _value.averageAssociationsPerPathogen
          : averageAssociationsPerPathogen // ignore: cast_nullable_to_non_nullable
              as double,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$PathogenStatsImplCopyWith<$Res>
    implements $PathogenStatsCopyWith<$Res> {
  factory _$$PathogenStatsImplCopyWith(
          _$PathogenStatsImpl value, $Res Function(_$PathogenStatsImpl) then) =
      __$$PathogenStatsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'total_pathogens') int totalPathogens,
      @JsonKey(name: 'total_associations') int totalAssociations,
      @JsonKey(name: 'pathogens_with_associations')
      int pathogensWithAssociations,
      @JsonKey(name: 'average_associations_per_pathogen')
      double averageAssociationsPerPathogen});
}

/// @nodoc
class __$$PathogenStatsImplCopyWithImpl<$Res>
    extends _$PathogenStatsCopyWithImpl<$Res, _$PathogenStatsImpl>
    implements _$$PathogenStatsImplCopyWith<$Res> {
  __$$PathogenStatsImplCopyWithImpl(
      _$PathogenStatsImpl _value, $Res Function(_$PathogenStatsImpl) _then)
      : super(_value, _then);

  /// Create a copy of PathogenStats
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalPathogens = null,
    Object? totalAssociations = null,
    Object? pathogensWithAssociations = null,
    Object? averageAssociationsPerPathogen = null,
  }) {
    return _then(_$PathogenStatsImpl(
      totalPathogens: null == totalPathogens
          ? _value.totalPathogens
          : totalPathogens // ignore: cast_nullable_to_non_nullable
              as int,
      totalAssociations: null == totalAssociations
          ? _value.totalAssociations
          : totalAssociations // ignore: cast_nullable_to_non_nullable
              as int,
      pathogensWithAssociations: null == pathogensWithAssociations
          ? _value.pathogensWithAssociations
          : pathogensWithAssociations // ignore: cast_nullable_to_non_nullable
              as int,
      averageAssociationsPerPathogen: null == averageAssociationsPerPathogen
          ? _value.averageAssociationsPerPathogen
          : averageAssociationsPerPathogen // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$PathogenStatsImpl implements _PathogenStats {
  const _$PathogenStatsImpl(
      {@JsonKey(name: 'total_pathogens') required this.totalPathogens,
      @JsonKey(name: 'total_associations') required this.totalAssociations,
      @JsonKey(name: 'pathogens_with_associations')
      required this.pathogensWithAssociations,
      @JsonKey(name: 'average_associations_per_pathogen')
      required this.averageAssociationsPerPathogen});

  factory _$PathogenStatsImpl.fromJson(Map<String, dynamic> json) =>
      _$$PathogenStatsImplFromJson(json);

  @override
  @JsonKey(name: 'total_pathogens')
  final int totalPathogens;
  @override
  @JsonKey(name: 'total_associations')
  final int totalAssociations;
  @override
  @JsonKey(name: 'pathogens_with_associations')
  final int pathogensWithAssociations;
  @override
  @JsonKey(name: 'average_associations_per_pathogen')
  final double averageAssociationsPerPathogen;

  @override
  String toString() {
    return 'PathogenStats(totalPathogens: $totalPathogens, totalAssociations: $totalAssociations, pathogensWithAssociations: $pathogensWithAssociations, averageAssociationsPerPathogen: $averageAssociationsPerPathogen)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PathogenStatsImpl &&
            (identical(other.totalPathogens, totalPathogens) ||
                other.totalPathogens == totalPathogens) &&
            (identical(other.totalAssociations, totalAssociations) ||
                other.totalAssociations == totalAssociations) &&
            (identical(other.pathogensWithAssociations,
                    pathogensWithAssociations) ||
                other.pathogensWithAssociations == pathogensWithAssociations) &&
            (identical(other.averageAssociationsPerPathogen,
                    averageAssociationsPerPathogen) ||
                other.averageAssociationsPerPathogen ==
                    averageAssociationsPerPathogen));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      totalPathogens,
      totalAssociations,
      pathogensWithAssociations,
      averageAssociationsPerPathogen);

  /// Create a copy of PathogenStats
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PathogenStatsImplCopyWith<_$PathogenStatsImpl> get copyWith =>
      __$$PathogenStatsImplCopyWithImpl<_$PathogenStatsImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PathogenStatsImplToJson(
      this,
    );
  }
}

abstract class _PathogenStats implements PathogenStats {
  const factory _PathogenStats(
      {@JsonKey(name: 'total_pathogens') required final int totalPathogens,
      @JsonKey(name: 'total_associations') required final int totalAssociations,
      @JsonKey(name: 'pathogens_with_associations')
      required final int pathogensWithAssociations,
      @JsonKey(name: 'average_associations_per_pathogen')
      required final double
          averageAssociationsPerPathogen}) = _$PathogenStatsImpl;

  factory _PathogenStats.fromJson(Map<String, dynamic> json) =
      _$PathogenStatsImpl.fromJson;

  @override
  @JsonKey(name: 'total_pathogens')
  int get totalPathogens;
  @override
  @JsonKey(name: 'total_associations')
  int get totalAssociations;
  @override
  @JsonKey(name: 'pathogens_with_associations')
  int get pathogensWithAssociations;
  @override
  @JsonKey(name: 'average_associations_per_pathogen')
  double get averageAssociationsPerPathogen;

  /// Create a copy of PathogenStats
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PathogenStatsImplCopyWith<_$PathogenStatsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

PathogenImportResult _$PathogenImportResultFromJson(Map<String, dynamic> json) {
  return _PathogenImportResult.fromJson(json);
}

/// @nodoc
mixin _$PathogenImportResult {
  bool get success => throw _privateConstructorUsedError;
  @JsonKey(name: 'pathogens_processed')
  int get pathogensProcessed => throw _privateConstructorUsedError;
  @JsonKey(name: 'pathogens_created')
  int get pathogensCreated => throw _privateConstructorUsedError;
  @JsonKey(name: 'pathogens_updated')
  int get pathogensUpdated => throw _privateConstructorUsedError;
  @JsonKey(name: 'associations_processed')
  int get associationsProcessed => throw _privateConstructorUsedError;
  @JsonKey(name: 'associations_created')
  int get associationsCreated => throw _privateConstructorUsedError;
  List<String> get errors => throw _privateConstructorUsedError;
  List<String> get warnings => throw _privateConstructorUsedError;

  /// Serializes this PathogenImportResult to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PathogenImportResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PathogenImportResultCopyWith<PathogenImportResult> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PathogenImportResultCopyWith<$Res> {
  factory $PathogenImportResultCopyWith(PathogenImportResult value,
          $Res Function(PathogenImportResult) then) =
      _$PathogenImportResultCopyWithImpl<$Res, PathogenImportResult>;
  @useResult
  $Res call(
      {bool success,
      @JsonKey(name: 'pathogens_processed') int pathogensProcessed,
      @JsonKey(name: 'pathogens_created') int pathogensCreated,
      @JsonKey(name: 'pathogens_updated') int pathogensUpdated,
      @JsonKey(name: 'associations_processed') int associationsProcessed,
      @JsonKey(name: 'associations_created') int associationsCreated,
      List<String> errors,
      List<String> warnings});
}

/// @nodoc
class _$PathogenImportResultCopyWithImpl<$Res,
        $Val extends PathogenImportResult>
    implements $PathogenImportResultCopyWith<$Res> {
  _$PathogenImportResultCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PathogenImportResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? pathogensProcessed = null,
    Object? pathogensCreated = null,
    Object? pathogensUpdated = null,
    Object? associationsProcessed = null,
    Object? associationsCreated = null,
    Object? errors = null,
    Object? warnings = null,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      pathogensProcessed: null == pathogensProcessed
          ? _value.pathogensProcessed
          : pathogensProcessed // ignore: cast_nullable_to_non_nullable
              as int,
      pathogensCreated: null == pathogensCreated
          ? _value.pathogensCreated
          : pathogensCreated // ignore: cast_nullable_to_non_nullable
              as int,
      pathogensUpdated: null == pathogensUpdated
          ? _value.pathogensUpdated
          : pathogensUpdated // ignore: cast_nullable_to_non_nullable
              as int,
      associationsProcessed: null == associationsProcessed
          ? _value.associationsProcessed
          : associationsProcessed // ignore: cast_nullable_to_non_nullable
              as int,
      associationsCreated: null == associationsCreated
          ? _value.associationsCreated
          : associationsCreated // ignore: cast_nullable_to_non_nullable
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
abstract class _$$PathogenImportResultImplCopyWith<$Res>
    implements $PathogenImportResultCopyWith<$Res> {
  factory _$$PathogenImportResultImplCopyWith(_$PathogenImportResultImpl value,
          $Res Function(_$PathogenImportResultImpl) then) =
      __$$PathogenImportResultImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool success,
      @JsonKey(name: 'pathogens_processed') int pathogensProcessed,
      @JsonKey(name: 'pathogens_created') int pathogensCreated,
      @JsonKey(name: 'pathogens_updated') int pathogensUpdated,
      @JsonKey(name: 'associations_processed') int associationsProcessed,
      @JsonKey(name: 'associations_created') int associationsCreated,
      List<String> errors,
      List<String> warnings});
}

/// @nodoc
class __$$PathogenImportResultImplCopyWithImpl<$Res>
    extends _$PathogenImportResultCopyWithImpl<$Res, _$PathogenImportResultImpl>
    implements _$$PathogenImportResultImplCopyWith<$Res> {
  __$$PathogenImportResultImplCopyWithImpl(_$PathogenImportResultImpl _value,
      $Res Function(_$PathogenImportResultImpl) _then)
      : super(_value, _then);

  /// Create a copy of PathogenImportResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? pathogensProcessed = null,
    Object? pathogensCreated = null,
    Object? pathogensUpdated = null,
    Object? associationsProcessed = null,
    Object? associationsCreated = null,
    Object? errors = null,
    Object? warnings = null,
  }) {
    return _then(_$PathogenImportResultImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      pathogensProcessed: null == pathogensProcessed
          ? _value.pathogensProcessed
          : pathogensProcessed // ignore: cast_nullable_to_non_nullable
              as int,
      pathogensCreated: null == pathogensCreated
          ? _value.pathogensCreated
          : pathogensCreated // ignore: cast_nullable_to_non_nullable
              as int,
      pathogensUpdated: null == pathogensUpdated
          ? _value.pathogensUpdated
          : pathogensUpdated // ignore: cast_nullable_to_non_nullable
              as int,
      associationsProcessed: null == associationsProcessed
          ? _value.associationsProcessed
          : associationsProcessed // ignore: cast_nullable_to_non_nullable
              as int,
      associationsCreated: null == associationsCreated
          ? _value.associationsCreated
          : associationsCreated // ignore: cast_nullable_to_non_nullable
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
class _$PathogenImportResultImpl implements _PathogenImportResult {
  const _$PathogenImportResultImpl(
      {required this.success,
      @JsonKey(name: 'pathogens_processed') required this.pathogensProcessed,
      @JsonKey(name: 'pathogens_created') required this.pathogensCreated,
      @JsonKey(name: 'pathogens_updated') required this.pathogensUpdated,
      @JsonKey(name: 'associations_processed')
      required this.associationsProcessed,
      @JsonKey(name: 'associations_created') required this.associationsCreated,
      required final List<String> errors,
      required final List<String> warnings})
      : _errors = errors,
        _warnings = warnings;

  factory _$PathogenImportResultImpl.fromJson(Map<String, dynamic> json) =>
      _$$PathogenImportResultImplFromJson(json);

  @override
  final bool success;
  @override
  @JsonKey(name: 'pathogens_processed')
  final int pathogensProcessed;
  @override
  @JsonKey(name: 'pathogens_created')
  final int pathogensCreated;
  @override
  @JsonKey(name: 'pathogens_updated')
  final int pathogensUpdated;
  @override
  @JsonKey(name: 'associations_processed')
  final int associationsProcessed;
  @override
  @JsonKey(name: 'associations_created')
  final int associationsCreated;
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
    return 'PathogenImportResult(success: $success, pathogensProcessed: $pathogensProcessed, pathogensCreated: $pathogensCreated, pathogensUpdated: $pathogensUpdated, associationsProcessed: $associationsProcessed, associationsCreated: $associationsCreated, errors: $errors, warnings: $warnings)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PathogenImportResultImpl &&
            (identical(other.success, success) || other.success == success) &&
            (identical(other.pathogensProcessed, pathogensProcessed) ||
                other.pathogensProcessed == pathogensProcessed) &&
            (identical(other.pathogensCreated, pathogensCreated) ||
                other.pathogensCreated == pathogensCreated) &&
            (identical(other.pathogensUpdated, pathogensUpdated) ||
                other.pathogensUpdated == pathogensUpdated) &&
            (identical(other.associationsProcessed, associationsProcessed) ||
                other.associationsProcessed == associationsProcessed) &&
            (identical(other.associationsCreated, associationsCreated) ||
                other.associationsCreated == associationsCreated) &&
            const DeepCollectionEquality().equals(other._errors, _errors) &&
            const DeepCollectionEquality().equals(other._warnings, _warnings));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      success,
      pathogensProcessed,
      pathogensCreated,
      pathogensUpdated,
      associationsProcessed,
      associationsCreated,
      const DeepCollectionEquality().hash(_errors),
      const DeepCollectionEquality().hash(_warnings));

  /// Create a copy of PathogenImportResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PathogenImportResultImplCopyWith<_$PathogenImportResultImpl>
      get copyWith =>
          __$$PathogenImportResultImplCopyWithImpl<_$PathogenImportResultImpl>(
              this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PathogenImportResultImplToJson(
      this,
    );
  }
}

abstract class _PathogenImportResult implements PathogenImportResult {
  const factory _PathogenImportResult(
      {required final bool success,
      @JsonKey(name: 'pathogens_processed')
      required final int pathogensProcessed,
      @JsonKey(name: 'pathogens_created') required final int pathogensCreated,
      @JsonKey(name: 'pathogens_updated') required final int pathogensUpdated,
      @JsonKey(name: 'associations_processed')
      required final int associationsProcessed,
      @JsonKey(name: 'associations_created')
      required final int associationsCreated,
      required final List<String> errors,
      required final List<String> warnings}) = _$PathogenImportResultImpl;

  factory _PathogenImportResult.fromJson(Map<String, dynamic> json) =
      _$PathogenImportResultImpl.fromJson;

  @override
  bool get success;
  @override
  @JsonKey(name: 'pathogens_processed')
  int get pathogensProcessed;
  @override
  @JsonKey(name: 'pathogens_created')
  int get pathogensCreated;
  @override
  @JsonKey(name: 'pathogens_updated')
  int get pathogensUpdated;
  @override
  @JsonKey(name: 'associations_processed')
  int get associationsProcessed;
  @override
  @JsonKey(name: 'associations_created')
  int get associationsCreated;
  @override
  List<String> get errors;
  @override
  List<String> get warnings;

  /// Create a copy of PathogenImportResult
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PathogenImportResultImplCopyWith<_$PathogenImportResultImpl>
      get copyWith => throw _privateConstructorUsedError;
}

PathogenProperties _$PathogenPropertiesFromJson(Map<String, dynamic> json) {
  return _PathogenProperties.fromJson(json);
}

/// @nodoc
mixin _$PathogenProperties {
  String? get classification => throw _privateConstructorUsedError;
  String? get nt => throw _privateConstructorUsedError;
  @JsonKey(name: 'pathogen_id')
  String? get pathogenId => throw _privateConstructorUsedError;
  @JsonKey(name: 'pathogen_name')
  String get pathogenName => throw _privateConstructorUsedError;
  String? get vaccine => throw _privateConstructorUsedError;
  String? get toxin => throw _privateConstructorUsedError;
  String? get transmission => throw _privateConstructorUsedError;
  @JsonKey(name: 'ab_resistance')
  String? get abResistance => throw _privateConstructorUsedError;
  String? get host => throw _privateConstructorUsedError;
  String? get commensal => throw _privateConstructorUsedError;
  String? get disease => throw _privateConstructorUsedError;
  String? get incubation => throw _privateConstructorUsedError;
  String? get diagnosis => throw _privateConstructorUsedError;
  String? get treatment => throw _privateConstructorUsedError;
  String? get prevention => throw _privateConstructorUsedError;
  String? get notes => throw _privateConstructorUsedError;

  /// Serializes this PathogenProperties to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PathogenProperties
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PathogenPropertiesCopyWith<PathogenProperties> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PathogenPropertiesCopyWith<$Res> {
  factory $PathogenPropertiesCopyWith(
          PathogenProperties value, $Res Function(PathogenProperties) then) =
      _$PathogenPropertiesCopyWithImpl<$Res, PathogenProperties>;
  @useResult
  $Res call(
      {String? classification,
      String? nt,
      @JsonKey(name: 'pathogen_id') String? pathogenId,
      @JsonKey(name: 'pathogen_name') String pathogenName,
      String? vaccine,
      String? toxin,
      String? transmission,
      @JsonKey(name: 'ab_resistance') String? abResistance,
      String? host,
      String? commensal,
      String? disease,
      String? incubation,
      String? diagnosis,
      String? treatment,
      String? prevention,
      String? notes});
}

/// @nodoc
class _$PathogenPropertiesCopyWithImpl<$Res, $Val extends PathogenProperties>
    implements $PathogenPropertiesCopyWith<$Res> {
  _$PathogenPropertiesCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PathogenProperties
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? classification = freezed,
    Object? nt = freezed,
    Object? pathogenId = freezed,
    Object? pathogenName = null,
    Object? vaccine = freezed,
    Object? toxin = freezed,
    Object? transmission = freezed,
    Object? abResistance = freezed,
    Object? host = freezed,
    Object? commensal = freezed,
    Object? disease = freezed,
    Object? incubation = freezed,
    Object? diagnosis = freezed,
    Object? treatment = freezed,
    Object? prevention = freezed,
    Object? notes = freezed,
  }) {
    return _then(_value.copyWith(
      classification: freezed == classification
          ? _value.classification
          : classification // ignore: cast_nullable_to_non_nullable
              as String?,
      nt: freezed == nt
          ? _value.nt
          : nt // ignore: cast_nullable_to_non_nullable
              as String?,
      pathogenId: freezed == pathogenId
          ? _value.pathogenId
          : pathogenId // ignore: cast_nullable_to_non_nullable
              as String?,
      pathogenName: null == pathogenName
          ? _value.pathogenName
          : pathogenName // ignore: cast_nullable_to_non_nullable
              as String,
      vaccine: freezed == vaccine
          ? _value.vaccine
          : vaccine // ignore: cast_nullable_to_non_nullable
              as String?,
      toxin: freezed == toxin
          ? _value.toxin
          : toxin // ignore: cast_nullable_to_non_nullable
              as String?,
      transmission: freezed == transmission
          ? _value.transmission
          : transmission // ignore: cast_nullable_to_non_nullable
              as String?,
      abResistance: freezed == abResistance
          ? _value.abResistance
          : abResistance // ignore: cast_nullable_to_non_nullable
              as String?,
      host: freezed == host
          ? _value.host
          : host // ignore: cast_nullable_to_non_nullable
              as String?,
      commensal: freezed == commensal
          ? _value.commensal
          : commensal // ignore: cast_nullable_to_non_nullable
              as String?,
      disease: freezed == disease
          ? _value.disease
          : disease // ignore: cast_nullable_to_non_nullable
              as String?,
      incubation: freezed == incubation
          ? _value.incubation
          : incubation // ignore: cast_nullable_to_non_nullable
              as String?,
      diagnosis: freezed == diagnosis
          ? _value.diagnosis
          : diagnosis // ignore: cast_nullable_to_non_nullable
              as String?,
      treatment: freezed == treatment
          ? _value.treatment
          : treatment // ignore: cast_nullable_to_non_nullable
              as String?,
      prevention: freezed == prevention
          ? _value.prevention
          : prevention // ignore: cast_nullable_to_non_nullable
              as String?,
      notes: freezed == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$PathogenPropertiesImplCopyWith<$Res>
    implements $PathogenPropertiesCopyWith<$Res> {
  factory _$$PathogenPropertiesImplCopyWith(_$PathogenPropertiesImpl value,
          $Res Function(_$PathogenPropertiesImpl) then) =
      __$$PathogenPropertiesImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String? classification,
      String? nt,
      @JsonKey(name: 'pathogen_id') String? pathogenId,
      @JsonKey(name: 'pathogen_name') String pathogenName,
      String? vaccine,
      String? toxin,
      String? transmission,
      @JsonKey(name: 'ab_resistance') String? abResistance,
      String? host,
      String? commensal,
      String? disease,
      String? incubation,
      String? diagnosis,
      String? treatment,
      String? prevention,
      String? notes});
}

/// @nodoc
class __$$PathogenPropertiesImplCopyWithImpl<$Res>
    extends _$PathogenPropertiesCopyWithImpl<$Res, _$PathogenPropertiesImpl>
    implements _$$PathogenPropertiesImplCopyWith<$Res> {
  __$$PathogenPropertiesImplCopyWithImpl(_$PathogenPropertiesImpl _value,
      $Res Function(_$PathogenPropertiesImpl) _then)
      : super(_value, _then);

  /// Create a copy of PathogenProperties
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? classification = freezed,
    Object? nt = freezed,
    Object? pathogenId = freezed,
    Object? pathogenName = null,
    Object? vaccine = freezed,
    Object? toxin = freezed,
    Object? transmission = freezed,
    Object? abResistance = freezed,
    Object? host = freezed,
    Object? commensal = freezed,
    Object? disease = freezed,
    Object? incubation = freezed,
    Object? diagnosis = freezed,
    Object? treatment = freezed,
    Object? prevention = freezed,
    Object? notes = freezed,
  }) {
    return _then(_$PathogenPropertiesImpl(
      classification: freezed == classification
          ? _value.classification
          : classification // ignore: cast_nullable_to_non_nullable
              as String?,
      nt: freezed == nt
          ? _value.nt
          : nt // ignore: cast_nullable_to_non_nullable
              as String?,
      pathogenId: freezed == pathogenId
          ? _value.pathogenId
          : pathogenId // ignore: cast_nullable_to_non_nullable
              as String?,
      pathogenName: null == pathogenName
          ? _value.pathogenName
          : pathogenName // ignore: cast_nullable_to_non_nullable
              as String,
      vaccine: freezed == vaccine
          ? _value.vaccine
          : vaccine // ignore: cast_nullable_to_non_nullable
              as String?,
      toxin: freezed == toxin
          ? _value.toxin
          : toxin // ignore: cast_nullable_to_non_nullable
              as String?,
      transmission: freezed == transmission
          ? _value.transmission
          : transmission // ignore: cast_nullable_to_non_nullable
              as String?,
      abResistance: freezed == abResistance
          ? _value.abResistance
          : abResistance // ignore: cast_nullable_to_non_nullable
              as String?,
      host: freezed == host
          ? _value.host
          : host // ignore: cast_nullable_to_non_nullable
              as String?,
      commensal: freezed == commensal
          ? _value.commensal
          : commensal // ignore: cast_nullable_to_non_nullable
              as String?,
      disease: freezed == disease
          ? _value.disease
          : disease // ignore: cast_nullable_to_non_nullable
              as String?,
      incubation: freezed == incubation
          ? _value.incubation
          : incubation // ignore: cast_nullable_to_non_nullable
              as String?,
      diagnosis: freezed == diagnosis
          ? _value.diagnosis
          : diagnosis // ignore: cast_nullable_to_non_nullable
              as String?,
      treatment: freezed == treatment
          ? _value.treatment
          : treatment // ignore: cast_nullable_to_non_nullable
              as String?,
      prevention: freezed == prevention
          ? _value.prevention
          : prevention // ignore: cast_nullable_to_non_nullable
              as String?,
      notes: freezed == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$PathogenPropertiesImpl implements _PathogenProperties {
  const _$PathogenPropertiesImpl(
      {this.classification,
      this.nt,
      @JsonKey(name: 'pathogen_id') this.pathogenId,
      @JsonKey(name: 'pathogen_name') required this.pathogenName,
      this.vaccine,
      this.toxin,
      this.transmission,
      @JsonKey(name: 'ab_resistance') this.abResistance,
      this.host,
      this.commensal,
      this.disease,
      this.incubation,
      this.diagnosis,
      this.treatment,
      this.prevention,
      this.notes});

  factory _$PathogenPropertiesImpl.fromJson(Map<String, dynamic> json) =>
      _$$PathogenPropertiesImplFromJson(json);

  @override
  final String? classification;
  @override
  final String? nt;
  @override
  @JsonKey(name: 'pathogen_id')
  final String? pathogenId;
  @override
  @JsonKey(name: 'pathogen_name')
  final String pathogenName;
  @override
  final String? vaccine;
  @override
  final String? toxin;
  @override
  final String? transmission;
  @override
  @JsonKey(name: 'ab_resistance')
  final String? abResistance;
  @override
  final String? host;
  @override
  final String? commensal;
  @override
  final String? disease;
  @override
  final String? incubation;
  @override
  final String? diagnosis;
  @override
  final String? treatment;
  @override
  final String? prevention;
  @override
  final String? notes;

  @override
  String toString() {
    return 'PathogenProperties(classification: $classification, nt: $nt, pathogenId: $pathogenId, pathogenName: $pathogenName, vaccine: $vaccine, toxin: $toxin, transmission: $transmission, abResistance: $abResistance, host: $host, commensal: $commensal, disease: $disease, incubation: $incubation, diagnosis: $diagnosis, treatment: $treatment, prevention: $prevention, notes: $notes)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PathogenPropertiesImpl &&
            (identical(other.classification, classification) ||
                other.classification == classification) &&
            (identical(other.nt, nt) || other.nt == nt) &&
            (identical(other.pathogenId, pathogenId) ||
                other.pathogenId == pathogenId) &&
            (identical(other.pathogenName, pathogenName) ||
                other.pathogenName == pathogenName) &&
            (identical(other.vaccine, vaccine) || other.vaccine == vaccine) &&
            (identical(other.toxin, toxin) || other.toxin == toxin) &&
            (identical(other.transmission, transmission) ||
                other.transmission == transmission) &&
            (identical(other.abResistance, abResistance) ||
                other.abResistance == abResistance) &&
            (identical(other.host, host) || other.host == host) &&
            (identical(other.commensal, commensal) ||
                other.commensal == commensal) &&
            (identical(other.disease, disease) || other.disease == disease) &&
            (identical(other.incubation, incubation) ||
                other.incubation == incubation) &&
            (identical(other.diagnosis, diagnosis) ||
                other.diagnosis == diagnosis) &&
            (identical(other.treatment, treatment) ||
                other.treatment == treatment) &&
            (identical(other.prevention, prevention) ||
                other.prevention == prevention) &&
            (identical(other.notes, notes) || other.notes == notes));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      classification,
      nt,
      pathogenId,
      pathogenName,
      vaccine,
      toxin,
      transmission,
      abResistance,
      host,
      commensal,
      disease,
      incubation,
      diagnosis,
      treatment,
      prevention,
      notes);

  /// Create a copy of PathogenProperties
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PathogenPropertiesImplCopyWith<_$PathogenPropertiesImpl> get copyWith =>
      __$$PathogenPropertiesImplCopyWithImpl<_$PathogenPropertiesImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PathogenPropertiesImplToJson(
      this,
    );
  }
}

abstract class _PathogenProperties implements PathogenProperties {
  const factory _PathogenProperties(
      {final String? classification,
      final String? nt,
      @JsonKey(name: 'pathogen_id') final String? pathogenId,
      @JsonKey(name: 'pathogen_name') required final String pathogenName,
      final String? vaccine,
      final String? toxin,
      final String? transmission,
      @JsonKey(name: 'ab_resistance') final String? abResistance,
      final String? host,
      final String? commensal,
      final String? disease,
      final String? incubation,
      final String? diagnosis,
      final String? treatment,
      final String? prevention,
      final String? notes}) = _$PathogenPropertiesImpl;

  factory _PathogenProperties.fromJson(Map<String, dynamic> json) =
      _$PathogenPropertiesImpl.fromJson;

  @override
  String? get classification;
  @override
  String? get nt;
  @override
  @JsonKey(name: 'pathogen_id')
  String? get pathogenId;
  @override
  @JsonKey(name: 'pathogen_name')
  String get pathogenName;
  @override
  String? get vaccine;
  @override
  String? get toxin;
  @override
  String? get transmission;
  @override
  @JsonKey(name: 'ab_resistance')
  String? get abResistance;
  @override
  String? get host;
  @override
  String? get commensal;
  @override
  String? get disease;
  @override
  String? get incubation;
  @override
  String? get diagnosis;
  @override
  String? get treatment;
  @override
  String? get prevention;
  @override
  String? get notes;

  /// Create a copy of PathogenProperties
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PathogenPropertiesImplCopyWith<_$PathogenPropertiesImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
