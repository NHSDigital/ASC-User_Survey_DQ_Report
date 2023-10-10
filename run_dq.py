# this runs the cleaning scripts, the creation of the DQ tables and the the creation of all the dq reports per council.

# this takes a while to run and it is much quicker to run the dq tables seperately and then the create ascof script.

# make sure to restart kernel before running this if you are using a jupyter notebook

# you may get an error when outputing DQ report for councils from the admin proportion table. If so, simple resave the admin proprtion shhet s will fix the error

from Clean_input_data import main
from dq_tables.eligible_and_sample_populations import create_salt_population_table
from dq_tables.missing_admin_proportions import main
from dq_tables._admin_prop import main
from dq_tables._response_rates import main
from dq_tables.weighted_response_proportions import main
import create_report
