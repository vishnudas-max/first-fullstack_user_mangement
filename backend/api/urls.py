from . import views
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    path('user/register/', views.RegisterView.as_view(),name='register'),
    path('',views.getAccountsRoutes.as_view(),),
    path('user/login/',views.LoginView.as_view(),name='login'),
    path("user/current", views.UserView.as_view(), name="user-current"),
    path("user/detail/", views.UserDetails.as_view(), name="user-details"),
    path("user/detail/update", views.UserDetailsUpdate.as_view(), name="user-details-update"),

    path('admin/users/', views.AdminUserListCreateView.as_view(), name='admin-user-list-create'),
    path('admin/users/view/<int:id>', views.AdminUserRetrieveView.as_view(), name='admin-user-view-by-id'),
    path('admin/users/user-update/<int:id>', views.AdminUserUpdateView.as_view(), name='admin-user-view-by-id'),
    path('admin/users/user-delete/<int:id>',views.AdminUserDelete.as_view(),name='admin-delete-user'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
