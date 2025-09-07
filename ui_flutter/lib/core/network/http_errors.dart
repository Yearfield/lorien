/// HTTP error types for API client abstraction
abstract class ApiError implements Exception {
  final int statusCode;
  final String message;
  
  const ApiError(this.statusCode, this.message);
  
  @override
  String toString() => 'ApiError($statusCode): $message';
}

/// 422 Unprocessable Entity - validation errors
class Validation422 extends ApiError {
  final List<Map<String, dynamic>> detail;
  
  const Validation422(this.detail) : super(422, 'Validation failed');
  
  @override
  String toString() => 'Validation422: $detail';
}

/// 409 Conflict - resource conflicts
class Conflict409 extends ApiError {
  const Conflict409(String message) : super(409, message);
}

/// 404 Not Found
class NotFound404 extends ApiError {
  const NotFound404(String message) : super(404, message);
}

/// 503 Service Unavailable
class ServiceUnavailable extends ApiError {
  const ServiceUnavailable(String message) : super(503, message);
}

/// Generic API error for other non-2xx responses
class GenericApiError extends ApiError {
  const GenericApiError(int statusCode, String message) : super(statusCode, message);
}
