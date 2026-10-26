from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.hero.views import HeroHighlightViewSet, HeroSectionManagementView

router = SimpleRouter()
router.register("hero_highlights", HeroHighlightViewSet, basename="hero_highlight")

urlpatterns = [
    path("hero_section/", HeroSectionManagementView.as_view(), name="hero_section"),
    *router.urls,
]
