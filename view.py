import datetime
import json
import os
import pprint
import shutil

from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import yaml

from betse_app import DEFAULT_BETSE_GEOP, EXPRP, DEFAULT_BETSE_GRN
from betse_app.runner import BetseRunner
from betse_app.s.main import BetseConfigSerializer
from bm.settings import TEST_USER_ID
from file.yaml import load_yaml

import logging
logger = logging.getLogger(__name__)

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

class BetseSimulationView(APIView):
    """
    API view to handle BETSE simulation requests.  It expects a full
    BETSE configuration as input, serializes it, saves it to a YAML
    file, runs the simulation, and returns the results.
    """

    serializer_class = BetseConfigSerializer

    def save_logs(self, phase, stdout, stderr, log_file):
        with open(log_file, "a") as f:
            f.write(f"\n--- {phase.upper()} LOG ({datetime.datetime.now().isoformat()}) ---\n")
            f.write(stdout.decode("utf-8"))
            f.write("\n--- ERRORS ---\n")
            f.write(stderr.decode("utf-8"))
            f.write("\n\n")



    def create_folder_structure(self, user_id):
        save_base_path = f"betse_data/{user_id}"
        os.makedirs(save_base_path, exist_ok=True)

        save_base_path = self.create_next_folder(save_base_path)
        print("save_base_path set", save_base_path)

        # Copy Images folder in working dir
        geo_dest = f"{save_base_path}/geo"
        shutil.copytree(
            DEFAULT_BETSE_GEOP,
            geo_dest,
            dirs_exist_ok=True
        )
        return save_base_path, geo_dest


    def create_next_folder(self, base_path):
        os.makedirs(base_path, exist_ok=True)  # Create base dir if needed
        items = os.listdir(base_path)
        new_folder_name = f"new_run_{len(items)+1}"
        new_folder_path = f"{base_path}/{new_folder_name}"
        os.makedirs(new_folder_path, exist_ok=True)
        print("Folder created", new_folder_path)
        return new_folder_path

    def set_saving_paths(self, validated_data, file_paths):
        """

        path handling
        does not work:
        - file name
        - rel from betse_data
        -

        """
        validated_data["general network"]["expression data file"] = "expression_data.yaml" #file_paths["expression_data"]

        validated_data["sim file saving"] = {
            "directory": f"SIMS",
            "file": "sim_1.betse.gz"
        }

        print("validated_data set", validated_data["sim file saving"])

        validated_data["init file saving"] = {
            "directory": f"INITS",
            "file": "init_1.betse.gz",
            "worldfile": "world_1.betse.gz",
        }

        validated_data["results file saving"] = {
            "init directory": os.path.join(f"RESULTS","init_1"),
            "sim directory": os.path.join(f"RESULTS","sim_1"),
        }

        # File handling
        validated_data["file handling"] = {}
        validated_data["file handling"]["init file saving"] = {
            "directory": f"INITS",
            "worldfile": "world_1.betse.gz",
            "file": "init_1.betse.gz"
        }

        validated_data["file handling"]["sim file saving"] = {
            "directory": f"SIMS",
            "file": "sim_1.betse.gz"
        }

        validated_data["file handling"]["results file saving"] = {
            "init directory": os.path.join(f"RESULTS","init_1"),
            "sim directory": os.path.join(f"RESULTS","sim_1"),
        }

        validated_data["gene regulatory network settings"]["gene regulatory network config"] = "grn_basic.yaml" # file_paths["grn_basic"]
        validated_data["gene regulatory network settings"]["sim-grn settings"]["save to directory"] = os.path.join(f"RESULTS","GRN")
        validated_data["gene regulatory network settings"]["sim-grn settings"]["save to file"] = f"GRN_1.betse.gz"

        # Metabolism Config File

        return validated_data



    def get_file_paths(self, files, base_path):
        """
        Get al received files, save them local in final base data folder

        :return: dict include file_name and
        """
        if os.name == "nt":
            base_ref_file_path = r"C:\Users\wired\OneDrive\Desktop\base_dj\betse_app\betse-1.5.0\betse\data\yaml\extra_configs"
        else:
            base_ref_file_path = "betse_app/betse-1.5.0/betse/data/yaml/extra_configs"

        file_paths = {}
        for f in os.listdir(base_ref_file_path):
            file_name = f.split("/")[-1].split(".")[0]
            save_path = os.path.join(base_path, f"{f}")
            # check for missing fields
            if files.get(file_name) is None:
                print(f"File {f} not provided")
                yaml_confc = load_yaml(os.path.join(base_ref_file_path, f"{f}"))
            else:
                print(f"Provided {f}")
                # Write the file to dest data dir (gz folder)
                yaml_confc = files[file_name].read()
                save_path = os.path.join(base_path, f"{f}")

            with open(save_path, "w") as yf:
                yf.write(yaml.dump(yaml_confc, default_flow_style=False, sort_keys=False))

            file_paths[file_name] = save_path

        print("File Paths")
        pprint.pp(file_paths)
        return file_paths


    def read_sim_cfg(self, uploaded_file):
        # Read received cfg
        try:
            file_content = uploaded_file.read().decode('utf-8')
            validated_data = yaml.safe_load(file_content)
        except Exception as e:
            error = f"Error handling provided config file: {e}"
            # print(error)
            return None
        return validated_data

    def post(self, request):
        print("=======================")
        print("Betse Request received")
        print("=======================")
        user_id = TEST_USER_ID
        print("TEST_USER_ID", user_id)

        files = request.FILES
        print("files", files)

        sim_data_json:dict = request.data.get("sim_config_data")
        sim_data_file = files.get("sim_config_file")
        print("sim_data_json", sim_data_json)
        print("sim_data_file", sim_data_file)
        if sim_data_json is None and sim_data_file is None:
            print("Nothing received -> return")
            return Response("Super bad request", status=status.HTTP_400_BAD_REQUEST)

        if sim_data_json is not None:

            validated_data = sim_data_json
            print("Vkeys sim_data_json", [key for key in validated_data.keys()])
        else:

            validated_data=self.read_sim_cfg(sim_data_file)
            print("Vkeys", [key for key in validated_data.keys()])

        if validated_data is None:
            return Response("Content not valid", status=status.HTTP_400_BAD_REQUEST)

        # CREATE FOLDER, SAVE PATHS
        save_base_path, geo_dest = self.create_folder_structure(user_id)
        file_paths:dict = self.get_file_paths(files, base_path=save_base_path)

        # Set saving pathis in cfg
        validated_data = self.set_saving_paths(validated_data, file_paths)

        # save adapted content
        config_path = os.path.abspath(os.path.join(save_base_path, f"sim_config_file.yaml"))
        yaml_confc = yaml.dump(validated_data, default_flow_style=False, sort_keys=False)
        with open(config_path, "w") as yf:
            yf.write(yaml_confc)

        # 4. Execute BETSE Simulation
        betse_runner = BetseRunner(
            config_path=config_path,
            save_dir=save_base_path,
        )

        zip_path = betse_runner.execute(geo_dest, zip=True)
        bz_content = open(zip_path, "rb")

        # Remove local content todo -> cloud
        shutil.rmtree(save_base_path)

        print("Process finished")
        return FileResponse(
            bz_content,
            as_attachment=True,
            filename=os.path.basename(zip_path),
            content_type="application/zip"
        )



