from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    
    # User
    path('register', UserView.register),
    path('login', UserView.login),
    path('logout', UserView.logout),
    path('search-user', UserView.search_user),

    # Task
    path('create-task', TaskView.create_task),
    # path('list-task', TaskView.list_task),
    path('update-task/<pk>', TaskView.update_task),
    path('delete-task/<pk>', TaskView.delete_task),
    # path('list-task', ListTodo.as_view()),
    path('list-task/<pk>', ListTodo.as_view()),
]