from django.urls import path

from _betse.grn_predictor.view import CreatGrnView
from _betse.view import BetseSimulationView

app_name = "_betse"
urlpatterns = [
    path('run/', BetseSimulationView.as_view()),
    path('grn-create/', CreatGrnView.as_view()),
]

