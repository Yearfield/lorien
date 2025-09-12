# Authentication & RBAC Documentation

## Overview

Lorien implements a comprehensive Role-Based Access Control (RBAC) system with ETag-based concurrency control for secure, multi-user access to the decision tree API.

## Features

- **Role-Based Access Control**: Fine-grained permissions based on user roles
- **ETag Concurrency Control**: Optimistic concurrency control to prevent lost updates
- **Session Management**: Secure token-based authentication with configurable expiration
- **User Management**: Complete user lifecycle management with admin controls
- **Permission System**: Granular permissions for different API operations

## Configuration

### Environment Variables

```bash
# Enable RBAC system
RBAC_ENABLED=true

# Legacy simple token authentication (still supported)
AUTH_TOKEN=your-secret-token

# Analytics (for metrics)
ANALYTICS_ENABLED=true
```

## User Roles

### Viewer (`viewer`)
- **Read-only access** to all tree data
- Can view trees, triage, flags, and exports
- Cannot modify any data

**Permissions:**
- `read:tree` - View tree structure
- `read:triage` - View triage data
- `read:flags` - View flags
- `read:dictionary` - View dictionary
- `read:export` - View exports
- `read:health` - View health status

### Editor (`editor`)
- **Full read/write access** to tree data
- Can create, update, and delete tree nodes
- Can manage triage and flags
- Cannot manage users or system settings

**Permissions:**
- All viewer permissions
- `write:tree` - Modify tree structure
- `write:triage` - Modify triage data
- `write:flags` - Modify flags
- `write:dictionary` - Modify dictionary
- `write:export` - Create exports

### Admin (`admin`)
- **Full access** to tree data and user management
- Can manage users, roles, and permissions
- Can view audit logs
- Cannot modify system settings

**Permissions:**
- All editor permissions
- `admin:users` - Manage users
- `admin:roles` - Manage roles
- `admin:audit` - View audit logs

### Super Admin (`super_admin`)
- **Complete system access**
- All permissions including system administration
- Can modify system settings and configurations

**Permissions:**
- All permissions in the system

## Default Users

When RBAC is enabled, the system creates three default users:

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| `admin` | `admin123` | `super_admin` | Full system access |
| `editor` | `editor123` | `editor` | Tree editing access |
| `viewer` | `viewer123` | `viewer` | Read-only access |

**⚠️ Security Note**: Change default passwords in production!

## Authentication

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/rbac/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_at": "2023-12-31T23:59:59Z",
  "user": {
    "id": "admin",
    "username": "admin",
    "email": "admin@lorien.local",
    "roles": ["super_admin"],
    "permissions": ["read:tree", "write:tree", "admin:users", ...]
  }
}
```

### Using Authentication

Include the token in the `Authorization` header:

```bash
curl -H "Authorization: Bearer your-token-here" \
  "http://localhost:8000/api/v1/rbac/me"
```

### Logout

```bash
curl -X POST "http://localhost:8000/api/v1/rbac/auth/logout" \
  -H "Authorization: Bearer your-token-here"
```

## User Management

### List Users (Admin Only)

```bash
curl -H "Authorization: Bearer admin-token" \
  "http://localhost:8000/api/v1/rbac/users"
```

### Create User (Admin Only)

```bash
curl -X POST "http://localhost:8000/api/v1/rbac/users" \
  -H "Authorization: Bearer admin-token" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepassword123",
    "roles": ["editor"]
  }'
```

### Assign Roles (Admin Only)

```bash
curl -X POST "http://localhost:8000/api/v1/rbac/users/user-id/roles" \
  -H "Authorization: Bearer admin-token" \
  -H "Content-Type: application/json" \
  -d '{
    "roles": ["admin", "editor"]
  }'
```

### Delete User (Admin Only)

```bash
curl -X DELETE "http://localhost:8000/api/v1/rbac/users/user-id" \
  -H "Authorization: Bearer admin-token"
```

## ETag Concurrency Control

### Overview

ETags provide optimistic concurrency control to prevent lost updates when multiple users edit the same data simultaneously.

### How It Works

1. **GET Request**: Server returns data with `ETag` header
2. **Modification**: Client includes `If-Match` header with ETag
3. **Validation**: Server checks if ETag matches current state
4. **Success/Conflict**: Update proceeds or returns 412 Precondition Failed

### Example Workflow

#### 1. Get Data with ETag

```bash
curl -v "http://localhost:8000/api/v1/tree/1/children"
```

**Response Headers:**
```
ETag: W/"abc123def456"
Cache-Control: no-cache, must-revalidate
```

#### 2. Modify with ETag Validation

```bash
curl -X POST "http://localhost:8000/api/v1/tree/1/children" \
  -H "If-Match: W/\"abc123def456\"" \
  -H "Content-Type: application/json" \
  -d '{"slots": [{"slot": 1, "label": "Updated Node"}]}'
