---
description: PROVIDE cross-component context when EDITING stats-related files to ENSURE consistent implementation
globs: backend/api/v1/endpoints/stats.py, backend/schemas/stats.py, frontend/src/components/stats/*.tsx, frontend/src/components/dashboard/*.tsx
alwaysApply: false
---

# Stats Module Cross-Component Context

<version>1.0.0</version>

## Context
- When editing any stats-related files in either backend or frontend
- When implementing new stats features that span both backend and frontend
- When debugging stats functionality issues

## Requirements
- Always consider both backend and frontend implementations when making changes
- Ensure API contract consistency between backend endpoints and frontend API clients
- After backend schema changes, run the API generation script (`npm run generate:api`)
- Check for UI impacts when modifying backend stats behavior
- Ensure stats are properly displayed in the UI
- Handle data visualization and chart components

## Related Files

[StatsCard.module.css](mdc:frontend/src/components/stats/StatsCard.module.css)

[DashboardCharts.tsx](mdc:frontend/src/components/dashboard/DashboardCharts/DashboardCharts.tsx)

[StatsGrid.tsx](mdc:frontend/src/components/dashboard/StatsGrid/StatsGrid.tsx)

## Examples
<example>
When adding a new stat metric to the dashboard:
1. Update the stats schema if needed
2. Update any API endpoints that provide the stat data
3. Run `npm run generate:api` to update frontend types
4. Update the dashboard components to display the new stat
5. Add appropriate data visualization
6. Run `npm run typecheck` to verify type consistency
</example>

<example type="invalid">
Adding a new stat metric to the dashboard without updating the backend API endpoints to provide the data, causing the stat to display incorrect or missing data.
</example>
