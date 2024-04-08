from django.urls import path,include
from pan_app import views
urlpatterns = [
    path('pan_extraction',views.ext_data_from_pan,name="panapp")
]