"""


    def convert_input_to_yaml(
            self,
            validated_data,
            save_base_path,
            expression_data_file_path,
            grn_data_file_path

    ):
        config_path = "betse_config.yaml"
        # 2. Convert to YAML
        try:
            yaml_confc = yaml.dump(validated_data, default_flow_style=False, sort_keys=False)
            yaml_exprc = yaml.dump(load_yaml(EXPRP), default_flow_style=False, sort_keys=False)
            yaml_grnc = yaml.dump(load_yaml(DEFAULT_BETSE_GRN), default_flow_style=False, sort_keys=False)
        except yaml.YAMLError as e:
            return Response(
                {"error": "Failed to convert data to YAML", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 3. Save YAML to File
        try:
            # General config
            with open(os.path.join(save_base_path, config_path), "w") as f:
                f.write(yaml_confc)
                f.flush()
                os.fsync(f.fileno())

            # Expression Data
            with open(os.path.join(save_base_path, "expression_data.yaml"), "w") as f:
                f.write(yaml_exprc)
                f.flush()
                os.fsync(f.fileno())

            # GRN Data
            with open(os.path.join(save_base_path, "grn_basic.yaml"), "w") as f:
                f.write(yaml_grnc)
                f.flush()
                os.fsync(f.fileno())

        except OSError as e:
            return Response(
                {"error": "Failed to write YAML to file", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return config_path
"""






