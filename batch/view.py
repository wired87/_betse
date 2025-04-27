import asyncio
import os

from rest_framework.views import APIView

from bm_process.dj import DEFAULT_BETSE_CONTENT, DEFAULT_BETSE_GEOP
from bm_process.dj.s.main import BetseConfigSerializer
from utils.utils import GraphUtils


class BatchSimView(APIView):

    """
    Represent step 2 of the Pipe (Step 1 = CR-entry)
    Workflow:
    Loop though all items of the content field. compare each top lvl key name to a given list.
    if inside: validate the key to run a specific method on it
    """
    request_url = None # todo
    serializer_class = BetseConfigSerializer
    phases = [
        "noise", # add small, random changes in params
        "single",  # isolate individual effects
        "pair",  # capture direct 2-way interactions
        "grouped", # variations between parameter groups (e.g. all ion influencers)
        "sum"  # capture cumulative, nonlinear/global effects
    ]
    current_phase="single"
    g_utils = GraphUtils(upload_to="sp")
    spacial_functions = ['gradient_x', 'gradient_y', 'gradient_r', 'None', "f_sweep", "gradient_bitmap", "single_cell", "periodic"]
    gradient_multipliers = [0.5, 1, 1.5, 2]
    comp_grid_steps = 5
    multiplier_steps = [
        0,
        .25,
        .5,
        .75,
        1,
        1.25,
        1.5,
        1.75,
        2
    ]
    len_sim = 100
    all_ion_profiles = [
        "basic",
        "basic_Ca",
        "mammal",
        "amphibian",
        "custom"
    ]
    def post(self, request):
        change_ion_conc_enc_content = DEFAULT_BETSE_CONTENT.copy()
        content = DEFAULT_BETSE_CONTENT.copy()
        noise_content = None
        for k,v in content["general options"]:  # start line 91 default cnf
            # todo defineire beim loop gleich schritt "sum" u. "noise" -> auslagern ordentlicher
            # Reset comp grids min.
            if k == "comp grid size":
                comp_content = DEFAULT_BETSE_CONTENT.copy()
                comp_content[k]["comp grid size"] = 10
                for _ in range(8):  # 8 loops with more cells
                    comp_content[k]["comp grid size"] += self.comp_grid_steps
                    self.all_variations(comp_content)
            elif k == "ion profile":
                profile_content = DEFAULT_BETSE_CONTENT.copy()
                for profile in self.all_ion_profiles:
                    profile_content["general options"][k] = profile
                    self.all_variations(profile_content)
            elif k == "customized ion profile":
                # Multiply each Conc
                grouped_custom_ion_content=DEFAULT_BETSE_CONTENT.copy() # todo

                for key, value in grouped_custom_ion_content.items(): # extracellular Na+ concentration
                    single_custom_ion_content = DEFAULT_BETSE_CONTENT.copy()

                    for multiplier in self.multiplier_steps:
                        single_custom_ion_content["general options"][key] *= multiplier
                        self.all_variations(single_custom_ion_content)


            # ----------------------------------------------------------------------------------------------------------------------
            # GLOBAL INTERVENTIONS
            # ----------------------------------------------------------------------------------------------------------------------
            # Change Ion Conc env
            """elif k.startswith("change") and k.endswith("env"):
                for k, v in v.items()"""



        for k,v in content["world options"]:
            if k in ["world size", "cell radius", "cell height", "cell spacing", "lattice disorder", "alpha shape"]:
                world_options_multiply_content = DEFAULT_BETSE_CONTENT.copy()

                for multiplier in self.multiplier_steps:
                    world_options_multiply_content["world_options"][k] *= multiplier
            elif k=="simulate single cell":
                #todo
                return


        #### MULTIPLY ALL VALUES
        async def change_all_vals(content):
            for k,v in content["general options"]:  # start line 91 default cnf
                if isinstance(v, dict):
                    for key, val in v.items():
                        list_exists = any(isinstance(item, (list)) for item in val)
                        if list_exists:
                            for item in val:
                                item = await change_all_vals(content = item)

                """if isinstance(v, bool):
                if isinstance(v, str):
                if isinstance(v, list):"""
                if isinstance(v, int):
                    content[k] *= v
                return content


        for multiply in self.multiplier_steps:
            content=DEFAULT_BETSE_CONTENT.copy()
            content=  change_all_vals(content)
            self.all_variations(content)


        #### MULTIPLY GROUPED VALUES

    def all_variations(self, content):
        for key, value in content.items():
            if key.startswith("change") or key.startswith("break") or key.startswith("block"):
                if self.current_phase == "single":
                    asyncio.run(self.handle_block_change(self.multiplier_steps, key, self.len_sim))

            elif key.startswith("apply"):
                asyncio.run(self.handle_apply(self.multiplier_steps, key, self.len_sim))

            elif key == "modulator function properties":
                asyncio.run(self.handle_apply(self.multiplier_steps, key, self.len_sim))

    async def handle_apply(self, multiplier_steps, key, len_sim):
        """

        runs * multiplier * boundary

        """
        async def run_sim(multiplier, key, len_sim):
            content = self.set_event_base(
                content=DEFAULT_BETSE_CONTENT.copy(),
                key=key,
                len_sim=len_sim
            )

            if key == "apply external voltage":
                content[key]["peak voltage"] *= multiplier
                for boundary in ["top", "bottom", "left", "right"]:
                    content[key]["positive voltage boundary"] = boundary
                    negative_boundary = None
                    if boundary == "top":
                        negative_boundary = "bottom"
                    if boundary == "bottom":
                        negative_boundary = "top"
                    if boundary == "left":
                        negative_boundary = "right"
                    if boundary == "right":
                        negative_boundary = "left"
                    content[key]["negative voltage boundary"] = negative_boundary
                    response = await self.g_utils.utils.aget(url=self.request_url)

            elif key == "apply pressure":
                content[key]["multiplier"] *= multiplier
                await self.run_sim_for_spacial_func(content, key)

            elif key == "break ecm junctions":
                # line 380 base config
                content[key]["multiplier"] = content[key]["multiplier"] * multiplier if not int(content[key]["multiplier"]) == 0 else 1 * multiplier

        await asyncio.gather(*[run_sim(multiplier, key, len_sim) for multiplier in multiplier_steps])

    async def handle_block_change(self, multiplier_steps, key, len_sim):

        async def run_sim(multiplier, key, len_sim):
            content = self.set_event_base(
                content=DEFAULT_BETSE_CONTENT.copy(),
                key=key,
                len_sim=len_sim
            )
            if key.startswith("change"):
                content[key]["multiplier"] *= multiplier
                if key in ["change Ca mem", "change Cl mem", "change K mem", "change Na mem"]:
                    await self.run_sim_for_spacial_func(content, key)

            elif key.startswith("block"):
                if key == "block gap junctions":
                    content[key]["random fraction"] *= multiplier


            # Start sim & upload generated data directly to sp -> include check in main sim
            response = await self.g_utils.utils.aget(url=self.request_url)

        await asyncio.gather(*[run_sim(multiplier, key, len_sim) for multiplier in multiplier_steps])


    async def run_sim_for_spacial_func(self, content, key):

        """
        Capture here all variations of all gradients
        """

        for func in self.spacial_functions:
            # Set modulator
            content[key]["modulator function"] = func

            # Change props of modulator
            if func in ["gradient_x", "gradient_y", "gradient_r"]:
                for modul_multi in self.gradient_multipliers:
                    content["modulator function properties"][func]["slope"] *= modul_multi
                    content["modulator function properties"][func]["x-offset"] *= modul_multi
                    content["modulator function properties"][func]["x-offset"] *= modul_multi
                    content["modulator function properties"][func]["exponent"] *= modul_multi
                    response = await self.g_utils.utils.aget(url=self.request_url)
            elif func == "periodic":
                for modul_multi in self.gradient_multipliers:
                    content["modulator function properties"][func]["frequency"] *= modul_multi

            elif func == "f_sweep":
                for modul_multi in self.gradient_multipliers:
                    content["modulator function properties"][func]["start frequency"] *= modul_multi
                    content["modulator function properties"][func]["end frequency"] *= modul_multi
                    response = await self.g_utils.utils.aget(url=self.request_url)

            elif func == "gradient_bitmap":
                for root, _, files in os.walk(DEFAULT_BETSE_GEOP):
                    for f in files:
                        file_path = os.path.join(root, f)
                        if file_path.endswith(".png"):
                            content["modulator function properties"][func]["file"] = file_path
                            response = await self.g_utils.utils.aget(url=self.request_url)

            elif func == "single_cell":
                response = await self.g_utils.utils.aget(url=self.request_url)

    def set_event_base(self, content, key, len_sim):

        content[key]["event happens"] = True
        content[key]["change start"] = 0
        content[key]["change finish"] = len_sim
        content[key]["change rate"] = len_sim / 10
        return content

    def set_event_base2(self, content,k, v):
        """if isinstance(v, bool):

        if isinstance(v, str):
        if isinstance(v, list):"""
        if isinstance(v, int):
            content[k] *= v
        return content







