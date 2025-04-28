from django.urls import path

from betse_app.grn_predictor.view import CreatGrnView
from betse_app.view import BetseSimulationView

app_name = "betse_app"
urlpatterns = [
    path('run/', BetseSimulationView.as_view()),
    path('grn-create/', CreatGrnView.as_view()),
]

