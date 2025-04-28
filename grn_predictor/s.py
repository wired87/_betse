from rest_framework import serializers

from betse_app import DEFAULT_BETSE_GRNC


class GrowthDecaySerializer(serializers.Serializer):
    production_rate = serializers.FloatField(default=2.0, help_text="Maximum rate at which molecule is produced in the cytoplasm (mmol/L/s)")
    decay_rate = serializers.FloatField(default=1.0, help_text="Maximum rate at which molecule is degraded in the cytoplasm (mmol/L/s)")
    Km = serializers.FloatField(default=1.0, help_text="Half-maximum concentration for production/decay (mmol/L)")
    n = serializers.FloatField(default=1.0, help_text="Hill coefficient describing cooperativity")
    apply_to = serializers.CharField(default="all", help_text="Profiles to which production applies (default: all)")
    modulator_function = serializers.CharField(default=None, allow_null=True, help_text="Spatial function to modulate production ('gradient_x', 'gradient_y', 'gradient_r', or None)")
    activators = serializers.ListField(child=serializers.CharField(), default=None, allow_null=True, help_text="Substances or ions activating expression")
    Km_activators = serializers.ListField(child=serializers.FloatField(), default=None, allow_null=True, help_text="Half-maximum values for activators")
    n_activators = serializers.ListField(child=serializers.FloatField(), default=None, allow_null=True, help_text="Hill coefficients for activators")
    inhibitors = serializers.ListField(child=serializers.CharField(), default=None, allow_null=True, help_text="Substances or ions inhibiting expression")
    Km_inhibitors = serializers.ListField(child=serializers.FloatField(), default=None, allow_null=True, help_text="Half-maximum values for inhibitors")
    n_inhibitors = serializers.ListField(child=serializers.FloatField(), default=None, allow_null=True, help_text="Hill coefficients for inhibitors")

class PlottingSerializer(serializers.Serializer):
    plot_2D = serializers.BooleanField(default=True, help_text="Create a 2D plot for this substance")
    animate = serializers.BooleanField(default=True, help_text="Animate the substance over simulation time")
    autoscale_colorbar = serializers.BooleanField(default=True, help_text="Autoscale colorbar based on data range")
    max_val = serializers.FloatField(default=2.0, help_text="Max value for colorbar if autoscale is False (umol/L)")
    min_val = serializers.FloatField(default=0.0, help_text="Min value for colorbar if autoscale is False (umol/L)")

class BiomoleculeSerializer(serializers.Serializer):
    name = serializers.CharField(help_text="Name/identifier of the molecule")
    Dm = serializers.FloatField(default=0.0, help_text="Membrane diffusion coefficient (m²/s)")
    Do = serializers.FloatField(default=1.0e-12, help_text="Free diffusion constant (m²/s)")
    z = serializers.FloatField(default=0.0, help_text="Charge (oxidation state)")
    env_conc = serializers.FloatField(default=0.0, help_text="Initial concentration in the environment (mmol/L)")
    cell_conc = serializers.FloatField(default=0.0, help_text="Initial concentration in the cytoplasm (mmol/L)")
    mit_conc = serializers.FloatField(default=0.0, help_text="Initial concentration in mitochondria (mmol/L)")
    TJ_permeable = serializers.BooleanField(default=False, help_text="Can pass through tight junctions?")
    GJ_impermeable = serializers.BooleanField(default=True, help_text="Is impermeable through gap junctions?")
    TJ_factor = serializers.FloatField(default=1.0, help_text="Relative factor for tight junction permeability")
    ignore_ECM = serializers.BooleanField(default=True, help_text="Ignore small extracellular space volume?")
    growth_and_decay = GrowthDecaySerializer()
    plotting = PlottingSerializer()

class OptimizationSerializer(serializers.Serializer):
    optimize_network = serializers.BooleanField(default=True, help_text="Enable network optimization")
    optimization_steps = serializers.IntegerField(default=50, help_text="Number of optimization iterations")
    optimization_method = serializers.CharField(default="L-BFGS-B", help_text="Optimization algorithm used")
    optimization_T = serializers.FloatField(default=1.0, help_text="Temperature parameter for basinhopper")
    optimization_step = serializers.FloatField(default=0.5, help_text="Optimization step size")
    target_Vmem = serializers.FloatField(default=-50e-3, help_text="Target membrane potential (V)")

class GRNConfigSerializer(serializers.Serializer):
    enable_mitochondria = serializers.BooleanField(default=False, help_text="Enable distinct mitochondrial volumes?")
    optimization = OptimizationSerializer()
    biomolecules = BiomoleculeSerializer(many=True, default=DEFAULT_BETSE_GRNC.copy()["biomolecules"])
