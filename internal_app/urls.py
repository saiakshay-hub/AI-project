from django.urls import path
from . import views

urlpatterns = [
    path("",views.starting_page, name='starting'),
    path('signup/',views.signup, name='signup'),
    path('login/',views.login_view, name='login'),
    path('logout/',views.logoutview,name='logout'),
    path('news/',views.education_news,name="education_news"),
    path('internships/', views.internships, name='internships'),
    path('documentation/', views.documentation, name='documentation'),
    path("ai-tutor/<int:session_id>/", views.ai_tutor, name="aitutor"),
    path('new-chat/', views.new_chat, name='new_chat'),
    path('delete-chat/<int:session_id>/', views.delete_chat, name='delete_chat'),

]
