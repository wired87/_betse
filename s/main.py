from django.core.validators import FileExtensionValidator
from rest_framework import serializers

from _betse import DEFAULT_BETSE_CONTENT
from _betse.s.general_network import GeneralNetworkSerializer
from _betse.s.grn import GeneRegulatoryNetworkSettingsSerializer
from _betse.s.internal_params import InternalParametersSerializer
from _betse.s.results import ResultsOptionsSerializer
from _betse.s.variables import VariableSettingsSerializer


def profile_values(serializer_class):
    for field_name, field in serializer_class().fields.items():
        for k, v in get_diff_const_profiles():
            if field_name == k:
                field.default = v
    return serializer_class


def get_diff_const_profiles():
    return {
        'Dm_Na': 5.0e-18,
        'Dm_K': 1.0e-18,
        'Dm_Cl': 1.0e-18,
        'Dm_Ca': 1.0e-18,
        'Dm_M': 1.0e-18,
        'Dm_P': 0.0
    },


def default_diff_const():
    return {  # Membrane diffusion constants applied to all unprofiled cells.
        "Dm_Na": 1.0e-18,  # Na+ membrane diffusion constant [m2/s]
        "Dm_K": 50.0e-18,  # K+ membrane diffusion constant [m2/s]
        "Dm_Cl": 1.0e-18,  # Cl- membrane diffusion constant [m2/s]
        "Dm_Ca": 1.0e-18,  # Ca2+ membrane diffusion constant [m2/s]
        "Dm_M": 1.0e-18,  # M- membrane diffusion constant [m2/s]
        "Dm_P": 0.0,
    }


# ------------------------------------------------------------------------------
# SOLVER SETTINGS
# ------------------------------------------------------------------------------

class SolverOptionsSerializer(serializers.Serializer):
    type = serializers.CharField(
        default='full',
        help_text='Type of solver to enable for this simulation ("full" or "fast").',
    )



class SolverSettingsSerializer(serializers.Serializer):
    solver_options = SolverOptionsSerializer(
        help_text='Settings specific to simulation solvers.',
        default=lambda: SolverOptionsSerializer().to_internal_value({}),
    )


# ------------------------------------------------------------------------------
# FILE HANDLING
# ------------------------------------------------------------------------------


class InitFileSavingSerializer(serializers.Serializer):
    directory = serializers.CharField(
        default='INITS', help_text='Directory containing initialization files.'
    )
    worldfile = serializers.CharField(
        default='world_1.betse.gz', help_text='File with cell _qfn_cluster_node created by "betse seed".'
    )
    file = serializers.CharField(
        default='init_1.betse.gz', help_text='File of initialization results created by "betse init".'
    )



class SimFileSavingSerializer(serializers.Serializer):
    directory = serializers.CharField(
        default='SIMS', help_text='Directory containing simulation files.'
    )
    file = serializers.CharField(
        default='sim_1.betse.gz', help_text='File of simulation results created by "betse sim".'
    )



class ResultsFileSavingSerializer(serializers.Serializer):
    init_directory = serializers.CharField(
        default='RESULTS/init_1', help_text='Directory of initialization exports.'
    )
    sim_directory = serializers.CharField(
        default='RESULTS/sim_1', help_text='Directory of simulation exports.'
    )



class FileHandlingSerializer(serializers.Serializer):
    init_file_saving = InitFileSavingSerializer(
        help_text='Initialization file saving settings.',
        default=lambda: InitFileSavingSerializer().to_internal_value({}),
    )
    sim_file_saving = SimFileSavingSerializer(
        help_text='Simulation file saving settings.',
        default=lambda: SimFileSavingSerializer().to_internal_value({}),
    )
    results_file_saving = ResultsFileSavingSerializer(
        help_text='Results file saving settings.',
        default=lambda: ResultsFileSavingSerializer().to_internal_value({}),
    )


# ------------------------------------------------------------------------------
# INITIALIZATION SETTINGS
# ------------------------------------------------------------------------------

class InitTimeSettingsSerializer(serializers.Serializer):
    time_step = serializers.FloatField(
        default=1.0e-2, help_text='Time step-size [s].'
    )
    total_time = serializers.FloatField(
        default=5.0, help_text='End time [s].'
    )
    sampling_rate = serializers.FloatField(
        default=1.0, help_text='Time interval to sample data [s].'
    )


# ------------------------------------------------------------------------------
# SIMULATION SETTINGS
# ------------------------------------------------------------------------------

