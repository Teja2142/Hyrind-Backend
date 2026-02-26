# Role Suggestions - Ultra-Simplified System

## Overview

**Ultra-simple role suggestion system** where admins directly type role titles for users - no predefined role database needed!

---

## How It Works

### For Admins

1. **Navigate to Admin Dashboard** → Jobs → Role Suggestions
2. **Add New Role Suggestion**:
   - Select User/Client (autocomplete search)
   - Type Role Title (e.g., "Software Engineer", "Data Analyst")
   - Add optional Category (e.g., "Engineering", "Data Science")
   - Add optional notes explaining why this role is suggested
   - Click Save

**That's it!** No need to maintain a predefined role database.

The system automatically tracks:
- Who added the suggestion (you)
- When it was added
- User's selection status

### For Users/Clients

1. **View Suggestions**: Users see all role suggestions on their dashboard
2. **Select Desired Roles**: Users can select/deselect roles they're interested in
3. **Submit Selections**: Users submit their desired role selections

---

## API Endpoints

### List Role Suggestions (User)
```http
GET /api/jobs/suggestions/
```

**Response:**
```json
{
  "count": 5,
  "selected_count": 2,
  "suggestions": [
    {
      "id": "uuid",
      "role_title": "Software Engineer",
      "role_category": "Engineering",
      "admin_notes": "Great fit based on your Python skills",
      "is_selected": true,
      "selected_at": "2026-02-22T10:30:00Z",
      "added_by_name": "Admin User",
      "created_at": "2026-02-20T09:00:00Z"
    }
  ]
}
```

**Filters:**
- `?status=selected` - Only selected suggestions
- `?status=unselected` - Only unselected suggestions
- `?category=Engineering` - Filter by role category

### Get Suggestion Detail
```http
GET /api/jobs/suggestions/{id}/
```

### Toggle Role Selection
```http
PATCH /api/jobs/suggestions/{id}/toggle/
```

**Body:**
```json
{
  "is_selected": true
}
```

**Response:**
```json
{
  "message": "Role selected successfully",
  "suggestion": {
    "id": "uuid",
    "role_title": "Software Engineer",
    "role_category": "Engineering",
    "is_selected": true,
    "selected_at": "2026-02-22T10:30:00Z",
    "admin_notes": "...",
    "added_by_name": "Admin User",
    "created_at": "..."
  }
}
```

### Submit Selected Roles
```http
POST /api/jobs/suggestions/submit/
```

**Response:**
```json
{
  "message": "Successfully submitted 3 role selections",
  "selected_count": 3,
  "selections": [...]
}
```

### Bulk Select Multiple Roles
```http
POST /api/jobs/suggestions/bulk_select/
```

**Body:**
```json
{
  "suggestion_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response:**
```json
{
  "message": "Successfully selected 3 suggestions",
  "updated_count": 3
}
```

### Get Suggestions by Category
```http
GET /api/jobs/suggestions/by_category/
```

**Response:**
```json
{
  "Engineering": [...],
  "Data Science": [...],
  "Marketing": [...]
}
```

### Get Categories List
```http
GET /api/jobs/suggestions/categories/
```

**Response:**
```json
{
  "categories": ["Engineering", "Data Science", "Marketing"]
}
```

---

## Database Model

### UserRoleSuggestion

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user | ForeignKey | User/client receiving suggestion |
| role_title | CharField(200) | **Role title (admin types this directly)** |
| role_category | CharField(100) | **Optional category (admin types this)** |
| added_by | ForeignKey | Admin who added suggestion |
| admin_notes | TextField | Admin's reason/notes (optional) |
| is_selected | Boolean | User selected this role |
| selected_at | DateTime | When user selected it |
| created_at | DateTime | When suggestion was created |
| updated_at | DateTime | Last update time |

**Key Features:**
- ✅ No foreign key to predefined roles
- ✅ Admin types role titles directly
- ✅ Optional categorization for filtering
- ✅ Simple and flexible

---

## Admin Interface Features

### Role Suggestions Admin

- **Simple Input**: Type role title and category directly - no dropdowns of predefined roles
- **Search**: By username, email, role title, category, or admin notes
- **Filters**: 
  - Selection status (selected/unselected)
  - Role category
  - Creation date
- **List View**: Shows user, role title, category, who added it, selection status
- **Autocomplete**: For user field (easy selection)
- **Auto-tracking**: Automatically records who added each suggestion
- **Descriptions**: Helpful field descriptions guide admins

**Admin can type anything** - "Software Engineer", "Backend Developer", "ML Engineer", etc. No need to create roles beforehand!

---

## Setup Instructions

### Local Development (SQLite)

```bash
# Set environment to local
$env:ENV = "local"

# Apply migrations
& C:/Users/NREDD27/mine/hy_env/Scripts/Activate.ps1
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### Production/Staging (MySQL)

```bash
# Set environment
$env:ENV = "prod"  # or "stag"

# Apply migrations
python manage.py migrate
```

