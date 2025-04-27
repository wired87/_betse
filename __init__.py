"""
Batch Configs
-------------
Collect config sections

Sim
---
Cloud run entry
Compute Engine with unlmtd workers -> only thing changes = input file
Spanner

Save
----
Node types:



Cfg section : each config section gets a node_t incl all variations
File stuff : Each file linked to all its Cfg sections

GNN
---





Erinner dich daran was du wirklih willst.
Betse funktioniert zwar aber du wolltest von anfang an dein gehirn verbessern  !!!



"""
import os

from utils.file.yaml import load_yaml

if os.name == "nt":
    DEFAULT_BETSE_GEOP = r"C:\Users\wired\OneDrive\Desktop\Projects\bm\_betse\betse-1.5.0\betse\data\yaml\geo"
    DEFAULT_BETSE_CONFP = r"C:\Users\wired\OneDrive\Desktop\Projects\bm\_betse\betse-1.5.0\betse\data\yaml\sim_config.yaml"
    DEFAULT_BETSE_GRN = r"C:\Users\wired\OneDrive\Desktop\Projects\bm\_betse\betse-1.5.0\betse\data\yaml\extra_configs\grn_basic.yaml"
    EXPRP=r"C:\Users\wired\OneDrive\Desktop\Projects\bm\_betse\betse-1.5.0\betse\data\yaml\extra_configs\expression_data.yaml"
else:
    DEFAULT_BETSE_GEOP = os.path.abspath(r"_betse/betse-1.5.0/betse/data/yaml/geo")
    DEFAULT_BETSE_CONFP = os.path.abspath(r"_betse/betse-1.5.0/betse/data/yaml/sim_config.yaml")
    DEFAULT_BETSE_GRN = os.path.abspath("_betse/betse-1.5.0/betse/data/yaml/extra_configs/grn_basic.yaml")
    EXPRP = os.path.abspath("_betse/betse-1.5.0/betse/data/yaml/extra_configs/expression_data.yaml")

DEFAULT_BETSE_GRNC = load_yaml(filepath=DEFAULT_BETSE_GRN)
DEFAULT_BETSE_CONTENT = load_yaml(filepath=DEFAULT_BETSE_CONFP)

# THESE SECTIONS KEEP STABLE -> Not include in train process
OUTSOURCED_CONF_SECTIONS = [
    "file handling",
    "sim time settings",
    "init time settings",
    "solver settings",
    "results options",
    "sim config file",
    "automatically run initialization",
    "sim file saving",
    "init file saving",
    "results file saving",
]

CONF_SECTIONS = [
    "gene regulatory network settings",
    "general network",
    "modulator function properties",
    "block NaKATP pump",
    "block gap junctions",
    "general options",
    "world options",
    "tissue profile definition",
    "change Na mem",
    "change K mem",
    "change Cl mem",
    "change Ca mem",
    "apply pressure",
    "apply external voltage",
    "break ecm junctions",
    "cutting event",
    "change K env",
    "change Cl env",
    "change Na env",
    "change temperature"
    "internal parameters",
    "variable settings",
]
