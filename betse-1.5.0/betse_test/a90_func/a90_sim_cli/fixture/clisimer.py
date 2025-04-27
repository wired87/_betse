#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright 2014-2025 by Alexis Pietak & Cecil Curry.
# See "LICENSE" for further details.

'''
Fixtures and fixture classes efficiently exercising multiple subcommands of the
BETSE CLI in the active Python interpreter.
'''

# ....................{ IMPORTS                            }....................
from betse_test._fixture.simconf.simconfclser import SimConfTestInternal
from betse_test.a90_func._fixture.clier import CLITester
from betse_test.a90_func.a90_sim_cli.fixture.clisimclser import CLISimTester
from pytest import fixture

# ....................{ FIXTURES                           }....................
@fixture
def betse_cli_sim(
    betse_cli: CLITester,
    betse_sim_conf: SimConfTestInternal,
) -> CLISimTester:
    '''
    Per-test fixture returning an object suitable for running one or more BETSE
    CLI simulation subcommands (e.g., ``betse seed``, ``betse sim``) with a
    temporary minified simulation configuration isolated to the current fixture
    or test.

    Parameters
    ----------
    betse_cli : CLITester
        Object running a single simulation-specific BETSE CLI subcommand.
    betse_sim_conf : SimConfTestInternal
        Object encapsulating a temporary minified simulation configuration.

    Returns
    ----------
    CLISimTester
        Object running multiple minified BETSE CLI simulation subcommands.
    '''

    return CLISimTester(
        cli_tester=betse_cli,
        sim_state=betse_sim_conf,
    )


@fixture
def betse_cli_sim_default(
    betse_cli: CLITester,
    betse_sim_conf_default: SimConfTestInternal,
) -> CLISimTester:
    '''
    Per-test fixture returning an object suitable for running one or more BETSE
    CLI simulation subcommands (e.g., ``betse seed``, ``betse sim``) with the
    temporary default simulation configuration isolated to the current fixture
    or test.

    Caveats
    ----------
    **This fixture is intended only for tests exercising the default simulation
    configuration.** This configuration has *not* been modified for testing
    purposes and hence is *not* minified. Most tests prefer the minified
    configuration produced by the :func:`betse_cli_sim` fixture instead.

    Parameters
    ----------
    betse_cli : CLITester
        Object running a single simulation-specific BETSE CLI subcommand.
    betse_sim_conf_default : SimConfTestInternal
        Wrapper around a temporary non-minified simulation configuration file.

    Returns
    ----------
    CLISimTester
        Object running multiple non-minified BETSE CLI simulation subcommands.
    '''

    return CLISimTester(
        cli_tester=betse_cli,
        sim_state=betse_sim_conf_default,
    )


@fixture
def betse_cli_sim_compat(
    betse_cli: CLITester,
    betse_sim_conf_compat: SimConfTestInternal,
) -> CLISimTester:
    '''
    Per-test fixture returning an object suitable for running one or more BETSE
    CLI simulation subcommands (e.g., ``betse seed``, ``betse sim``) with the
    temporary simulation configuration isolated to the current fixture or test
    (complete with a pickled seed, initialization, and simulation) produced by
    the oldest version of this application for which the current version of
    this application guarantees backward compatibility.

    Parameters
    ----------
    betse_cli : CLITester
        Object running a single simulation-specific BETSE CLI subcommand.
    betse_sim_conf_compat : SimConfTestInternal
        Object encapsulating a temporary simulation configuration produced by
        this oldest version of this application.

    Returns
    ----------
    CLISimTester
        Object running multiple BETSE CLI simulation subcommands.
    '''

    return CLISimTester(
        cli_tester=betse_cli,
        sim_state=betse_sim_conf_compat,
    )
