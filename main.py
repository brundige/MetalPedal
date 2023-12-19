import streamlit as st
import pandas as pd
import pydeck as pdk

import seaborn as sns

from matplotlib import pyplot as plt

st.set_option('deprecation.showPyplotGlobalUse', False)
light_conditions = {
    0: "Dark - Lighted",
    1: "Daylight",
    2: "Dark - Unknown Lighting",
    3: "Dawn",
    4: "Dark - Not Lighted",
    5: "Dusk",
    6: "Unknown"
}

columns = {
    "Incident Number": {"Description": "CPD Incident Number that is unique to each incident.", "Type": "Plain Text"},
    "Incident Date": {"Description": "Date the vehicle incident occurred.", "Type": "Date & Time"},
    "Time Num": {"Description": "24-hour time rounded to the nearest half-hour saved as a number data type.",
                 "Type": "Number"},
    "Street": {"Description": "Street address where the incident occurred.", "Type": "Plain Text"},
    "Alt Street": {"Description": "Alternative name for the street if it is a state highway.", "Type": "Plain Text"},
    "City": {"Description": "City where the incident occurred.", "Type": "Plain Text"},
    "County": {"Description": "County where the incident occurred.", "Type": "Plain Text"},
    "Intersection": {"Description": "Closest intersecting street to the vehicle incident.", "Type": "Plain Text"},
    "Mile Post": {"Description": "Mile post where the incident occurred if applicable.", "Type": "Number"},
    "Accident Type": {"Description": "General type of vehicle incident that occurred.", "Type": "Plain Text"},
    "Collision Type": {"Description": "Type of collision that occurred, description of how it occurred.",
                       "Type": "Plain Text"},
    "Hit and Run": {"Description": "Checked (true), indicates the incident was a hit and run.", "Type": "Plain Text"},
    "Involved Fatal Injury": {"Description": "Checked (true), indicates the incident involves a fatal injury.",
                              "Type": "Plain Text"},
    "Involved Medical Transport": {
        "Description": "Checked (true), indicates medical transport was needed for the incident.",
        "Type": "Plain Text"},
    "Involved Placarded Truck": {"Description": "Checked (true), indicates the incident involves a truck.",
                                 "Type": "Plain Text"},
    "Posted Speed": {"Description": "The posted speed of the address where the incident occurred.", "Type": "Number"},
    "Total Vehicles Involved": {"Description": "Total number of vehicles involved in the incident.", "Type": "Number"},
    "Weather Code": {"Description": "Describes the condition of the weather at the time.", "Type": "Plain Text"},
    "Pedestrian Involved": {"Description": "Checked (true), indicates the incident involves a pedestrian.",
                            "Type": "Plain Text"},
    "Bicycle Involved": {"Description": "Checked (true), indicates the incident involves a bicycle.",
                         "Type": "Plain Text"},
    "Drug Involved": {"Description": "Checked (true), indicates the incident involves drugs.", "Type": "Plain Text"},
    "Alcohol Involved": {"Description": "Checked (true), indicates the incident involves alcohol.",
                         "Type": "Plain Text"},
    "Latitude": {"Description": "", "Type": "Number"},
    "Longitude": {"Description": "", "Type": "Number"},
    "Location WKT": {"Description": "Point", "Type": ""},
    "Location": {"Description": "", "Type": "Plain Text"},
    "Light Condition": {"Description": "", "Type": "Plain Text"},
}

months = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: "May",
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: "October",
    11: 'November',
    12: 'December'
}

days = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: "Friday",
    5: 'Saturday',
    6: 'Sunday',
}


def add_padding():
    return st.text(' '), st.text(' '), st.text(' '), st.text(' '), st.text(' '), st.text(' '), st.text(' ')


def corr_matrix(df):
    coorColA, coorColB = st.columns(2)

    df = df.drop(['pedestrian', 'bicycle'], axis=1)
    sns.set(style="darkgrid")
    coor = df.corr()

    with coorColA:
        sns.heatmap(coor, cmap='viridis')
        st.pyplot()

    with coorColB:
        st.dataframe(coor)


