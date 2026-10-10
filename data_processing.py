"""Cleaning and metrics shared by the dashboard and its tests."""
from pathlib import Path
import numpy as np
import pandas as pd

CATEGORIES = ['Weather', 'Traffic', 'Vehicle', 'Area', 'Category']
REQUIRED = ['Order_ID', 'Delivery_Time', 'Agent_Age', 'Agent_Rating', 'Order_Date', *CATEGORIES]

def prepare_data(source):
    df = pd.read_csv(source)
    missing = sorted(set(REQUIRED) - set(df.columns))
    if missing:
        raise ValueError('Missing required columns: ' + ', '.join(missing))
    audit = {'Source records': len(df)}
    for col in CATEGORIES + ['Order_ID']:
        df[col] = df[col].astype('string').str.strip()
        df[col] = df[col].mask(df[col].str.lower().isin(['', 'nan', 'none', 'null', 'na', 'n/a']))
    df['Area'] = df['Area'].replace({'Metropolitian': 'Metropolitan'})
    for col in ['Delivery_Time', 'Agent_Age', 'Agent_Rating']:
        df[col] = pd.to_numeric(df[col], errors='coerce').replace([np.inf, -np.inf], np.nan)
    valid = df['Order_ID'].notna() & df['Delivery_Time'].gt(0)
    audit['Invalid ID or delivery time removed'] = int((~valid).sum())
    df = df.loc[valid].copy()
    audit['Duplicate order IDs removed'] = int(df['Order_ID'].duplicated().sum())
    df = df.drop_duplicates('Order_ID', keep='first').copy()
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%Y-%m-%d', errors='coerce')
    audit['Missing or invalid dates retained'] = int(df['Order_Date'].isna().sum())
    audit['Missing category cells filled'] = int(df[CATEGORIES].isna().sum().sum())
    df[CATEGORIES] = df[CATEGORIES].fillna('Unknown')
    bad_age = ~df['Agent_Age'].between(0, 100)
    audit['Missing or implausible ages'] = int(bad_age.sum())
    df.loc[bad_age, 'Agent_Age'] = np.nan
    # Explicit analytical assumption: ratings use a 1–5 scale. Keep orders,
    # but omit out-of-range/missing ratings from the rating scatter plot.
    bad_rating = ~df['Agent_Rating'].between(1, 5)
    audit['Ratings excluded from rating analysis'] = int(bad_rating.sum())
    df.loc[bad_rating, 'Agent_Rating'] = np.nan
    df['Age_Group'] = pd.cut(df['Agent_Age'], [-np.inf, 25, 40, np.inf], right=False,
                             labels=['Under 25', '25–39', '40 and above']).astype('string').fillna('Unknown')
    threshold = float(df['Delivery_Time'].mean() + df['Delivery_Time'].std(ddof=1)) if len(df) > 1 else float(df['Delivery_Time'].mean())
    df['Late_Flag'] = df['Delivery_Time'].gt(threshold)
    audit['Cleaned records'] = len(df)
    return df, audit, threshold

def filter_data(df, selections, dates=None):
    mask = pd.Series(True, index=df.index)
    for col, values in selections.items():
        if values:  # Empty selection means all categories.
            mask &= df[col].isin(values)
    if dates is not None:
        start, end = map(pd.Timestamp, dates)
        mask &= df['Order_Date'].between(start, end)
    return df.loc[mask].copy()

def summaries(df, col):
    return df.groupby(col, observed=True)['Delivery_Time'].agg(Average='mean', Records='size').reset_index()
