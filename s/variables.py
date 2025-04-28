from rest_framework import serializers


class EnvBoundaryConcentrationsSerializer(serializers.Serializer):
    Na = serializers.FloatField(default=145.0, help_text="Na+ concentration at bound [mM]")
    K = serializers.FloatField(default=4.0, help_text="K+ concentration at bound [mM]")
    Cl = serializers.FloatField(default=115.0, help_text="Cl- concentration at bound [mM]")
    Ca = serializers.FloatField(default=2.0, help_text="Ca2+ concentration at bound [mM]")
    P = serializers.FloatField(default=9.0, help_text="Protein- concentration at bound [mM]")
    M = serializers.FloatField(default=29.0, help_text="Anion (bicarbonate) concentration at bound [mM]")


class FluidFlowSerializer(serializers.Serializer):
    include_fluid_flow = serializers.BooleanField(default=False,
                                                  help_text="Calculate fluid flow between cells and in extracellular environment?")
    water_viscocity = serializers.FloatField(default=1.0,
                                             help_text="Viscosity of water [Pa s] (applies to ease of flow)")


class DeformationSerializer(serializers.Serializer):
    turn_on = serializers.BooleanField(default=False,
                                       help_text="Include deformation under the osmotic pressure influx and electric fields?")
    galvanotropism = serializers.FloatField(default=1.0e-9,
                                            help_text="Factor by which cells change shape to global electric field (can be 0.0 or negative)")
    viscous_damping = serializers.FloatField(default=0.01,
                                             help_text="Viscous damping of elastic waves in tissue (0.0 to 1.0; larger = higher damping)")
    fixed_cluster_boundary = serializers.BooleanField(default=True,
                                                      help_text="Exterior cells of the cluster are fixed (True) or free to move (False)")
    young_modulus = serializers.FloatField(default=1.0e3,
                                           help_text="Young's modulus (elastic modulus) of individual cell [Pa] (1 kPa to 10e6 Pa)")


class PressuresSerializer(serializers.Serializer):
    include_osmotic_pressure = serializers.BooleanField(default=False,
                                                        help_text="Include osmotic pressure in flow & deformation?")
    membrane_water_conductivity = serializers.FloatField(default=1e-2,
                                                         help_text="Membrane conductivity for osmotic inflow (aquaporin per unit surface) (~ 1e-3)")


class NoiseSerializer(serializers.Serializer):
    static_noise_level = serializers.FloatField(default=0,
                                                help_text="Level of variance in K+ leaks on cell membranes (0 to 10.0)")
    dynamic_noise = serializers.BooleanField(default=False, help_text="Is dynamic noise desired? Options True or False")
    dynamic_noise_level = serializers.FloatField(default=1e-6,
                                                 help_text="Level of dynamic noise (0 to 1e-5). High values may cause simulation instability")


class GapJunctionsSerializer(serializers.Serializer):
    gap_junction_surface_area = serializers.FloatField(default=5.0e-8,
                                                       help_text="Surface area of gap junction as fraction of cell area (1.0e-5 open, 1e-9 closed)")
    voltage_sensitive_gj = serializers.BooleanField(default=False,
                                                    help_text="Gap junctions close with voltage difference between cells?")
    gj_voltage_threshold = serializers.FloatField(default=15,
                                                  help_text="Voltage at which gap junctions are half closed [mV] (10 to 80 mV suggested)")
    gj_voltage_window = serializers.FloatField(default=15,
                                               help_text="Steepness of gating function (currently not used)")
    gj_minimum = serializers.FloatField(default=0.10,
                                        help_text="Minimum permeability fraction when channel is 'closed'")


class TightJunctionRelativeDiffusionSerializer(serializers.Serializer):
    Na = serializers.FloatField(default=1)
    K = serializers.FloatField(default=1)
    Cl = serializers.FloatField(default=1)
    Ca = serializers.FloatField(default=1)
    M = serializers.FloatField(default=1)
    P = serializers.FloatField(default=1)


class MicrotubulesSerializer(serializers.Serializer):
    use_microtubules = serializers.BooleanField(default=False, help_text="Compute microtubule dynamics?")
    charge_per_micrometer = serializers.FloatField(default=-360,
                                                   help_text="Charge of tubulin molecule in electron charge units per micrometer")
    radius = serializers.FloatField(default=15.0e-9, help_text="Microtubule radius in meters")
    length = serializers.FloatField(default=1.0e-5, help_text="Average microtubule length in meters")
    tethered_tubule = serializers.BooleanField(default=True,
                                               help_text="Microtubule tethered to centrosome or free-floating?")
    time_dilation_factor = serializers.FloatField(default=1.0, help_text="Alter simulation timestep for microtubules")
    microtubule_density = serializers.CharField(default=None, allow_null=True,
                                                help_text="Bitmap for microtubule spatial density (None = homogeneous)")
    initial_x_coorinate = serializers.CharField(default=None, allow_null=True,
                                                help_text="Bitmap for initial x-coordinates (None = randomized)")
    initial_y_coorinate = serializers.CharField(default=None, allow_null=True,
                                                help_text="Bitmap for initial y-coordinates (None = randomized)")
    rotate_initialization_axis = serializers.FloatField(default=0.0,
                                                        help_text="Angle (degrees) to rotate x-y axis of initialization coords")


class VariableSettingsSerializer(serializers.Serializer):
    env_boundary_concentrations = EnvBoundaryConcentrationsSerializer(
        default=lambda: EnvBoundaryConcentrationsSerializer().to_internal_value({}),
        help_text="Ion concentrations at global boundary during init and sim.",
    )
    fluid_flow = FluidFlowSerializer(
        help_text="Fluid flow simulation options.",
        default=lambda: FluidFlowSerializer().to_internal_value({}),

    )
    deformation = DeformationSerializer(
        default=lambda: DeformationSerializer().to_internal_value({}),
        help_text="Deformation under osmotic pressure and electric fields."
    )
    temperature = serializers.FloatField(default=310, help_text="System temperature [K]")

    pressures = PressuresSerializer(
        help_text="Pressure-related simulation parameters.",
        default=lambda: PressuresSerializer().to_internal_value({}),
    )
    noise = NoiseSerializer(
        help_text="Membrane noise simulation options.",
        default=lambda: NoiseSerializer().to_internal_value({}))
    gap_junctions = GapJunctionsSerializer(
        help_text="Gap junction simulation parameters.",
        default=lambda: GapJunctionsSerializer().to_internal_value({}))
    tight_junction_scaling = serializers.FloatField(
        default=1.0,
        help_text="Scaling factor for tight junctions (1.0 to 5.0e-2)")
    tight_junction_relative_diffusion = TightJunctionRelativeDiffusionSerializer(
        help_text="Relative permeability of ions through tight junctions.",
        default=lambda: TightJunctionRelativeDiffusionSerializer().to_internal_value({}))
    adherens_junction_scaling = serializers.FloatField(
        default=1.0,
        help_text="Scaling factor for adherens junction diffusion.")
    microtubules = MicrotubulesSerializer(
        help_text="Microtubule-related simulation options.",
        default=lambda: MicrotubulesSerializer().to_internal_value({}))
    use_Goldman_calculator = serializers.BooleanField(
        default=False,
        help_text="Use Goldman-Hodgkin-Katz voltage equation for comparison?"
    )
