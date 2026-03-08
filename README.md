# AI-Guided Web Application

This Django project provides a simple full-stack environment with user
authentication, an AI chat tutor, education news integration, and an internship
finder module. The design centres around educating and assisting students with
resources powered by APIs and internal models.

---

## 🚀 Features

1. **User Management**
   - Sign up, log in, and log out using Django's built-in auth system.
   - Forms customized for a better UX (placeholders, validation messages).

2. **AI Tutor**
   - Chat interface where users ask questions and receive responses from the
     `Meta-Llama-3.1-8B-Instruct` model via the SanbanoVa API.
   - Conversations are grouped into sessions; each session stores question/
     answer history in the database (`ChatSession`, `Question` models).
   - Sessions can be created, deleted, and renamed automatically based on the
     first prompt.

3. **Education News**
   - Fetches the latest education/employment-related articles from the [GNews
     API](https://gnews.io/) and displays them to users.

4. **Internship Finder**
   - **Static prototype** originally shipped with hard-coded cards and
     JavaScript filtering.
   - **Back-end logic** (added in this release) uses a new `Internship` model to
     store postings and a view that applies GET-parameter filters.
   - Template now renders internships dynamically; users can search by skill,
     stipend, work-from-home, part-time, etc.
   - Database-backed approach allows future enhancements such as importing data
     from external APIs or user submissions.

5. **Administrative Dashboard**
   - Django admin is customized with site headers/titles and includes question
     and internship models for easy content management.

6. **Static Assets and Templates**
   - CSS located under `internal_app/static/internal/`.
   - HTML templates in `internal_app/templates/internal/` with `base.html`
     providing a shared layout.

---

## 📁 Project Structure

```
ai_guided/                  # Django project root
├── ai_guided/              # Settings, URLs, WSGI/ASGI
├── internal_app/           # Main application
│   ├── models.py           # Database models (ChatSession, Question, Internship...)
│   ├── views.py            # Request handlers and business logic
│   ├── forms.py            # Django forms for signup, login, questions
│   ├── urls.py             # App URL patterns
│   ├── templates/internal/ # HTML templates used by the app
│   └── static/internal/    # CSS, images, and JS used by templates
├── manage.py               # Django management utility
└── db.sqlite3              # Default SQLite database (for development)
```

---

## 🛠️ Setup & Installation

1. **Create and activate a virtual environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```
   *(create `requirements.txt` by running `pip freeze > requirements.txt`)*

3. **Apply migrations**
   ```powershell
   python manage.py migrate
   ```

4. **Create a superuser (optional, for admin access)**
   ```powershell
   python manage.py createsuperuser
   ```

5. **Run the development server**
   ```powershell
   python manage.py runserver
   ```

6. **Visit** `http://127.0.0.1:8000/` in your browser.

---

## 🔧 Internship Finder Implementation

The internship finder initially provided a purely front‑end prototype.  To make
it functional:

1. **Model**
   ```python
   class Internship(models.Model):
       title = models.CharField(max_length=255)
       company = models.CharField(max_length=255)
       location = models.CharField(max_length=255, blank=True)
       work_from_home = models.BooleanField(default=False)
       part_time = models.BooleanField(default=False)
       stipend_min = models.IntegerField(null=True, blank=True)
       stipend_max = models.IntegerField(null=True, blank=True)
       duration_months = models.IntegerField(null=True, blank=True)
       start_date = models.DateField(null=True, blank=True)
       skills = models.CharField(max_length=512, blank=True)
       post_offer = models.CharField(max_length=255, blank=True)
       description = models.TextField(blank=True)
       posted_at = models.DateTimeField(auto_now_add=True)
   ```

2. **View**
   ```python
   @login_required
def internships(request):
    qs = Internship.objects.all()
    # apply filters based on request.GET (see code in views.py above)
    return render(request, 'internal/internship.html', {'internships': qs})
   ```

3. **URL routing**
   ```python
   path('internships/', views.internships, name='internships')
   ```

4. **Template changes**
   - Use a loop to render `internships` from the context instead of hard-coding
     cards.
   - Provide an HTML form whose inputs correspond to the GET parameters
     consumed by the view.

5. **Admin registration** so staff can add/edit postings.
   ```python
   admin.site.register(Internship)
   ```

6. **Populate data**: either manually via the admin, or write a management
   command/script to pull listings from an external API (e.g. LinkedIn or
   Handshake) and save them to the database.

The documentation within the project (see `internal_app/templates/internal/documentation.html`) reiterates these steps and shows example queries.

---

## ✅ Next Steps & Enhancements

- Add authentication-protected user profiles to save favourite internships.
- Establish an API endpoint to fetch internships so the front end can do
  asynchronous filtering.
- Persist chat sessions in a more scalable database (PostgreSQL) and add
  pagination.
- Implement caching for external API responses (news, AI tutor) to reduce
  latency and hit counts.
- Improve front-end using a JS framework (React/Vue) if interactivity grows
  more complex.

---

## 📄 Documentation Page

A user-facing HTML page (`/documentation/`) has been added to house the
information above inside the application.  This allows students to view
project details without leaving the site.

---

Feel free to expand or modify the documentation as the project evolves!  The
source is under `internal_app/templates/internal/documentation.html` if
you need to adjust the HTML directly.