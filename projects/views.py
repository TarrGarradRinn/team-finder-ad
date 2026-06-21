import json

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import Project, Skill


from team_finder.constants import (
    PAGINATE_BY
)
from .constants import (
    STATUS_OPEN,
    STATUS_CLOSED,
)


class List(ListView):
    """Главная страница - список проектов с фильтрацией по навыкам"""

    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    ordering = "-created_at"
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        queryset = super().get_queryset()
        skill = self.request.GET.get("skill")
        if skill:
            queryset = queryset.filter(skills__name=skill)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_skills"] = Skill.objects.values_list(
            "name", flat=True).order_by("name")
        context["active_skill"] = self.request.GET.get("skill")
        return context


class Detail(DetailView):
    """Страница проекта"""

    model = Project
    template_name = "projects/project-details.html"
    context_object_name = "project"
    pk_url_kwarg = "project_id"


class Create(LoginRequiredMixin, CreateView):
    """Создание проекта"""

    model = Project
    fields = ["name", "description", "github_url", "status"]
    template_name = "projects/create-project.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = False
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        form.instance.participants.add(self.request.user)
        return response

    def get_success_url(self):
        return f"/projects/{self.object.id}/"


class Edit(LoginRequiredMixin, UpdateView):
    """Редактирование проекта"""

    model = Project
    fields = ["name", "description", "github_url", "status"]
    template_name = "projects/create-project.html"
    pk_url_kwarg = "project_id"

    def dispatch(self, request, *args, **kwargs):
        project = get_object_or_404(Project, id=kwargs['project_id'])
        if project.owner != request.user:
            return redirect(f"/projects/{project.id}/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context

    def get_success_url(self):
        return f"/projects/{self.object.id}/"


class ToggleParticipation(LoginRequiredMixin, View):
    """Участвовать/отказаться от участия в проекте"""

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        if request.user in project.participants.all():
            project.participants.remove(request.user)
            is_participant = False
        else:
            project.participants.add(request.user)
            is_participant = True
        return JsonResponse({"status": "ok", "is_participant": is_participant})


class Complete(LoginRequiredMixin, View):
    """Завершить проект (только для автора)"""

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)

        if project.owner != request.user:
            return JsonResponse(
                {"status": "error", "message": "Не автор проекта"},
                status=403
            )

        if project.status != STATUS_OPEN:
            return JsonResponse(
                {"status": "error", "message": "Проект уже завершен"},
                status=400
            )

        project.status = STATUS_CLOSED
        project.save()
        return JsonResponse({"status": "ok", "project_status": STATUS_CLOSED})


class SkillsAutocomplete(View):
    """Автодополнение навыков"""

    def get(self, request):
        q = request.GET.get("q", "")
        skills = Skill.objects.filter(name__istartswith=q).order_by("name")[
            :10] if q else Skill.objects.none()
        data = [{"id": skill.id, "name": skill.name} for skill in skills]
        return JsonResponse(data, safe=False)


class AddSkill(LoginRequiredMixin, View):
    """Добавить навык проекту"""

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)

        if project.owner != request.user:
            return JsonResponse({"status": "error"}, status=403)

        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, AttributeError):
            data = request.POST

        skill_id = data.get("skill_id")
        skill_name = data.get("name")

        if not skill_id and not skill_name:
            return JsonResponse({"status": "error"}, status=400)

        if skill_id:
            skill = get_object_or_404(Skill, id=skill_id)
            created = False
        else:
            skill, created = Skill.objects.get_or_create(name=skill_name)

        added = False
        if skill not in project.skills.all():
            project.skills.add(skill)
            added = True

        return JsonResponse({
            "skill_id": skill.id,
            "name": skill.name,
            "created": created,
            "added": added,
        })


class RemoveSkill(LoginRequiredMixin, View):
    """Удалить навык у проекта"""

    def post(self, request, project_id, skill_id):
        project = get_object_or_404(Project, id=project_id)

        if project.owner != request.user:
            return JsonResponse({"status": "error"}, status=403)

        skill = get_object_or_404(Skill, id=skill_id)

        if skill in project.skills.all():
            project.skills.remove(skill)

        return JsonResponse({"status": "ok"})
