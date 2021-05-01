from rest_framework import routers

from .views import ActViewSet, ActToForwardViewSet, DocumentViewSet


router = routers.SimpleRouter()
router.register(r'acts', ActViewSet)
router.register(r'acts-to-forward', ActToForwardViewSet)
router.register(r'documents', DocumentViewSet, basename='document')
urlpatterns = router.urls
