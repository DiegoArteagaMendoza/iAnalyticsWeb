from django.urls import path

from apps.page_content.views import PageContentView

urlpatterns = [
    path("page_content/", PageContentView.as_view(), name="page_content"),
]
