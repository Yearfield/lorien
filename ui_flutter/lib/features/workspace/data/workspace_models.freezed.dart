// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'workspace_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

ImportJob _$ImportJobFromJson(Map<String, dynamic> json) {
  return _ImportJob.fromJson(json);
}

/// @nodoc
mixin _$ImportJob {
  String get id => throw _privateConstructorUsedError;
  String get fileName => throw _privateConstructorUsedError;
  String get status => throw _privateConstructorUsedError;
  DateTime get startedAt => throw _privateConstructorUsedError;
  DateTime? get completedAt => throw _privateConstructorUsedError;
  int get totalRows => throw _privateConstructorUsedError;
  int get processedRows => throw _privateConstructorUsedError;
  int get importedRows => throw _privateConstructorUsedError;
  List<String>? get errors => throw _privateConstructorUsedError;
  List<String>? get warnings => throw _privateConstructorUsedError;
  Map<String, dynamic>? get headerMapping => throw _privateConstructorUsedError;
  Map<String, dynamic>? get validationResults =>
      throw _privateConstructorUsedError;

  /// Serializes this ImportJob to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ImportJob
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ImportJobCopyWith<ImportJob> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ImportJobCopyWith<$Res> {
  factory $ImportJobCopyWith(ImportJob value, $Res Function(ImportJob) then) =
      _$ImportJobCopyWithImpl<$Res, ImportJob>;
  @useResult
  $Res call(
      {String id,
      String fileName,
      String status,
      DateTime startedAt,
      DateTime? completedAt,
      int totalRows,
      int processedRows,
      int importedRows,
      List<String>? errors,
      List<String>? warnings,
      Map<String, dynamic>? headerMapping,
      Map<String, dynamic>? validationResults});
}

/// @nodoc
class _$ImportJobCopyWithImpl<$Res, $Val extends ImportJob>
    implements $ImportJobCopyWith<$Res> {
  _$ImportJobCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ImportJob
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? fileName = null,
    Object? status = null,
    Object? startedAt = null,
    Object? completedAt = freezed,
    Object? totalRows = null,
    Object? processedRows = null,
    Object? importedRows = null,
    Object? errors = freezed,
    Object? warnings = freezed,
    Object? headerMapping = freezed,
    Object? validationResults = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      fileName: null == fileName
          ? _value.fileName
          : fileName // ignore: cast_nullable_to_non_nullable
              as String,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      startedAt: null == startedAt
          ? _value.startedAt
          : startedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      completedAt: freezed == completedAt
          ? _value.completedAt
          : completedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      totalRows: null == totalRows
          ? _value.totalRows
          : totalRows // ignore: cast_nullable_to_non_nullable
              as int,
      processedRows: null == processedRows
          ? _value.processedRows
          : processedRows // ignore: cast_nullable_to_non_nullable
              as int,
      importedRows: null == importedRows
          ? _value.importedRows
          : importedRows // ignore: cast_nullable_to_non_nullable
              as int,
      errors: freezed == errors
          ? _value.errors
          : errors // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      warnings: freezed == warnings
          ? _value.warnings
          : warnings // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      headerMapping: freezed == headerMapping
          ? _value.headerMapping
          : headerMapping // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      validationResults: freezed == validationResults
          ? _value.validationResults
          : validationResults // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ImportJobImplCopyWith<$Res>
    implements $ImportJobCopyWith<$Res> {
  factory _$$ImportJobImplCopyWith(
          _$ImportJobImpl value, $Res Function(_$ImportJobImpl) then) =
      __$$ImportJobImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String fileName,
      String status,
      DateTime startedAt,
      DateTime? completedAt,
      int totalRows,
      int processedRows,
      int importedRows,
      List<String>? errors,
      List<String>? warnings,
      Map<String, dynamic>? headerMapping,
      Map<String, dynamic>? validationResults});
}

