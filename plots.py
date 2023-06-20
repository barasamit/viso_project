import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import random
import numpy as np
import plotly.express as px

# Add the map to the sidebar
st.title("Help for the beginning high tech worker")
st.header("Choose your future job")
st.write("You can see the most popular programming languages for the job you want to do. Select your desired position, work level, and employee state from the dropdown menus below.")

df = pd.read_csv("clean_new.csv")


df['first_word'] = df['first_word'].str.lower()  # Convert to lower case
df['first_word'] = df['first_word'].replace(np.nan, 'unknown')  # Replace NaN values with 'unknown'

top10_positions = df['position'].value_counts().nlargest(10).index
df_top10 = df[df['position'].isin(top10_positions)]
tech_names = [name for i, name in enumerate(df_top10['first_word'].unique()) if
              all(name != other and not pd.isna(other) for other in df_top10['first_word'].unique()[:i])]

# Include 'work_level' and 'emp_state' in the pivot_table
tech_pivot = pd.pivot_table(data=df_top10, index=['position', 'work_level', 'emp_state'], columns='first_word',
                            values='yearly_salary', aggfunc='count')
tech_pivot = tech_pivot[tech_names]

random.seed(42)


def random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f'rgb({r},{g},{b})'


color_dict = {tech: random_color() for tech in df['first_word'].unique()}


def create_plot(position, work_level, emp_state, sort_by):
    try:
        # Filter based on position, work_level, and emp_state and get the top 10 technologies
        filtered_df = tech_pivot.loc[position, work_level, emp_state].nlargest(10)

        if sort_by == 'Name':
            filtered_df = filtered_df.sort_index(ascending=False)

        elif sort_by == 'Percentage':
            total_workers = filtered_df.sum()  # Calculate the total number of workers
            filtered_df = (filtered_df / total_workers) * 100  # Calculate the percentage

        fig = go.Figure()

        for tech, count in zip(filtered_df.index, filtered_df.values):
            fig.add_trace(go.Scatter(
                x=[count],
                y=[tech],
                mode='markers',
                marker=dict(color=color_dict[tech], size=10),
                line=dict(color='gray', width=1)
            ))

            fig.add_trace(go.Scatter(
                x=[0, count],
                y=[tech, tech],
                mode='lines',
                line=dict(color='black', width=1)
            ))

        fig.update_layout(
            title='Top Technologies for Role',
            xaxis=dict(title='Count' if sort_by == 'Count' else 'Percentage of workers' if sort_by == 'Percentage' else ''),
            yaxis=dict(title='Technology'),
            showlegend=False,
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)'
        )

        st.plotly_chart(fig)
    except KeyError:
        st.error('No data available for the selected combination of Position, Work Level, and Employee State. Try a different combination.')


# Create dropdown widgets with positions, work levels, and employee states
dropdown = st.selectbox('Position:', top10_positions)
work_levels = df['work_level'].unique()
work_level_dropdown = st.selectbox('Work Level:', work_levels)
emp_states = df['emp_state'].unique()
emp_state_dropdown = st.selectbox('Employee State:', emp_states)
sort_by_radio = st.radio('Sort By:', ['Name', 'Percentage'])

# Call the create_plot function with the selected position, work level, employee state, and sort by option
create_plot(dropdown, work_level_dropdown, emp_state_dropdown, sort_by_radio)
st.write("---------------------------------------")

################################### second plot #########################################
st.header("Choose your gender and age")
st.write("You can see the average salary according to your details. "
         "Select your gender from the dropdown menu and adjust your age using the slider below.")
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
age_slider = st.slider('Age:', min_value=22, max_value=int(df['age'].max()), value=22, step=1)

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
st.write("---------------------------------------")

############################ third plot #########################################
st.header("Choose your work experience")

df = df[df['work_level'] != 'Working Student']

avg_experience = df.groupby('work_level')['experience'].mean().reset_index()

job_levels = avg_experience["work_level"]
required_experience = avg_experience["experience"].astype(int)

sorted_indices = required_experience.argsort()
job_levels_sorted = job_levels.iloc[sorted_indices]
required_experience_sorted = required_experience.iloc[sorted_indices]

# Creating a color gradient
color_gradient = ['rgb(150,0,90)', 'rgb(0,0,200)']
color_scale = np.interp(required_experience_sorted, (required_experience_sorted.min(), required_experience_sorted.max()), [0,1])

# Create the bar plot using Plotly
fig = go.Figure(data=go.Bar(
    x=job_levels_sorted,
    y=required_experience_sorted,
    marker=dict(
        color=color_scale,  # Adding color gradient
        colorscale=color_gradient,
        line=dict(color='rgb(8,48,107)', width=1.5),
    ),
    opacity=0.6
))

# Configure the layout
fig.update_layout(
    title={
        'text': 'Job Level Based on Required Experience',
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    xaxis_title='Job Level',
    yaxis_title='Required Experience',
    showlegend=False
)

# Add a two-way slider
experience_range = st.slider("Select your experience range",
                             int(required_experience_sorted.min()),
                             int(required_experience_sorted.max()),
                             (int(required_experience_sorted.min()), int(required_experience_sorted.median())))

# Filter the data based on the selected range
filtered_job_levels_sorted = job_levels_sorted[(required_experience_sorted >= experience_range[0]) & (required_experience_sorted <= experience_range[1])]
filtered_required_experience_sorted = required_experience_sorted[(required_experience_sorted >= experience_range[0]) & (required_experience_sorted <= experience_range[1])]

# Update the plot based on the filtered data
fig.data[0].x = filtered_job_levels_sorted
fig.data[0].y = filtered_required_experience_sorted

st.plotly_chart(fig)

st.write("---------------------------------------")

############################ fourth plot #########################################

st.header("Most popular job titles in Europe")
st.write("As the job becomes more popular, there are more open positions. The bar chart below shows the percentage of each job title in Europe in 2020. Click on a bar to see the percentage of that job title.")

# Filter to only include data from Europe in 2020
df_europe_2020 = df[(df['city'].isin(['Berlin', 'London', 'Paris']))]

# Count the occurrences of each job title
job_title_counts = df_europe_2020['position'].value_counts().reset_index()

# Rename the columns to 'position' and 'count'
job_title_counts.columns = ['position', 'count']

# Create a list of columns to exclude
columns_to_exclude = ['Position 1', 'Position 2']  # Add the columns you want to exclude

# Remove the excluded columns
job_title_counts = job_title_counts[~job_title_counts['position'].isin(columns_to_exclude)]

# Calculate percentage
total_jobs = job_title_counts['count'].sum()
job_title_counts['percentage'] = job_title_counts['count'] / total_jobs * 100

# Filter to only include job titles with a percentage of at least 1.5%
job_title_counts = job_title_counts[job_title_counts['percentage'] >= 1.5]

# Create a custom color scale
color_scale = px.colors.qualitative.Pastel

# Create bar plot using Plotly Express
fig = px.bar(job_title_counts, y='position', x='percentage', color='position', orientation='h',
             labels={'position': 'Job Title', 'percentage': 'Percentage'},
             title='Job Titles in Europe in 2020',
             color_discrete_sequence=color_scale)

# Update layout to add interactivity
fig.update_layout(
    width=800,
    height=600,
    hovermode='y',
    xaxis=dict(title='Percentage'),
    yaxis=dict(title='Job Title', automargin=True, side='right'),  # Align y-axis labels to the right
    showlegend=False
)

# Display the plot using Streamlit's plotly_chart function
st.plotly_chart(fig)