class SimTimeSettingsSerializer(serializers.Serializer):
    time_step = serializers.FloatField(
        default=1.0e-2, help_text='Time step-size [s].'
    )
    total_time = serializers.FloatField(
        default=5.0, help_text='Time to end simulation run [s].'
    )
    sampling_rate = serializers.FloatField(
        default=0.1, help_text='Period to sample data [s].'
    )


# ------------------------------------------------------------------------------
# GENERAL OPTIONS
# ------------------------------------------------------------------------------

class CustomizedIonProfileSerializer(serializers.Serializer):
    extracellular_Na_concentration = serializers.FloatField(
        default=145.0, help_text='Extracellular sodium concentration [mmol/L].'
    )
    extracellular_K_concentration = serializers.FloatField(
        default=5.0, help_text='Extracellular potassium concentration [mmol/L].'
    )
    extracellular_Cl_concentration = serializers.FloatField(
        default=115.0, help_text='Extracellular chloride concentration [mmol/L].'
    )
    extracellular_Ca2_concentration = serializers.FloatField(
        default=2.0, help_text='Extracellular calcium concentration [mmol/L].'
    )
    extracellular_protein_concentration = serializers.FloatField(
        default=10.0, help_text='Extracellular protein concentration [mmol/L].'
    )
    cytosolic_Na_concentration = serializers.FloatField(
        default=12.0, help_text='Intracellular sodium concentration [mmol/L].'
    )
    cytosolic_K_concentration = serializers.FloatField(
        default=139.00, help_text='Intracellular potassium concentration [mmol/L].'
    )
    cytosolic_Cl_concentration = serializers.FloatField(
        default=4.0, help_text='Intracellular chloride concentration [mmol/L].'
    )
    cytosolic_Ca2_concentration = serializers.FloatField(
        default=2.0e-5, help_text='Intracellular calcium concentration [mmol/L].'
    )
    cytosolic_protein_concentration = serializers.FloatField(
        default=135.0, help_text='Intracellular protein concentration [mmol/L].'
    )
    endoplasmic_reticulum_Ca2 = serializers.FloatField(
        default=0.1, help_text='Starting level of Ca2+ in the ER store [mmol/L].'
    )



class GeneralOptionsSerializer(serializers.Serializer):
    comp_grid_size = serializers.IntegerField(
        default=25, help_text='Grid used in computation of environmental parameters.'
    )
    simulate_extracellular_spaces = serializers.BooleanField(
        default=True, help_text='Include extracellular spaces and true environment simulation?'
    )
    ion_profile = serializers.CharField(
        default='basic', help_text='Ion profile options ("basic", "basic_Ca", "mammal", "amphibian", "custom").'
    )
    customized_ion_profile = CustomizedIonProfileSerializer(
        help_text='User-defined initial values of ion concentrations.'
    )


# ------------------------------------------------------------------------------
# WORLD OPTIONS
# ------------------------------------------------------------------------------

class MeshRefinementSerializer(serializers.Serializer):
    refine_mesh = serializers.BooleanField(
        default=True, help_text='Turn on mesh optimization?'
    )
    maximum_steps = serializers.IntegerField(
        default=25, help_text='Maximum number of iterations for mesh optimization.'
    )
    convergence_threshold = serializers.FloatField(
        default=1.5, help_text='Threshold for mesh optimization completion.'
    )



class WorldOptionsSerializer(serializers.Serializer):
    world_size = serializers.FloatField(
        default=150e-6, help_text='Dimension of the square world space [m].'
    )
    cell_radius = serializers.FloatField(
        default=5.0e-6, help_text='Radius of a single cell [m].'
    )
    cell_height = serializers.FloatField(
        default=10.0e-6, help_text='Height of a cell in the z-direction [m].'
    )
    cell_spacing = serializers.FloatField(
        default=26.0e-9, help_text='Spacing between cells [m].'
    )
    lattice_type = serializers.CharField(
        default='hex', help_text='Type of Base cell lattice ("hex" or "square").'
    )
    lattice_disorder = serializers.FloatField(
        default=0.4, help_text='Noise level for the lattice.'
    )
    mesh_refinement = MeshRefinementSerializer(
        help_text="Mesh refinement options"
    )
    alpha_shape = serializers.FloatField(
        default=0.01, help_text='Alpha shape threshold.'
    )
    use_centers = serializers.BooleanField(
        default=False, help_text='Use cell centroids instead of circumcentres when building meshes?'
    )


# ------------------------------------------------------------------------------
# TISSUE PROFILE DEFINITION
# ------------------------------------------------------------------------------


