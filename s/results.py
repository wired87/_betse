from rest_framework import serializers






###############################
# WHILE SOLVING
###############################

class AnimationColorbarSerializer(serializers.Serializer):
    colormap = serializers.CharField(
        default=None,
        help_text='Matplotlib-specific name of colormap displayed by this colorbar or\n"None" to default to "default colormap". See above for details.',
        allow_null=True
    )
    autoscale = serializers.BooleanField(
        default=True,
        help_text="Automatically scale colorbar to minimum and maximum values of\nunderlying data series?"
    )
    minimum = serializers.FloatField(
        default=-70.0,
        help_text='Minimum fixed colorbar value. Ignored if "autoscale" is True.'
    )
    maximum = serializers.FloatField(
        default=20.0,
        help_text='Maximum fixed colorbar value. Ignored if "autoscale" is True.'
    )

class WhileSolvingAnimationsSerializer(serializers.Serializer):
    show = serializers.BooleanField(
        default=False,
        help_text="Display animations during simulation computation?"
    )
    save = serializers.BooleanField(
        default=True,
        help_text="Save animations with the animation saving options\nspecified below during simulation computation?"
    )
    colorbar = AnimationColorbarSerializer(help_text="Animation colorbar settings.")

class WhileSolvingSerializer(serializers.Serializer):
    animations = WhileSolvingAnimationsSerializer(
        help_text="Animations exported during simulation computation.",
        default=lambda: WhileSolvingAnimationsSerializer().to_internal_value({}),
    )

### !!! WHILE SOLVING


class CsvPipelineItemSerializer(serializers.Serializer):
    type = serializers.CharField(
        help_text='CSV file type, including any following string:\n* "cell_series" for single-cell time series (Vmem, ion concentrations,\n  voltage-gated ion channel pump rates) for "plot cell index" cell.\n  Ignored if full solver disabled.\n* "cell_vmem_fft" for single-cell finite Fourier transform (FFT) time series of\n  transmembrane voltages (Vmem) for "plot cell index" cell.\n  Ignored if extracellular spaces disabled.\n* "cells_vmem" for all-cells transmembrane voltage (Vmem) time series, producing\n  one CSV file containing all Vmem voltages for each time step.'
    )
    enabled = serializers.BooleanField(
        default=True,
        help_text="Enable this CSV file?"
    )

###############################
# AFTER SOLVING
###############################

single_cell_pipeline_default=[
    {
        "type": "voltage_membrane",
        "enabled": True,
    }, {
        "type": "currents_membrane",
        "enabled": True,
    },
]

cell_cluster_pipe_default=[{
                "type": "voltage_membrane",
                "enabled": True,
                "colorbar":{
                    "autoscale": True,
                    "minimum": -70,
                    "maximum": 10
                }
            },{
                "type": "electric_intra",
                "enabled": True,
                "colorbar":{
                    "autoscale": True,
                    "minimum": -70,
                    "maximum": 10
                }
            },
    ]

# # # PLOT


class CellClusterPipelineItemColorbarSerializer(serializers.Serializer):
    autoscale = serializers.BooleanField(
        default=True,
        help_text="Automatically scale colorbar to minimum and\nmaximum values of underlying data series?"
    )
    minimum = serializers.FloatField(
        default=-70.0,
        help_text='Minimum fixed colorbar value. Ignored if\n"autoscale" is True.'
    )
    maximum = serializers.FloatField(
        default=10.0,
        help_text='Maximum fixed colorbar value. Ignored if\n"autoscale" is True.'
    )