def temporal_frequency(df):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader('By year')
        sns.countplot(x='year', data=df)
        st.pyplot()

    with col2:
        st.subheader('By month')
        df['month'] = df['month'].map(months)
        # put the months in order
        df['month'] = pd.Categorical(df['month'], categories=months.values(), ordered=True)
        sns.countplot(x='month', data=df)
        # set the xticks to the months
        plt.xticks(rotation=45)
        st.pyplot()

    with col3:
        st.subheader('By day of the week')
        df['day_of_week'] = df['day_of_week'].map(days)
        # put the months in order
        df['day_of_week'] = pd.Categorical(df['day_of_week'], categories=days.values(), ordered=True)
        sns.countplot(x='day_of_week', data=df)
        # set the xticks to the months
        plt.xticks(rotation=45)
        st.pyplot()


def show_map(df):
    try:
        layers = {
            "Pedestrian Safety": pdk.Layer(
                "HexagonLayer",
                data=df,
                get_position=["Longitude", "Latitude"],
                radius=100,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        }
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={"latitude": 35.0456, "longitude": -85.3097, "zoom": 11, "pitch": 50},
            layers=[layers["Pedestrian Safety"]],
        ))
    except Exception as e:
        st.error(e)
        st.write(df.head())


def most_dangerous_streets(df):
    colA, colB = st.columns(2)

    with colA:
        sns.countplot(y='Street', data=df, order=df['Street'].value_counts().iloc[:10].index)
        st.pyplot()

    with colB:
        df['intersection'] = df['Street'] + ' and ' + df['Intersection']

        # set y label to "intersection"

        sns.countplot(y='intersection', data=df, order=df['intersection'].value_counts().iloc[:10].index)
        st.pyplot()


