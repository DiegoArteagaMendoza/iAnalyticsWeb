from rest_framework.routers import SimpleRouter

from apps.media_library.views import MediaFileViewSet

router = SimpleRouter()
router.register("media_files", MediaFileViewSet, basename="media_file")

urlpatterns = router.urls