class CellClusterPipelineItemSerializer(serializers.Serializer):
    type = serializers.CharField(
        help_text='Plot type, as any following string:\n* "cluster_mask" for the all-cells image mask defining the cell cluster shape.\n* "currents_intra" for final all-cells intracellular current density.\n  Ignored if full solver disabled.\n* "currents_extra" for final all-cells extracellular current density.\n  Ignored if full solver disabled.\n* "deform_total" for final all-cells total cellular deformation = osmotic +\n  galvanotropic. Ignored if either full solver or deformation disabled.\n* "diffusion_extra" for final all-cells extracellular diffusion weights\n  (logarithm-scaled). Ignored if extracellular spaces disabled.\n* "electric_intra" for final all-cells intracellular electric field.\n  Ignored if full solver disabled.\n* "electric_extra" for final all-cells extracellular electric field.\n  Ignored if either full solver or extracellular spaces disabled.\n* "fluid_intra" for final all-cells intracellular fluid flow.\n  Ignored if either full solver or fluid flow disabled.\n* "fluid_extra" for final all-cells extracellular fluid flow.\n  Ignored if either full solver, fluid flow, or extracellular spaces disabled.\n* "gj_connectivity" for the all-cells gap junction connectivity network.\n* "gj_permeability" for final all-cells gap junction relative permeabilities.\n* "ion_calcium_intra" for final all-cells intracellular calcium ion (Ca2+)\n  concentration. Ignored if either full solver disabled or calcium ions disabled\n  by ion profile.\n* "ion_calcium_extra" for final all-cells extracellular calcium ion (Ca2+)\n  concentration. Ignored if either full solver or extracellular spaces disabled or\n  calcium ions disabled by ion profile.\n* "microtubule" for final all-cells microtubule orientation.\n  Ignored if full solver disabled.\n* "pressure_total" for final all-cells total pressure = osmotic + mechanical.\n  Ignored if either full solver, osmotic pressure, or mechanical pressure event\n  disabled.\n* "pump_nakatpase" for final all-cells cell membrane Na-K-ATPase pump rate.\n  Ignored if full solver disabled.\n* "tissue_cuts" for all-cells tissue and cut profiles.\n* "voltage_membrane" for final all-cells transmembrane voltage (Vmem).\n* "voltage_membrane_average" for final all-cells transmembrane\n  voltage (Vmem) average.\n* "voltage_membrane_ghk" for final all-cells transmembrane voltage\n  (Vmem) calculated by Goldman-Hodgkin-Katz (GHK) equation.\n  Ignored if either full solver or GHK calculation disabled.\n* "voltage_extra" for final all-cells extracellular voltage.\n  Ignored if either full solver or extracellular spaces disabled.\n* "voltage_polarity" for final all-cells cellular voltage polarization.\n  Ignored if either full solver or cell polarizability disabled.'
    )
    enabled = serializers.BooleanField(
        default=True,
        help_text="Enable this plot?"
    )
    colorbar = CellClusterPipelineItemColorbarSerializer(help_text="Plot colorbar settings.", allow_null=True, required=False)

class SingleCellPipelineItemSerializer(serializers.Serializer):
    type = serializers.CharField(
        help_text='Plot type, as any following string:\n* "currents_membrane" for single-cell transmembrane current density.\n* "deform_total" for total cellular deformation = osmotic + galvanotropic.\n  Ignored if either full solver or deformation disabled.\n* "ion_calcium" for single-cell calcium ion (Ca2+) concentration.\n  Ignored if either full solver disabled or calcium ions disabled by ion profile.\n* "ion_calcium_er" for single-cell endoplasmic reticulum (ER) calcium ion (Ca2+)\n  concentration.\n  Ignored if full solver disabled, full calcium dynamics disabled, or calcium\n  ions disabled by ion profile.\n* "ion_m_anion" for single-cell M anion (M-) concentration.\n  Ignored if either full solver disabled or M anions disabled by ion profile.\n* "ion_potassium" for single-cell potassium ion (K+) concentration.\n  Ignored if either full solver disabled or potassium ions disabled by ion profile.\n* "ion_sodium" for single-cell sodium ion (Na+) concentration.\n  Ignored if either full solver disabled or sodium ions disabled by ion profile.\n* "pressure_osmotic" for single-cell osmotic pressure.\n  Ignored if either full solver or osmotic pressure disabled.\n* "pressure_total" for single-cell total pressure = osmotic + mechanical.\n  Ignored if either full solver, osmotic pressure, or mechanical pressure event\n  disabled.\n* "pump_nakatpase" for single-cell Na-K-ATPase pump rate.\n  Ignored if full solver disabled.\n* "voltage_membrane" for single-cell transmembrane voltage (Vmem) average.\n* "voltage_membrane_er" for single-cell endoplasmic reticulum (ER) transmembrane\n  voltage (Vmem).\n  Ignored if full solver disabled, full calcium dynamics disabled, or calcium\n  ions disabled by ion profile.\n* "voltage_membrane_fft" for single-cell transmembrane voltage (Vmem) finite\n  Fourier transform (FFT).'
    )
    enabled = serializers.BooleanField(
        default=True,
        help_text="Enable this plot?"
    )