class DiffusionConstantsTissueProfile(serializers.Serializer):
    Dm_Na = serializers.FloatField(default=5.0e-18, help_text='Na+ membrane diffusion constant [m2/s]')
    Dm_K = serializers.FloatField(default=1.0e-18, help_text='K+ membrane diffusion constant [m2/s]')
    Dm_Cl = serializers.FloatField(default=1.0e-18, help_text='Cl- membrane diffusion constant [m2/s]')
    Dm_Ca = serializers.FloatField(default=1.0e-18, help_text='Ca2+ membrane diffusion constant [m2/s]')
    Dm_M = serializers.FloatField(default=1.0e-18, help_text='M- membrane diffusion constant [m2/s]')
    Dm_P = serializers.FloatField(default=0.0, help_text='proteins- membrane diffusion constant [m2/s]')



class DiffusionConstantsTissueDefault(serializers.Serializer):
    Dm_Na = serializers.FloatField(default=1.0e-18, help_text='Na+ membrane diffusion constant [m2/s]')
    Dm_K = serializers.FloatField(default=50.0e-18, help_text='K+ membrane diffusion constant [m2/s]')
    Dm_Cl = serializers.FloatField(default=1.0e-18, help_text='Cl- membrane diffusion constant [m2/s]')
    Dm_Ca = serializers.FloatField(default=1.0e-18, help_text='Ca2+ membrane diffusion constant [m2/s]')
    Dm_M = serializers.FloatField(default=1.0e-18, help_text='M- membrane diffusion constant [m2/s]')
    Dm_P = serializers.FloatField(default=0.0, help_text='proteins- membrane diffusion constant [m2/s]')



class DefaultTissueProfileSerializer(serializers.Serializer):
    name = serializers.CharField(default='Base', help_text='Arbitrary unique profile name.')
    image = serializers.CharField(default='geo/circle/circle_Base.png',
                                  help_text='Filename of the image defining the cell _qfn_cluster_node shape.')
    diffusion_constants = DiffusionConstantsTissueDefault(
        help_text='Membrane diffusion constants applied to all unprofiled cells.')



class CellTargetsSerializer(serializers.Serializer):
    type = serializers.CharField(default="image", help_text="Cell population type as any following string:\n\
        * \"all\", uniformly applying this tissue profile to all cells.\n\
        * \"color\", matching only cells whose cell centres are simple circles with\n\
          a fill color (specified by the \"color\" setting below) of a vector image\n\
          (specified by the \"cells from svg\" setting above).\n\
        * \"image\", matching only cells whose cell centres are pure-black pixels\n\
          in a raster image (specified by the \"image\" setting below).\n\
        * \"indices\", matching only cells whose indices are listed below.\n\
        * \"percent\", matching only a random subset of cells."
                                 )
    color = serializers.CharField(
        default="ff0000", help_text='Color in hexadecimal format of simple circles.'
    )
    image = serializers.CharField(
        default="geo/circle/Spot_3.png",
        help_text='Absolute or relative filename of this raster image.'
    )
    indices = serializers.ListField(
        default=[3, 14, 15, 9, 265],
        child=serializers.IntegerField(),
        help_text='List of cell indices.',
    )
    percent = serializers.IntegerField(
        default=50,
        help_text='# Percentage of all cells in this _qfn_cluster_node to randomly apply this tissue profile to in the range [0, 100] (e.g., 50 selects 50% of all cells. Ignored unless "type: random" specified above,'
    )



class ProfileSerializer(serializers.Serializer):
    name = serializers.CharField(default="Spot", help_text='Tissue profile name')
    insular = serializers.BooleanField(default=False, help_text='Is the profile insular?')
    diffusion_constants = DiffusionConstantsTissueProfile(
        default=lambda: DiffusionConstantsTissueProfile().to_internal_value({}),
        help_text='Membrane diffusion constants.',
    )
    cell_targets = CellTargetsSerializer(
        default=lambda: CellTargetsSerializer().to_internal_value({}),
        help_text='Cell target options.'
    )



class CutProfileSerializer(serializers.Serializer):
    name = serializers.CharField(
        default="surgery",
        help_text='Arbitrary unique profile name.'
    )
    image = serializers.CharField(
        default="geo/circle/wedge.png",
        help_text='Absolute or relative filename of the raster image whose pure-black pixels define the region of cells to remove.',
    )


default_profile_struct = DEFAULT_BETSE_CONTENT["tissue profile definition"]["tissue"]["profiles"]
for struct in default_profile_struct:
    struct["cell targets"]["image"] = struct["cell targets"]["image"]



