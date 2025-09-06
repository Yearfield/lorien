// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'vm_builder_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

VitalMeasurementDraft _$VitalMeasurementDraftFromJson(
    Map<String, dynamic> json) {
  return _VitalMeasurementDraft.fromJson(json);
}

/// @nodoc
mixin _$VitalMeasurementDraft {
  String get label => throw _privateConstructorUsedError;
  List<NodeDraft>? get nodes => throw _privateConstructorUsedError;
  bool? get isTemplate => throw _privateConstructorUsedError;

  /// Serializes this VitalMeasurementDraft to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of VitalMeasurementDraft
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $VitalMeasurementDraftCopyWith<VitalMeasurementDraft> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $VitalMeasurementDraftCopyWith<$Res> {
  factory $VitalMeasurementDraftCopyWith(VitalMeasurementDraft value,
          $Res Function(VitalMeasurementDraft) then) =
      _$VitalMeasurementDraftCopyWithImpl<$Res, VitalMeasurementDraft>;
  @useResult
  $Res call({String label, List<NodeDraft>? nodes, bool? isTemplate});
}

/// @nodoc
class _$VitalMeasurementDraftCopyWithImpl<$Res,
        $Val extends VitalMeasurementDraft>
    implements $VitalMeasurementDraftCopyWith<$Res> {
  _$VitalMeasurementDraftCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of VitalMeasurementDraft
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? label = null,
    Object? nodes = freezed,
    Object? isTemplate = freezed,
  }) {
    return _then(_value.copyWith(
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      nodes: freezed == nodes
          ? _value.nodes
          : nodes // ignore: cast_nullable_to_non_nullable
              as List<NodeDraft>?,
      isTemplate: freezed == isTemplate
          ? _value.isTemplate
          : isTemplate // ignore: cast_nullable_to_non_nullable
              as bool?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$VitalMeasurementDraftImplCopyWith<$Res>
    implements $VitalMeasurementDraftCopyWith<$Res> {
  factory _$$VitalMeasurementDraftImplCopyWith(
          _$VitalMeasurementDraftImpl value,
          $Res Function(_$VitalMeasurementDraftImpl) then) =
      __$$VitalMeasurementDraftImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String label, List<NodeDraft>? nodes, bool? isTemplate});
}

/// @nodoc
class __$$VitalMeasurementDraftImplCopyWithImpl<$Res>
    extends _$VitalMeasurementDraftCopyWithImpl<$Res,
        _$VitalMeasurementDraftImpl>
    implements _$$VitalMeasurementDraftImplCopyWith<$Res> {
  __$$VitalMeasurementDraftImplCopyWithImpl(_$VitalMeasurementDraftImpl _value,
      $Res Function(_$VitalMeasurementDraftImpl) _then)
      : super(_value, _then);

  /// Create a copy of VitalMeasurementDraft
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? label = null,
    Object? nodes = freezed,
    Object? isTemplate = freezed,
  }) {
    return _then(_$VitalMeasurementDraftImpl(
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      nodes: freezed == nodes
          ? _value._nodes
          : nodes // ignore: cast_nullable_to_non_nullable
              as List<NodeDraft>?,
      isTemplate: freezed == isTemplate
          ? _value.isTemplate
          : isTemplate // ignore: cast_nullable_to_non_nullable
              as bool?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$VitalMeasurementDraftImpl implements _VitalMeasurementDraft {
  const _$VitalMeasurementDraftImpl(
      {required this.label, final List<NodeDraft>? nodes, this.isTemplate})
      : _nodes = nodes;

  factory _$VitalMeasurementDraftImpl.fromJson(Map<String, dynamic> json) =>
      _$$VitalMeasurementDraftImplFromJson(json);

  @override
  final String label;
  final List<NodeDraft>? _nodes;
  @override
  List<NodeDraft>? get nodes {
    final value = _nodes;
    if (value == null) return null;
    if (_nodes is EqualUnmodifiableListView) return _nodes;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  @override
  final bool? isTemplate;

  @override
  String toString() {
    return 'VitalMeasurementDraft(label: $label, nodes: $nodes, isTemplate: $isTemplate)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$VitalMeasurementDraftImpl &&
            (identical(other.label, label) || other.label == label) &&
            const DeepCollectionEquality().equals(other._nodes, _nodes) &&
            (identical(other.isTemplate, isTemplate) ||
                other.isTemplate == isTemplate));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, label,
      const DeepCollectionEquality().hash(_nodes), isTemplate);

  /// Create a copy of VitalMeasurementDraft
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$VitalMeasurementDraftImplCopyWith<_$VitalMeasurementDraftImpl>
      get copyWith => __$$VitalMeasurementDraftImplCopyWithImpl<
          _$VitalMeasurementDraftImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$VitalMeasurementDraftImplToJson(
      this,
    );
  }
}

abstract class _VitalMeasurementDraft implements VitalMeasurementDraft {
  const factory _VitalMeasurementDraft(
      {required final String label,
      final List<NodeDraft>? nodes,
      final bool? isTemplate}) = _$VitalMeasurementDraftImpl;

  factory _VitalMeasurementDraft.fromJson(Map<String, dynamic> json) =
      _$VitalMeasurementDraftImpl.fromJson;

  @override
  String get label;
  @override
  List<NodeDraft>? get nodes;
  @override
  bool? get isTemplate;

  /// Create a copy of VitalMeasurementDraft
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$VitalMeasurementDraftImplCopyWith<_$VitalMeasurementDraftImpl>
      get copyWith => throw _privateConstructorUsedError;
}

NodeDraft _$NodeDraftFromJson(Map<String, dynamic> json) {
  return _NodeDraft.fromJson(json);
}

/// @nodoc
mixin _$NodeDraft {
  int get depth => throw _privateConstructorUsedError;
  int get slot => throw _privateConstructorUsedError;
  String get label => throw _privateConstructorUsedError;
  List<NodeDraft>? get children => throw _privateConstructorUsedError;

  /// Serializes this NodeDraft to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of NodeDraft
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $NodeDraftCopyWith<NodeDraft> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $NodeDraftCopyWith<$Res> {
  factory $NodeDraftCopyWith(NodeDraft value, $Res Function(NodeDraft) then) =
      _$NodeDraftCopyWithImpl<$Res, NodeDraft>;
  @useResult
  $Res call({int depth, int slot, String label, List<NodeDraft>? children});
}

/// @nodoc
class _$NodeDraftCopyWithImpl<$Res, $Val extends NodeDraft>
    implements $NodeDraftCopyWith<$Res> {
  _$NodeDraftCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of NodeDraft
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? depth = null,
    Object? slot = null,
    Object? label = null,
    Object? children = freezed,
  }) {
    return _then(_value.copyWith(
      depth: null == depth
          ? _value.depth
          : depth // ignore: cast_nullable_to_non_nullable
              as int,
      slot: null == slot
          ? _value.slot
          : slot // ignore: cast_nullable_to_non_nullable
              as int,
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      children: freezed == children
          ? _value.children
          : children // ignore: cast_nullable_to_non_nullable
              as List<NodeDraft>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$NodeDraftImplCopyWith<$Res>
    implements $NodeDraftCopyWith<$Res> {
  factory _$$NodeDraftImplCopyWith(
          _$NodeDraftImpl value, $Res Function(_$NodeDraftImpl) then) =
      __$$NodeDraftImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({int depth, int slot, String label, List<NodeDraft>? children});
}

/// @nodoc
class __$$NodeDraftImplCopyWithImpl<$Res>
    extends _$NodeDraftCopyWithImpl<$Res, _$NodeDraftImpl>
    implements _$$NodeDraftImplCopyWith<$Res> {
  __$$NodeDraftImplCopyWithImpl(
      _$NodeDraftImpl _value, $Res Function(_$NodeDraftImpl) _then)
      : super(_value, _then);

  /// Create a copy of NodeDraft
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? depth = null,
    Object? slot = null,
    Object? label = null,
    Object? children = freezed,
  }) {
    return _then(_$NodeDraftImpl(
      depth: null == depth
          ? _value.depth
          : depth // ignore: cast_nullable_to_non_nullable
              as int,
      slot: null == slot
          ? _value.slot
          : slot // ignore: cast_nullable_to_non_nullable
              as int,
      label: null == label
          ? _value.label
          : label // ignore: cast_nullable_to_non_nullable
              as String,
      children: freezed == children
          ? _value._children
          : children // ignore: cast_nullable_to_non_nullable
              as List<NodeDraft>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$NodeDraftImpl implements _NodeDraft {
  const _$NodeDraftImpl(
      {required this.depth,
      required this.slot,
      required this.label,
      final List<NodeDraft>? children})
      : _children = children;

  factory _$NodeDraftImpl.fromJson(Map<String, dynamic> json) =>
      _$$NodeDraftImplFromJson(json);

  @override
  final int depth;
  @override
  final int slot;
  @override
  final String label;
  final List<NodeDraft>? _children;
  @override
  List<NodeDraft>? get children {
    final value = _children;
    if (value == null) return null;
    if (_children is EqualUnmodifiableListView) return _children;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  @override
  String toString() {
    return 'NodeDraft(depth: $depth, slot: $slot, label: $label, children: $children)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$NodeDraftImpl &&
            (identical(other.depth, depth) || other.depth == depth) &&
            (identical(other.slot, slot) || other.slot == slot) &&
            (identical(other.label, label) || other.label == label) &&
            const DeepCollectionEquality().equals(other._children, _children));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, depth, slot, label,
      const DeepCollectionEquality().hash(_children));

  /// Create a copy of NodeDraft
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$NodeDraftImplCopyWith<_$NodeDraftImpl> get copyWith =>
      __$$NodeDraftImplCopyWithImpl<_$NodeDraftImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$NodeDraftImplToJson(
      this,
    );
  }
}

abstract class _NodeDraft implements NodeDraft {
  const factory _NodeDraft(
      {required final int depth,
      required final int slot,
      required final String label,
      final List<NodeDraft>? children}) = _$NodeDraftImpl;

  factory _NodeDraft.fromJson(Map<String, dynamic> json) =
      _$NodeDraftImpl.fromJson;

  @override
  int get depth;
  @override
  int get slot;
  @override
  String get label;
  @override
  List<NodeDraft>? get children;

  /// Create a copy of NodeDraft
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$NodeDraftImplCopyWith<_$NodeDraftImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

SheetDraft _$SheetDraftFromJson(Map<String, dynamic> json) {
  return _SheetDraft.fromJson(json);
}

/// @nodoc
mixin _$SheetDraft {
  String get name => throw _privateConstructorUsedError;
  List<VitalMeasurementDraft> get vitalMeasurements =>
      throw _privateConstructorUsedError;
  Map<String, dynamic>? get metadata => throw _privateConstructorUsedError;

  /// Serializes this SheetDraft to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SheetDraft
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SheetDraftCopyWith<SheetDraft> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SheetDraftCopyWith<$Res> {
  factory $SheetDraftCopyWith(
          SheetDraft value, $Res Function(SheetDraft) then) =
      _$SheetDraftCopyWithImpl<$Res, SheetDraft>;
  @useResult
  $Res call(
      {String name,
      List<VitalMeasurementDraft> vitalMeasurements,
      Map<String, dynamic>? metadata});
}

/// @nodoc
class _$SheetDraftCopyWithImpl<$Res, $Val extends SheetDraft>
    implements $SheetDraftCopyWith<$Res> {
  _$SheetDraftCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SheetDraft
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? vitalMeasurements = null,
    Object? metadata = freezed,
  }) {
    return _then(_value.copyWith(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      vitalMeasurements: null == vitalMeasurements
          ? _value.vitalMeasurements
          : vitalMeasurements // ignore: cast_nullable_to_non_nullable
              as List<VitalMeasurementDraft>,
      metadata: freezed == metadata
          ? _value.metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SheetDraftImplCopyWith<$Res>
    implements $SheetDraftCopyWith<$Res> {
  factory _$$SheetDraftImplCopyWith(
          _$SheetDraftImpl value, $Res Function(_$SheetDraftImpl) then) =
      __$$SheetDraftImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String name,
      List<VitalMeasurementDraft> vitalMeasurements,
      Map<String, dynamic>? metadata});
}

/// @nodoc
class __$$SheetDraftImplCopyWithImpl<$Res>
    extends _$SheetDraftCopyWithImpl<$Res, _$SheetDraftImpl>
    implements _$$SheetDraftImplCopyWith<$Res> {
  __$$SheetDraftImplCopyWithImpl(
      _$SheetDraftImpl _value, $Res Function(_$SheetDraftImpl) _then)
      : super(_value, _then);

  /// Create a copy of SheetDraft
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? name = null,
    Object? vitalMeasurements = null,
    Object? metadata = freezed,
  }) {
    return _then(_$SheetDraftImpl(
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      vitalMeasurements: null == vitalMeasurements
          ? _value._vitalMeasurements
          : vitalMeasurements // ignore: cast_nullable_to_non_nullable
              as List<VitalMeasurementDraft>,
      metadata: freezed == metadata
          ? _value._metadata
          : metadata // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SheetDraftImpl implements _SheetDraft {
  const _$SheetDraftImpl(
      {required this.name,
      required final List<VitalMeasurementDraft> vitalMeasurements,
      final Map<String, dynamic>? metadata})
      : _vitalMeasurements = vitalMeasurements,
        _metadata = metadata;

  factory _$SheetDraftImpl.fromJson(Map<String, dynamic> json) =>
      _$$SheetDraftImplFromJson(json);

  @override
  final String name;
  final List<VitalMeasurementDraft> _vitalMeasurements;
  @override
  List<VitalMeasurementDraft> get vitalMeasurements {
    if (_vitalMeasurements is EqualUnmodifiableListView)
      return _vitalMeasurements;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_vitalMeasurements);
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
    return 'SheetDraft(name: $name, vitalMeasurements: $vitalMeasurements, metadata: $metadata)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SheetDraftImpl &&
            (identical(other.name, name) || other.name == name) &&
            const DeepCollectionEquality()
                .equals(other._vitalMeasurements, _vitalMeasurements) &&
            const DeepCollectionEquality().equals(other._metadata, _metadata));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      name,
      const DeepCollectionEquality().hash(_vitalMeasurements),
      const DeepCollectionEquality().hash(_metadata));

  /// Create a copy of SheetDraft
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SheetDraftImplCopyWith<_$SheetDraftImpl> get copyWith =>
      __$$SheetDraftImplCopyWithImpl<_$SheetDraftImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SheetDraftImplToJson(
      this,
    );
  }
}

abstract class _SheetDraft implements SheetDraft {
  const factory _SheetDraft(
      {required final String name,
      required final List<VitalMeasurementDraft> vitalMeasurements,
      final Map<String, dynamic>? metadata}) = _$SheetDraftImpl;

  factory _SheetDraft.fromJson(Map<String, dynamic> json) =
      _$SheetDraftImpl.fromJson;

  @override
  String get name;
  @override
  List<VitalMeasurementDraft> get vitalMeasurements;
  @override
  Map<String, dynamic>? get metadata;

  /// Create a copy of SheetDraft
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SheetDraftImplCopyWith<_$SheetDraftImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ValidationResult _$ValidationResultFromJson(Map<String, dynamic> json) {
  return _ValidationResult.fromJson(json);
}

/// @nodoc
mixin _$ValidationResult {
  bool get isValid => throw _privateConstructorUsedError;
  List<String>? get errors => throw _privateConstructorUsedError;
  List<String>? get warnings => throw _privateConstructorUsedError;
  Map<String, dynamic>? get suggestions => throw _privateConstructorUsedError;

  /// Serializes this ValidationResult to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ValidationResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ValidationResultCopyWith<ValidationResult> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ValidationResultCopyWith<$Res> {
  factory $ValidationResultCopyWith(
          ValidationResult value, $Res Function(ValidationResult) then) =
      _$ValidationResultCopyWithImpl<$Res, ValidationResult>;
  @useResult
  $Res call(
      {bool isValid,
      List<String>? errors,
      List<String>? warnings,
      Map<String, dynamic>? suggestions});
}

/// @nodoc
class _$ValidationResultCopyWithImpl<$Res, $Val extends ValidationResult>
    implements $ValidationResultCopyWith<$Res> {
  _$ValidationResultCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ValidationResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? isValid = null,
    Object? errors = freezed,
    Object? warnings = freezed,
    Object? suggestions = freezed,
  }) {
    return _then(_value.copyWith(
      isValid: null == isValid
          ? _value.isValid
          : isValid // ignore: cast_nullable_to_non_nullable
              as bool,
      errors: freezed == errors
          ? _value.errors
          : errors // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      warnings: freezed == warnings
          ? _value.warnings
          : warnings // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      suggestions: freezed == suggestions
          ? _value.suggestions
          : suggestions // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ValidationResultImplCopyWith<$Res>
    implements $ValidationResultCopyWith<$Res> {
  factory _$$ValidationResultImplCopyWith(_$ValidationResultImpl value,
          $Res Function(_$ValidationResultImpl) then) =
      __$$ValidationResultImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool isValid,
      List<String>? errors,
      List<String>? warnings,
      Map<String, dynamic>? suggestions});
}

/// @nodoc
class __$$ValidationResultImplCopyWithImpl<$Res>
    extends _$ValidationResultCopyWithImpl<$Res, _$ValidationResultImpl>
    implements _$$ValidationResultImplCopyWith<$Res> {
  __$$ValidationResultImplCopyWithImpl(_$ValidationResultImpl _value,
      $Res Function(_$ValidationResultImpl) _then)
      : super(_value, _then);

  /// Create a copy of ValidationResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? isValid = null,
    Object? errors = freezed,
    Object? warnings = freezed,
    Object? suggestions = freezed,
  }) {
    return _then(_$ValidationResultImpl(
      isValid: null == isValid
          ? _value.isValid
          : isValid // ignore: cast_nullable_to_non_nullable
              as bool,
      errors: freezed == errors
          ? _value._errors
          : errors // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      warnings: freezed == warnings
          ? _value._warnings
          : warnings // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      suggestions: freezed == suggestions
          ? _value._suggestions
          : suggestions // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ValidationResultImpl implements _ValidationResult {
  const _$ValidationResultImpl(
      {required this.isValid,
      final List<String>? errors,
      final List<String>? warnings,
      final Map<String, dynamic>? suggestions})
      : _errors = errors,
        _warnings = warnings,
        _suggestions = suggestions;

  factory _$ValidationResultImpl.fromJson(Map<String, dynamic> json) =>
      _$$ValidationResultImplFromJson(json);

  @override
  final bool isValid;
  final List<String>? _errors;
  @override
  List<String>? get errors {
    final value = _errors;
    if (value == null) return null;
    if (_errors is EqualUnmodifiableListView) return _errors;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  final List<String>? _warnings;
  @override
  List<String>? get warnings {
    final value = _warnings;
    if (value == null) return null;
    if (_warnings is EqualUnmodifiableListView) return _warnings;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  final Map<String, dynamic>? _suggestions;
  @override
  Map<String, dynamic>? get suggestions {
    final value = _suggestions;
    if (value == null) return null;
    if (_suggestions is EqualUnmodifiableMapView) return _suggestions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'ValidationResult(isValid: $isValid, errors: $errors, warnings: $warnings, suggestions: $suggestions)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ValidationResultImpl &&
            (identical(other.isValid, isValid) || other.isValid == isValid) &&
            const DeepCollectionEquality().equals(other._errors, _errors) &&
            const DeepCollectionEquality().equals(other._warnings, _warnings) &&
            const DeepCollectionEquality()
                .equals(other._suggestions, _suggestions));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      isValid,
      const DeepCollectionEquality().hash(_errors),
      const DeepCollectionEquality().hash(_warnings),
      const DeepCollectionEquality().hash(_suggestions));

  /// Create a copy of ValidationResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ValidationResultImplCopyWith<_$ValidationResultImpl> get copyWith =>
      __$$ValidationResultImplCopyWithImpl<_$ValidationResultImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ValidationResultImplToJson(
      this,
    );
  }
}

abstract class _ValidationResult implements ValidationResult {
  const factory _ValidationResult(
      {required final bool isValid,
      final List<String>? errors,
      final List<String>? warnings,
      final Map<String, dynamic>? suggestions}) = _$ValidationResultImpl;

  factory _ValidationResult.fromJson(Map<String, dynamic> json) =
      _$ValidationResultImpl.fromJson;

  @override
  bool get isValid;
  @override
  List<String>? get errors;
  @override
  List<String>? get warnings;
  @override
  Map<String, dynamic>? get suggestions;

  /// Create a copy of ValidationResult
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ValidationResultImplCopyWith<_$ValidationResultImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CreationResult _$CreationResultFromJson(Map<String, dynamic> json) {
  return _CreationResult.fromJson(json);
}

/// @nodoc
mixin _$CreationResult {
  bool get success => throw _privateConstructorUsedError;
  List<int>? get createdVmIds => throw _privateConstructorUsedError;
  List<int>? get createdNodeIds => throw _privateConstructorUsedError;
  MaterializationResult? get materializationResult =>
      throw _privateConstructorUsedError;
  List<String>? get errors => throw _privateConstructorUsedError;

  /// Serializes this CreationResult to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of CreationResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $CreationResultCopyWith<CreationResult> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CreationResultCopyWith<$Res> {
  factory $CreationResultCopyWith(
          CreationResult value, $Res Function(CreationResult) then) =
      _$CreationResultCopyWithImpl<$Res, CreationResult>;
  @useResult
  $Res call(
      {bool success,
      List<int>? createdVmIds,
      List<int>? createdNodeIds,
      MaterializationResult? materializationResult,
      List<String>? errors});

  $MaterializationResultCopyWith<$Res>? get materializationResult;
}

/// @nodoc
class _$CreationResultCopyWithImpl<$Res, $Val extends CreationResult>
    implements $CreationResultCopyWith<$Res> {
  _$CreationResultCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of CreationResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? createdVmIds = freezed,
    Object? createdNodeIds = freezed,
    Object? materializationResult = freezed,
    Object? errors = freezed,
  }) {
    return _then(_value.copyWith(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      createdVmIds: freezed == createdVmIds
          ? _value.createdVmIds
          : createdVmIds // ignore: cast_nullable_to_non_nullable
              as List<int>?,
      createdNodeIds: freezed == createdNodeIds
          ? _value.createdNodeIds
          : createdNodeIds // ignore: cast_nullable_to_non_nullable
              as List<int>?,
      materializationResult: freezed == materializationResult
          ? _value.materializationResult
          : materializationResult // ignore: cast_nullable_to_non_nullable
              as MaterializationResult?,
      errors: freezed == errors
          ? _value.errors
          : errors // ignore: cast_nullable_to_non_nullable
              as List<String>?,
    ) as $Val);
  }

  /// Create a copy of CreationResult
  /// with the given fields replaced by the non-null parameter values.
  @override
  @pragma('vm:prefer-inline')
  $MaterializationResultCopyWith<$Res>? get materializationResult {
    if (_value.materializationResult == null) {
      return null;
    }

    return $MaterializationResultCopyWith<$Res>(_value.materializationResult!,
        (value) {
      return _then(_value.copyWith(materializationResult: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$CreationResultImplCopyWith<$Res>
    implements $CreationResultCopyWith<$Res> {
  factory _$$CreationResultImplCopyWith(_$CreationResultImpl value,
          $Res Function(_$CreationResultImpl) then) =
      __$$CreationResultImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool success,
      List<int>? createdVmIds,
      List<int>? createdNodeIds,
      MaterializationResult? materializationResult,
      List<String>? errors});

  @override
  $MaterializationResultCopyWith<$Res>? get materializationResult;
}

/// @nodoc
class __$$CreationResultImplCopyWithImpl<$Res>
    extends _$CreationResultCopyWithImpl<$Res, _$CreationResultImpl>
    implements _$$CreationResultImplCopyWith<$Res> {
  __$$CreationResultImplCopyWithImpl(
      _$CreationResultImpl _value, $Res Function(_$CreationResultImpl) _then)
      : super(_value, _then);

  /// Create a copy of CreationResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? success = null,
    Object? createdVmIds = freezed,
    Object? createdNodeIds = freezed,
    Object? materializationResult = freezed,
    Object? errors = freezed,
  }) {
    return _then(_$CreationResultImpl(
      success: null == success
          ? _value.success
          : success // ignore: cast_nullable_to_non_nullable
              as bool,
      createdVmIds: freezed == createdVmIds
          ? _value._createdVmIds
          : createdVmIds // ignore: cast_nullable_to_non_nullable
              as List<int>?,
      createdNodeIds: freezed == createdNodeIds
          ? _value._createdNodeIds
          : createdNodeIds // ignore: cast_nullable_to_non_nullable
              as List<int>?,
      materializationResult: freezed == materializationResult
          ? _value.materializationResult
          : materializationResult // ignore: cast_nullable_to_non_nullable
              as MaterializationResult?,
      errors: freezed == errors
          ? _value._errors
          : errors // ignore: cast_nullable_to_non_nullable
              as List<String>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CreationResultImpl implements _CreationResult {
  const _$CreationResultImpl(
      {required this.success,
      final List<int>? createdVmIds,
      final List<int>? createdNodeIds,
      this.materializationResult,
      final List<String>? errors})
      : _createdVmIds = createdVmIds,
        _createdNodeIds = createdNodeIds,
        _errors = errors;

  factory _$CreationResultImpl.fromJson(Map<String, dynamic> json) =>
      _$$CreationResultImplFromJson(json);

  @override
  final bool success;
  final List<int>? _createdVmIds;
  @override
  List<int>? get createdVmIds {
    final value = _createdVmIds;
    if (value == null) return null;
    if (_createdVmIds is EqualUnmodifiableListView) return _createdVmIds;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  final List<int>? _createdNodeIds;
  @override
  List<int>? get createdNodeIds {
    final value = _createdNodeIds;
    if (value == null) return null;
    if (_createdNodeIds is EqualUnmodifiableListView) return _createdNodeIds;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  @override
  final MaterializationResult? materializationResult;
  final List<String>? _errors;
  @override
  List<String>? get errors {
    final value = _errors;
    if (value == null) return null;
    if (_errors is EqualUnmodifiableListView) return _errors;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  @override
  String toString() {
    return 'CreationResult(success: $success, createdVmIds: $createdVmIds, createdNodeIds: $createdNodeIds, materializationResult: $materializationResult, errors: $errors)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CreationResultImpl &&
            (identical(other.success, success) || other.success == success) &&
            const DeepCollectionEquality()
                .equals(other._createdVmIds, _createdVmIds) &&
            const DeepCollectionEquality()
                .equals(other._createdNodeIds, _createdNodeIds) &&
            (identical(other.materializationResult, materializationResult) ||
                other.materializationResult == materializationResult) &&
            const DeepCollectionEquality().equals(other._errors, _errors));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      success,
      const DeepCollectionEquality().hash(_createdVmIds),
      const DeepCollectionEquality().hash(_createdNodeIds),
      materializationResult,
      const DeepCollectionEquality().hash(_errors));

  /// Create a copy of CreationResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$CreationResultImplCopyWith<_$CreationResultImpl> get copyWith =>
      __$$CreationResultImplCopyWithImpl<_$CreationResultImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CreationResultImplToJson(
      this,
    );
  }
}

abstract class _CreationResult implements CreationResult {
  const factory _CreationResult(
      {required final bool success,
      final List<int>? createdVmIds,
      final List<int>? createdNodeIds,
      final MaterializationResult? materializationResult,
      final List<String>? errors}) = _$CreationResultImpl;

  factory _CreationResult.fromJson(Map<String, dynamic> json) =
      _$CreationResultImpl.fromJson;

  @override
  bool get success;
  @override
  List<int>? get createdVmIds;
  @override
  List<int>? get createdNodeIds;
  @override
  MaterializationResult? get materializationResult;
  @override
  List<String>? get errors;

  /// Create a copy of CreationResult
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$CreationResultImplCopyWith<_$CreationResultImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

DuplicateCheckResult _$DuplicateCheckResultFromJson(Map<String, dynamic> json) {
  return _DuplicateCheckResult.fromJson(json);
}

/// @nodoc
mixin _$DuplicateCheckResult {
  bool get hasDuplicates => throw _privateConstructorUsedError;
  List<String>? get duplicateLabels => throw _privateConstructorUsedError;
  Map<String, List<String>>? get conflicts =>
      throw _privateConstructorUsedError;

  /// Serializes this DuplicateCheckResult to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of DuplicateCheckResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DuplicateCheckResultCopyWith<DuplicateCheckResult> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DuplicateCheckResultCopyWith<$Res> {
  factory $DuplicateCheckResultCopyWith(DuplicateCheckResult value,
          $Res Function(DuplicateCheckResult) then) =
      _$DuplicateCheckResultCopyWithImpl<$Res, DuplicateCheckResult>;
  @useResult
  $Res call(
      {bool hasDuplicates,
      List<String>? duplicateLabels,
      Map<String, List<String>>? conflicts});
}

/// @nodoc
class _$DuplicateCheckResultCopyWithImpl<$Res,
        $Val extends DuplicateCheckResult>
    implements $DuplicateCheckResultCopyWith<$Res> {
  _$DuplicateCheckResultCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of DuplicateCheckResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? hasDuplicates = null,
    Object? duplicateLabels = freezed,
    Object? conflicts = freezed,
  }) {
    return _then(_value.copyWith(
      hasDuplicates: null == hasDuplicates
          ? _value.hasDuplicates
          : hasDuplicates // ignore: cast_nullable_to_non_nullable
              as bool,
      duplicateLabels: freezed == duplicateLabels
          ? _value.duplicateLabels
          : duplicateLabels // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      conflicts: freezed == conflicts
          ? _value.conflicts
          : conflicts // ignore: cast_nullable_to_non_nullable
              as Map<String, List<String>>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DuplicateCheckResultImplCopyWith<$Res>
    implements $DuplicateCheckResultCopyWith<$Res> {
  factory _$$DuplicateCheckResultImplCopyWith(_$DuplicateCheckResultImpl value,
          $Res Function(_$DuplicateCheckResultImpl) then) =
      __$$DuplicateCheckResultImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool hasDuplicates,
      List<String>? duplicateLabels,
      Map<String, List<String>>? conflicts});
}

/// @nodoc
class __$$DuplicateCheckResultImplCopyWithImpl<$Res>
    extends _$DuplicateCheckResultCopyWithImpl<$Res, _$DuplicateCheckResultImpl>
    implements _$$DuplicateCheckResultImplCopyWith<$Res> {
  __$$DuplicateCheckResultImplCopyWithImpl(_$DuplicateCheckResultImpl _value,
      $Res Function(_$DuplicateCheckResultImpl) _then)
      : super(_value, _then);

  /// Create a copy of DuplicateCheckResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? hasDuplicates = null,
    Object? duplicateLabels = freezed,
    Object? conflicts = freezed,
  }) {
    return _then(_$DuplicateCheckResultImpl(
      hasDuplicates: null == hasDuplicates
          ? _value.hasDuplicates
          : hasDuplicates // ignore: cast_nullable_to_non_nullable
              as bool,
      duplicateLabels: freezed == duplicateLabels
          ? _value._duplicateLabels
          : duplicateLabels // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      conflicts: freezed == conflicts
          ? _value._conflicts
          : conflicts // ignore: cast_nullable_to_non_nullable
              as Map<String, List<String>>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DuplicateCheckResultImpl implements _DuplicateCheckResult {
  const _$DuplicateCheckResultImpl(
      {required this.hasDuplicates,
      final List<String>? duplicateLabels,
      final Map<String, List<String>>? conflicts})
      : _duplicateLabels = duplicateLabels,
        _conflicts = conflicts;

  factory _$DuplicateCheckResultImpl.fromJson(Map<String, dynamic> json) =>
      _$$DuplicateCheckResultImplFromJson(json);

  @override
  final bool hasDuplicates;
  final List<String>? _duplicateLabels;
  @override
  List<String>? get duplicateLabels {
    final value = _duplicateLabels;
    if (value == null) return null;
    if (_duplicateLabels is EqualUnmodifiableListView) return _duplicateLabels;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  final Map<String, List<String>>? _conflicts;
  @override
  Map<String, List<String>>? get conflicts {
    final value = _conflicts;
    if (value == null) return null;
    if (_conflicts is EqualUnmodifiableMapView) return _conflicts;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'DuplicateCheckResult(hasDuplicates: $hasDuplicates, duplicateLabels: $duplicateLabels, conflicts: $conflicts)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DuplicateCheckResultImpl &&
            (identical(other.hasDuplicates, hasDuplicates) ||
                other.hasDuplicates == hasDuplicates) &&
            const DeepCollectionEquality()
                .equals(other._duplicateLabels, _duplicateLabels) &&
            const DeepCollectionEquality()
                .equals(other._conflicts, _conflicts));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      hasDuplicates,
      const DeepCollectionEquality().hash(_duplicateLabels),
      const DeepCollectionEquality().hash(_conflicts));

  /// Create a copy of DuplicateCheckResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DuplicateCheckResultImplCopyWith<_$DuplicateCheckResultImpl>
      get copyWith =>
          __$$DuplicateCheckResultImplCopyWithImpl<_$DuplicateCheckResultImpl>(
              this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DuplicateCheckResultImplToJson(
      this,
    );
  }
}

abstract class _DuplicateCheckResult implements DuplicateCheckResult {
  const factory _DuplicateCheckResult(
      {required final bool hasDuplicates,
      final List<String>? duplicateLabels,
      final Map<String, List<String>>? conflicts}) = _$DuplicateCheckResultImpl;

  factory _DuplicateCheckResult.fromJson(Map<String, dynamic> json) =
      _$DuplicateCheckResultImpl.fromJson;

  @override
  bool get hasDuplicates;
  @override
  List<String>? get duplicateLabels;
  @override
  Map<String, List<String>>? get conflicts;

  /// Create a copy of DuplicateCheckResult
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DuplicateCheckResultImplCopyWith<_$DuplicateCheckResultImpl>
      get copyWith => throw _privateConstructorUsedError;
}
