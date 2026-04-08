# MongoDB Database Management Utilities

This module provides utilities for managing MongoDB collections, including key management and custom roles.

## Key Collection

The `keys` collection is designed to store and manage access keys for various services.

### Schema:
- `_id`: ObjectId - Unique identifier for each key.
- `service_name`: String - Name of the service the key is associated with.
- `key`: String - The actual access key.
- `created_at`: Date - Timestamp of when the key was created.
- `expires_at`: Date - Optional timestamp for when the key expires.

### Functions:
1. `add_key(service_name, key, expires_at=None)` : Adds a new key to the collection.
2. `get_key(service_name)` : Retrieves the key for the specified service.
3. `delete_key(service_name)` : Deletes the key for the specified service.

## Custom Role Collection

The `roles` collection is designed to manage user roles and permissions.

### Schema:
- `_id`: ObjectId - Unique identifier for each role.
- `role_name`: String - The name of the role (e.g., `admin`, `editor`).
- `permissions`: Array - List of permissions associated with the role.
- `created_at`: Date - Timestamp of when the role was created.

### Functions:
1. `add_role(role_name, permissions)` : Adds a new role.
2. `get_role(role_name)` : Retrieves the specified role.
3. `delete_role(role_name)` : Deletes the specified role.