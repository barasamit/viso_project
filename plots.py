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
# Filter the data for men and women
# Filter the data for men and women
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
############################ third plot #########################################

avg_experience = df.groupby('work_level')['experience'].mean().reset_index()

# Define the job levels and corresponding required experience
job_levels = avg_experience["work_level"]
required_experience = avg_experience["experience"].astype(int)

# Sort the job levels in ascending order
sorted_indices = required_experience.argsort()
job_levels_sorted = job_levels.iloc[sorted_indices]
required_experience_sorted = required_experience.iloc[sorted_indices]

# Create the bar plot using Plotly
fig = go.Figure(data=go.Bar(
    x=job_levels_sorted,
    y=required_experience_sorted,
    marker_color='steelblue'
))

# Configure the layout
fig.update_layout(
    title='Job Level Based on Required Experience',
    xaxis_title='Job Level',
    yaxis_title='Required Experience',
    showlegend=False
)


# Create the interactive function to update the relevant job levels
def update_job_levels(work_experience):
    relevant_job_levels = job_levels_sorted[required_experience_sorted <= work_experience]
    fig.data[0].x = relevant_job_levels


# Create the interactive widget using Streamlit
work_experience_slider = st.slider('Work Experience:', min_value=0, max_value=max(required_experience), value=0)

# Register the interactive function to handle widget changes
update_job_levels(work_experience_slider)

# Display the plot using Streamlit's plotly_chart function
st.plotly_chart(fig)

# Export the plot as an interactive HTML file
fig.write_html('interactive_plot.html', include_plotlyjs='cdn')

############################ fourth plot #########################################
# Filter to only include data from Europe in 2020
df_europe_2020 = df[(df['city'].isin(['Berlin', 'London', 'Paris']))]

# Count the occurrences of each job title
job_title_counts = df_europe_2020['position'].value_counts().reset_index()

# Create a list of columns to exclude
columns_to_exclude = ['Position 1', 'Position 2']  # Add the columns you want to exclude

# Remove the excluded columns
job_title_counts = job_title_counts[~job_title_counts['index'].isin(columns_to_exclude)]

# Calculate percentage
total_jobs = job_title_counts['position'].sum()
job_title_counts['percentage'] = job_title_counts['position'] / total_jobs * 100

# Create a custom color scale
color_scale = px.colors.qualitative.Pastel

# Create bar plot using Plotly Express
fig = px.bar(job_title_counts, y='index', x='percentage', color='index', orientation='h',
             labels={'index': 'Job Title', 'percentage': 'Percentage'},
             title='Job Titles in Europe in 2020',
             color_discrete_sequence=color_scale)

# Update layout to add interactivity
fig.update_layout(
    height=600,
    hovermode='y',
    xaxis=dict(title='Percentage'),
    yaxis=dict(title='Job Title'),
    showlegend=False
)

# Display the plot using Streamlit's plotly_chart function
st.plotly_chart(fig)

############################ fifth plot #########################################
data_scientist_df = df[df['position'] == 'Data Scientist'].copy()
top_tech = pd.Series(', '.join(df['main_tech']).split(', ')).value_counts().nlargest(10).index.tolist()

skills = top_tech
qualifications = data_scientist_df["work_level"]

skills = ['Python', 'R', 'SQL', 'Java', 'C++']
qualifications = data_scientist_df["work_level"]

# Calculate the frequency of each skill-qualification combination
freq_df = df[df['main_tech'].isin(skills)].groupby(['main_tech', 'emp_state']).size().reset_index(name='frequency')
freq_df = freq_df.pivot(index='emp_state', columns='main_tech', values='frequency').fillna(0)
freq_df = freq_df.apply(lambda x: x/x.sum(), axis=1)
freq_df = freq_df.loc[:, freq_df.sum(axis=0).nlargest(5).index]

# Create the heatmap
fig = px.imshow(freq_df.values,
                x=freq_df.columns,
                y=freq_df.index,
                color_continuous_scale='Blues',
                labels=dict(x='Skills', y='Qualifications', color='Frequency'),
                title='Skill-Qualification Heatmap')

# Set the colorbar format to percentage
fig.update_layout(coloraxis_colorbar=dict(title='Frequency', tickformat='%'))

# Display the plot using Streamlit's plotly_chart function
st.plotly_chart(fig)
