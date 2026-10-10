# LogiSight — Last Mile Delivery Dashboard

# About the App

LogiSight is an interactive dashboard that explores last-mile delivery performance—the final stage of transporting an order from a store to a customer. It turns the supplied delivery dataset into charts, summaries, and filters that help logistics managers understand delivery patterns.

This app was developed for the Maths for AI-II FA-2 project using Python, Pandas, Streamlit, and Plotly.

# Why We Built This App
Delivery performance can vary across traffic conditions, weather, vehicle types, agents, areas, and product categories. Looking through thousands of spreadsheet rows makes these patterns difficult to compare. We built LogiSight to bring these comparisons into one dashboard with clear charts and shared filters.
Managers can select conditions, check delivery metrics, and identify questions for further investigation. The app supports decisions about routes, fleet allocation, training, and handling or scheduling without claiming that a chart alone proves the cause of longer deliveries.

# What the App Helps Users Do

- Explore traffic and weather conditions associated with longer deliveries.
- Compare vehicle performance under selected operating conditions.
- Examine agent ratings and age-group patterns.
- Identify area types that need further operational investigation.
- Compare delivery-time distributions across product categories.
- Filter records by date and delivery conditions.
- Download selected records for further analysis.

# How to Use the App

1. Open the dashboard and review the overall delivery metrics.
2. Choose date, weather, traffic, vehicle, area, or category filters.
3. Compare the updated charts and record counts.
4. Identify a question or pattern that needs further investigation.
5. Reset the filters to return to the complete dataset.

# Dataset

The supplied dataset contains 43,739 records and 16 columns. Its order dates cover 11 February to 6 April 2022.

The dashboard displays delivery time in source units because the unit has not been confirmed.

# Main features
- Traffic and weather comparisons to explore longer delivery times.
- Vehicle comparisons with record counts to show sample sizes.
- Agent-rating scatter plot coloured by age group.
- Area and traffic heatmap to explore operating conditions.
- Product-category boxplots to compare delivery-time distributions.
- Shared category and date filters, reset controls, and filtered-data download.
- KPI cards for record count, average, median, and analytical late percentage.

# Limitations

- Results describe the supplied historical dataset, not live deliveries.
- Dates outside the dataset’s coverage return no matching records.
- Small samples, particularly bicycle and Semi-Urban deliveries, require cautious interpretation.
- Agent age does not measure experience.
- The app assumes a rating scale of 1–5, which needs confirmation.
- Analytical late percentage uses the full dataset mean plus one sample standard deviation. It does not measure missed promised deadlines.
- Comparisons show associations and cannot prove what caused longer deliveries.
- The app supports investigation; it does not automatically predict delivery times or optimise routes.

streamlit- https://1000330phreyadhavalshethwalafa2-tyne8c4tknlhcgpg7yc7ps.streamlit.app/

