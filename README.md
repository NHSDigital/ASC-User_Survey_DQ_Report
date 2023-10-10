# ASCS Data Quality reports

# Adult Social Care Data Quality Reports.

The DQ reports are a summary of the councils survey submission. They show the aggregated totals alongside the councils data for last year and the England mean and values are flagged if the differ to the England mean. They provide a quick high level summary of the administrative and questionnaire data to allow councils to spot any potential issues in the data submitted


# Initial package set up

Run the following command to set up your environment correctly **from the root directory**

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If, while developing this package, you change the installed packages, please update the environment file using

```
pip list --format=freeze > requirements.txt
```

## VSCode specific setup

For Visual Studio Code it is necessary that you change your default interpreter to be the virtual environment you just created `.venv`. To do this use the shortcut `Ctrl-Shift-P`, search for `Python: Select interpreter` and select `.venv` from the list.


# Running the code

Please check that the settings, including the path to the input files, are correct in `params.py`.

This codebase cleans the initial input file and outputs to seecure location before producing seven (7) tables needed to create each data quality report.

Depending on which files you need, here are the short codes for outputting each from the base directory:
    - to clean the input data: python -m Clean_input_data
    - to produce the tables needed for DQ report: python -m create_dq_sheets
    - to produce the data quality report for each council: python -m create_report
    - To run the entire codebase to clean the data,create all the files and the report: python -m run_dq (takes longer to run)

After running the codes, you will get a prompt asking to enter the council code for one particularly or "*" to prodce the reports for all councils. Enter the prompt and the DQ report will be saved in the location stated in the parameters.


# Author(s)
Tomide Adeyeye

Repo Owner Contact Details: tomide.adeyeye1@nhs.net, liz.selfridge@nhs.net

# Licence

The Personal Social Care Services codebase is released under the MIT License.
The documentation is © Crown copyright and available under the terms of the Open Government 3.0 licence.



