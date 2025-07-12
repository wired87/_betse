from rest_framework import serializers

class InitFileSavingSerializer(serializers.Serializer):
    directory = serializers.CharField(
        default='INITS',
        help_text='Directory containing initialization files.'
    )
    worldfile = serializers.CharField(
        default='world_1.betse.gz',
        help_text='File with cell _qfn_cluster_node from "betse seed". Supported extensions: '
                  '".betse", ".betse.gz", ".betse.bz2", ".betse.xz".'
    )
    file = serializers.CharField(
        default='init_1.betse.gz',
        help_text='File of initialization results from "betse init". Same supported types as worldfile.'
    )


class SimFileSavingSerializer(serializers.Serializer):
    directory = serializers.CharField(
        default='SIMS',
        help_text='Directory containing simulation file.'
    )
    file = serializers.CharField(
        default='sim_1.betse.gz',
        help_text='File of simulation results from "betse sim". Supported types as in init.'
    )


class ResultsFileSavingSerializer(serializers.Serializer):
    init_directory = serializers.CharField(
        default='RESULTS/init_1',
        help_text='Directory of exports from "betse plot init" (e.g., plots, animations).'
    )
    sim_directory = serializers.CharField(
        default='RESULTS/sim_1',
        help_text='Directory of exports from "betse plot sim" (e.g., plots, animations).'
    )