class TissueS(serializers.Serializer):
    default = DefaultTissueProfileSerializer(
        help_text='Cut profile name.'
    )
    profiles = serializers.ListField(  ################
        help_text='List of all non-default tissue profiles. Ignored if "profiles enabled" is False',
        child=ProfileSerializer(),
        default=default_profile_struct,
    )



class TissueProfileDefinitionSerializer(serializers.Serializer):
    profiles_enabled = serializers.BooleanField(
        default=True,
        help_text='Apply tissue and cut profiles?')
    tissue = TissueS(
        help_text='Tissue profiles (i.e., regions whose cells all share the same initial conditions).',
    )
    cut_profiles = CutProfileSerializer(
        many=True,
        default=[
            {
                "name": "surgery",
                "image": "geo/circle/wedge.png"
            }
        ],
        help_text='List of all cut profiles (i.e., cell _qfn_cluster_node regions to be permanently removed by a cutting event triggered during the simulation phase). Ignored if "profiles enabled" is False or cutting event is disabled.'
    )


# ------------------------------------------------------------------------------
# TARGETED INTERVENTIONS
# ------------------------------------------------------------------------------

class TargetedInterventionBaseSerializer(serializers.Serializer):
    event_happens = serializers.BooleanField(default=False, help_text='Turn the event on (True) or off (False).')
    change_start = serializers.FloatField(default=1.0, help_text='Time to start change [s].')
    change_finish = serializers.FloatField(default=1.0, help_text='Time to end change and return to original [s].')
    change_rate = serializers.FloatField(default=1.0, help_text='Rate of change [s].')
    multiplier = serializers.FloatField(default=1.0, help_text='Factor to multiply Base level.')
    modulator_function = serializers.CharField(allow_null=True, required=False, default=None,
                                               help_text='Spatial function ("gradient_x", "gradient_y", "gradient_r", or None).')
    apply_to = serializers.ListField(child=serializers.CharField(),
                                     help_text='Name(s) of the tissue profile(s) to apply intervention to.')



class ChangeNaMemSerializer(TargetedInterventionBaseSerializer):
    change_start = serializers.FloatField(default=1.0, help_text='Time to start change [s].')
    change_finish = serializers.FloatField(default=4.0, help_text='Time to end change [s].')
    change_rate = serializers.FloatField(default=1.0, help_text='Rate of change [s].')
    multiplier = serializers.FloatField(default=10.0, help_text='Factor to multiply Base level.')
    apply_to = serializers.ListField(child=serializers.CharField(), default=['Spot'],
                                     help_text='Name(s) of the tissue profile(s) to apply intervention to.')



class ChangeKMemSerializer(TargetedInterventionBaseSerializer):
    change_start = serializers.FloatField(default=1.0, help_text='Time to start change [s].')
    change_finish = serializers.FloatField(default=2.0, help_text='Time to end change [s].')
    change_rate = serializers.FloatField(default=0.5, help_text='Rate of change [s].')
    multiplier = serializers.FloatField(default=50.0, help_text='Factor to multiply Base level.')
    apply_to = serializers.ListField(child=serializers.CharField(), default=['Spot'],
                                     help_text='Name(s) of the tissue profile(s) to apply intervention to.')



class ChangeClMemSerializer(TargetedInterventionBaseSerializer):
    change_start = serializers.FloatField(default=1.0, help_text='Time to start change [s].')
    change_finish = serializers.FloatField(default=4.0, help_text='Time to end change [s].')
    change_rate = serializers.FloatField(default=0.5, help_text='Rate of change [s].')
    multiplier = serializers.FloatField(default=10, help_text='Factor to multiply Base level.')
    apply_to = serializers.ListField(child=serializers.CharField(), default=['Spot'],
                                     help_text='Name(s) of the tissue profile(s) to apply intervention to.')



class ChangeCaMemSerializer(TargetedInterventionBaseSerializer):
    change_start = serializers.FloatField(default=2.0, help_text='Time to start change [s].')
    change_finish = serializers.FloatField(default=8.0, help_text='Time to end change [s].')
    change_rate = serializers.FloatField(default=1.0, help_text='Rate of change [s].')
    multiplier = serializers.FloatField(default=10, help_text='Factor to multiply Base level.')
    apply_to = serializers.ListField(child=serializers.CharField(), default=['Base'],
                                     help_text='Name(s) of the tissue profile(s) to apply intervention to.')