/// @nodoc
class __$$ImportJobImplCopyWithImpl<$Res>
    extends _$ImportJobCopyWithImpl<$Res, _$ImportJobImpl>
    implements _$$ImportJobImplCopyWith<$Res> {
  __$$ImportJobImplCopyWithImpl(
      _$ImportJobImpl _value, $Res Function(_$ImportJobImpl) _then)
      : super(_value, _then);

  /// Create a copy of ImportJob
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? fileName = null,
    Object? status = null,
    Object? startedAt = null,
    Object? completedAt = freezed,
    Object? totalRows = null,
    Object? processedRows = null,
    Object? importedRows = null,
    Object? errors = freezed,
    Object? warnings = freezed,
    Object? headerMapping = freezed,
    Object? validationResults = freezed,
  }) {
    return _then(_$ImportJobImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      fileName: null == fileName
          ? _value.fileName
          : fileName // ignore: cast_nullable_to_non_nullable
              as String,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      startedAt: null == startedAt
          ? _value.startedAt
          : startedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      completedAt: freezed == completedAt
          ? _value.completedAt
          : completedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      totalRows: null == totalRows
          ? _value.totalRows
          : totalRows // ignore: cast_nullable_to_non_nullable
              as int,
      processedRows: null == processedRows
          ? _value.processedRows
          : processedRows // ignore: cast_nullable_to_non_nullable
              as int,
      importedRows: null == importedRows
          ? _value.importedRows
          : importedRows // ignore: cast_nullable_to_non_nullable
              as int,
      errors: freezed == errors
          ? _value._errors
          : errors // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      warnings: freezed == warnings
          ? _value._warnings
          : warnings // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      headerMapping: freezed == headerMapping
          ? _value._headerMapping
          : headerMapping // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      validationResults: freezed == validationResults
          ? _value._validationResults
          : validationResults // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ImportJobImpl implements _ImportJob {
  const _$ImportJobImpl(
      {required this.id,
      required this.fileName,
      required this.status,
      required this.startedAt,
      this.completedAt,
      required this.totalRows,
      required this.processedRows,
      required this.importedRows,
      final List<String>? errors,
      final List<String>? warnings,
      final Map<String, dynamic>? headerMapping,
      final Map<String, dynamic>? validationResults})
      : _errors = errors,
        _warnings = warnings,
        _headerMapping = headerMapping,
        _validationResults = validationResults;

  factory _$ImportJobImpl.fromJson(Map<String, dynamic> json) =>
      _$$ImportJobImplFromJson(json);

  @override
  final String id;
  @override
  final String fileName;
  @override
  final String status;
  @override
  final DateTime startedAt;
  @override
  final DateTime? completedAt;
  @override
  final int totalRows;
  @override
  final int processedRows;
  @override
  final int importedRows;
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

  final Map<String, dynamic>? _headerMapping;
  @override
  Map<String, dynamic>? get headerMapping {
    final value = _headerMapping;
    if (value == null) return null;
    if (_headerMapping is EqualUnmodifiableMapView) return _headerMapping;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  final Map<String, dynamic>? _validationResults;
  @override
  Map<String, dynamic>? get validationResults {
    final value = _validationResults;
    if (value == null) return null;
    if (_validationResults is EqualUnmodifiableMapView)
      return _validationResults;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'ImportJob(id: $id, fileName: $fileName, status: $status, startedAt: $startedAt, completedAt: $completedAt, totalRows: $totalRows, processedRows: $processedRows, importedRows: $importedRows, errors: $errors, warnings: $warnings, headerMapping: $headerMapping, validationResults: $validationResults)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ImportJobImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.fileName, fileName) ||
                other.fileName == fileName) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.startedAt, startedAt) ||
                other.startedAt == startedAt) &&
            (identical(other.completedAt, completedAt) ||
                other.completedAt == completedAt) &&
            (identical(other.totalRows, totalRows) ||
                other.totalRows == totalRows) &&
            (identical(other.processedRows, processedRows) ||
                other.processedRows == processedRows) &&
            (identical(other.importedRows, importedRows) ||
                other.importedRows == importedRows) &&
            const DeepCollectionEquality().equals(other._errors, _errors) &&
            const DeepCollectionEquality().equals(other._warnings, _warnings) &&
            const DeepCollectionEquality()
                .equals(other._headerMapping, _headerMapping) &&
            const DeepCollectionEquality()
                .equals(other._validationResults, _validationResults));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      fileName,
      status,
      startedAt,
      completedAt,
      totalRows,
      processedRows,
      importedRows,
      const DeepCollectionEquality().hash(_errors),
      const DeepCollectionEquality().hash(_warnings),
      const DeepCollectionEquality().hash(_headerMapping),
      const DeepCollectionEquality().hash(_validationResults));

  /// Create a copy of ImportJob
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ImportJobImplCopyWith<_$ImportJobImpl> get copyWith =>
      __$$ImportJobImplCopyWithImpl<_$ImportJobImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ImportJobImplToJson(
      this,
    );
  }
}

abstract class _ImportJob implements ImportJob {
  const factory _ImportJob(
      {required final String id,
      required final String fileName,
      required final String status,
      required final DateTime startedAt,
      final DateTime? completedAt,
      required final int totalRows,
      required final int processedRows,
      required final int importedRows,
      final List<String>? errors,
      final List<String>? warnings,
      final Map<String, dynamic>? headerMapping,
      final Map<String, dynamic>? validationResults}) = _$ImportJobImpl;

  factory _ImportJob.fromJson(Map<String, dynamic> json) =
      _$ImportJobImpl.fromJson;

  @override
  String get id;
  @override
  String get fileName;
  @override
  String get status;
  @override
  DateTime get startedAt;
  @override
  DateTime? get completedAt;
  @override
  int get totalRows;
  @override
  int get processedRows;
  @override
  int get importedRows;
  @override
  List<String>? get errors;
  @override
  List<String>? get warnings;
  @override
  Map<String, dynamic>? get headerMapping;
  @override
  Map<String, dynamic>? get validationResults;

