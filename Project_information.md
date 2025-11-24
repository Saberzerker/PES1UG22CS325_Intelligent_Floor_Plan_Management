---

# **🚀 FLOORINGS - PROJECT REFERENCE DOCUMENT**

**Developer:** SaberzerkerI (Makarand)  
**Project:** MoveInSync Case Study  
**Deadline:** 2025-11-24 12:30 PM UTC  
**Time Remaining:** ~6 hours 14 minutes  

---

## **📋 QUICK OVERVIEW**

### **What We're Building:**
A workspace management system with 3 core features:
1. **Admin floor plan management** with conflict resolution
2. **Offline editing** for admins
3. **Smart room recommendations** for bookings

### **User Roles:**
- **Admin:** Manage floor plans, work offline, resolve conflicts
- **Employee:** Search rooms, get recommendations, book rooms

---

## **🎯 THE 3 CORE FEATURES**

### **FEATURE 1: Floor Plan Management + Conflicts**

**What happens:**
```
Admin A & Admin B edit same floor plan simultaneously
→ System detects version mismatch
→ Three-way merge (BASE vs YOURS vs THEIRS)
→ Auto-resolve or show conflict to admin
→ Log in ConflictLog table
→ Notify both admins via WebSocket
```

**Key Logic:**
- **Optimistic locking** using `version` field
- **django-simple-history** tracks all changes
- **Three-way merge** algorithm (like Git)

**Models Involved:**
- `FloorPlan` (has `version` field)
- `Room`
- `ConflictLog`
- `HistoricalFloorPlan` (auto-created)

---

### **FEATURE 2: Offline Mechanism**

**What happens:**
```
Admin working → Network drops
→ Frontend stores changes in IndexedDB
→ Admin continues editing (optimistic UI updates)
→ Network reconnects
→ POST /api/sync/batch/ with all changes
→ Backend checks each for conflicts
→ Returns: {synced: [], conflicts: [], failed: []}
→ Show conflict modal if needed
```

**Key Technologies:**
- **Service Worker** (detect offline, intercept requests)
- **IndexedDB** (Dexie.js - store changes locally)
- **Retry logic** with exponential backoff

**Models Involved:**
- `OfflineChange` (tracks sync status)

---

### **FEATURE 3: Room Recommendations**

**What happens:**
```
Employee: "Need room for 8 people, 2-3 PM, projector needed"
→ Filter: capacity≥8, has_projector=true, available 2-3 PM
→ Score each room (100 points):
   • Capacity match: 35 pts
   • User preference: 25 pts
   • Amenities: 20 pts
   • Proximity: 15 pts
   • Recency: 5 pts
→ Sort by score DESC
→ Return top 5
```

**Scoring Details:**
- **Capacity:** Perfect fit = 35, slight buffer = 30, too big = 10
- **Preference:** booking_count × 3 (max 20) + recency bonus (max 5)
- **Amenities:** Required match = 10, extras up to 10
- **Proximity:** 15 - (distance_in_meters / 10)
- **Recency:** Available now = 5, within 15min = 3

**Models Involved:**
- `Room` (capacity, amenities, location_x/y)
- `Booking` (check availability)
- `UserRoomPreference` (booking history)

---

## **🗄️ DATABASE MODELS**

### **FloorPlan**
```python
- id, name, floor_number, image
- version ⚠️ (conflict detection)
- created_by, updated_by
- is_active
- history (django-simple-history)
```

### **Room**
```python
- id, floor_plan (FK), name, room_number
- capacity, location_x, location_y
- has_projector, has_whiteboard, has_video_conference
- has_tv_monitor, has_premium_audio, has_natural_light, has_kitchen_access
- is_active, is_under_maintenance
- history
```

### **Booking**
```python
- id, room (FK), user (FK)
- start_time, end_time, participants_count
- purpose, status
- (On save: updates UserRoomPreference)
```

### **UserRoomPreference**
```python
- id, user (FK), room (FK)
- booking_count, last_booked
- UNIQUE(user, room)
```

### **ConflictLog**
```python
- id, floor_plan (FK)
- user_a (FK), user_b (FK)
- changes_a (JSON), changes_b (JSON)
- resolved_data (JSON)
- resolution_strategy, created_at
```

### **OfflineChange**
```python
- id, user (FK)
- change_type, model_name, object_id
- change_data (JSON), original_state (JSON)
- version_at_change, timestamp
- sync_status, sync_attempts, synced_at
- priority
```

