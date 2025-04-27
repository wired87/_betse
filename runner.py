
import shutil
import subprocess

from utils.ggoogle.vertexai import ask_gem
from utils.utils import GraphUtils


class BetseRunner:
    """
    write() → puts data in a buffer (RAM).

    flush() → moves data from buffer to OS file handle.

    os.fsync() → tells the OS to physically write it to disk.

    """

    def __init__(self, save_dir, config_path=None):
        self.phases = [
            "seed",
            "init",
            "sim",
            "plot init",
            "plot sim"
        ]
        self.g = GraphUtils(upload_to="sp")

        self.config_path = config_path or "sample_sim.yaml"
        self.save_dir = save_dir
        print("config_path", config_path)
        print("save_dir", save_dir)

    def execute(self, geo_dest, zip=False):
        print("Start execution")
        phase_stats = self.run_batch()  # dict: status, error, output

        # Save logs

        for k, v in phase_stats.items():
            if v["status"] == "failed":
                save_logs_path = f"{self.save_dir}/{k}_fail_logs.txt"
                cfg_content = open(self.config_path, "r")
                prompt = f"""
                You receive a config file for BETSE (Tiisue stimmulation engine) AND an error message that includes 
                information why the simmulatiino was faield.
                Formulate a short and easy to understand reason why the simulation might faield.

                Extend theis explanation with suggestions on how to adapt the config file to solve the issue by analyzing each line.
                Return nothing but a formell written text of max 3 sentences that best possible describes solution steps in max 3 precise points

                YAML CONFIG CONTENT:
                 {cfg_content}

                ERROR MESSAGE:
                {v}
                """

                response = ask_gem(prompt)

                v = f"""
                {response}
                ================
                OUT
                ===                
                {v}
                """
                with open(save_logs_path, "w") as f:
                    print(v)
                    f.write(v)

        if zip is True:
            # Rm geo folder
            shutil.rmtree(geo_dest)
            # Zip the entire folder
            zip_path = shutil.make_archive(self.save_dir, 'zip', self.save_dir)

            return zip_path
        else:
            """
            SP up proc
            """

            pass

    def upload_sp_process(self):

        import os
        import csv

        csv_data = {}

        for root, _, files in os.walk(self.save_dir):
            for file in files:
                if file.endswith(".csv"):
                    file_path = os.path.join(root, file)
                    with open(file_path, newline='') as f:
                        reader = csv.DictReader(f)
                        rows = list(reader)
                        schema = reader.fieldnames
                        csv_data[file_path] = {
                            "schema": schema,
                            "rows": rows
                        }

        pass

    def run_batch(self):
        phase_stats = {}

        for phase in self.phases:
            print("run", phase)
            try:
                cmd_parts = ["betse"] + phase.split() + [self.config_path]

                result = subprocess.run(
                    cmd_parts,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    text=True,  # auto-decodes stdout/stderr to strings
                    cwd=self.save_dir,
                )
                print("Process finished", result)

                if result.returncode != 0:
                    print(f"{phase} NON exit code 0")
                    phase_stats[phase] = {
                        "status": f"failed", "details": f"{result.stdout.strip(), result.stderr.strip()}",
                    }
                    return phase_stats
                else:
                    phase_stats[phase] = {
                        "status": "success",
                        "details": result.stdout.strip(),
                    }

            except FileNotFoundError:
                phase_stats[phase] = {
                    "status": "failed",
                    "details": "BETSE FileNotFoundError",
                }
            except subprocess.TimeoutExpired:
                phase_stats[phase] = {"status": "failed", "details": "BETSE simulation timed out. 120s"}
            except OSError as e:
                phase_stats[phase] = {"status": "failed", "details": "OSError running BETSE." + str(e)}
            except Exception as e:
                phase_stats[phase] = {"status": "failed", "details": "An unexpected Exception occurred." + str(e)}

        print("Run sum")
        # pprint.pp(phase_stats)
        return phase_stats