  /// Create a copy of ImportJob
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ImportJobImplCopyWith<_$ImportJobImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

BackupRestoreStatus _$BackupRestoreStatusFromJson(Map<String, dynamic> json) {
  return _BackupRestoreStatus.fromJson(json);
}

/// @nodoc
mixin _$BackupRestoreStatus {
  String get operation => throw _privateConstructorUsedError;
  String get status => throw _privateConstructorUsedError;
  DateTime get startedAt => throw _privateConstructorUsedError;
  DateTime? get completedAt => throw _privateConstructorUsedError;
  int get totalItems => throw _privateConstructorUsedError;
  int get processedItems => throw _privateConstructorUsedError;
  String? get errorMessage => throw _privateConstructorUsedError;
  Map<String, dynamic>? get details => throw _privateConstructorUsedError;
  bool? get integrityCheckPassed => throw _privateConstructorUsedError;

  /// Serializes this BackupRestoreStatus to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of BackupRestoreStatus
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $BackupRestoreStatusCopyWith<BackupRestoreStatus> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $BackupRestoreStatusCopyWith<$Res> {
  factory $BackupRestoreStatusCopyWith(
          BackupRestoreStatus value, $Res Function(BackupRestoreStatus) then) =
      _$BackupRestoreStatusCopyWithImpl<$Res, BackupRestoreStatus>;
  @useResult
  $Res call(
      {String operation,
      String status,
      DateTime startedAt,
      DateTime? completedAt,
      int totalItems,
      int processedItems,
      String? errorMessage,
      Map<String, dynamic>? details,
      bool? integrityCheckPassed});
}

/// @nodoc
class _$BackupRestoreStatusCopyWithImpl<$Res, $Val extends BackupRestoreStatus>
    implements $BackupRestoreStatusCopyWith<$Res> {
  _$BackupRestoreStatusCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of BackupRestoreStatus
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? operation = null,
    Object? status = null,
    Object? startedAt = null,
    Object? completedAt = freezed,
    Object? totalItems = null,
    Object? processedItems = null,
    Object? errorMessage = freezed,
    Object? details = freezed,
    Object? integrityCheckPassed = freezed,
  }) {
    return _then(_value.copyWith(
      operation: null == operation
          ? _value.operation
          : operation // ignore: cast_nullable_to_non_nullable
              as String,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      startedAt: null == startedAt
          ? _value.startedAt
          : startedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      completedAt: freezed == completedAt
          ? _value.completedAt
          : completedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      totalItems: null == totalItems
          ? _value.totalItems
          : totalItems // ignore: cast_nullable_to_non_nullable
              as int,
      processedItems: null == processedItems
          ? _value.processedItems
          : processedItems // ignore: cast_nullable_to_non_nullable
              as int,
      errorMessage: freezed == errorMessage
          ? _value.errorMessage
          : errorMessage // ignore: cast_nullable_to_non_nullable
              as String?,
      details: freezed == details
          ? _value.details
          : details // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      integrityCheckPassed: freezed == integrityCheckPassed
          ? _value.integrityCheckPassed
          : integrityCheckPassed // ignore: cast_nullable_to_non_nullable
              as bool?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$BackupRestoreStatusImplCopyWith<$Res>
    implements $BackupRestoreStatusCopyWith<$Res> {
  factory _$$BackupRestoreStatusImplCopyWith(_$BackupRestoreStatusImpl value,
          $Res Function(_$BackupRestoreStatusImpl) then) =
      __$$BackupRestoreStatusImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String operation,
      String status,
      DateTime startedAt,
      DateTime? completedAt,
      int totalItems,
      int processedItems,
      String? errorMessage,
      Map<String, dynamic>? details,
      bool? integrityCheckPassed});
}

/// @nodoc
class __$$BackupRestoreStatusImplCopyWithImpl<$Res>
    extends _$BackupRestoreStatusCopyWithImpl<$Res, _$BackupRestoreStatusImpl>
    implements _$$BackupRestoreStatusImplCopyWith<$Res> {
  __$$BackupRestoreStatusImplCopyWithImpl(_$BackupRestoreStatusImpl _value,
      $Res Function(_$BackupRestoreStatusImpl) _then)
      : super(_value, _then);

  /// Create a copy of BackupRestoreStatus
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? operation = null,
    Object? status = null,
    Object? startedAt = null,
    Object? completedAt = freezed,
    Object? totalItems = null,
    Object? processedItems = null,
    Object? errorMessage = freezed,
    Object? details = freezed,
    Object? integrityCheckPassed = freezed,
  }) {
    return _then(_$BackupRestoreStatusImpl(
      operation: null == operation
          ? _value.operation
          : operation // ignore: cast_nullable_to_non_nullable
              as String,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      startedAt: null == startedAt
          ? _value.startedAt
          : startedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      completedAt: freezed == completedAt
          ? _value.completedAt
          : completedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      totalItems: null == totalItems
          ? _value.totalItems
          : totalItems // ignore: cast_nullable_to_non_nullable
              as int,
      processedItems: null == processedItems
          ? _value.processedItems
          : processedItems // ignore: cast_nullable_to_non_nullable
              as int,
      errorMessage: freezed == errorMessage
          ? _value.errorMessage
          : errorMessage // ignore: cast_nullable_to_non_nullable
              as String?,
      details: freezed == details
          ? _value._details
          : details // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      integrityCheckPassed: freezed == integrityCheckPassed
          ? _value.integrityCheckPassed
          : integrityCheckPassed // ignore: cast_nullable_to_non_nullable
              as bool?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$BackupRestoreStatusImpl implements _BackupRestoreStatus {
  const _$BackupRestoreStatusImpl(
      {required this.operation,
      required this.status,
      required this.startedAt,
      this.completedAt,
      required this.totalItems,
      required this.processedItems,
      this.errorMessage,
      final Map<String, dynamic>? details,
      this.integrityCheckPassed})
      : _details = details;

  factory _$BackupRestoreStatusImpl.fromJson(Map<String, dynamic> json) =>
      _$$BackupRestoreStatusImplFromJson(json);

  @override
  final String operation;
  @override
  final String status;
  @override
  final DateTime startedAt;
  @override
  final DateTime? completedAt;
  @override
  final int totalItems;
  @override
  final int processedItems;
  @override
  final String? errorMessage;
  final Map<String, dynamic>? _details;
  @override
  Map<String, dynamic>? get details {
    final value = _details;
    if (value == null) return null;
    if (_details is EqualUnmodifiableMapView) return _details;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  final bool? integrityCheckPassed;

  @override
  String toString() {
    return 'BackupRestoreStatus(operation: $operation, status: $status, startedAt: $startedAt, completedAt: $completedAt, totalItems: $totalItems, processedItems: $processedItems, errorMessage: $errorMessage, details: $details, integrityCheckPassed: $integrityCheckPassed)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$BackupRestoreStatusImpl &&
            (identical(other.operation, operation) ||
                other.operation == operation) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.startedAt, startedAt) ||
                other.startedAt == startedAt) &&
            (identical(other.completedAt, completedAt) ||
                other.completedAt == completedAt) &&
            (identical(other.totalItems, totalItems) ||
                other.totalItems == totalItems) &&
            (identical(other.processedItems, processedItems) ||
                other.processedItems == processedItems) &&
            (identical(other.errorMessage, errorMessage) ||
                other.errorMessage == errorMessage) &&
            const DeepCollectionEquality().equals(other._details, _details) &&
            (identical(other.integrityCheckPassed, integrityCheckPassed) ||
                other.integrityCheckPassed == integrityCheckPassed));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      operation,
      status,
      startedAt,
      completedAt,
      totalItems,
      processedItems,
      errorMessage,
      const DeepCollectionEquality().hash(_details),
      integrityCheckPassed);

  /// Create a copy of BackupRestoreStatus
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$BackupRestoreStatusImplCopyWith<_$BackupRestoreStatusImpl> get copyWith =>
      __$$BackupRestoreStatusImplCopyWithImpl<_$BackupRestoreStatusImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$BackupRestoreStatusImplToJson(
      this,
    );
  }
}

abstract class _BackupRestoreStatus implements BackupRestoreStatus {
  const factory _BackupRestoreStatus(
      {required final String operation,
      required final String status,
      required final DateTime startedAt,
      final DateTime? completedAt,
      required final int totalItems,
      required final int processedItems,
      final String? errorMessage,
      final Map<String, dynamic>? details,
      final bool? integrityCheckPassed}) = _$BackupRestoreStatusImpl;

