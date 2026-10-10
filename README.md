# LogiSight Last Mile Delivery Dashboard

FA-2 Mathematics for AI-II. Python 3.11 or 3.12 recommended.

## Run on Windows

Extract the ZIP. Open PowerShell in the LogiSight folder.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Using the environment's Python directly avoids PowerShell activation-policy issues.

## GitHub and Streamlit Cloud

1. Create a GitHub repository for this assessment.
2. Upload app.py, data_processing.py, requirements.txt, README.md, the data folder and .streamlit/config.toml. Preserve folder paths. Do not upload .venv.
3. In Streamlit Community Cloud create an app from that repository, choose the branch and app.py as the entry point.
4. Choose Python 3.12 in advanced settings and deploy.
5. Test the public URL and submit it. This package has not itself been published.

## Required features

Weather and traffic mean bars, vehicle mean bar, rating/time scatter coloured by age groups, Area × Traffic mean heatmap, Category distribution boxplot. Filters affect every chart and KPI. Optional histogram and daily trend, record export, cleaning audit and reset are included.

## Method

Delivery_Time's unit is not specified in the CSV, so no unverified unit is asserted. Analytical late means time > full cleaned dataset mean + sample standard deviation; this is not a promised-deadline breach. The fixed threshold does not change with filters. Missing categories become Unknown. Invalid ratings are excluded from scatter only under an explicit 1–5 assumption. Confirm the rating scale with your teacher. Age is not experience; comparisons are associations. Area is a categorical field, so the heatmap does not invent geographic locations.

## Tests

Install pytest separately and run `python -m pytest tests -q`. Tests use Streamlit AppTest plus data checks; see TEST_RESULTS.md for the verification performed on this package.

## Date controls
Select one or more years, months, and days of month independently. Empty selections mean all. Optional calendar range can be combined with these controls. Only 2022 exists in the supplied data; all twelve months and days 1–31 are selectable, with empty results handled safely. The calendar range is no longer restricted to source bounds. Reset clears all date selections.
