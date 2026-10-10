from pathlib import Path
import sys
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from data_processing import prepare_data, filter_data, summaries
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]

def test_actual_dataset():
    df,audit,t=prepare_data(ROOT/'data/last_mile_delivery.csv')
    assert len(df)==43739
    assert df.Delivery_Time.mean()==pytest.approx(124.90564484784746)
    assert df.Delivery_Time.median()==125
    assert 'Metropolitian' not in df.Area.unique()
    assert 'Unknown' in df.Traffic.unique()
    assert df.Agent_Rating.dropna().between(1,5).all()
    assert t==pytest.approx(df.Delivery_Time.mean()+df.Delivery_Time.std(ddof=1))
    jam=filter_data(df,{'Traffic':['Jam']})
    assert len(jam)==13725
    assert jam.Delivery_Time.mean()==pytest.approx(147.76,abs=.01)
    assert summaries(df,'Vehicle').Records.sum()==len(df)
    assert filter_data(df,{'Vehicle':['does not exist']}).empty

def test_dirty_data(tmp_path):
    p=tmp_path/'dirty.csv'
    base={'Order_ID':['a','a','b','c'],'Delivery_Time':[10,20,-1,30],'Agent_Age':[24,40,1000,32],'Agent_Rating':[6,4,3,None],'Order_Date':['2022-01-01']*4,'Weather':[' Sunny ']*4,'Traffic':['NaN']*4,'Vehicle':['van']*4,'Area':['Metropolitian']*4,'Category':['']*4}
    pd.DataFrame(base).to_csv(p,index=False)
    df,a,t=prepare_data(p)
    assert len(df)==2 and a['Duplicate order IDs removed']==1
    assert df.Traffic.eq('Unknown').all() and df.Category.eq('Unknown').all()
    assert df.Agent_Rating.isna().all()
    pd.DataFrame({'x':[1]}).to_csv(p,index=False)
    with pytest.raises(ValueError,match='Missing required columns'): prepare_data(p)

def test_ui_filters_and_reset():
    at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run()
    assert not at.exception
    assert at.metric[0].value=='43,739'
    assert len(at.get('plotly_chart'))==8
    at.multiselect[1].set_value(['Jam']).run()
    assert not at.exception and at.metric[0].value=='13,725'
    for i, value in [(0,'Sunny'),(2,'scooter'),(3,'Urban'),(4,'Clothing')]:
        at.multiselect[i].set_value([value]).run()
        assert not at.exception
    at.button[0].click().run()
    assert not at.exception and at.metric[0].value=='43,739'
    at.multiselect[2].set_value(['bicycle']).run()
    at.multiselect[3].set_value(['Semi-Urban']).run()
    assert not at.exception and any('No deliveries match' in w.value for w in at.warning)
    at.button[0].click().run()
    at.checkbox[0].check().run()
    assert not at.exception and at.metric[0].value=='43,739'


def test_year_month_day_filters():
    at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run()
    at.multiselect[5].set_value([2022]).run()
    at.multiselect[6].set_value([3]).run()
    at.multiselect[7].set_value([19]).run()
    assert not at.exception
    df,_,_=prepare_data(ROOT/'data/last_mile_delivery.csv')
    expected=df.loc[df.Order_Date.eq(pd.Timestamp('2022-03-19'))]
    assert at.metric[0].value==f'{len(expected):,}'
    at.multiselect[6].set_value([12]).run()
    assert not at.exception and any('No deliveries match' in w.value for w in at.warning)
    at.button[0].click().run()
    assert not at.exception and at.metric[0].value=='43,739'
