# Active Context: Endurain - Routes Feature (Phase 1)

## Current Work Focus

The current primary task is the implementation of **Phase 1 of the "Routes" feature**. This phase focuses on establishing the core functionality for users to manually create, manage, and view routes, and to associate activities with these routes.

The previously planned work on "Activities List Page Filtering" (Date Range and Name/Location Search) will be deferred until after the initial implementation of the Routes feature, or addressed as a parallel task if feasible.

## Requirements for Current Implementation (Routes - Phase 1)

*   **Backend:**
    1.  **Database Model Updates:**
        *   Create a new `Route` table in `backend/app/activities/models.py` (or a new `backend/app/routes/models.py`). Key fields: `id`, `user_id` (FK to users), `name` (String), `description` (Text, nullable), `source_type` (Enum: 'gpx_upload', 'from_activity'), `gpx_file_content` (Text, to store raw GPX), `created_at`, `updated_at`.
        *   Modify the existing `Activity` model (`backend/app/activities/models.py`): Add a nullable `route_id` (FK to new `Route` table).
        *   Run Alembic migrations to apply schema changes.
    2.  **API Endpoints & Logic (New module: `backend/app/routes/router.py` and `crud.py`):**
        *   `POST /api/v1/routes/upload`: Allows authenticated user to upload a GPX file. Creates a `Route`, stores GPX.
        *   `POST /api/v1/routes/from_activity/{activity_id}`: Creates a `Route` from an existing activity's GPX data.
        *   `GET /api/v1/routes/`: Lists all routes for the authenticated user.
        *   `GET /api/v1/routes/{route_id}`: Retrieves details for a specific route (including GPX data).
        *   `PUT /api/v1/routes/{route_id}`: Updates route name/description.
        *   `DELETE /api/v1/routes/{route_id}`: Deletes a route.
        *   `PUT /api/v1/activities/{activity_id}/link_route/{route_id}`: Manually links an activity to a route.
        *   `PUT /api/v1/activities/{activity_id}/unlink_route`: Removes activity-route association.
    3.  **CRUD Operations:** Implement corresponding CRUD functions in `backend/app/routes/crud.py`.
    4.  **Schemas:** Define Pydantic schemas in `backend/app/routes/schema.py` for request/response models.
*   **Frontend:**
    1.  **Navigation:** Add "Routes" link in the main navigation bar (e.g., in `frontend/app/src/App.vue` or a layout component).
    2.  **Vue Router:** Add new routes in `frontend/app/src/router/index.js` for:
        *   `/routes` (Routes List Page)
        *   `/routes/create` (or modal for route creation)
        *   `/routes/{id}` (Route Detail Page)
    3.  **Services:** Create `frontend/app/src/services/routesService.js` to interact with the new backend route endpoints.
    4.  **Store (Pinia):** Potentially create a new store module `frontend/app/src/stores/routesStore.js` to manage routes state.
    5.  **Routes List Page (`frontend/app/src/views/RoutesView.vue`):**
        *   Displays a table of user's routes (Name, Source, Date Created, # Activities).
        *   "Create New Route" button/options.
    6.  **Route Creation UI (e.g., `frontend/app/src/components/Routes/RouteCreateForm.vue`):**
        *   Form for GPX upload (name, description, file input).
        *   Mechanism to select an existing activity to create a route from.
    7.  **Route Detail Page (`frontend/app/src/views/RouteDetailView.vue`):**
        *   Display route name, description.
        *   Render map with route track (e.g., using Leaflet.js and a GPX plugin, leveraging `gpx_file_content`).
        *   List associated activities (fetch activities linked to this `route_id`).
    8.  **Activity Association UI:**
        *   On the existing Activity detail page (`frontend/app/src/views/ActivityDetailView.vue` or similar), add UI to link/unlink the activity to/from a route (e.g., a dropdown of available routes).

## Recent Changes / User Input

*   User approved the plan for the "Routes" feature.
*   The implementation will start with Phase 1 as detailed above.
*   Previous work on "Activities List Page Filtering" is now deferred.

## Current Status & Next Steps

*   **Status:** Ready to begin implementation of Phase 1 for the "Routes" feature. Memory Bank is being updated to reflect this new task.
*   **Next Steps (Routes - Phase 1):**
    1.  Update `memory-bank/progress.md` to include the Routes feature.
    2.  Update `memory-bank/systemPatterns.md` to reflect new DB tables and API modules.
    3.  Begin backend implementation:
        *   Define `Route` model and update `Activity` model.
        *   Create Alembic migration scripts.
        *   Develop Pydantic schemas for routes.
        *   Implement CRUD operations for routes.
        *   Create API router and endpoints for routes.
    4.  Proceed with frontend implementation once backend basics are in place.
