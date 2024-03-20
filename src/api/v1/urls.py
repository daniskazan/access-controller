from django.urls import path

from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from api.v1.views.application import ApplicationViewSet
from api.v1.views.user import UserViewSet
from api.v1.views.resource import ResourceViewSet


router = SimpleRouter()

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]


router.register("applications", ApplicationViewSet, basename="applications")
router.register("users", UserViewSet, basename="users")
router.register("resources", ResourceViewSet, basename="resources")
urlpatterns += router.urls
