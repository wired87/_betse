# views.py
from django.http import StreamingHttpResponse
from time import sleep
import random

from ggoogle.spanner.dj.views.GraphRenderData import event_stream

html_url = r"C:\Users\wired\OneDrive\Desktop\Projects\bm\ggoogle\spanner\dj\views\visualisation\images\g.html"


class LiveUpdateStreamView:
    def __call__(self, request):
        return StreamingHttpResponse(
            event_stream(),
            content_type='text/event-stream'
        )
