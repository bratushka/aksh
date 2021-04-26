from rest_framework import routers

from .views import ActViewSet, DocumentViewSet


router = routers.SimpleRouter()
router.register(r'acts', ActViewSet)
router.register(r'documents', DocumentViewSet, basename='document')
urlpatterns = router.urls
