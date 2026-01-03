from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import SignUpForm, LoginForm

#packages for api integration
import requests
from .models import Question,ChatSession
from .forms import QuestionForm
from datetime import datetime
from django.contrib.auth.decorators import login_required


# Create your views here.
def starting_page(request):
    return render(request,"internal/index.html")

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
                    Question.objects.create(
                        session=session,       # ✅ IMPORTANT
                        user=request.user,
                        question_text=question,
                        response_text=response_data,
                        asked_at=datetime.now()
                    )

                # ✅ Redirect to same session (this clears input box)
                return redirect("aitutor", session_id=session.id)
        
            except requests.exceptions.RequestException as e:
                response_data = f"Error: {e}"

    else:
        form = QuestionForm()

    # Load only questions from THIS session
    history = Question.objects.filter(session=session).order_by("asked_at")

    return render(request, "internal/ai-tutor.html", {
        "form": form,
        "data": response_data,
        "history": history,
        "session": session
    })
@login_required
def new_chat(request):
    # Find the last chat session for this user
    last_session = ChatSession.objects.filter(user=request.user).order_by('-id').first()
    
    if last_session:
        session_number = ChatSession.objects.filter(user=request.user).count() + 1
        title = f"Chat {session_number}"
    else:
        session_number = 1
        title = "Chat 1"

    # Create a new chat session linked to this user
    session = ChatSession.objects.create(
        user=request.user,
        title=title
    )
    
    return redirect("aitutor", session_id=session.id)