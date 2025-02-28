---
description: PROVIDE cross-component context when EDITING dashboard-related files to ENSURE consistent implementation
globs: backend/api/v1/endpoints/dashboard.py, frontend/src/pages/Dashboard.tsx, frontend/src/components/dashboard/**/*.tsx
alwaysApply: false
---

# Dashboard Module Cross-Component Context

<version>1.0.0</version>

## Context
- When editing any dashboard-related files in either backend or frontend
- When implementing new dashboard features that span both backend and frontend
- When debugging dashboard functionality issues

## Requirements
- Always consider both backend and frontend implementations when making changes
- Ensure API contract consistency between backend endpoints and frontend API clients
- After backend schema changes, run the API generation script (`npm run generate:api`)
- Check for UI impacts when modifying backend dashboard behavior
- Ensure dashboard components are properly displayed in the UI
- Handle data visualization and chart components

## Related Files

[Dashboard.tsx](mdc:frontend/src/pages/Dashboard.tsx)

[Dashboard.module.css](mdc:frontend/src/pages/Dashboard.module.css)

[AutomationTypeGrid.tsx](mdc:frontend/src/components/dashboard/AutomationTypeGrid/AutomationTypeGrid.tsx)

[DashboardCharts.tsx](mdc:frontend/src/components/dashboard/DashboardCharts/DashboardCharts.tsx)

[EnhancedStatsGrid.tsx](mdc:frontend/src/components/dashboard/EnhancedStatsGrid/EnhancedStatsGrid.tsx)

[StatsGrid.tsx](mdc:frontend/src/components/dashboard/StatsGrid/StatsGrid.tsx)

## Examples
<example>
When adding a new dashboard widget:
1. Update the dashboard API endpoint to provide the necessary data
2. Run `npm run generate:api` to update frontend types
3. Create a new component for the widget in the dashboard directory
4. Update the Dashboard.tsx page to include the new widget
5. Add appropriate data visualization
6. Run `npm run typecheck` to verify type consistency
</example>

<example type="invalid">
Adding a new dashboard widget without updating the backend API endpoints to provide the data, causing the widget to display incorrect or missing data.
</example>