**Note**: Settings automatically use SQLite for `ENV=local` or `ENV=dev`, MySQL for other environments.

---

## Frontend Integration

### Display Suggestions on User Dashboard

```javascript
// Fetch suggestions
fetch('/api/jobs/suggestions/')
  .then(res => res.json())
  .then(data => {
    // Display count
    console.log(`Total: ${data.count}, Selected: ${data.selected_count}`);
    
    // Render suggestions
    data.suggestions.forEach(suggestion => {
      renderSuggestionCard(suggestion);
    });
  });

// Render suggestion card
function renderSuggestionCard(suggestion) {
  return `
    <div class="suggestion-card">
      <h3>${suggestion.role_title}</h3>
      ${suggestion.role_category ? `<span class="category">${suggestion.role_category}</span>` : ''}
      ${suggestion.admin_notes ? `<p>${suggestion.admin_notes}</p>` : ''}
      <label>
        <input 
          type="checkbox" 
          ${suggestion.is_selected ? 'checked' : ''}
          onchange="toggleSelection('${suggestion.id}')"
        />
        Interested in this role
      </label>
      <small>Suggested by ${suggestion.added_by_name}</small>
    </div>
  `;
}

// Toggle selection
function toggleSelection(id) {
  const isSelected = event.target.checked;
  
  fetch(`/api/jobs/suggestions/${id}/toggle/`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    },
    body: JSON.stringify({ is_selected: isSelected })
  })
  .then(res => res.json())
  .then(data => {
    console.log(data.message);
  });
}

// Submit selections
function submitSelections() {
  fetch('/api/jobs/suggestions/submit/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  })
  .then(res => res.json())
  .then(data => {
    alert(data.message);
  });
}
```

---

## Benefits

✅ **No maintenance overhead**: No predefined role database to manage  
✅ **Maximum flexibility**: Admin can suggest ANY role title  
✅ **Fast setup**: Just type and save  
✅ **User-specific**: Tailor suggestions based on each user's profile  
✅ **Simple API**: Clean endpoints for frontend integration  
✅ **Optional categorization**: Add categories for filtering if needed  
✅ **Trackable**: See which users select which roles  

---

## Example Usage

### Admin Flow

1. Admin reviews user profile: "John has 3 years Python experience"
2. Admin goes to Role Suggestions
3. Admin adds:
   - User: John Doe
   - Role Title: `Backend Python Developer`
   - Category: `Engineering`
   - Notes: `Strong match - you have the Python skills we're looking for`
4. Save

### User Flow

1. John logs into dashboard
2. Sees role suggestion: "Backend Python Developer"
3. Reads admin notes
4. Checks the box: "Yes, I'm interested"
5. Submits selections

### Admin Follow-up

1. Admin filters by `is_selected=True`
2. Sees John selected "Backend Python Developer"
3. Admin can proceed with matching John to actual job opportunities

---

## Migration History

- **v3.0** (Feb 2026) - **Ultra-simplified**: Removed predefined JobRole model, admin types roles directly
- **v2.0** (Feb 2026) - Simplified to manual admin-managed system  
- **v1.0** (Previous) - Complex automated recommendation engine (archived)

---

## Testing

```bash
# Local SQLite database
$env:ENV = "local"
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Access admin: http://localhost:8000/admin
# Username: admin
# Add role suggestions and test the API
```


---

## How It Works

### For Admins

1. **Navigate to Admin Dashboard** → Jobs → Role Suggestions
2. **Add New Role Suggestion**:
   - Select User/Client
   - Select Role (from predefined job roles)
   - Add optional notes explaining why this role is suggested
   - Click Save

The system automatically tracks:
- Who added the suggestion (you)
- When it was added
- User's selection status

### For Users/Clients

1. **View Suggestions**: Users see all role suggestions on their dashboard
2. **Select Desired Roles**: Users can select/deselect roles they're interested in
3. **Submit Selections**: Users submit their desired role selections

---

## API Endpoints

### List Role Suggestions (User)
```http
GET /api/jobs/suggestions/
```

**Response:**
```json
{
  "count": 5,
  "selected_count": 2,
  "suggestions": [
    {
      "id": "uuid",
      "role": {
        "id": "uuid",
        "title": "Software Engineer",
        "category": "Engineering",
        "description": "...",
        "required_skills": ["Python", "Django"],
        "min_years_experience": 2,
        "max_years_experience": 5
      },
      "admin_notes": "Great fit based on your Python skills",
      "is_selected": true,
      "selected_at": "2026-02-22T10:30:00Z",
      "added_by_name": "Admin User",
      "created_at": "2026-02-20T09:00:00Z"
    }
  ]
}
```

**Filters:**
- `?status=selected` - Only selected suggestions
- `?status=unselected` - Only unselected suggestions
- `?category=Engineering` - Filter by role category

### Toggle Role Selection
```http
PATCH /api/jobs/suggestions/{id}/toggle/
```

**Body:**
```json
{
  "is_selected": true
}
```

