from urllib.parse import urlparse

from django import forms

from .constants import GITHUB_ALLOWED_HOSTS


class GitHubURLValidationMixin:

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "")

        if not url:
            return url

        parsed_url = urlparse(url)
        hostname = parsed_url.hostname or ""

        if parsed_url.scheme not in ("http", "https"):
            raise forms.ValidationError(
                "Ссылка должна начинаться с http:// или https://"
            )

        if hostname.lower() not in GITHUB_ALLOWED_HOSTS:
            raise forms.ValidationError(
                "Ссылка должна вести на github.com"
            )

        if parsed_url.path in ("", "/"):
            raise forms.ValidationError(
                "Ссылка должна вести на конкретный ресурс GitHub"
            )

        return url
