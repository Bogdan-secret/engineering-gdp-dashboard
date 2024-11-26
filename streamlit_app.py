from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db


def firebase_init():
    if not firebase_admin._apps:
        cred = credentials.Certificate("test-94202-firebase-adminsdk-4zyte-2dddb3c879.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://test-94202-default-rtdb.firebaseio.com/'
        })


def set_page_config():
    st.set_page_config(
        page_title='Metal Prices Dashboard',
        page_icon=':earth_americas:',
    )


def flatten_data(data):
    records = []
    for key, value in data.items():
        if isinstance(value, dict):
            record = {"id": key}
            record.update(value)
            records.append(record)
    return records


@st.cache_data
def get_metal_data_from_firebase():
    ref = db.reference('/')
    metal_data = ref.get()
    print("Fetched metal data:", metal_data)

    if metal_data:
        flat_data = flatten_data(metal_data)
        df_metal = pd.DataFrame(flat_data)
        if 'Date' in df_metal.columns:
            df_metal['Date'] = pd.to_datetime(df_metal['Date'], errors='coerce').dt.date
        return df_metal
    else:
        print("Metal data not found")
        return pd.DataFrame()


def set_title():
    st.title(':earth_americas: Metal Prices Dashboard')
    st.write("Explore historical data on precious metals prices.")


def add_slider() -> (any, any, any, any):
    min_date = metal_df['Date'].min()
    max_date = metal_df['Date'].max()

    from_date, to_date = st.slider(
        'Select date range:',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    return min_date, max_date, from_date, to_date


def plot_diagram():
    if not filtered_df[selected_metals].empty:
        st.header('Metal Prices Changes')
        st.line_chart(filtered_df.set_index('Date')[selected_metals])
    else:
        st.warning("data for metals not found")

    print("filtered df shape:", filtered_df.shape)
    print("filtered df head:", filtered_df.head())


if __name__ == '__main__':
    load_dotenv()

    firebase_init()

    set_page_config()

    metal_df = get_metal_data_from_firebase()
    print("metal df:")
    print(metal_df.head())

    (min_date, max_date, from_date, to_date) = add_slider()

    metal_columns = ['Gold AM Fix', 'Gold PM Fix', 'Platinum AM Fix', 'Palladium AM Fix', 'Palladium PM Fix', 'Iridium',
                     'Silver Fix', 'Ruthenium', 'Rhodium', 'Platinum PM Fix', ]

    selected_metals = st.multiselect(
        'Select metals to view:',
        metal_columns,
        default=['Palladium AM Fix', 'Ruthenium', 'Rhodium']
    )

    filtered_df = metal_df[(metal_df['Date'] >= from_date) & (metal_df['Date'] <= to_date)]

    filtered_df[selected_metals] = filtered_df[selected_metals].apply(pd.to_numeric, errors='coerce')

    filtered_df = filtered_df.dropna(axis=1, how='all')

    plot_diagram()

    from_dateA, to_dateB = st.slider(
        'Select date range:',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
        key="date_slider"
    )
    filtered_df = filtered_df[(filtered_df['Date'] >= from_dateA) & (filtered_df['Date'] <= to_dateB)]
    st.subheader('Filtered Data')
    st.dataframe(filtered_df[['Date'] + selected_metals])
