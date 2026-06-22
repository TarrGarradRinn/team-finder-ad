from django import forms

from team_finder.forms_mixins import GitHubURLValidationMixin

from .models import Project


class ProjectForm(GitHubURLValidationMixin, forms.ModelForm):

    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