class PlotsSerializer(serializers.Serializer):
    show = serializers.BooleanField(
        default=False,
        help_text="Display plots after simulating?"
    )

    save = serializers.BooleanField(
        default=True,
        help_text="Save plots after simulating with save options defined below?"
    )

    single_cell_pipeline = serializers.ListSerializer(
        child=SingleCellPipelineItemSerializer(),
        help_text='List of all single-cell plots for the cell selected by\n"plot cell index" for all time steps. '
                  'Ignored if\n"show" and "save" are False.',
        default=single_cell_pipeline_default
    )

    cell_cluster_pipeline = serializers.ListSerializer(
        child=CellClusterPipelineItemSerializer(),
        help_text='List of all cell cluster plots for all cells\nat the last time step. Ignored if "show" and\n"save" are False.',
        default=cell_cluster_pipe_default
    )



### ANIMATIONS
default_pipeline = [
    {"type": "cell_series", "enabled": True},
    {"type": "cells_vmem", "enabled": True},
]


animation_pipeline = [
            {
                "type": "voltage_membrane",
                "enabled": True,
                "colorbar": {
                    "autoscale": True,
                    "minimum": -70,
                    "maximum": 10
                }
            },
            {
                "type": "electric_intra",
                "enabled": True,
                "colorbar": {
                    "autoscale": True,
                    "minimum": -70,
                    "maximum": 10
                }
            },
        ]
class AnimationPipelineItemColorbarSerializer(serializers.Serializer):
    autoscale = serializers.BooleanField(
        default=True,
        help_text="Automatically scale colorbar to minimum and\nmaximum values of underlying data series?"
    )
    minimum = serializers.FloatField(
        default=-70.0,
        help_text='Minimum fixed colorbar value. Ignored if\n"autoscale" is True.'
    )
    maximum = serializers.FloatField(
        default=10.0,
        help_text='Maximum fixed colorbar value. Ignored if\n"autoscale" is True.'
    )


class AnimationPipelineItemSerializer(serializers.Serializer):
    type = serializers.CharField(
        help_text='Animation type, including any following string:\n* "currents_intra" for intracellular current density.\n  Ignored if full solver disabled.\n* "currents_extra" for extracellular current density.\n  Ignored if either full solver or extracellular spaces disabled.\n* "deform_total" for total cellular deformation = osmotic + galvanotropic.\n  Ignored if either full solver or deformation disabled.\n* "electric_intra" for intracellular electric field.\n  Ignored if full solver disabled.\n* "electric_extra" for extracellular electric field.\n  Ignored if either full solver or extracellular spaces disabled.\n* "fluid_intra" for intracellular fluid flow.\n  Ignored if either full solver or fluid flow disabled.\n* "fluid_extra" for extracellular fluid flow.\n  Ignored if either full solver, fluid flow, or extracellular spaces disabled.\n* "gj_permeability" for gap junction connectivity state.\n* "ion_calcium_intra" for intracellular calcium ion (Ca2+) concentration.\n  Ignored if either full solver disabled or calcium ions disabled by ion profile.\n* "microtubule" for microtubule orientation.\n  Ignored if full solver disabled.\n* "pressure_osmotic" for cellular osmotic pressure.\n  Ignored if either full solver or osmotic pressure disabled.\n* "pressure_total" for cellular total pressure = osmotic + mechanical.\n  Ignored if either full solver, osmotic pressure, or mechanical pressure event\n  disabled.\n* "voltage_membrane" for transmembrane voltage (Vmem).\n* "voltage_extra" for extracellular voltage.\n  Ignored if either full solver or extracellular spaces disabled.\n* "voltage_polarity" for cellular voltage polarization.\n  Ignored if either full solver or cell polarizability disabled.'
    )
    enabled = serializers.BooleanField(
        default=True,
        help_text="Enable this animation?"
    )
    colorbar = AnimationPipelineItemColorbarSerializer(help_text="Animation colorbar settings.", allow_null=True, required=False)