class ApplyPressureSerializer(TargetedInterventionBaseSerializer):
    change_start = serializers.FloatField(default=0.0, help_text='Time to start change [s].')
    change_finish = serializers.FloatField(default=1.0, help_text='Time to end change [s].')
    change_rate = serializers.FloatField(default=5.0e-2, help_text='Rate of change [s].')
    multiplier = serializers.FloatField(default=100, help_text='Pressure applied at maximum [Pa].')
    modulator_function = serializers.CharField(allow_null=True, required=False, default='periodic',
                                               help_text='Spatial function ("gradient_x", "gradient_y", "gradient_r", or None).')
    apply_to = serializers.ListField(child=serializers.CharField(), default=['Spot'],
                                     help_text='Name(s) of the tissue profile(s) to apply intervention to.')



class ApplyExternalVoltageSerializer(serializers.Serializer):
    event_happens = serializers.BooleanField(default=False, help_text='Enable or disable this event.')
    change_start = serializers.FloatField(default=0.5, help_text='Time [s] at which to begin applying voltage.')
    change_finish = serializers.FloatField(default=1.0, help_text='Time [s] at which to cease applying voltage.')
    change_rate = serializers.FloatField(default=0.1, help_text='Time [s] over which voltage proceeds from background.')
    peak_voltage = serializers.FloatField(default=1.0e-3, help_text='Max voltage [V] applied by this event.')
    positive_voltage_boundary = serializers.CharField(default='top',
                                                      help_text='Environment boundary to apply positive voltage ("top", "bottom", "left", or "right").')
    negative_voltage_boundary = serializers.CharField(default='bottom',
                                                      help_text='Environment boundary to apply negative voltage ("top", "bottom", "left", or "right").')



class BreakEcmJunctionsSerializer(TargetedInterventionBaseSerializer):
    change_start = serializers.FloatField(default=2.0, help_text='Time to start change [s].')
    change_finish = serializers.FloatField(default=7.0, help_text='Time to end change [s].')
    change_rate = serializers.FloatField(default=0.5, help_text='Rate of change [s].')
    multiplier = serializers.FloatField(default=0.0, help_text='Fraction of original TJ magnitude.')
    apply_to = serializers.ListField(child=serializers.CharField(), default=['Spot'],
                                     help_text='Tissue profile(s) to apply intervention to.')



class CuttingEventSerializer(serializers.Serializer):
    event_happens = serializers.BooleanField(default=True, help_text='Enable or disable this event?')
    apply_to = serializers.ListField(child=serializers.CharField(), default=['surgery'],
                                     help_text='List of names of cut profiles selecting cells to be removed.')
    break_TJ = serializers.BooleanField(default=True, help_text='Break tight junctions?')
    wound_TJ = serializers.FloatField(default=1.0e-1,
                                      help_text='How leaky are the tight junctions at the wound (max 1.0)')


# ------------------------------------------------------------------------------
# MODULATOR FUNCTION PROPERTIES
# ------------------------------------------------------------------------------

class GradientXSerializer(serializers.Serializer):
    slope = serializers.FloatField(default=1.0, help_text='Rate of change of gradient per unit x-dimension.')
    x_offset = serializers.IntegerField(default=0, help_text='Offset to all gradient values along the horizontal axis.')
    z_offset = serializers.IntegerField(default=0)
    exponent = serializers.IntegerField(default=1, help_text='Hill exponent for gradient values.')



class GradientYSerializer(serializers.Serializer):
    slope = serializers.FloatField(default=1.0, help_text='Rate of change of gradient per unit x-dimension.')
    x_offset = serializers.IntegerField(default=0, help_text='Offset to all gradient values.')
    z_offset = serializers.IntegerField(default=0)
    exponent = serializers.IntegerField(default=1, help_text='Hill exponent for gradient values.')



class GradientRSerializer(serializers.Serializer):
    slope = serializers.FloatField(default=1.0, help_text='Radial gradient rate of change per unit radius.')
    x_offset = serializers.IntegerField(default=0)
    z_offset = serializers.IntegerField(default=0)
    exponent = serializers.IntegerField(default=1, help_text='Hill exponent for gradient values.')



class PeriodicSerializer(serializers.Serializer):
    frequency = serializers.IntegerField(default=10, help_text='Frequency of oscillation [Hz].')
    phase = serializers.IntegerField(default=0, help_text='Phase-offset of oscillation.')



class FSweepSerializer(serializers.Serializer):
    start_frequency = serializers.FloatField(default=0.1e3, help_text='Start frequency.')
    end_frequency = serializers.FloatField(default=1e3, help_text='End frequency.')



class GradientBitmapSerializer(serializers.Serializer):
    file = serializers.CharField(default='geo/ellipse/gradient.png', help_text='Filename of the bitmap image (png).')
    z_offset = serializers.FloatField(default=0.0)


