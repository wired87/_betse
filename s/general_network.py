from rest_framework import serializers


class GrowthAndDecaySerializer(serializers.Serializer):
    production_rate = serializers.FloatField(
        default=0.1,
        help_text="Maximum rate at which molecule is produced in the cytoplasm"
    )
    decay_rate = serializers.FloatField(
        default=0.1,
        help_text="Maximum rate at which molecule is degraded in the cytoplasm"
    )
    apply_to = serializers.ListField(
        child=serializers.CharField(),
        default=["Spot"],
        help_text="Apply growth only to one or more specific tissue profiles (e.g., ['Spot', 'Crest']) or 'all' for everything."
    )
    modulator_function = serializers.ChoiceField(
        choices=['gradient_x', 'gradient_y', 'gradient_r', None],
        default=None,
        help_text="Spatial modulation of production, options: 'gradient_x', 'gradient_y', 'gradient_r' or 'None'"
    )


class PlottingSerializer(serializers.Serializer):
    plot_2D = serializers.BooleanField(default=True, help_text="Create a unique set of plots for the substance")
    animate = serializers.BooleanField(default=True, help_text="Animate the substance during sampled time-steps")
    autoscale_colorbar = serializers.BooleanField(default=True,
                                                  help_text="Autoscale the min-max values of the colorbar")
    max_val = serializers.FloatField(
        default=2.0,
        help_text="If autoscale is False, max value to use for plot in umol/L")
    min_val = serializers.FloatField(
        default=0.0,
        help_text="If autoscale is False, min value to use for plot in umol/L")


class BiomoleculeSerializer(serializers.Serializer):
    name = serializers.CharField(default='X', help_text="Gating ligand")
    Dm = serializers.FloatField(default=0.0, help_text="Membrane diffusion coefficient [m2/s]")
    Do = serializers.FloatField(default=1.0e-10,
                                help_text="Free diffusion constant in extra and intracellular spaces [m2/s]")
    Dgj = serializers.FloatField(default=1.0e-15, help_text="Effective diffusion constant through gap junctions")
    z = serializers.IntegerField(default=0, help_text="Ionic charge")
    env_conc = serializers.FloatField(default=0.0, help_text="Initial concentration in the environment [mmol/L]")
    cell_conc = serializers.FloatField(default=0.0, help_text="Initial concentration in the cytoplasm [mmol/L]")
    scale_factor = serializers.FloatField(default=1.0,
                                          help_text="Amount to scale molecule concentration by in charge calculations")
    update_intracellular = serializers.BooleanField(default=False,
                                                    help_text="Shuts off intracellular transport for fast diffusion with stability")
    use_time_dilation = serializers.BooleanField(default=False,
                                                 help_text="Use time dilation factor for transport and growth/decay of this substance?")
    transmem = serializers.BooleanField(default=False,
                                        help_text="Substance embedded in membrane (and therefore movable by extracellular fields, flow?)")
    initial_asymmetry = serializers.CharField(allow_null=True, default=None,
                                              help_text="Modulator function applied to initial cell concentrations")
    TJ_permeable = serializers.BooleanField(default=False,
                                            help_text="Can substances pass through tight junctions (e.g. dissolved oxygen)")
    GJ_impermeable = serializers.BooleanField(default=False,
                                              help_text="Are substances impermeable through gap junctions (i.e. due to size)")
    TJ_factor = serializers.FloatField(default=1.0,
                                       help_text="TJ factor (relative factor to decrease tight junction permeability)")
    plotting = PlottingSerializer(default=lambda: PlottingSerializer().to_internal_value({}))
    growth_and_decay = GrowthAndDecaySerializer(
        default=lambda: GrowthAndDecaySerializer().to_internal_value({}),
        help_text="settings for production/decay of substances (standard GRN model)"
    )


class ChannelSerializer(serializers.Serializer):
    name = serializers.CharField(help_text="Unique name of the channel")
    channel_class = serializers.CharField(help_text="Class of the channel (Na, K, Ca, Cl, Fun, Cat, ML)")
    channel_type = serializers.CharField(help_text="Specific type of channel (e.g. Kv1p5, Nav1p3, etc.)")
    max_Dm = serializers.FloatField(
        help_text="Maximum membrane diffusion constant to ion when channel fully open [m2/s]")
    apply_to = serializers.CharField(help_text="List of profiles to apply channel to or 'all' for all cells")
    init_active = serializers.BooleanField(
        help_text="Is the channel active during Init (True) or only during Sim (False)?")
    channel_inhibitors = serializers.ListField(child=serializers.CharField(), required=False,
                                               help_text="List of substances inhibiting this channel")
    inhibitor_Km = serializers.ListField(child=serializers.FloatField(), required=False,
                                         help_text="List of Km values for inhibitors")
    inhibitor_n = serializers.ListField(child=serializers.FloatField(), required=False,
                                        help_text="List of Hill coefficients for inhibitors")
    inhibitor_zone = serializers.ListField(child=serializers.CharField(), required=False,
                                           help_text="Zones where inhibition is applied")


class GeneralNetworkSerializer(serializers.Serializer):
    implement_network = serializers.BooleanField(
        help_text="Turn the entire network defined below on (True) or off (False)",
        default=True
    )
    expression_data_file = serializers.CharField(
        help_text="Path to expression data file.",
        default="betse_app/betse/data/yaml/extra_configs/expression_data.yaml"
    )
    biomolecules = BiomoleculeSerializer(
        many=True,
        help_text="List of custom biomolecules with full properties",
        default=lambda: [BiomoleculeSerializer().to_internal_value({})],
    )

    channels = ChannelSerializer(
        many=True,
        required=False,
        help_text="List of channels with gating and inhibition configuration",
        default=[
            {
                "name": "Nav",
                "channel_class": "Na",
                "channel_type": "Nav1p3",
                "max_Dm": 2.0e-14,
                "apply_to": "all",
                "init_active": False
            },
            {
                "name": "Kv",
                "channel_class": "K",
                "channel_type": "Kv1p5",
                "max_Dm": 1.0e-15,
                "apply_to": "all",
                "init_active": False
            },
            {
                "name": "K_Leak",
                "channel_class": "K",
                "channel_type": "KLeak",
                "max_Dm": 0.6e-17,
                "apply_to": "all",
                "init_active": True,
                "channel_inhibitors": ["X"],
                "inhibitor_Km": [0.05],
                "inhibitor_n": [2.0],
                "inhibitor_zone": ["cell"]
            }
        ]
    )
    reactions = serializers.ListField(
        child=serializers.DictField(),
        help_text="Define chemical reactions between biomolecules and ions.",
        required=False
    )
    transporters = serializers.ListField(
        child=serializers.DictField(),
        help_text="Define transmembrane transporters and reactions.",
        required=False
    )
    modulators = serializers.ListField(
        child=serializers.DictField(),
        help_text="Define modulators that affect gap junctions or pumps.",
        required=False
    )
