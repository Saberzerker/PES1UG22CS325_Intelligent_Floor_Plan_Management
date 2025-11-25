# Conflict Resolution Demo Logs\n\nThis file documents **example** conflict resolution events used in the Floorings demo.\nThese are not live system logs, but sample entries you can talk through during the demo.\n\n---\n\n## Sample Events\n\n1. `2025-11-24 18:30`  \
   **Floor Plan**: MoveInSync HQ - Floor 1  \
   **Users**: admin_demo vs admin_beta  \
   **Resolution Strategy**: Timestamp priority (latest wins)  \
   **Outcome**: Auto-resolved. Latest edit to seating layout kept.  \
   **Notes**: Older version stored in version history for rollback.\n\n2. `2025-11-24 17:10`  \
   **Floor Plan**: MoveInSync HQ - Floor 2  \
   **Users**: admin_demo vs admin_gamma  \
   **Resolution Strategy**: Role priority (admin wins)  \
   **Outcome**: admin_demo changes accepted, conflicting edits rejected.  \
   **Notes**: Rejected changes serialized into conflict record for audit.\n\n3. `2025-11-24 19:05`  \
   **Floor Plan**: MoveInSync HQ - Floor 1  \
   **Users**: admin_demo (online) vs admin_beta (offline queue)  \
   **Resolution Strategy**: Hybrid (timestamp + semantic merge)  \
   **Outcome**: Non-overlapping changes merged, overlapping capacity edits resolved using latest timestamp.  \
   **Notes**: Merge summary displayed in Admin Panel under Version History.\n\n---\n\n## Demo Explanation\n\nIn the demo Admin Panel (`/admin-panel`):\n\n- The **Conflicts** tab shows mock conflicts derived from entries like these.\n- The **Version History** tab presents merged versions such as *"Floor 1 – v3"* that result from auto/assisted resolution.\n- The **Activity Log** tab mirrors high-level lines such as:\n  - `admin_demo auto-resolved 2 conflict(s) at 2025-11-24 19:15 using timestamp priority.`\n  - `admin_demo approved merge for Floor 1 v3.`\n\nThese examples illustrate how a real implementation would log:\n\n- Which floor plan was affected.\n- Which users were involved.\n- What resolution strategy was applied.\n- Whether the resolution was automatic or manual.\n- Where to inspect the resulting version in the UI.\n