class SCS(serializers.Serializer):
    z_offset = serializers.FloatField(default=0.0)



class ModulatorFunctionPropertiesSerializer(serializers.Serializer):
    gradient_x = GradientXSerializer(
        help_text='Generate a spatial gradient in the x-direction',
        default=lambda: GradientXSerializer().get_initial()
    )
    gradient_y = GradientYSerializer(
        help_text='Generate a spatial gradient in the y-direction',
        default=lambda: GradientYSerializer().get_initial()
    )
    gradient_r = GradientRSerializer(
        help_text='Generate a radial spatial gradient',
        default=lambda: GradientRSerializer().get_initial()
    )
    periodic = PeriodicSerializer(
        help_text='Generate a sinusoidal oscillation',
        default=lambda: PeriodicSerializer().get_initial()
    )
    f_sweep = FSweepSerializer(
        help_text='Apply a sinusoidal oscillation as a sequence of frequencies',
        default=lambda: FSweepSerializer().get_initial()
    )
    gradient_bitmap = GradientBitmapSerializer(
        help_text='Generate a spatial gradient from an imported bitmap image',
        default=lambda: GradientBitmapSerializer().get_initial()
    )
    single_cell = SCS(
        help_text="Randomly select a boundary cell and make that the maxima of the modulation",
        default=lambda: SCS().get_initial()
    )


# ------------------------------------------------------------------------------
# GLOBAL INTERVENTIONS
# ------------------------------------------------------------------------------

class GlobalChangeEnvBaseSerializer(serializers.Serializer):
    event_happens = serializers.BooleanField(default=False, help_text='Turn the event on (True) or off (False).')
    change_start = serializers.FloatField(default=1.00, help_text='Time to start change [s].')
    change_finish = serializers.FloatField(default=1.00, help_text='Time to end change and return to original [s].')
    change_rate = serializers.FloatField(default=1.00, help_text='Rate of change [s].')
    multiplier = serializers.FloatField(default=1.00, help_text='Factor to multiply Base level.')



class ChangeKEnvSerializer(GlobalChangeEnvBaseSerializer):
    change_start = serializers.FloatField(default=1.00, help_text='Time to start change [s].')
    change_finish = serializers.FloatField(default=12.00, help_text='Time to end change [s].')
    change_rate = serializers.FloatField(default=1.0, help_text='Rate of change [s].')
    multiplier = serializers.FloatField(default=20.0, help_text='Factor to multiply Base level.')



class ChangeClEnvSerializer(GlobalChangeEnvBaseSerializer):
    change_start = serializers.FloatField(default=5.0, help_text='Time to start change [s].')
    change_finish = serializers.FloatField(default=25.0, help_text='Time to end change [s].')
    change_rate = serializers.FloatField(default=2.0, help_text='Rate of change [s].')
    multiplier = serializers.FloatField(default=10.0, help_text='Factor to multiply Base level.')



class ChangeNaEnvSerializer(GlobalChangeEnvBaseSerializer):
    change_start = serializers.FloatField(default=1.0, help_text='Time to start change [s].')
    change_finish = serializers.FloatField(default=9.0, help_text='Time to end change [s].')
    change_rate = serializers.FloatField(default=1.0, help_text='Rate of change [s].')
    multiplier = serializers.FloatField(default=5.0, help_text='Factor to multiply Base level.')



class ChangeTemperatureSerializer(GlobalChangeEnvBaseSerializer):
    change_start = serializers.FloatField(default=1.0, help_text='Time to start change [s].')
    change_finish = serializers.FloatField(default=9.0, help_text='Time to end change [s].')
    change_rate = serializers.FloatField(default=0.5, help_text='Rate of change [s].')
    multiplier = serializers.FloatField(default=0.5, help_text='Factor to multiply Base level.')



class BlockGapJunctionsSerializer(serializers.Serializer):
    event_happens = serializers.BooleanField(default=False, help_text='Turn the event on (True) or off (False).')
    change_start = serializers.FloatField(default=2.00, help_text='Time to start change [s].')
    change_finish = serializers.FloatField(default=6.00, help_text='Time to end change [s].')
    change_rate = serializers.FloatField(default=1.5, help_text='Rate of change [s].')
    random_fraction = serializers.IntegerField(default=100, help_text='Percentage of gap junctions to block (0-100).')



class BlockNaKATPSerializer(serializers.Serializer):
    event_happens = serializers.BooleanField(default=False, help_text='Turn the event on (True) or off (False).')
    change_start = serializers.IntegerField(default=5, help_text='Time at which event begins [s]')
    change_finish = serializers.IntegerField(default=25, help_text='Time at which event ends [s]')
    change_rate = serializers.FloatField(default=1.0, help_text='Rate of change [s]')