if __name__ == '__main__':
    st.set_page_config(layout="wide")

    # IMPORT DATA

    serious_incidents = pd.read_csv('serious.csv')
    all_data = pd.read_csv('ps_cleaned.csv')

    st.title('Pedestrian Safety in Chattanooga')
    st.write(
        'This dataset piggybacks off of the amazing work that Charlie Mix did in his project "Pedestrian Safety in '
        'Chattanooga".  Tim Mooreland raised some questions about how we could use this data to help improve '
        'pedestrian safety in Chattanooga. A good first step is to evaluate the data temporally and spatially to see '
        'if there are any trends that we can identify.  This will help us to identify areas of concern and to develop '
        'a plan to address them.')

    st.header('Data Description')
    st.write(
        'This dataset contains information about incidents where a pedestrian or cyclist was involved in a collision '
        'with a vehicle. The dataset was collected from the Chattanooga Police Department and spans from June 2019 to '
        'present with daily updates. the dataset contains 27 columns and ~ 650 rows. The data can be found at '
        'https://data.chattlibrary.org/Transportation/Pedestrian-Safety-Incidents/5vex-7wgt/data.')

    # Display Features in a Dropdown

    feature = st.selectbox('Select a feature to learn more about it.', list(columns.keys()))
    st.write('Description: ', columns[feature]['Description'])

    # Discuss the data cleaning process

    st.header('Data Cleaning')
    st.write('The dataset is mostly complete and does not require much cleaning.  The following steps were taken to '
             'optimize the data for analysis. All of the incidents occured in teh city of Chattanooga in Hamilton '
             'county, the city and county columns were dropped. The mile post column was dropped because it was '
             'mostly null values.  The location column was dropped because it was redundant with the latitude and '
             'longitude columns.  The location WKT column was dropped because it was not needed.  The time column was '
             'dropped because it was redundant with the time num column.  The incident number column was dropped '
             'because it was not needed.  The incident date column was dropped because it was redundant with the '
             'year, month, and day of week columns.  The street and intersection columns were dropped because they '
             'were redundant with the latitude and longitude columns. Discrete features were one hot encoded. '
             'Features with multiple options were categoricaly encoded   The data was then split into two dataframes, '
             'one for all incidents and one for serious incidents.')

    # Display the data cleaning process

    st.header('Data limitations')
    st.write('The dataset only contains incidents that were reported to the police.  There are likely many incidents '
             'that were not reported. Utilty could be added by evaluating the data against other datasets such as '
             'population density and traffic volume to identify areas of concern.')

    st.header('Data Analysis')
    st.divider()
    st.write(
        'First, an Objective was defined. We want to identfy causes of pedestrian accidents and evaluate solutions that maximze impact while minmizing cost.')
    st.subheader('Descriptive Analysis')
    st.write('todo: add descriptive analysis')
    st.subheader('Diagnostic Analysis')
    st.write('todo: add diagnostic analysis')
    st.subheader('Predictive Analysis')
    st.write('todo: add predictive analysis')
    st.subheader('Prescriptive Analysis')
    st.write('todo: add prescriptive analysis')

    st.header('Data Visualization')
    st.write('Charlie Mix did a fantastic job of visualizing the the data spatially. We wanted to build on his work by'
             'visualizing the data temporally and by other features.  We also wanted to identify features that were '
             'correlated with more serious outcomes.')

    st.header('impact on policy')
    st.write(
        'Data is only useful if it is used to make decisions. Limited Civic resources require us to be strategic as '
        'we implement solutions to improve pedestrian safety'
        'An Impact Matrix was created to evaluate the impact of each intervention and the effort required to '
        'address it.')

    st.write('data conclusions')
    st.write('data recommendations')
    st.write('data next steps')

    # MAP OF ALL INCIDENTS AND SERIOUS INCIDENTS

    incident_col1, incident_col2 = st.columns(2)

    with incident_col1:
        st.header('All Incidents')
        st.write(
            'Map of all incidents.')
        show_map(all_data)

    with incident_col2:
        st.header('Serious Incidents')
        st.write(
            'This section is a subset of the data that only includes accidents where there was a fatality or the '
            'patient was transported to the hospital.')
        show_map(serious_incidents)

    st.subheader('Temporal Analasys')
    st.write('The data was analyzed temporally to identify trends and areas of concern.'
             'Data was analyzed by year, month, and day of the week.  The data was also analyzed by time of day.'
             'From 2018-2023, the number of incidents has been generally increasing.  There was a sharp increase in '
             'in 2021')
    st.subheader('Monthly and Weekly Trends')
    st.subheader('Daylight and Traffic Volume could explain the monthly and weekly trends')
    st.write('The number of incidents peaks in Feburary and stays around the same untl May, when it begins to '
             'decrease. In September, the number of incidents begins to increase again. Our hypothesis is that incdents are highly correlated with daylight'
             'the highest incidents occur on Tuesdays and Fridays.  The lowest number of incidents occur on Sundays. '
             'Our hypothesis is that incidents are highly correlated with traffic volume.')

    temporal_frequency(all_data)

    # time of day, light condition, weather, posted speed, alcohol, drugs,  fatal, pedestrian, bicycle
    st.subheader('Time of Day')
    st.divider()

    st.subheader('the number of incidents peak around commute times, lunch time, and social hours')
    st.write('incidents are low in early moring and gnerally trend up until 830pm. The number of incidents then '
             'decreases. Statistically significant increases occur during the morning commute, lunch time, and '
             'social hours.')

    st.bar_chart(all_data['Time Num'].value_counts())

    # WEATHER

    st.header('Weather')
    st.divider()
    st.bar_chart(all_data['Weather Code'].value_counts())

    # LIGHT CONDITION

    st.header('Light Condition')
    st.divider()
    # convert the light condition to a string
    all_data['Light Condition'] = all_data['Light Condition'].map(light_conditions)
    st.bar_chart(all_data['Light Condition'].value_counts())

    # DISPLAY THE MOST DANGEROUS STREETS
    st.subheader('Incidents by street & Intersection')
    st.divider()
    most_dangerous_streets(all_data)
    add_padding()

    # CORRELATION MATRIX
    st.subheader('Features that are highly correlated')
    st.write('The correlation matrix reveals that there is a strong correlation between the posted speed limit, '
             'alcohol and drug use, as well as the time of day. Lets look at these in more detail.')
    st.divider()

    foo = pd.read_csv('df_corr.csv')
    corr_matrix(foo)

    add_padding()

    # filter the correlation matrix to only show the most correlated values