class AnimationsAfterSolvingSerializer(serializers.Serializer):
    show = serializers.BooleanField(
        default=False,
        help_text="Display animations after simulating?"
    )
    save = serializers.BooleanField(
        default=True,
        help_text="Save animations after simulating with save options defined below?"
    )
    pipeline = serializers.ListSerializer(
        child=AnimationPipelineItemSerializer(),
        default=animation_pipeline,
        help_text="List of all animations. Ignored if \"show\" and \"save\" are False.",
    )


class CsvsSerializer(serializers.Serializer):
    save = serializers.BooleanField(
        default=True,
        help_text="Save CSV files after simulating with save options defined below?"
    )
    pipeline = serializers.ListSerializer(
        child=CsvPipelineItemSerializer(),
        default=default_pipeline,
        help_text='List of all CSV files. Ignored if "save" is False.'
    )




class AfterSolvingSerializer(serializers.Serializer):
    csvs = CsvsSerializer(
        help_text="Comma-separated value (CSV) files exported after simulating.",
        default=lambda: CsvsSerializer().to_internal_value({}),

    )
    plots = PlotsSerializer(
        help_text="Plots exported after simulating.",
        default=lambda: PlotsSerializer().to_internal_value({}),

    )
    animations = AnimationsAfterSolvingSerializer(
        help_text="Animations exported after simulating.",
        default=lambda: AnimationsAfterSolvingSerializer().to_internal_value({}),
    )



### !!! AFTER SOLVING
# SAVING
###############################

class SaveAnimationsImagesSerializer(serializers.Serializer):
    enabled = serializers.BooleanField(
        default=True,
        help_text="Save animation frames as a series of images?"
    )
    filetype = serializers.CharField(
        default="png",
        help_text="Image filetype."
    )
    dpi = serializers.IntegerField(
        default=300,
        help_text="Image dots per inch (DPI)."
    )


class SaveAnimationsVideoMetadataSerializer(serializers.Serializer):
    artist = serializers.CharField(
        default="BETSE",
        help_text="Video author name(s)."
    )
    genre = serializers.CharField(
        default="Bioinformatics",
        help_text="Video target genre."
    )
    subject = serializers.CharField(
        default="Bioinformatics",
        help_text="Video target subject."
    )
    comment = serializers.CharField(
        default="Produced by BETSE.",
        help_text="Video comment string."
    )
    # Optional: add 'copyright' if needed


class SaveAnimationsVideoSerializer(serializers.Serializer):
    enabled = serializers.BooleanField(
        default=False,
        help_text="Encode animation frames as a compressed video?"
    )
    filetype = serializers.CharField(
        default="mp4",
        help_text="Video filetype (e.g., mkv, mp4, mov, avi, webm, ogv, gif)."
    )
    dpi = serializers.IntegerField(
        default=150,
        help_text="Image DPI of each video frame."
    )
    bitrate = serializers.IntegerField(
        default=6000,
        help_text="Video bitrate in bits per second."
    )
    framerate = serializers.IntegerField(
        default=15,
        help_text="Video framerate in frames per second."
    )
    metadata = SaveAnimationsVideoMetadataSerializer()
    writers = serializers.ListField(
        child=serializers.CharField(),
        default=["ffmpeg", "avconv", "mencoder", "imagemagick"],
        help_text="Preferred matplotlib animation writers (in order)."
    )
    codecs = serializers.ListField(
        child=serializers.CharField(),
        default=["auto"],
        help_text='Preferred codecs (e.g., libx264, hevc, auto). "auto" uses the best available.'
    )


class SaveAnimationsSerializer(serializers.Serializer):
    images = SaveAnimationsImagesSerializer(
        default=lambda: SaveAnimationsImagesSerializer().to_internal_value({}),
        help_text="Animation frames saved as a series of images."
    )
    video = SaveAnimationsVideoSerializer(
        default=lambda: SaveAnimationsVideoSerializer().to_internal_value({}),
        help_text="Animation frames encoded as a compressed video."
    )