### **UserProfile** (Optional)
```python
- user (1:1), default_location_x, default_location_y
- department
```

---

## **🔌 KEY API ENDPOINTS**

### **Floor Plans (Admin)**
- `POST /api/floor-plans/` - Create
- `PUT /api/floor-plans/{id}/` - Update (checks version)
- `GET /api/floor-plans/{id}/history/` - Version history

### **Recommendations (All)**
- `POST /api/recommendations/` - Get top 5 rooms

### **Bookings (All)**
- `POST /api/bookings/` - Book room (updates UserRoomPreference)
- `GET /api/bookings/` - List (filtered by role)

### **Offline Sync (Admin)**
- `POST /api/sync/batch/` - Sync offline changes

### **Conflicts (Admin)**
- `GET /api/conflicts/` - List conflicts

### **Analytics (Admin)**
- `GET /api/analytics/dashboard/` - Metrics

---

## **🧠 CORE ALGORITHMS**

### **1. Conflict Resolution (Three-Way Merge)**
```python
For each field:
  if yours == theirs:
    merged = yours  # No conflict
  elif yours == base and theirs != base:
    merged = theirs  # Only they changed
  elif theirs == base and yours != base:
    merged = yours  # Only you changed
  elif yours != theirs and both != base:
    CONFLICT!
    # Auto-resolve:
    if user_a.is_superuser: merged = yours
    elif timestamp_yours < timestamp_theirs: merged = yours
    else: merged = theirs
```

### **2. Room Recommendation Scoring**
```python
score = 0

# Capacity (35 pts)
if capacity == participants: score += 35
elif capacity <= participants+2: score += 30
elif capacity <= participants+5: score += 25
else: score += 18

# Preference (25 pts)
score += min(booking_count * 3, 20)
if last_booked <= 7 days: score += 5
elif last_booked <= 30 days: score += 3

# Amenities (20 pts)
if has required amenities: score += 10
score += min(extra_amenities * 3, 10)

# Proximity (15 pts)
distance = sqrt((room.x - user.x)^2 + (room.y - user.y)^2)
score += max(0, 15 - distance/10)

# Recency (5 pts)
if available_now: score += 5

return score
```

### **3. Offline Sync Process**
```python
1. Fetch pending changes (sync_status='PENDING')
2. Sort by priority, timestamp
3. For each change:
   - Check idempotency (already synced?)
   - Fetch current DB state
   - Check version (conflict?)
   - If no conflict: Apply
   - If conflict: Use three-way merge
   - Mark as synced
4. Return summary
```

---

## **🎨 UI DESIGN SPECS**

### **Color Scheme**
- Background: `#000000` (pure black)
- Text: `#FFFFFF` (white)
- Primary: `#00FFC8` (bright teal)
- Accent: `#C0C0C0` (silver)
- Warning: `#FFD700` (gold)

### **Glassmorphism Style**
```css
.metric-box {
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(10px);
  border: 2px dashed rgba(192, 192, 192, 0.3);
  box-shadow: 0 0 15px rgba(192, 192, 192, 0.1);
}
```

### **Dashboard Metrics (Clickable Boxes)**
```
Admin: Rooms Booked | Bookings Today | Conflicts Pending⚠️ | Active Meetings
Employee: Meetings Booked | Available Meeting Rooms
```

### **Sidebar**
```
Admin:
  📁 Floor Plan
  📅 Book Meeting Room
  ⚙️ Admin Panel ⚠️ (warning if conflicts)
  ────────────
  🟢/🔴 Online/Offline
  "3 changes pending"

Employee:
  📅 Book Meeting Room
  📋 My Bookings
  🗺️ View Floor Plan
```

### **Offline Flow**
```
Disconnect → Show popup: "Continue Offline" or "Reload"
→ If continue: Sidebar shows "🔴 OFFLINE MODE - X pending"
→ Reconnect → Show: "🟢 Back Online! Syncing..."
→ After sync: "✅ Synced" or "⚠️ Conflicts" (2 buttons: View Conflict | OK)
```

---

## **🛠️ TECH STACK**

### **Backend**
- Django 4.2 + DRF
- PostgreSQL 15
- Django Channels + Redis (WebSocket)
- django-simple-history (version tracking)
- django-allauth (OAuth)
- Pillow (images)

