import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import random
import numpy as np
import plotly.express as px

df = pd.read_csv("clean_new.csv")

# Assuming df is your DataFrame
df['first_word'] = df['first_word'].str.lower()  # Convert to lower case
df['first_word'] = df['first_word'].replace(np.nan, 'unknown')  # Replace NaN values with 'unknown'

# Same data manipulation steps as in your initial code
top10_positions = df['position'].value_counts().nlargest(10).index
df_top10 = df[df['position'].isin(top10_positions)]
tech_names = [name for i, name in enumerate(df_top10['first_word'].unique()) if
              all(name != other and not pd.isna(other) for other in df_top10['first_word'].unique()[:i])]
tech_pivot = pd.pivot_table(data=df_top10, index='position', columns='first_word', values='yearly_salary',
                            aggfunc='count')
tech_pivot = tech_pivot[tech_names]


# Function to create a random color
def random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f'rgb({r},{g},{b})'


# Create a dictionary with a random color for each technology
color_dict = {tech: random_color() for tech in df['first_word'].unique()}


# Function to create the plot
def create_plot(position):
    # Filter based on position and get the top 10 technologies
    filtered_df = tech_pivot.loc[position].nlargest(10)

    # Get the colors for the technologies in the filtered data
    colors = [color_dict[tech] for tech in filtered_df.index]

    # Create an empty Figure
    fig = go.Figure()

    # Add the bar to the figure
    fig.add_trace(go.Bar(
        x=filtered_df.index,
        y=filtered_df.values,
        hoverinfo='y',
        marker_color=colors  # use colors from the dictionary
    ))

    # Update layout for the bar chart and add title/labels
    fig.update_layout(
        title='Top Technologies for Role',
        xaxis=dict(title='Technology'),
        yaxis=dict(title='Count'),
        plot_bgcolor='rgba(0, 0, 0, 0)',  # you can set the background color here
        paper_bgcolor='rgba(0, 0, 0, 0)'  # and here
    )

    # Show the plot using Plotly's Streamlit support
    st.plotly_chart(fig)


# Create a dropdown widget with the positions
dropdown = st.selectbox('Position:', top10_positions)

# Call the create_plot function with the selected position
create_plot(dropdown)
################################### second plot #########################################
## Filter the data for men and women
df_men = df[df['gender'] == 'Male']
df_women = df[df['gender'] == 'Female']

# Calculate the mean value per age and gender
mean_values_men = df_men.groupby('age')['yearly_salary'].mean()
mean_values_women = df_women.groupby('age')['yearly_salary'].mean()

# Create the line traces
men_line = go.Scatter(x=mean_values_men.index, y=mean_values_men, name='Men', mode='lines')
women_line = go.Scatter(x=mean_values_women.index, y=mean_values_women, name='Women', mode='lines')

# Create the layout
layout = go.Layout(
    title='Trend of Yearly Salary over Age (Men vs Women)',
    xaxis=dict(title='Age', range=[22, int(df['age'].max())]),
    yaxis=dict(title='Yearly Salary'),
    showlegend=True
)

# Create the figure
fig = go.Figure(data=[men_line, women_line], layout=layout)

# Create the interactive widgets using Streamlit
gender_dropdown = st.selectbox('Gender:', ['Men', 'Women'])
age_slider = st.slider('Age:', min_value=21, max_value=int(df['age'].max()), value=21)

# Define the function to update the plot
def update_plot():
    gender = gender_dropdown
    age = age_slider

    if gender == 'Men':
        line = men_line
        mean_values = mean_values_men
    else:
        line = women_line
        mean_values = mean_values_women

    # Update line trace
    line.x = mean_values.index
    line.y = mean_values.values

    # Update annotation
    salary = mean_values.get(age, '')
    fig.update_layout(annotations=[
        go.layout.Annotation(
            x=age,
            y=salary,
            text=f"Age: {age}<br>Salary: {salary}",
            showarrow=True,
            arrowhead=7,
            ax=0,
            ay=-40,
            bgcolor='white',
            bordercolor='black',
            borderwidth=1,
            borderpad=4,
            font=dict(size=12)
        )
    ])

# Call the update_plot function initially to populate the plot
update_plot()

# Display the plot using Streamlit's plotly_chart function
st.plotly_chart(fig)



