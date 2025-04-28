#query_file


from rest_framework.views import APIView

from betse_app.s.main import BetseConfigSerializer

r"""

Traceback (most recent call last):
  File "C:\Users\wired\OneDrive\Desktop\Projects\bm\venv\lib\site-packages\django\core\handlers\exception.py", line 55, in inner
    response = get_response(request)
  File "C:\Users\wired\OneDrive\Desktop\Projects\bm\venv\lib\site-packages\django\core\handlers\base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
  File "C:\Users\wired\OneDrive\Desktop\Projects\bm\venv\lib\site-packages\django\views\decorators\csrf.py", line 56, in wrapper_view
    return view_func(*args, **kwargs)
  File "C:\Users\wired\OneDrive\Desktop\Projects\bm\venv\lib\site-packages\django\views\generic\base.py", line 104, in view
    return self.dispatch(request, *args, **kwargs)
  File "C:\Users\wired\OneDrive\Desktop\Projects\bm\venv\lib\site-packages\rest_framework\views.py", line 509, in dispatch
    response = self.handle_exception(exc)
  File "C:\Users\wired\OneDrive\Desktop\Projects\bm\venv\lib\site-packages\rest_framework\views.py", line 469, in handle_exception
    self.raise_uncaught_exception(exc)
  File "C:\Users\wired\OneDrive\Desktop\Projects\bm\venv\lib\site-packages\rest_framework\views.py", line 480, in raise_uncaught_exception
    raise exc
  File "C:\Users\wired\OneDrive\Desktop\Projects\bm\venv\lib\site-packages\rest_framework\views.py", line 506, in dispatch
    response = handler(request, *args, **kwargs)
  File "C:\Users\wired\OneDrive\Desktop\Projects\bm\bm_process\dj\view.py", line 236, in post
    os.remove(zip_path)  # now it's safe
PermissionError: [WinError 32] Der Prozess kann nicht auf die Datei zugreifen, da sie von einem anderen Prozess verwendet wird: 'C:\\Users\\wired\\OneDrive\\Desktop\\Projects\\bm\\betse_data\\rajtigesomnlhfyqzbvx\\new_run_2.zip'
2025-04-24 19:36:55,306 - ERROR - Internal Server Error: /betse/run/
Traceback (most recent call last):
  File "C:\Users\wired\OneDrive\Desktop\Projects\bm\venv\lib\site-packages\django\core\handlers\exception.py", line 55, in inner
    response = get_response(request)
  File "C:\Users\wired\OneDrive\Desktop\Projects\bm\venv\lib\site-packages\django\core\handlers\base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
  File "C:\Users\wired\OneDrive\Desktop\Projects\bm\venv\lib\site-packages\django\views\decorators\csrf.py", line 56, in wrapper_view
    return view_func(*args, **kwargs)
  File "C:\Users\wired\OneDrive\Desktop\Projects\bm\venv\lib\site-packages\django\views\generic\base.py", line 104, in view
    return self.dispatch(request, *args, **kwargs)
  File "C:\Users\wired\OneDrive\Desktop\Projects\bm\venv\lib\site-packages\rest_framework\views.py", line 509, in dispatch
    response = self.handle_exception(exc)
  File "C:\Users\wired\OneDrive\Desktop\Projects\bm\venv\lib\site-packages\rest_framework\views.py", line 469, in handle_exception
    self.raise_uncaught_exception(exc)
  File "C:\Users\wired\OneDrive\Desktop\Projects\bm\venv\lib\site-packages\rest_framework\views.py", line 480, in raise_uncaught_exception
    raise exc
  File "C:\Users\wired\OneDrive\Desktop\Projects\bm\venv\lib\site-packages\rest_framework\views.py", line 506, in dispatch
    response = handler(request, *args, **kwargs)
  File "C:\Users\wired\OneDrive\Desktop\Projects\bm\bm_process\dj\view.py", line 236, in post
    os.remove(zip_path)  # now it's safe
PermissionError: [WinError 32] Der Prozess kann nicht auf die Datei zugreifen, da sie von einem anderen Prozess verwendet wird: 'C:\\Users\\wired\\OneDrive\\Desktop\\Projects\\bm\\betse_data\\rajtigesomnlhfyqzbvx\\new_run_2.zip'
[24/Apr/2025 19:36:55] "POST /betse/run/ HTTP/1.1" 500 149507

urchlaufe projekt von researcher stat-end alles was added werden kann, -> wissen wie sich e.g. medika X in zelle Y verhält
"""


def replace_underscores_in_keys(attributes):
    """Recursively replaces underscores with spaces in all dict keys, including nested ones."""
    if isinstance(attributes, dict):
        return {
            replace_key(k): replace_underscores_in_keys(v)
            for k, v in attributes.items()
        }
    elif isinstance(attributes, list):
        return [replace_underscores_in_keys(item) for item in attributes]
    else:
        return attributes


ion_charges = {
    "Na": "Na+",
    "K": "K+",
    "Cl": "Cl-",
    "Ca2": "Ca2+",
    "Mg": "Mg2+",
    "protein": "protein-",
    "anion": "anion-",
    "H": "H+"
}

def replace_key(key):
    # Only skip replacement if BOTH "gradient" AND "sweep" are in the key
    if "gradient" in key or "sweep" in key or "Do" in key or "alpha" in key or "Dm_" in key:
        return key  # skip only special compound keys
    elif "offset" in key:
        return key.replace('_', '-')
    elif key == "sim_grn_settings":
        return "sim-grn settings"
    elif "concentration" in key:
        for ion, ion_with_charge in ion_charges.items():
            if f"{ion}" in key or f"{ion}-" in key or f"{ion}+" in key:
                key = key.replace(ion, ion_with_charge, 1)
    return key.replace('_', ' ')

class BetseResultQueryView(APIView):

    serializer_class = BetseConfigSerializer

    def post(self, request):
        return







