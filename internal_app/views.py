from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import SignUpForm, LoginForm

#packages for api integration
import requests
from .models import Question, ChatSession, Internship
from .forms import QuestionForm
from datetime import datetime
from django.contrib.auth.decorators import login_required
from .scraper import get_all_internships


# Create your views here.
def starting_page(request):
    return render(request,"internal/index.html")


def documentation(request):
    # simple informational page; no auth required
    return render(request, "internal/documentation.html")

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save() 
            return redirect('login')
        
    else:
        form = SignUpForm()

    return render(request, 'internal/signup.html', {
        'form': form})


def login_view(request):
    # Force logout of any existing session before new login
    if request.user.is_authenticated:
        logout(request)

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            return redirect('starting')
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()

    return render(request, 'internal/login.html', {'form': form})


def logoutview(request):
    logout(request)  
    messages.success(request, "You have been logged out successfully.")
    return redirect('login') 


def education_news(request):
    api_url = "https://gnews.io/api/v4/search" #the url help me to get response from this api 
    params = {
        "q": "education OR jobs OR employment OR aicareer",  # keywords for my nedded content 
        "lang": "en",
        "country": "in",
        "max": 10,
        "apikey": "93b4a3a99d744afde3fce9589163a0c3"
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # raises error if statuse != 200
        data = response.json()
        news = data.get("articles", [])
    except requests.exceptions.RequestException as e:
        print("Error fetching news:", e)
        news = []

    return render(request, "internal/news.html", {"news": news})


def ai_tutor(request, session_id):
    response_data = None
    api_key = "6149bef7-bdad-41b3-b128-36d9161a4748"
    base_url = "https://api.sambanova.ai/v1/chat/completions"

    # Get the session for this chat
    session = ChatSession.objects.get(id=session_id, user=request.user)

    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.cleaned_data["question"]

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "Meta-Llama-3.1-8B-Instruct",
                "messages": [{"role": "user", "content": question}]
            }

            try:
                response = requests.post(base_url, headers=headers, json=payload)
                response.raise_for_status()
                api_result = response.json()

                # Extract reply
                if "choices" in api_result and len(api_result["choices"]) > 0:
                    response_data = api_result["choices"][0]["message"]["content"]
                else:
                    response_data = "No response received."

                # ✅ Save Q/A with session
                if request.user.is_authenticated:
                    q = Question.objects.create(
                        session=session,       # ✅ IMPORTANT
                        user=request.user,
                        question_text=question,
                        response_text=response_data,
                        asked_at=datetime.now()
                    )

                    # If this session doesn't have a meaningful title yet, set it
                    # to the first question (trimmed) so the sidebar shows the prompt.
                    if not session.title or session.title.strip() == "":
                        session.title = (question[:140]).strip()
                        session.save()

                # ✅ Redirect to same session (this clears input box)
                return redirect("aitutor", session_id=session.id)
        
            except requests.exceptions.RequestException as e:
                response_data = f"Error: {e}"

    else:
        form = QuestionForm()

    # Load only questions from THIS session
    history = Question.objects.filter(session=session).order_by("asked_at")

    # Load all sessions for the left sidebar (so user can switch between sessions)
    sessions = ChatSession.objects.filter(user=request.user).order_by('-id')

    return render(request, "internal/ai-tutor.html", {
        "form": form,
        "data": response_data,
        "history": history,
        "session": session,
        "sessions": sessions,
    })
    
@login_required
def internships(request):
    if request.method == "POST":
        skill = request.POST.get("skill")
        description = request.POST.get("description")

        query = skill if skill else description

        if query:
            query = query.lower().strip()

        data = get_all_internships(query)

        # clear old data
        Internship.objects.all().delete()

        # save to DB
        for item in data:
            Internship.objects.create(
                title=item["title"],
                company=item["company"],
                location=item["location"],
                skills=item["skills_required"],
                apply_link=item["apply_link"],
                source=item["source"]
            )

        internships = Internship.objects.all()

        return render(request, "internal/internship_result.html", {
            "internships": internships,
            "query": query
        })

    return render(request, "internal/internship.html")

@login_required
def new_chat(request):
    # Find the last chat session for this user
    last_session = ChatSession.objects.filter(user=request.user).order_by('-id').first()
    
    # Create a new chat session linked to this user.
    # Leave the title empty so it can be set to the first question asked.
    session = ChatSession.objects.create(
        user=request.user,
        title=""
    )
    
    return redirect("aitutor", session_id=session.id)


@login_required
def delete_chat(request, session_id):
    # Allow users to delete their own chat sessions
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
    except ChatSession.DoesNotExist:
        return redirect('starting')

    if request.method == 'POST':
        session.delete()

        # Redirect to another existing session if present, otherwise create a new one
        next_session = ChatSession.objects.filter(user=request.user).order_by('-id').first()
        if next_session:
            return redirect('aitutor', session_id=next_session.id)
        else:
            return redirect('new_chat')

    # If GET, just redirect back to the tutor view for this session
    return redirect('aitutor', session_id=session_id)