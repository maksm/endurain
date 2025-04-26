# Progress: Endurain

## What Works

*   Core application structure (Frontend/Backend/Database) is established.
*   User authentication and basic profile management likely exist.
*   Activity tracking, viewing (likely on a dashboard or individual activity pages), and manual upload (.gpx, .fit) are implemented based on project description.
*   Integrations with Strava and Garmin Connect are supported.
*   Gear tracking exists.
*   Health data tracking exists.
*   **Activities List Page (`/activities`):**
    *   Dedicated page implemented.
    *   Paginated table display (`ActivitiesTable.vue`) with columns: Type (icon), Name (link), Location, Start Time, Duration, Distance, Pace, Calories, Elevation, Avg HR.
    *   Pagination controls (`PaginationComponent.vue`).
    *   Sorting implemented for all columns.
    *   Filtering UI implemented.
    *   **Type Filter:** Fully functional (applies immediately on change).
    *   Translations added for new elements.
    *   **Refactoring:** Formatting logic (e.g., location) moved to `activityUtils.js`. Utility functions updated to use the global `i18n` instance for translations.
    *   **Scroll Fix (Page Collapse Prevention):** Implemented a fix by modifying `ActivitiesView.vue` and `ActivitiesTableComponent.vue` to prevent page collapse during sort-triggered table refresh. This involves keeping table data visible and showing an overlay.

## What's Left to Build (Current Focus)

*   **Routes Feature (Phase 1 - MVP):**
    *   **Backend:**
        *   Database models (`Route` table, `Activity.route_id`).
        *   Alembic migrations.
        *   API endpoints for route creation (GPX upload, from activity), listing, details, update, delete.
        *   API endpoints for linking/unlinking activities to routes.
        *   CRUD operations and Pydantic schemas for routes.
    *   **Frontend:**
        *   Navigation link to "Routes".
        *   Vue Router setup for routes pages.
        *   `routesService.js` and potentially `routesStore.js`.
        *   Routes List Page (`RoutesView.vue`).
        *   Route Creation UI (`RouteCreateForm.vue` or similar).
        *   Route Detail Page (`RouteDetailView.vue`) with map display and associated activities list.
        *   UI on Activity Detail page to link/unlink routes.
*   **Activities List Page (`/activities`) - Deferred:**
    *   Implement Date Range Filter.
    *   Implement Name/Location Search Filter.

## Current Status

*   The project focus has shifted to implementing Phase 1 of the "Routes" feature.
*   Memory Bank files (`activeContext.md`, `progress.md`) are being updated to reflect this new direction.
*   The previously planned work on advanced filtering for the Activities List page is deferred.

## Known Issues / Blockers

*   None currently identified for the initial phase of Routes development.
