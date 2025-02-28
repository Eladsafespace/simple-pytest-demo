---
description: USE ALWAYS when creating or using SVG icons to ENSURE consistent styling and implementation
globs: frontend/src/assets/icons/*.svg, frontend/src/components/icons/*.tsx
---

# SVG Icon Standards

<version>1.0.0</version>

## Context
- When creating or using SVG icons in the application
- When implementing new interface elements that require icons
- When styling or modifying icon appearance
- When adding new icons to the project

## Requirements
- Store all SVG icons in the `frontend/src/assets/icons/` directory
- Follow kebab-case naming convention for all icon files: e.g., `pipeline-runs.svg`
- SVG icons should be optimized for size and performance
- Each SVG icon should have the following attributes:
  - `width="24" height="24"` - Default dimensions
  - `viewBox="0 0 24 24"` - Standard coordinate system
  - `fill="none" stroke="currentColor"` - Allow color inheritance
  - `stroke-width="2" stroke-linecap="round" stroke-linejoin="round"` - Consistent style
- SVG icons should be simple, clean, and visually consistent with the overall design system
- Always use the `Icon` component from `components/common/Icon/Icon.tsx` to render icons
- Never embed raw SVG code directly in components
- Keep icon file sizes under 2KB
- When creating new icons, ensure they match the existing style and design language
- Group related icons using consistent prefixes (e.g., `user-add.svg`, `user-remove.svg`, etc.)
- Document all available icons in the storybook for reference

## Examples
<example>
// Good - Using the Icon component correctly
import { Icon } from "../../components/common/Icon/Icon";

const MyComponent = () => {
  return (
    <div className={styles.container}>
      <Icon type="pipeline-runs" size="medium" />
      <span>Pipeline Runs</span>
    </div>
  );
};
</example>

<example type="invalid">
// Bad - Embedding raw SVG directly in components
const MyComponent = () => {
  return (
    <div className={styles.container}>
      <svg width="24" height="24" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" />
        <path d="M16 12l-4-4-4 4" />
        <path d="M12 16V8" />
      </svg>
      <span>Pipeline Runs</span>
    </div>
  );
};
</example>

<example>
// Good - Proper SVG file format (pipeline-runs.svg)
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10" />
  <path d="M16 12l-4-4-4 4" />
  <path d="M12 16V8" />
</svg>
</example>

<example>
// Good - Icon component usage with different sizes
<header className={styles.header}>
  <Icon type="pipeline-runs" size="small" />
  <Icon type="active-jobs" size="medium" />
  <Icon type="success-rate" size="large" />
</header>
</example>  