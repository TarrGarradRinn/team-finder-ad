import json
from http import HTTPStatus

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from team_finder.constants import PAGINATE_BY

from .constants import AUTOCOMPLETE_LIMIT, STATUS_CLOSED, STATUS_OPEN
from .forms import ProjectForm
from .models import Project, Skill


class List(ListView):
    """Главная страница - список проектов с фильтрацией по навыкам"""

    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    ordering = "-created_at"
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("owner")
            .prefetch_related("participants", "skills")
        )
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
    form_class = ProjectForm
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
        return reverse("projects:detail", kwargs={"project_id": self.object.id})


class OwnerRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        project = get_object_or_404(Project, id=kwargs["project_id"])

        if project.owner != request.user:
            return redirect(
                reverse("projects:detail", kwargs={"project_id": project.id})
            )

        return super().dispatch(request, *args, **kwargs)


class Edit(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    """Редактирование проекта"""

    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"
    pk_url_kwarg = "project_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context

    def get_success_url(self):
        return reverse("projects:detail", kwargs={"project_id": self.object.id})


class ToggleParticipation(LoginRequiredMixin, View):
    """Участвовать/отказаться от участия в проекте"""

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        is_participant = project.participants.filter(id=request.user.id).exists()

        if is_participant:
            project.participants.remove(request.user)
        else:
            project.participants.add(request.user)

        return JsonResponse({"status": "ok", "is_participant": not is_participant})


class Complete(LoginRequiredMixin, View):
    """Завершить проект (только для автора)"""

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)

        if project.owner != request.user:
            return JsonResponse(
                {"status": "error", "message": "Не автор проекта"},
                status=HTTPStatus.FORBIDDEN
            )

        if project.status != STATUS_OPEN:
            return JsonResponse(
                {"status": "error", "message": "Проект уже завершен"},
                status=HTTPStatus.BAD_REQUEST
            )

        project.status = STATUS_CLOSED
        project.save()
        return JsonResponse({"status": "ok", "project_status": STATUS_CLOSED})


class SkillsAutocomplete(View):
    """Автодополнение навыков"""

    def get(self, request):
        q = request.GET.get("q", "")
        skills = Skill.objects.filter(name__istartswith=q).order_by("name")[
            :AUTOCOMPLETE_LIMIT] if q else Skill.objects.none()
        data = [{"id": skill.id, "name": skill.name} for skill in skills]
        return JsonResponse(data, safe=False)


class AddSkill(LoginRequiredMixin, View):
    """Добавить навык проекту"""

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)

        if project.owner != request.user:
            return JsonResponse({"status": "error"}, status=HTTPStatus.FORBIDDEN)

        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, AttributeError):
            data = request.POST

        skill_id = data.get("skill_id")
        skill_name = data.get("name")

        if not skill_id and not skill_name:
            return JsonResponse({"status": "error"}, status=HTTPStatus.BAD_REQUEST)

        if skill_id:
            skill = get_object_or_404(Skill, id=skill_id)
            created = False
        else:
            skill, created = Skill.objects.get_or_create(name=skill_name)

        added = False
        if not project.skills.filter(id=skill.id).exists():
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
            return JsonResponse({"status": "error"}, status=HTTPStatus.FORBIDDEN)

        skill = get_object_or_404(Skill, id=skill_id)

        if project.skills.filter(id=skill.id).exists():
            project.skills.remove(skill)

        return JsonResponse({"status": "ok"})