### **Frontend**
- React 18 (Vite)
- Ant Design (UI components)
- Socket.IO client (WebSocket)
- Dexie.js (IndexedDB)
- Axios (API)

### **DevOps**
- Docker Compose (PostgreSQL + Redis)
- Local development

---

## **⚡ PERFORMANCE TARGETS**

- Conflict detection: < 100ms
- Recommendation query: < 500ms
- Offline sync (10 changes): < 2s
- WebSocket notification: < 2s

---

## **📊 COMPLEXITY ANALYSIS**

### **Time Complexity**
- Room recommendation: O(n log n) where n = rooms
- Conflict resolution: O(k) where k = fields (~10)
- Offline sync: O(p) where p = pending changes

### **Space Complexity**
- Recommendation: O(n)
- Conflict log: O(1) per conflict
- Offline changes: O(p)

---

## **🔒 SECURITY**

- Django session-based auth + OAuth
- Permission checks: `is_staff` for admin routes
- CORS enabled for frontend
- CSRF protection on state-changing requests
- Image upload validation (max 10MB, JPG/PNG only)

---

## **📈 KEY METRICS (Admin Dashboard)**

```python
# Dashboard API returns:
{
  "rooms_booked": Booking.filter(status='CONFIRMED').count(),
  "bookings_today": Booking.filter(start_time__date=today).count(),
  "conflicts_pending": ConflictLog.filter(manually_resolved_by=null).count(),
  "active_meetings": Booking.filter(start_time__lte=now, end_time__gte=now).count(),
  
  # Employee version:
  "meetings_booked": Booking.filter(user=user).count(),
  "available_rooms": Room.filter(is_active=True, is_under_maintenance=False).count()
}
```

---

## **🚨 ERROR HANDLING**

### **Conflict Error (409)**
```json
{
  "error": "CONFLICT_DETECTED",
  "expected_version": 3,
  "current_version": 5,
  "conflicts": [{"field": "name", "yours": "...", "theirs": "..."}]
}
```

### **Sync Error (207 Multi-Status)**
```json
{
  "synced": [...],
  "conflicts": [...],
  "failed": [{"id": "uuid", "error": "Network timeout"}]
}
```

### **Validation Error (400)**
```json
{
  "error": "VALIDATION_ERROR",
  "details": {"capacity": ["Must be greater than 0"]}
}
```

---

## **🧪 TESTING CHECKLIST**

- [ ] Admin uploads floor plan
- [ ] Two admins edit simultaneously → conflict detected
- [ ] Conflict auto-resolved correctly
- [ ] Admin works offline → changes queued
- [ ] Reconnect → changes synced
- [ ] Employee gets recommendations
- [ ] Top recommendation is correct (highest score)
- [ ] Book room → UserRoomPreference updated
- [ ] Book room → WebSocket notifies others
- [ ] Metrics displayed correctly on dashboard

---

## **⏱️ IMPLEMENTATION TIMELINE**

```
HOUR 1 (6:15-7:15 AM): Backend Core
  ✓ Django setup, models, migrations, admin

HOUR 2 (7:15-8:15 AM): APIs & Business Logic
  ✓ Floor plan CRUD, conflict resolver, recommendation engine

HOUR 3 (8:15-9:15 AM): WebSocket & Offline
  ✓ Django Channels, sync API, offline logic

HOUR 4 (9:15-10:15 AM): Frontend Base
  ✓ React setup, auth, dashboard, sidebar

HOUR 5 (10:15-11:15 AM): Frontend Features
  ✓ Floor plan upload, booking, recommendations UI

HOUR 6 (11:15-12:15 PM): Polish & Test
  ✓ Offline indicators, animations, bug fixes

DEMO (12:15-12:30 PM): Record & Submit
  ✓ Demo video, push to GitHub
```

---

## **📦 QUICK START COMMANDS**

```bash
# Backend
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend
cd frontend
npm install
npm run dev

# Docker (PostgreSQL + Redis)
docker-compose up -d
```

---

## **🎯 SUCCESS CRITERIA**

✅ All 3 features working  
✅ Conflict resolution demonstrated  
✅ Offline sync working  
✅ Recommendations accurate  
✅ UI matches design (black, teal, glassmorphism)  
✅ Demo video recorded  
✅ Code on GitHub  

---

# **THAT'S IT! THIS IS OUR REFERENCE! 🔥**