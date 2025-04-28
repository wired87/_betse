from rest_framework import serializers


class SimGRNSettingsSerializer(serializers.Serializer):
    run_as_sim = serializers.BooleanField(
        default=False,
        help_text='Run network as an initialization (False) or simulation (True)?'
    )
    run_network_on = serializers.ChoiceField(
        choices=["seed", "init", "sim"],
        default="seed",
        help_text='Type of previously run simulation phase to "piggyback" from.'
    )
    """save_to_directory = serializers.CharField(
        default="RESULTS/GRN",
        help_text='Directory containing the following file.'
    )
    save_to_file = serializers.CharField(
        default="GRN_1.betse.gz",
        help_text='File of networking results created by "betse sim-grn".'
    )"""
    load_from = serializers.CharField(
        default="",
        allow_blank=True,
        help_text='Prior result file to restart from (relative path). Empty = start fresh.'
    )
    time_step = serializers.FloatField(
        default=0.1,
        help_text='Time step-size [s]'
    )
    total_time = serializers.FloatField(
        default=1.8e2,
        help_text='Time to end sim run [s]'
    )
    sampling_rate = serializers.FloatField(
        default=1.8e1,
        help_text='Period to sample data [s] (at least time step or larger)'
    )


class GeneRegulatoryNetworkSettingsSerializer(serializers.Serializer):
    gene_regulatory_network_simulated = serializers.BooleanField(
        default=False,
        help_text='Enable gene regulatory network (GRN)?'
    )
    gene_regulatory_network_config = serializers.CharField(
        default="betse_app/extra_configs/grn_basic.yaml",
        help_text='Config file path. Ignored if GRN is disabled.'
    )
    sim_grn_settings = SimGRNSettingsSerializer(
        default=lambda: SimGRNSettingsSerializer().to_internal_value({}),
        help_text='Settings for running "betse sim-grn" subcommand.'
    )
