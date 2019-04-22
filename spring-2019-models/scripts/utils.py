import orca
import numpy as np
from urbansim.utils import misc


def register_skim_access_variable(
        column_name, variable_to_summarize, impedance_measure,
        distance, skims_table, agg=np.sum, log=False):
    """
    Register skim-based accessibility variable with orca.
    Parameters
    ----------
    column_name : str
        Name of the orca column to register this variable as.
    impedance_measure : str
        Name of the skims column to use to measure inter-zone impedance.
    variable_to_summarize : str
        Name of the zonal variable to summarize.
    distance : int
        Distance to query in the skims (e.g. 30 minutes travel time).
    mode_name: str
        Name of the mode to query in the skims.
    period: str
        Period (AM, PM, OffPeak) to query in the skims.

    Returns
    -------
    column_func : function
    """
    @orca.column('zones', column_name, cache=True, cache_scope='iteration')
    def column_func(zones):
        df = skims_table.to_frame()
        results = misc.compute_range(
            df, zones.get_column(variable_to_summarize),
            impedance_measure, distance, agg=agg)

        if len(results) < len(zones):
            results = results.reindex(zones.index).fillna(0)

        # add vars from orig zone, typically not included in skims
        results = results + zones[variable_to_summarize]

        if log:
            results = results.apply(eval('np.log1p'))

        return results

    return
