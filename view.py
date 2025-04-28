import datetime
import json
import os
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

    def validate_cfg(self, grn_config_file, dest_dir, file_name):
        """
        Save custom GRN cfg else retur default path
        """
        if grn_config_file is not None:
            cfg_path = os.path.join(dest_dir, file_name)
            with open(cfg_path, "w") as f:
                f.write(yaml.dump(grn_config_file))
            cfg_path = os.path.abspath(cfg_path)
        else:
            cfg_path = "grn_basic.yaml"
        return cfg_path


    def create_next_folder(self, base_path):
        os.makedirs(base_path, exist_ok=True)  # Create base dir if needed
        items = os.listdir(base_path)
        new_folder_name = f"new_run_{len(items)+1}"
        new_folder_path = f"{base_path}/{new_folder_name}"
        os.makedirs(new_folder_path, exist_ok=True)
        print("Folder created", new_folder_path)
        return new_folder_path

    def set_saving_paths(self, validated_data, user_id, grn_config_file):
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


        # General
        expression_data_file_path = "expression_data.yaml"
        print("expression_data_file_path", expression_data_file_path)
        validated_data["general network"]["expression data file"] = expression_data_file_path

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

        # GRN
        grn_data_file_path = self.validate_cfg(
            grn_config_file,
            dest_dir=save_base_path,
            file_name="grn_cfg.yaml"
        )
        print("grn_data_file_path", grn_data_file_path)
        validated_data["gene regulatory network settings"]["gene regulatory network config"] = grn_data_file_path

        validated_data["gene regulatory network settings"]["sim-grn settings"]["save to directory"] = os.path.join(f"RESULTS","GRN")
        validated_data["gene regulatory network settings"]["sim-grn settings"]["save to file"] = f"GRN_1.betse.gz"

        # Expression data file:
        expression_data_file_path = self.validate_cfg(
            grn_config_file,
            dest_dir=save_base_path,
            file_name="grn_cfg.yaml"
        )
        print("expression_data_file_path", expression_data_file_path)
        validated_data["general network"]["expression data file"] = expression_data_file_path

        # Metabolism Config File




        return validated_data, save_base_path, expression_data_file_path, grn_data_file_path, geo_dest

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

    def post(self, request):
        print("=======================")
        print("Betse Request received")
        print("=======================")
        logger.info("=======================")
        logger.info("Betse Request received")
        logger.info("=======================")

        parsed_data = request.data

        print(parsed_data)
        user_id = TEST_USER_ID

        #base_betse_conc = load_yaml(base_betse_confp).copy()

        serializer = BetseConfigSerializer(data=parsed_data)  # Use the serializer
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data  # Get the validated data

        # Check fro provided config file
        uploaded_file = validated_data.get('sim_config_file')
        if uploaded_file is None:
            validated_data = replace_underscores_in_keys(attributes=validated_data)
        else:
            try:
                file_content = uploaded_file.read().decode('utf-8')
                validated_data = yaml.safe_load(file_content)
            except Exception as e:
                error = f"Error handling provided config file: {e}"
                #print(error)
                return Response(error, status=status.HTTP_400_BAD_REQUEST)


        # Check for custom GRN cfg
        grn_config_file = validated_data.get('grn_config_file')

        (validated_data,
         save_base_path,
         expression_data_file_path,
         grn_data_file_path,
         geo_dest) = self.set_saving_paths(validated_data, user_id, grn_config_file)

        config_path = self.convert_input_to_yaml(validated_data, save_base_path, expression_data_file_path, grn_data_file_path)

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