### Submit Selected Roles
```http
POST /api/jobs/suggestions/submit/
```

**Response:**
```json
{
  "message": "Successfully submitted 3 role selections",
  "selected_count": 3,
  "selections": [...]
}
```

### Bulk Select Multiple Roles
```http
POST /api/jobs/suggestions/bulk_select/
```

**Body:**
```json
{
  "suggestion_ids": ["uuid1", "uuid2", "uuid3"]
}
```

### Get Suggestions by Category
```http
GET /api/jobs/suggestions/by_category/
```

**Response:**
```json
{
  "Engineering": [...],
  "Data Science": [...],
  "Marketing": [...]
}
```

### List All Job Roles
```http
GET /api/jobs/roles/
```

### Get Role Categories
```http
GET /api/jobs/roles/categories/
```

---

## Database Models

### UserRoleSuggestion

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user | ForeignKey | User/client receiving suggestion |
| role | ForeignKey | Suggested job role |
| added_by | ForeignKey | Admin who added suggestion |
| admin_notes | TextField | Admin's reason/notes |
| is_selected | Boolean | User selected this role |
| selected_at | DateTime | When user selected it |
| created_at | DateTime | When suggestion was created |
| updated_at | DateTime | Last update time |

### JobRole

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| title | CharField | Role title (e.g., "Software Engineer") |
| category | CharField | Category (e.g., "Engineering") |
| description | TextField | Role description |
| required_skills | JSONField | List of required skills |
| preferred_skills | JSONField | List of preferred skills |
| min_years_experience | Integer | Minimum years required |
| max_years_experience | Integer | Maximum years |
| required_degrees | JSONField | Required education |
| alternative_titles | JSONField | Alternative job titles |
| avg_salary_min | Decimal | Minimum average salary |
| avg_salary_max | Decimal | Maximum average salary |
| is_active | Boolean | Active for suggestions |
| popularity_score | Integer | Popularity ranking |

---

## Admin Interface Features

### Role Suggestions Admin

- **Search**: By username, email, role title, or admin notes
- **Filters**: 
  - Selection status (selected/unselected)
  - Role category
  - Creation date
- **List View**: Shows user, role, who added it, selection status
- **Autocomplete**: For user and role fields (easy selection)
- **Auto-tracking**: Automatically records who added each suggestion

### Job Roles Admin

- **Search**: By title, category, description
- **Filters**: Category, active status, experience level
- **Full CRUD**: Create, read, update, delete roles

---

## Migration

To apply the simplified structure:

```bash
# Activate virtual environment
& C:/Users/NREDD27/mine/hy_env/Scripts/Activate.ps1

# Run migration
python manage.py migrate jobs
```

**Note**: This migration removes the old complex recommendation engine (automatic scoring, skill profiles, feedback system) and replaces it with the simple manual suggestion system.

---

## Removed Features (Old System)

The following complex features were removed for simplicity:

- ❌ Automatic recommendation engine with AI scoring
- ❌ Skill matching algorithms
- ❌ Multiple score components (skill, experience, education)
- ❌ User skill profiles auto-synced from intake sheets
- ❌ Recommendation feedback system
- ❌ Complex profile completeness tracking
- ❌ Automatic role generation based on algorithms

These were replaced with simple admin-managed role suggestions.

---

## Quick Start Guide

### For Admins

1. **Add Job Roles** (if not already done):
   - Go to Admin → Jobs → Job Roles
   - Add common roles in your industry
   - Set categories, skills, experience levels

2. **Add Suggestions for Users**:
   - Go to Admin → Jobs → Role Suggestions
   - Click "Add Role Suggestion"
   - Select user and role
   - Add notes explaining why (optional)
   - Save

3. **Monitor User Selections**:
   - View which roles users are selecting
   - Filter by selected/unselected
   - Use this data for job matching

### For Frontend/Client Integration

1. **Fetch suggestions on dashboard load**:
   ```javascript
   GET /api/jobs/suggestions/
   ```

2. **Display in a card/list format** with:
   - Role title and description
   - Required skills
   - Admin notes
   - Checkbox for selection

3. **Allow toggle selection**:
   ```javascript
   PATCH /api/jobs/suggestions/{id}/toggle/
   Body: { "is_selected": true }
   ```

4. **Submit button** to finalize selections:
   ```javascript
   POST /api/jobs/suggestions/submit/
   ```

---

## Benefits of Simplified System

✅ **Easy for Admins**: Just select user + role, no complex configuration  
✅ **Clear for Users**: Simple list of suggested roles with selection  
✅ **Maintainable**: No complex algorithms to debug  
✅ **Flexible**: Admin can add any role suggestion with reasoning  
✅ **Trackable**: See what users are selecting  
✅ **Fast**: No heavy computations or profile syncing  

---

## Version History

- **v2.0** (Feb 2026) - Simplified to manual admin-managed system
- **v1.0** (Previous) - Complex automated recommendation engine (archived)