  factory _BackupRestoreStatus.fromJson(Map<String, dynamic> json) =
      _$BackupRestoreStatusImpl.fromJson;

  @override
  String get operation;
  @override
  String get status;
  @override
  DateTime get startedAt;
  @override
  DateTime? get completedAt;
  @override
  int get totalItems;
  @override
  int get processedItems;
  @override
  String? get errorMessage;
  @override
  Map<String, dynamic>? get details;
  @override
  bool? get integrityCheckPassed;

  /// Create a copy of BackupRestoreStatus
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$BackupRestoreStatusImplCopyWith<_$BackupRestoreStatusImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

HeaderValidationError _$HeaderValidationErrorFromJson(
    Map<String, dynamic> json) {
  return _HeaderValidationError.fromJson(json);
}

/// @nodoc
mixin _$HeaderValidationError {
  int get row => throw _privateConstructorUsedError;
  int get colIndex => throw _privateConstructorUsedError;
  String get expected => throw _privateConstructorUsedError;
  String get received => throw _privateConstructorUsedError;
  String? get suggestion => throw _privateConstructorUsedError;

  /// Serializes this HeaderValidationError to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of HeaderValidationError
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $HeaderValidationErrorCopyWith<HeaderValidationError> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $HeaderValidationErrorCopyWith<$Res> {
  factory $HeaderValidationErrorCopyWith(HeaderValidationError value,
          $Res Function(HeaderValidationError) then) =
      _$HeaderValidationErrorCopyWithImpl<$Res, HeaderValidationError>;
  @useResult
  $Res call(
      {int row,
      int colIndex,
      String expected,
      String received,
      String? suggestion});
}

/// @nodoc
class _$HeaderValidationErrorCopyWithImpl<$Res,
        $Val extends HeaderValidationError>
    implements $HeaderValidationErrorCopyWith<$Res> {
  _$HeaderValidationErrorCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of HeaderValidationError
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? row = null,
    Object? colIndex = null,
    Object? expected = null,
    Object? received = null,
    Object? suggestion = freezed,
  }) {
    return _then(_value.copyWith(
      row: null == row
          ? _value.row
          : row // ignore: cast_nullable_to_non_nullable
              as int,
      colIndex: null == colIndex
          ? _value.colIndex
          : colIndex // ignore: cast_nullable_to_non_nullable
              as int,
      expected: null == expected
          ? _value.expected
          : expected // ignore: cast_nullable_to_non_nullable
              as String,
      received: null == received
          ? _value.received
          : received // ignore: cast_nullable_to_non_nullable
              as String,
      suggestion: freezed == suggestion
          ? _value.suggestion
          : suggestion // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$HeaderValidationErrorImplCopyWith<$Res>
    implements $HeaderValidationErrorCopyWith<$Res> {
  factory _$$HeaderValidationErrorImplCopyWith(
          _$HeaderValidationErrorImpl value,
          $Res Function(_$HeaderValidationErrorImpl) then) =
      __$$HeaderValidationErrorImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int row,
      int colIndex,
      String expected,
      String received,
      String? suggestion});
}

/// @nodoc
class __$$HeaderValidationErrorImplCopyWithImpl<$Res>
    extends _$HeaderValidationErrorCopyWithImpl<$Res,
        _$HeaderValidationErrorImpl>
    implements _$$HeaderValidationErrorImplCopyWith<$Res> {
  __$$HeaderValidationErrorImplCopyWithImpl(_$HeaderValidationErrorImpl _value,
      $Res Function(_$HeaderValidationErrorImpl) _then)
      : super(_value, _then);

  /// Create a copy of HeaderValidationError
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? row = null,
    Object? colIndex = null,
    Object? expected = null,
    Object? received = null,
    Object? suggestion = freezed,
  }) {
    return _then(_$HeaderValidationErrorImpl(
      row: null == row
          ? _value.row
          : row // ignore: cast_nullable_to_non_nullable
              as int,
      colIndex: null == colIndex
          ? _value.colIndex
          : colIndex // ignore: cast_nullable_to_non_nullable
              as int,
      expected: null == expected
          ? _value.expected
          : expected // ignore: cast_nullable_to_non_nullable
              as String,
      received: null == received
          ? _value.received
          : received // ignore: cast_nullable_to_non_nullable
              as String,
      suggestion: freezed == suggestion
          ? _value.suggestion
          : suggestion // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$HeaderValidationErrorImpl implements _HeaderValidationError {
  const _$HeaderValidationErrorImpl(
      {required this.row,
      required this.colIndex,
      required this.expected,
      required this.received,
      this.suggestion});

  factory _$HeaderValidationErrorImpl.fromJson(Map<String, dynamic> json) =>
      _$$HeaderValidationErrorImplFromJson(json);

  @override
  final int row;
  @override
  final int colIndex;
  @override
  final String expected;
  @override
  final String received;
  @override
  final String? suggestion;

  @override
  String toString() {
    return 'HeaderValidationError(row: $row, colIndex: $colIndex, expected: $expected, received: $received, suggestion: $suggestion)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$HeaderValidationErrorImpl &&
            (identical(other.row, row) || other.row == row) &&
            (identical(other.colIndex, colIndex) ||
                other.colIndex == colIndex) &&
            (identical(other.expected, expected) ||
                other.expected == expected) &&
            (identical(other.received, received) ||
                other.received == received) &&
            (identical(other.suggestion, suggestion) ||
                other.suggestion == suggestion));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode =>
      Object.hash(runtimeType, row, colIndex, expected, received, suggestion);

  /// Create a copy of HeaderValidationError
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$HeaderValidationErrorImplCopyWith<_$HeaderValidationErrorImpl>
      get copyWith => __$$HeaderValidationErrorImplCopyWithImpl<
          _$HeaderValidationErrorImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$HeaderValidationErrorImplToJson(
      this,
    );
  }
}

abstract class _HeaderValidationError implements HeaderValidationError {
  const factory _HeaderValidationError(
      {required final int row,
      required final int colIndex,
      required final String expected,
      required final String received,
      final String? suggestion}) = _$HeaderValidationErrorImpl;

  factory _HeaderValidationError.fromJson(Map<String, dynamic> json) =
      _$HeaderValidationErrorImpl.fromJson;

  @override
  int get row;
  @override
  int get colIndex;
  @override
  String get expected;
  @override
  String get received;
  @override
  String? get suggestion;

  /// Create a copy of HeaderValidationError
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$HeaderValidationErrorImplCopyWith<_$HeaderValidationErrorImpl>
      get copyWith => throw _privateConstructorUsedError;
}

ImportValidationResult _$ImportValidationResultFromJson(
    Map<String, dynamic> json) {
  return _ImportValidationResult.fromJson(json);
}

/// @nodoc
mixin _$ImportValidationResult {
  bool get isValid => throw _privateConstructorUsedError;
  List<HeaderValidationError>? get headerErrors =>
      throw _privateConstructorUsedError;
  Map<String, int>? get typeCounts => throw _privateConstructorUsedError;
  List<String>? get generalErrors => throw _privateConstructorUsedError;
  Map<String, dynamic>? get preview => throw _privateConstructorUsedError;

  /// Serializes this ImportValidationResult to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ImportValidationResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ImportValidationResultCopyWith<ImportValidationResult> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ImportValidationResultCopyWith<$Res> {
  factory $ImportValidationResultCopyWith(ImportValidationResult value,
          $Res Function(ImportValidationResult) then) =
      _$ImportValidationResultCopyWithImpl<$Res, ImportValidationResult>;
  @useResult
  $Res call(
      {bool isValid,
      List<HeaderValidationError>? headerErrors,
      Map<String, int>? typeCounts,
      List<String>? generalErrors,
      Map<String, dynamic>? preview});
}

/// @nodoc
class _$ImportValidationResultCopyWithImpl<$Res,
        $Val extends ImportValidationResult>
    implements $ImportValidationResultCopyWith<$Res> {
  _$ImportValidationResultCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ImportValidationResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? isValid = null,
    Object? headerErrors = freezed,
    Object? typeCounts = freezed,
    Object? generalErrors = freezed,
    Object? preview = freezed,
  }) {
    return _then(_value.copyWith(
      isValid: null == isValid
          ? _value.isValid
          : isValid // ignore: cast_nullable_to_non_nullable
              as bool,
      headerErrors: freezed == headerErrors
          ? _value.headerErrors
          : headerErrors // ignore: cast_nullable_to_non_nullable
              as List<HeaderValidationError>?,
      typeCounts: freezed == typeCounts
          ? _value.typeCounts
          : typeCounts // ignore: cast_nullable_to_non_nullable
              as Map<String, int>?,
      generalErrors: freezed == generalErrors
          ? _value.generalErrors
          : generalErrors // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      preview: freezed == preview
          ? _value.preview
          : preview // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ImportValidationResultImplCopyWith<$Res>
    implements $ImportValidationResultCopyWith<$Res> {
  factory _$$ImportValidationResultImplCopyWith(
          _$ImportValidationResultImpl value,
          $Res Function(_$ImportValidationResultImpl) then) =
      __$$ImportValidationResultImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {bool isValid,
      List<HeaderValidationError>? headerErrors,
      Map<String, int>? typeCounts,
      List<String>? generalErrors,
      Map<String, dynamic>? preview});
}

/// @nodoc
class __$$ImportValidationResultImplCopyWithImpl<$Res>
    extends _$ImportValidationResultCopyWithImpl<$Res,
        _$ImportValidationResultImpl>
    implements _$$ImportValidationResultImplCopyWith<$Res> {
  __$$ImportValidationResultImplCopyWithImpl(
      _$ImportValidationResultImpl _value,
      $Res Function(_$ImportValidationResultImpl) _then)
      : super(_value, _then);

  /// Create a copy of ImportValidationResult
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? isValid = null,
    Object? headerErrors = freezed,
    Object? typeCounts = freezed,
    Object? generalErrors = freezed,
    Object? preview = freezed,
  }) {
    return _then(_$ImportValidationResultImpl(
      isValid: null == isValid
          ? _value.isValid
          : isValid // ignore: cast_nullable_to_non_nullable
              as bool,
      headerErrors: freezed == headerErrors
          ? _value._headerErrors
          : headerErrors // ignore: cast_nullable_to_non_nullable
              as List<HeaderValidationError>?,
      typeCounts: freezed == typeCounts
          ? _value._typeCounts
          : typeCounts // ignore: cast_nullable_to_non_nullable
              as Map<String, int>?,
      generalErrors: freezed == generalErrors
          ? _value._generalErrors
          : generalErrors // ignore: cast_nullable_to_non_nullable
              as List<String>?,
      preview: freezed == preview
          ? _value._preview
          : preview // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ImportValidationResultImpl implements _ImportValidationResult {
  const _$ImportValidationResultImpl(
      {required this.isValid,
      final List<HeaderValidationError>? headerErrors,
      final Map<String, int>? typeCounts,
      final List<String>? generalErrors,
      final Map<String, dynamic>? preview})
      : _headerErrors = headerErrors,
        _typeCounts = typeCounts,
        _generalErrors = generalErrors,
        _preview = preview;

  factory _$ImportValidationResultImpl.fromJson(Map<String, dynamic> json) =>
      _$$ImportValidationResultImplFromJson(json);

  @override
  final bool isValid;
  final List<HeaderValidationError>? _headerErrors;
  @override
  List<HeaderValidationError>? get headerErrors {
    final value = _headerErrors;
    if (value == null) return null;
    if (_headerErrors is EqualUnmodifiableListView) return _headerErrors;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  final Map<String, int>? _typeCounts;
  @override
  Map<String, int>? get typeCounts {
    final value = _typeCounts;
    if (value == null) return null;
    if (_typeCounts is EqualUnmodifiableMapView) return _typeCounts;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  final List<String>? _generalErrors;
  @override
  List<String>? get generalErrors {
    final value = _generalErrors;
    if (value == null) return null;
    if (_generalErrors is EqualUnmodifiableListView) return _generalErrors;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  final Map<String, dynamic>? _preview;
  @override
  Map<String, dynamic>? get preview {
    final value = _preview;
    if (value == null) return null;
    if (_preview is EqualUnmodifiableMapView) return _preview;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(value);
  }

  @override
  String toString() {
    return 'ImportValidationResult(isValid: $isValid, headerErrors: $headerErrors, typeCounts: $typeCounts, generalErrors: $generalErrors, preview: $preview)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ImportValidationResultImpl &&
            (identical(other.isValid, isValid) || other.isValid == isValid) &&
            const DeepCollectionEquality()
                .equals(other._headerErrors, _headerErrors) &&
            const DeepCollectionEquality()
                .equals(other._typeCounts, _typeCounts) &&
            const DeepCollectionEquality()
                .equals(other._generalErrors, _generalErrors) &&
            const DeepCollectionEquality().equals(other._preview, _preview));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      isValid,
      const DeepCollectionEquality().hash(_headerErrors),
      const DeepCollectionEquality().hash(_typeCounts),
      const DeepCollectionEquality().hash(_generalErrors),
      const DeepCollectionEquality().hash(_preview));

  /// Create a copy of ImportValidationResult
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ImportValidationResultImplCopyWith<_$ImportValidationResultImpl>
      get copyWith => __$$ImportValidationResultImplCopyWithImpl<
          _$ImportValidationResultImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ImportValidationResultImplToJson(
      this,
    );
  }
}

abstract class _ImportValidationResult implements ImportValidationResult {
  const factory _ImportValidationResult(
      {required final bool isValid,
      final List<HeaderValidationError>? headerErrors,
      final Map<String, int>? typeCounts,
      final List<String>? generalErrors,
      final Map<String, dynamic>? preview}) = _$ImportValidationResultImpl;

  factory _ImportValidationResult.fromJson(Map<String, dynamic> json) =
      _$ImportValidationResultImpl.fromJson;

  @override
  bool get isValid;
  @override
  List<HeaderValidationError>? get headerErrors;
  @override
  Map<String, int>? get typeCounts;
  @override
  List<String>? get generalErrors;
  @override
  Map<String, dynamic>? get preview;

  /// Create a copy of ImportValidationResult
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ImportValidationResultImplCopyWith<_$ImportValidationResultImpl>
      get copyWith => throw _privateConstructorUsedError;
}

BackupMetadata _$BackupMetadataFromJson(Map<String, dynamic> json) {
  return _BackupMetadata.fromJson(json);
}

/// @nodoc
mixin _$BackupMetadata {
  String get version => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;
  String get checksum => throw _privateConstructorUsedError;
  Map<String, int> get recordCounts => throw _privateConstructorUsedError;
  Map<String, dynamic>? get settings => throw _privateConstructorUsedError;
  String? get description => throw _privateConstructorUsedError;

  /// Serializes this BackupMetadata to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of BackupMetadata
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $BackupMetadataCopyWith<BackupMetadata> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $BackupMetadataCopyWith<$Res> {
  factory $BackupMetadataCopyWith(
          BackupMetadata value, $Res Function(BackupMetadata) then) =
      _$BackupMetadataCopyWithImpl<$Res, BackupMetadata>;
  @useResult
  $Res call(
      {String version,
      DateTime createdAt,
      String checksum,
      Map<String, int> recordCounts,
      Map<String, dynamic>? settings,
      String? description});
}

/// @nodoc
class _$BackupMetadataCopyWithImpl<$Res, $Val extends BackupMetadata>
    implements $BackupMetadataCopyWith<$Res> {
  _$BackupMetadataCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of BackupMetadata
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? version = null,
    Object? createdAt = null,
    Object? checksum = null,
    Object? recordCounts = null,
    Object? settings = freezed,
    Object? description = freezed,
  }) {
    return _then(_value.copyWith(
      version: null == version
          ? _value.version
          : version // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      checksum: null == checksum
          ? _value.checksum
          : checksum // ignore: cast_nullable_to_non_nullable
              as String,
      recordCounts: null == recordCounts
          ? _value.recordCounts
          : recordCounts // ignore: cast_nullable_to_non_nullable
              as Map<String, int>,
      settings: freezed == settings
          ? _value.settings
          : settings // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$BackupMetadataImplCopyWith<$Res>
    implements $BackupMetadataCopyWith<$Res> {
  factory _$$BackupMetadataImplCopyWith(_$BackupMetadataImpl value,
          $Res Function(_$BackupMetadataImpl) then) =
      __$$BackupMetadataImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String version,
      DateTime createdAt,
      String checksum,
      Map<String, int> recordCounts,
      Map<String, dynamic>? settings,
      String? description});
}

/// @nodoc
class __$$BackupMetadataImplCopyWithImpl<$Res>
    extends _$BackupMetadataCopyWithImpl<$Res, _$BackupMetadataImpl>
    implements _$$BackupMetadataImplCopyWith<$Res> {
  __$$BackupMetadataImplCopyWithImpl(
      _$BackupMetadataImpl _value, $Res Function(_$BackupMetadataImpl) _then)
      : super(_value, _then);

  /// Create a copy of BackupMetadata
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? version = null,
    Object? createdAt = null,
    Object? checksum = null,
    Object? recordCounts = null,
    Object? settings = freezed,
    Object? description = freezed,
  }) {
    return _then(_$BackupMetadataImpl(
      version: null == version
          ? _value.version
          : version // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      checksum: null == checksum
          ? _value.checksum
          : checksum // ignore: cast_nullable_to_non_nullable
              as String,
      recordCounts: null == recordCounts
          ? _value._recordCounts
          : recordCounts // ignore: cast_nullable_to_non_nullable
              as Map<String, int>,
      settings: freezed == settings
          ? _value._settings
          : settings // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>?,
      description: freezed == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$BackupMetadataImpl implements _BackupMetadata {
  const _$BackupMetadataImpl(
      {required this.version,
      required this.createdAt,
      required this.checksum,
      required final Map<String, int> recordCounts,
      final Map<String, dynamic>? settings,
      this.description})
      : _recordCounts = recordCounts,
        _settings = settings;

  factory _$BackupMetadataImpl.fromJson(Map<String, dynamic> json) =>
      _$$BackupMetadataImplFromJson(json);

  @override
  final String version;
  @override
  final DateTime createdAt;
  @override
  final String checksum;
  final Map<String, int> _recordCounts;
  @override
  Map<String, int> get recordCounts {
    if (_recordCounts is EqualUnmodifiableMapView) return _recordCounts;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_recordCounts);
  }

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
  final String? description;

  @override
  String toString() {
    return 'BackupMetadata(version: $version, createdAt: $createdAt, checksum: $checksum, recordCounts: $recordCounts, settings: $settings, description: $description)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$BackupMetadataImpl &&
            (identical(other.version, version) || other.version == version) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.checksum, checksum) ||
                other.checksum == checksum) &&
            const DeepCollectionEquality()
                .equals(other._recordCounts, _recordCounts) &&
            const DeepCollectionEquality().equals(other._settings, _settings) &&
            (identical(other.description, description) ||
                other.description == description));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      version,
      createdAt,
      checksum,
      const DeepCollectionEquality().hash(_recordCounts),
      const DeepCollectionEquality().hash(_settings),
      description);

  /// Create a copy of BackupMetadata
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$BackupMetadataImplCopyWith<_$BackupMetadataImpl> get copyWith =>
      __$$BackupMetadataImplCopyWithImpl<_$BackupMetadataImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$BackupMetadataImplToJson(
      this,
    );
  }
}

abstract class _BackupMetadata implements BackupMetadata {
  const factory _BackupMetadata(
      {required final String version,
      required final DateTime createdAt,
      required final String checksum,
      required final Map<String, int> recordCounts,
      final Map<String, dynamic>? settings,
      final String? description}) = _$BackupMetadataImpl;

  factory _BackupMetadata.fromJson(Map<String, dynamic> json) =
      _$BackupMetadataImpl.fromJson;

  @override
  String get version;
  @override
  DateTime get createdAt;
  @override
  String get checksum;
  @override
  Map<String, int> get recordCounts;
  @override
  Map<String, dynamic>? get settings;
  @override
  String? get description;

  /// Create a copy of BackupMetadata
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$BackupMetadataImplCopyWith<_$BackupMetadataImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
