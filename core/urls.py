from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from users.views import UserViewSet
from finance.views import TransactionViewSet
from dashboard.views import DashboardSummaryView, AnalyticsView
from users.views import CustomTokenView

router = DefaultRouter()
router.register(r'users',        UserViewSet,       basename='user')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('admin/',               admin.site.urls),
    path('api/',                 include(router.urls)),
    # path('api/auth/login/',      TokenObtainPairView.as_view(),  name='token_obtain'),
    path('api/auth/login/', CustomTokenView.as_view(), name='token_obtain'),
    path('api/auth/refresh/',    TokenRefreshView.as_view(),     name='token_refresh'),
    path('api/dashboard/', DashboardSummaryView.as_view(), name='dashboard'),
    path('api/analytics/', AnalyticsView.as_view(),        name='analytics'),
    path('api/schema/',          SpectacularAPIView.as_view(),   name='schema'),
    path('api/docs/',            SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
]