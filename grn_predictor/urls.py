from django.urls import path

from betse_app.grn_predictor.view import CreatGrnView

name = "grn"

urlpatterns = [
    # default grn predictor
    path('create/', CreatGrnView.as_view(), name='create'),  # 1
]

