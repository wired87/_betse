from rest_framework import serializers


class InternalParametersSerializer(serializers.Serializer):
    Do_Na = serializers.FloatField(
        default=1.33e-9,
        help_text="free diffusion constant sodium [m2/s]"
    )
    Do_K = serializers.FloatField(
        default=1.96e-9,
        help_text="free diffusion constant potassium [m2/s]"
    )
    Do_Cl = serializers.FloatField(
        default=2.03e-9,
        help_text="free diffusion constant chloride [m2/s]"
    )
    Do_Ca = serializers.FloatField(
        default=1.0e-10,
        help_text="free diffusion constant calcium [m2/s]"
    )
    Do_M = serializers.FloatField(
        default=1.0e-9,
        help_text="free diffusion constant mystery anchor ion [m2/s]"
    )
    Do_P = serializers.FloatField(
        default=0.0,
        help_text="free diffusion constant protein [m2/s]"
    )

    alpha_NaK = serializers.FloatField(
        default=1.0e-7,
        help_text="max rate Na-K-ATPase pump [m/mol*s] (1.0e-6 to 1.0e-12)"
    )
    alpha_Ca = serializers.FloatField(
        default=5.0e-8,
        help_text="pump rate for calcium ATPase in membrane per unit surface area [m/mol*s]"
    )

    substances_affect_Vmem = serializers.BooleanField(
        default=True,
        help_text="do ionic biochemicals, metabolites and gene products affect charge state?"
    )

    environment_volume_multiplier = serializers.FloatField(
        default=1.0,
        help_text="level to multiply size of box-environment (applies for no ecm spaces only) 1.0"
    )

    membrane_capacitance = serializers.FloatField(
        default=0.05,
        help_text="~0.05 to 0.1 cell membrane capacitance [F/m2]"
    )

    cell_polarizability = serializers.FloatField(
        default=0.0,
        help_text="cell relative dielectric constant (static, low frequency) (0.0 to 5.0e7)"
    )

    dielectric_constant = serializers.FloatField(
        default=6.0,
        help_text="dielectric constant of electrical double layer"
    )

    fast_update_ecm = serializers.BooleanField(
        default=False,
        help_text="use a coarse (fast) or fine (slow) method to update between env and cell grids?"
    )

    sharpness_env = serializers.FloatField(
        default=1.0,
        help_text="Factor smoothing environmental concentrations, 0.0 max smoothing, 1.0 no smoothing"
    )

    sharpness_cell = serializers.FloatField(
        default=0.5,
        help_text="Factor smoothing cellular fields, 0.0 maximum smoothing, 1.0 no smoothing."
    )

    true_cell_size = serializers.FloatField(
        default=1.0e-5,
        help_text="True cell size (important for scaling larger grid patches) 1.0e-5 to 2.5e-6 m."
    )