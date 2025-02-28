---
description: PROVIDE cross-component context when EDITING settings-related files to ENSURE consistent implementation
globs: backend/api/v1/endpoints/settings.py, backend/schemas/settings.py, frontend/src/components/settings/*.tsx, frontend/src/pages/Settings.tsx
alwaysApply: false
---

# Settings Module Cross-Component Context

<version>1.0.0</version>

## Context
- When editing any settings-related files in either backend or frontend
- When implementing new settings features that span both backend and frontend
- When debugging settings functionality issues

## Requirements
- Always consider both backend and frontend implementations when making changes
- Ensure API contract consistency between backend endpoints and frontend API clients
- After backend schema changes, run the API generation script (`npm run generate:api`)
- Check for UI impacts when modifying backend settings behavior
- Ensure settings are properly displayed and can be modified in the UI
- Handle settings validation and error messages

## Related Files

[Settings.tsx](mdc:frontend/src/pages/Settings.tsx)

[Settings.module.css](mdc:frontend/src/pages/Settings.module.css)

[NotificationSection.tsx](mdc:frontend/src/components/settings/NotificationSection/NotificationSection.tsx)

## Examples
<example>
When adding a new setting to the settings page:
1. Update the settings schema if needed
2. Update any API endpoints that use this schema
3. Run `npm run generate:api` to update frontend types
4. Update the Settings.tsx page to include the new setting
5. Add appropriate validation and error handling
6. Run `npm run typecheck` to verify type consistency
</example>

<example type="invalid">
Adding a new setting to the settings page without updating the backend schema and API endpoints, causing the setting to not be properly saved or retrieved.
</example>