# ------------------------------------------------------------------------------
# BETSE CONFIGURATION SERIALIZER
# ------------------------------------------------------------------------------

class BetseConfigSerializer(serializers.Serializer):
    sim_config_file = serializers.FileField(
        help_text="""
        # The following settings can be changed to customize simulations in BETSE. When
        # editing the file, note that it is essential that the line indentations (tabs)
        # are maintained in their current order, and that only variable assignments are
        # changed. Variable names must not be changed. Comments are prefixed by "#" and
        # may be altered.
        #
        # Note that each BETSE simulation requires an initialization run. The
        # initialization is required to ensure that a simulation begins with a system in
        # a steady state. Each subsequent simulation depends on an initialization run
        # specific to the cell geometry and initialized parameters.
        """,
        label="Custom Config File (.yaml/.yml)",
        validators=[FileExtensionValidator(allowed_extensions=['yaml', "yml"])],
        allow_null=True,
        required=False,
    )

    grn_basic = serializers.FileField(
        help_text="""
        # The BETSE basic gene regulatory network configuration file, which takes a coarse view of a
        # GNR set-up. This file reproduces the GRN results from Figure 2, page 774 of: Karlebach, G.
        # & Shamir, R. Modelling and analysis of gene regulatory networks Nature Reviews Molecular
        """,
        label="GRN Config (.yaml/.yml)",
        validators=[FileExtensionValidator(allowed_extensions=['yaml', "yml"])],
        allow_null=True,
        required=False,
    )

    expression_data = serializers.FileField(
        help_text="""
        # This expression_data.yaml file allows for specific expression levels of any biomolecule, reaction, 
        # channel, or transporter to be set across all tissue profiles of the model. Expression levels 
        # are relative to the maximum:
        # production rate (for biomolecules)
        # reaction rate (for reactions)
        # conductivity (for channels)
        # rate (for transporters)
        # Use the expression data 
        """,
        label="Expression Data Config (.yaml/.yml)",
        validators=[FileExtensionValidator(allowed_extensions=['yaml', "yml"])],
        allow_null=True,
        required=False,
    )
    metabo_basic = serializers.FileField(
        help_text="""# The BETSE basic metabolism configuration file, which takes a coarse view of cell metabolism, only
        # considering the very basic production of ATP in a general reaction and background consumption.
        # All metabolism related config files must contain biomolecules with the name 'ATP', 'ADP', and 'Pi',
        # otherwise, the level of complexity/detail can be high or low.
        """,
        label="Metabo Base Config (.yaml/.yml)",
        validators=[FileExtensionValidator(allowed_extensions=['yaml', "yml"])],
        allow_null=True,
        required=False,
    )



