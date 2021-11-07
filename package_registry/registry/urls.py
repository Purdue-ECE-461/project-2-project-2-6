from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.apiOverview),
    path('packages/', views.packages_middleware, name='packages_middleware'),
    path('package/<int:pk>', views.package_middleware, name='package'),
    path('package/', views.create_package_middleware, name='create'),
    path('package/byName/<str:name>', views.byName_middleware, name='byName')

]