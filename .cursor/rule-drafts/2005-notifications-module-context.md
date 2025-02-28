---
description: PROVIDE cross-component context when EDITING notification-related files to ENSURE consistent implementation
globs: backend/api/v1/endpoints/notifications.py, backend/schemas/notification.py, frontend/src/components/notifications/*.tsx
alwaysApply: false
---

# Notifications Module Cross-Component Context

<version>1.0.0</version>

## Context
- When editing any notification-related files in either backend or frontend
- When implementing new notification features that span both backend and frontend
- When debugging notification functionality issues

## Requirements
- Always consider both backend and frontend implementations when making changes
- Ensure API contract consistency between backend endpoints and frontend API clients
- After backend schema changes, run the API generation script (`npm run generate:api`)
- Check for UI impacts when modifying backend notification behavior
- Ensure notifications are properly displayed in the UI
- Handle real-time notification updates via WebSockets

## Related Files

[notification.py](mdc:backend/schemas/notification.py)

[notification_service.py](mdc:backend/services/notification_service.py)

[NotificationIndicator.module.css](mdc:frontend/src/components/notifications/NotificationIndicator.module.css)

## Examples
<example>
When adding a new notification type to the notification.py schema:
1. Update the schema in notification.py
2. Update any API endpoints that use this schema
3. Run `npm run generate:api` to update frontend types
4. Update the notification components to handle the new notification type
5. Run `npm run typecheck` to verify type consistency
</example>

<example type="invalid">
Adding a new notification type to notification.py without running the API generation script and updating the frontend notification handling, causing the UI to not properly display the new notification type.
</example>