```

#### 3. Handle Conflicts

If the ETag doesn't match (data was modified), you'll get a 412 response:

```json
{
  "error": "etag_mismatch",
  "message": "Resource has been modified. Please refresh and try again.",
  "expected_etag": "W/\"abc123def456\"",
  "current_etag": "W/\"xyz789ghi012\"",
  "hint": "Use If-Match header with current ETag to resolve conflicts"
}
```

### ETag Types

#### Node ETags
- Generated from node ID, version, and timestamp
- Used for individual node operations

#### Tree ETags
- Generated from entire tree structure
- Used for tree-wide operations

#### Version ETags
- Generated from version number and timestamp
- Used for version-based concurrency

## API Endpoints

### RBAC Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/rbac/status` | Get RBAC system status | No |
| POST | `/api/v1/rbac/auth/login` | Authenticate user | No |
| POST | `/api/v1/rbac/auth/logout` | Logout user | Yes |
| GET | `/api/v1/rbac/me` | Get current user info | Yes |
| GET | `/api/v1/rbac/permissions` | Get user permissions | Yes |
| GET | `/api/v1/rbac/users` | List users | Admin |
| POST | `/api/v1/rbac/users` | Create user | Admin |
| GET | `/api/v1/rbac/users/{id}` | Get user details | Admin |
| POST | `/api/v1/rbac/users/{id}/roles` | Assign roles | Admin |
| DELETE | `/api/v1/rbac/users/{id}` | Delete user | Admin |

### Protected Endpoints

All write operations require appropriate permissions:

- **Tree Operations**: `write:tree` permission
- **Triage Operations**: `write:triage` permission
- **Flags Operations**: `write:flags` permission
- **Dictionary Operations**: `write:dictionary` permission
- **Export Operations**: `write:export` permission
- **Admin Operations**: `admin:*` permissions

## Error Handling

### Authentication Errors

```json
{
  "error": "authentication_required",
  "message": "Authorization header required"
}
```

### Authorization Errors

```json
{
  "error": "insufficient_permissions",
  "message": "Access denied. Required permissions: ['write:tree']",
  "user_permissions": ["read:tree", "read:triage"]
}
```

### Concurrency Errors

```json
{
  "error": "etag_mismatch",
  "message": "Resource has been modified. Please refresh and try again.",
  "expected_etag": "W/\"abc123\"",
  "current_etag": "W/\"def456\"",
  "hint": "Use If-Match header with current ETag to resolve conflicts"
}
```

## Security Considerations

### Token Security
- Tokens are generated using cryptographically secure random generation
- Tokens expire after 24 hours by default
- Tokens are stored in memory (not persistent)

### Password Security
- Passwords are hashed using SHA-256 with salt
- Default passwords should be changed in production
- Consider implementing password complexity requirements

### Session Management
- Sessions are stored in memory
- Expired sessions are automatically cleaned up
- Users can be logged out by revoking their session

### Permission Validation
- All write operations validate permissions
- Permissions are checked at the middleware level
- Role changes take effect immediately

## Migration from Simple Auth

If you're currently using simple token authentication:

1. **Enable RBAC**: Set `RBAC_ENABLED=true`
2. **Keep Legacy Auth**: Simple token auth still works alongside RBAC
3. **Gradual Migration**: Migrate users to RBAC accounts
4. **Disable Legacy**: Remove `AUTH_TOKEN` when ready

## Troubleshooting

### Common Issues

1. **"RBAC is not enabled"**: Set `RBAC_ENABLED=true`
2. **"Invalid credentials"**: Check username/password
3. **"Insufficient permissions"**: User needs appropriate role
4. **"ETag mismatch"**: Data was modified, refresh and retry

### Debug Mode

Enable debug logging to see authentication details:

```bash
export LOG_LEVEL=DEBUG
```

### Health Check

Check RBAC system status:

```bash
curl "http://localhost:8000/api/v1/rbac/status"
```

## Future Enhancements

- **Database Persistence**: Store users and sessions in database
- **Password Policies**: Configurable password complexity
- **Two-Factor Authentication**: TOTP support
- **API Key Authentication**: For programmatic access
- **Audit Logging**: Detailed operation logging
- **Role Hierarchies**: Nested role relationships
