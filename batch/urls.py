from django.urls import path

from bm_process.dj.view import BetseSimulationView


app_name = "betse"
urlpatterns = [
    # admin
    path('run/', BatchConfig.as_view()),
]