class SaveCsvsSerializer(serializers.Serializer):
    filetype = serializers.CharField(
        default="csv",
        help_text="CSV filetype."
    )


class SavePlotsSerializer(serializers.Serializer):
    filetype = serializers.CharField(
        default="png",
        help_text="Image filetype."
    )
    dpi = serializers.IntegerField(
        default=300,
        help_text="Image dots per inch (DPI)."
    )


class SaveSerializer(serializers.Serializer):
    csvs = SaveCsvsSerializer()
    plots = SavePlotsSerializer()
    animations = SaveAnimationsSerializer()


### !!! SAVE




class ResultsOptionsSerializer(serializers.Serializer):
    enumerate_cells = serializers.BooleanField(
        default=False,
        help_text="number the cells on 2D plots with their simulation index?"
    )
    plot_cell_index = serializers.IntegerField(
        default=0,
        help_text="State the cell index to use for single-cell time plots\nthe index of cells can be seen using enumerate cells feature."
    )
    show_cells = serializers.BooleanField(
        default=True,
        help_text="if True, plots and animations show individual cells,\neach displayed with color-coded data."
    )
    overlay_currents = serializers.BooleanField(
        default=False,
        help_text="overlay electric current or concentration\nflux streamlines on 2D plotted data?"
    )
    streamline_density = serializers.FloatField(
        default=2.0,
        help_text="for current plots, the density of streamlines. 0.5 to 5.0"
    )
    plot_total_current = serializers.BooleanField(
        default=True,
        help_text="for currents and morphgen fluxing, if simululating extracellular spaces, plot\ntotal current if true, plot gap junction current if false"
    )
    plot_cutlines = serializers.BooleanField(
        default=True,
        help_text="plot any scheduled cut-lines on the cell cluster plot as black regions"
    )
    plot_masked_geometry = serializers.BooleanField(
        default=True,
        help_text="plot the geometry using the overall shape as a mask"
    )
    default_colormap = serializers.CharField(
        default='RdBu_r',
        help_text="Specify the colormap to be used for main data (spanning - to +).\noptions include\ncoolwarm, hot, rainbow, jet, Blues, Greens, bone\nto reverse a colormap add _r to the name (e.g. cm.jet_r)\nfor all options please see\nhttp://matplotlib.org/examples/color/colormaps_reference.html"
    )
    background_colormap = serializers.CharField(
        default='RdBu_r',
        help_text="Specify colormap to be used for data with vector overlays and 0 --> + data,\nincluding:\ncurrents, flow, electric field and deformation."
    )
    network_colormap = serializers.CharField(
        default='rainbow',
        help_text="colormap used for concentration nodes of reaction network graphs"
    )
    gj_colormap = serializers.CharField(
        default='bone_r',
        help_text="colormap used for plotting gj currents on top of default colormap"
    )
    vector_and_stream_color = serializers.CharField(
        default='k',
        help_text="Specify color of vector arrows and streamlines ('k' = black, 'w' = white,\n'b' = blue, 'r' = red, 'y' = yellow, 'g' = green, 'm' = magenta,'c'=cyan)"
    )
    plot_networks = serializers.BooleanField(
        default=True,
        help_text="export regulatory networks to\ninterconnected graph images?"
    )
    plot_networks_single_cell = serializers.BooleanField(
        default=True,
        help_text="export regulatory networks for single cell to\ninterconnected graph images?"
    )
    while_solving=WhileSolvingSerializer(
        help_text="Results exported during simulation computation.",
        default=lambda: WhileSolvingSerializer().to_internal_value({}),

    )
    after_solving = AfterSolvingSerializer(
        default=lambda: AfterSolvingSerializer().to_internal_value({}),
        help_text="Results exported after simulation computation.",
    )
    save=SaveSerializer(
        help_text="Saving options for export types enabled above.",
        default=lambda: SaveSerializer().to_internal_value({}),
    )
    plot_cluster_mask= serializers.BooleanField(default=True, help_text="'plot seed' creates a plot showing the logarithm of environmental diffusion")