"""results_options = ResultsOptionsSerializer(
        default=lambda: ResultsOptionsSerializer().to_internal_value({}),

    )
    variable_settings = VariableSettingsSerializer(
        default=lambda: VariableSettingsSerializer().to_internal_value({}),
    )

    internal_parameters = InternalParametersSerializer(
        default=lambda: InternalParametersSerializer().to_internal_value({}),
        help_text=(
            "While the following settings are available to you, please avoid editing them. "
            "Simulation instability may result from poor choice of these more sensitive parameters. "
            "BETSE requires these parameters for its internal use only."
        )
    )

    solver_settings = SolverSettingsSerializer(
        help_text='Solver settings.',
        default=lambda: SolverSettingsSerializer().to_internal_value({}),

    )
    file_handling = FileHandlingSerializer(
        help_text='File handling settings.',
        default=lambda: FileHandlingSerializer().to_internal_value({}),
    )

    init_time_settings = InitTimeSettingsSerializer(
        help_text='Initialization time settings.',
        default=lambda: InitTimeSettingsSerializer().to_internal_value({}),

    )
    automatically_run_initialization = serializers.BooleanField(
        default=True,
        help_text='Automatically run initialization if init file is not found.'
    )

    sim_time_settings = SimTimeSettingsSerializer(
        help_text='Simulation time settings.',
        default=lambda: SimTimeSettingsSerializer().to_internal_value({}),

    )

    general_options = GeneralOptionsSerializer(
        help_text='General simulation options.',
        default = lambda: GeneralOptionsSerializer().to_internal_value({}),

    )
    world_options = WorldOptionsSerializer(
        help_text='World options.',
        default=lambda: WorldOptionsSerializer().to_internal_value({}),

    )
    tissue_profile_definition = TissueProfileDefinitionSerializer(
        help_text='Tissue profile definition.',
        default=lambda: TissueProfileDefinitionSerializer().to_internal_value({}),
    )

    # -----------------------------------------------------------------------------------------------------------------------
    # TARGETED INTERVENTIONS

    change_Na_mem = ChangeNaMemSerializer(
        help_text='Change the membrane permeability to Na+',
        default=lambda: ChangeNaMemSerializer().to_internal_value({}),
    )

    change_K_mem = ChangeKMemSerializer(
        help_text='Change the membrane permeability to K+',
        default=lambda: ChangeKMemSerializer().to_internal_value({}),
    )

    change_Cl_mem = ChangeClMemSerializer(
        help_text='Change the membrane permeability to Cl-',
        default=lambda: ChangeClMemSerializer().to_internal_value({}),
    )

    change_Ca_mem = ChangeCaMemSerializer(
        help_text='Change the membrane permeability to Ca2+',
        default=lambda: ChangeCaMemSerializer().to_internal_value({}),
    )

    apply_pressure = ApplyPressureSerializer(
        help_text='Schedule application of mechanical pressure',
        default=lambda: ApplyPressureSerializer().to_internal_value({}),
    )

    apply_external_voltage = ApplyExternalVoltageSerializer(
        help_text='Apply an external voltage',
        default=lambda: ApplyExternalVoltageSerializer().to_internal_value({}),
    )

    break_ecm_junctions = BreakEcmJunctionsSerializer(
        help_text='Break extracellular junctions between cells',
        default=lambda: BreakEcmJunctionsSerializer().to_internal_value({}),
    )

    cutting_event = CuttingEventSerializer(
        help_text='Remove cells selected by cut profiles',
        default=lambda: CuttingEventSerializer().to_internal_value({}),
    )
    # -----------------------------------------------------------------------------------------------------------------------
    # GLOBAL INTERVENTIONS
    change_K_env = ChangeKEnvSerializer(
        help_text='Change the environmental concentration of K+',
        default=lambda: ChangeKEnvSerializer().to_internal_value({})
    )

    change_Cl_env = ChangeClEnvSerializer(
        help_text='Change the environmental concentration of Cl-',
        default=lambda: ChangeClEnvSerializer().to_internal_value({})
    )

    change_Na_env = ChangeNaEnvSerializer(
        help_text='Change the environmental concentration of Na+',
        default=lambda: ChangeNaEnvSerializer().to_internal_value({})
    )

    change_temperature = ChangeTemperatureSerializer(
        help_text='Change the temperature of the system',
        default=lambda: ChangeTemperatureSerializer().to_internal_value({})
    )

    block_gap_junctions = BlockGapJunctionsSerializer(
        help_text='Block gap junctions between cells',
        default=lambda: BlockGapJunctionsSerializer().to_internal_value({})
    )

    block_NaKATP_pump = BlockNaKATPSerializer(
        help_text='Block the Na-K ATPase pump',
        default=lambda: BlockNaKATPSerializer().to_internal_value({})
    )
    # ----------------------------------------------------------------------------------------------------------------------
    # MODULATOR FUNCTION PROPERTIES
    modulator_function_properties = ModulatorFunctionPropertiesSerializer(
        help_text='Modulator function properties.',
        default=lambda: ModulatorFunctionPropertiesSerializer().to_internal_value({}),
    )
    # ----------------------------------------------------------------------------------------------------------------------
    #  GENERAL NETWORK
    general_network = GeneralNetworkSerializer(
        help_text="The General Network allows you to define a bioelectricity-integrated gene and reaction network with custom biomolecules, chemical reactions, channels, and transporters. Use this section to define general network main properties. See 'extra_config_template.yaml' in the 'extra_configs' directory for examples. NOTE: The 'optimization' is not required to run a general network; this is a tool that supplies you with a list of membrane diffusion constants and reaction/transporter maximum rate constants that are a best fit match to the target Vmem and initial concentrations listed for the custom biomolecules section of the network.",
        default=lambda: GeneralNetworkSerializer().to_internal_value({}),
    )
    # ----------------------------------------------------------------------------------------------------------------------
    gene_regulatory_network_settings = GeneRegulatoryNetworkSettingsSerializer(
        help_text="Define an auxillary network in an external config file and read it in and run from that extra file.",
        default=lambda: GeneRegulatoryNetworkSettingsSerializer().to_internal_value({}),
    )"""

    # run_config = RunConfigS(help_text="Min one of the following subcommands must be passed")

