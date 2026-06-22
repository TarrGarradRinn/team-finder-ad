from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    # pages
    path('list/', views.List.as_view(), name='list'),
    path('create-project/', views.Create.as_view(), name='create_project'),
    path('<int:project_id>/', views.Detail.as_view(), name='detail'),
    path('<int:project_id>/edit/', views.Edit.as_view(), name='edit_project'),

    # api
    path('<int:project_id>/toggle-participate/',
         views.ToggleParticipation.as_view(), name='toggle_participate'),
    path('<int:project_id>/complete/',
         views.Complete.as_view(), name='complete_project'),
    path('skills/', views.SkillsAutocomplete.as_view(),
         name='skills_autocomplete'),
    path('<int:project_id>/skills/add/',
         views.AddSkill.as_view(), name='add_skill'),
    path('<int:project_id>/skills/<int:skill_id>/remove/',
         views.RemoveSkill.as_view(), name='remove_skill'),
]
