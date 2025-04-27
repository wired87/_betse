#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2025 by Alexis Pietak & Cecil Curry.
# See "LICENSE" for further details.

'''
CLI-specific functional tests exercising **solver-agnostic simulations** (i.e.,
simulations arbitrarily supporting all simulation solvers, including both the
complete BETSE solver *and* the "fast" equivalent circuit solver).
'''

# ....................{ IMPORTS                           }....................
import pytest
from betse.util.test.pytest.mark.pytfail import xfail
from betse.util.test.pytest.mark.pytskip import (
    skip_unless_matplotlib_anim_writer,)

# ....................{ TESTS                             }....................
def test_cli_sim_compat(betse_cli_sim_compat: 'CLISimTester') -> None:
    '''
    Functional test exercising all simulation subcommands required to validate
    backward compatibility with a temporary simulation configuration file
    (complete with a pickled seed, initialization, and simulation) produced by
    the oldest version of this application for which the current version of
    this application guarantees backward compatibility.

    Design
    ----------
    Validating backward compatibility requires validating that the current
    version of this application can successfully load all:

    * Simulation configuration files loadable by this older version.
    * Pickled seeds, initializations, and simulations saved by this older
      version.

    Technically, running the:

    * ``plot sim`` subcommand would test the loadability of pickled
      simulations.
    * ``sim`` subcommand would test the loadability of pickled initializations.
    * ``init`` subcommand would test the loadability of pickled seeds.

    That said, running the ``init`` and ``sim`` subcommands would erroneously
    overwrite the pickled seeds and initializations saved by this older
    version. Doing so would invite edge-case issues that are best avoided; in
    particular, care would need to be taken to run the ``sim`` subcommand
    *after* the ``init`` subcommand. To ameliorate these concerns, plotting
    subcommands guaranteed to both test the loadability of pickled objects
    *and* be side effect-free are run instead.

    Parameters
    ----------
    betse_cli_sim_compat : CLISimTester
        Object running BETSE CLI simulation subcommands against a temporary
        simulation configuration produced by this older application version.
    '''

    # Test all simulation-specific plotting subcommands on this configuration.
    betse_cli_sim_compat.run_subcommands(
        #FIXME: Replace the following line with the following following line
        #*AFTER* bundling a working v0.5.0-era pickled initialization and
        #simulation with our test suite.
        *betse_cli_sim_compat.SUBCOMMANDS_TRY,
        # *betse_cli_sim_compat.SUBCOMMANDS_PLOT,
    )

    #FIXME: We unavoidably break backward compatibility with respect to pickled
    #objects and hence currently only test backward compatibility with respect
    #to the simulation configuration. This is non-ideal, but sufficient for the
    #moment. Ideally, this should be reverted on releasing a new version.
    # betse_cli_sim_compat.run_subcommands(
    #     ('seed',),
    #     is_overwriting_config=False,)


def test_cli_sim_default(betse_cli_sim_default: 'CLISimTester') -> None:
    '''
    Functional test exercising the default simulation configuration on all
    simulation phases (i.e., seed, initialization, and simulation), principally
    for computational instability.

    Unlike the minified simulation configuration leveraged by all other tests,
    the default simulation configuration leveraged by this test is unmodified
    (except for disabling interactive features, which non-interactive testing
    unavoidably requires). In particular, this configuration is *not* minified
    for efficient usage by tests and thus incurs a significant performance
    penalty. This test exercises only the minimal subset of this configuration
    required to detect computational instabilities in this configuration --
    namely, the first two simulation phases.

    Parameters
    ----------
    betse_cli_sim_default : CLISimTester
        Object running non-minified BETSE CLI simulation subcommands.
    '''

    # Test only the first two simulation-specific subcommands with this
    # configuration, as documented above.
    betse_cli_sim_default.run_subcommands_sim()


# Sadly, all existing higher-level parametrization decorators defined by the
# "betse.util.test.pytest.mark.params" submodule fail to support embedded py.test
# "skipif" and "xfail" markers. Consequently, we leverage the lower-level
# parametrization decorator shipped with py.test itself.
@pytest.mark.parametrize(
    ('writer_name', 'filetype'), (
        pytest.param(
            'avconv', 'mp4',
            marks=skip_unless_matplotlib_anim_writer('avconv')),
        pytest.param(
            'ffmpeg', 'mkv',
            marks=skip_unless_matplotlib_anim_writer('ffmpeg')),

        #FIXME: Research this deeper, please. Are all Mencoder-based writers
        #genuinely broken (doubtful), is this our fault (very possible), or is
        #this a platform- or version-specific issue and hence mostly not our
        #fault (also very possible)?
        # skip_unless_matplotlib_anim_writer('mencoder')(('mencoder', 'avi')),
        pytest.param(
            'mencoder', 'avi', marks=xfail(
                reason='Mencoder-based writers fail with obscure errors.')),

        # ImageMagick only supports encoding animated GIFs and hence is
        # effectively a joke writer. Since it remains supported, however, we
        # test it with a reasonable facsimile of a straight face.
        pytest.param(
            'imagemagick', 'gif',
            marks=skip_unless_matplotlib_anim_writer('imagemagick')),
    ),
)
def test_cli_sim_video(
    betse_cli_sim: 'CLISimTester', writer_name: str, filetype: str) -> None:
    '''
    Functional test simulating at least one animation (and all simulation
    features required by that animation) and encoding that animation as
    compressed video of the parametrized filetype via the matplotlib animation
    writer of the parametrized name.

    Since video encoding is justifiably expensive in both space and time, this
    test encodes only a single animation (rather than all available animations)
    for a single simulation-specific BETSE CLI subcommand (rather than all
    available subcommands). The existing :func:`test_cli_sim_visuals` test
    already exercises all animations for all subcommands, albeit with video
    encoding disabled.

    Parameters
    ----------
    betse_cli_sim : CLISimTester
        Object running BETSE CLI simulation subcommands.
    writer_name : str
        Name of the matplotlib animation writer with which to encode video
        (e.g., `ffmpeg`, `imagemagick`).
    filetype : str
        Filetype of videos to encode with this writer (e.g., `mkv`, `mp4`).
    '''

    # Test the minimum number of simulation-specific subcommands required to
    # exercise video encoding with this configuration. Since the "init"
    # subcommand requiring the "seed" subcommand satisfies this constraint, all
    # subsequent subcommands (e.g., "sim", "plot init") are omitted.
    betse_cli_sim.run_subcommands(('seed',), ('init',),)
