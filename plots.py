import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import random
import numpy as np
import plotly.express as px
import plotly.io as pio

# Add the map to the sidebar
st.title("Help for the beginning high tech worker")

# Add the select box for Position in the sidebar

# Rest of the code remains the same...

df = pd.read_csv("clean_new.csv")

df['first_word'] = df['first_word'].str.lower()  # Convert to lower case
df['first_word'] = df['first_word'].replace(np.nan, 'unknown')  # Replace NaN values with 'unknown'

top10_positions = df['position'].value_counts().nlargest(10).index

df_top10 = df[df['position'].isin(top10_positions)]
tech_names = [name for i, name in enumerate(df_top10['first_word'].unique()) if
              all(name != other and not pd.isna(other) for other in df_top10['first_word'].unique()[:i])]

# Add the select box for Position in the sidebar
top10_positions = list(top10_positions)
top10_positions.insert(0, "All")  # Add "All" as the first option

position_sidebar = st.sidebar.selectbox('Choose your dream job:', top10_positions,
                                        index=0)  # Set "All" as the default option
position_explanations = {
    'Software Engineer': 'A software engineer is responsible for designing, developing, and maintaining software applications. They work with programming languages, frameworks, and tools to create functional and efficient software solutions.',
    'Backend Developer': 'A backend developer focuses on server-side development. They handle databases, APIs, and business logic to ensure smooth data flow and efficient server operations.',
    'Data Scientist': 'A data scientist analyzes and interprets complex data to extract valuable insights and make data-driven decisions. They use statistical modeling, machine learning algorithms, and data visualization techniques to solve business problems.',
    'Frontend Developer': 'A frontend developer builds and implements user interfaces using HTML, CSS, and JavaScript. They are responsible for creating visually appealing and interactive web interfaces that provide a great user experience.',
    'Mobile Developer': 'A mobile developer specializes in creating applications for mobile devices, such as smartphones and tablets. They develop mobile apps using programming languages and frameworks specific to iOS or Android platforms.',
    'QA Engineer': 'A QA engineer ensures the quality and reliability of software products through testing and quality assurance processes. They create test plans, perform manual and automated tests, and identify and report software defects.',
    'DevOps': 'DevOps combines development and operations to streamline software delivery, deployment, and infrastructure management. DevOps engineers automate processes, manage software configurations, and ensure smooth collaboration between development and operations teams.',
    'ML Engineer': 'An ML engineer applies machine learning algorithms and techniques to build and deploy intelligent systems. They work on developing and optimizing machine learning models, implementing data pipelines, and deploying ML solutions in production environments.',
    'Data Engineer': 'A data engineer designs, develops, and manages data architectures and pipelines for data storage and processing. They build data infrastructure, integrate data from various sources, and ensure data quality, availability, and security.',
    'Engineering Manager': 'An engineering manager oversees a team of engineers, providing guidance, leadership, and project management. They collaborate with stakeholders, set technical goals, allocate resources, and ensure successful execution of engineering projects.',
    'All': 'This option provides an overview of various IT jobs. IT jobs encompass a wide range of roles and responsibilities, including software development, data analysis, infrastructure management, and project leadership. Each IT job requires specific skills and expertise, but all contribute to the development, implementation, and maintenance of technology solutions.'
}

st.sidebar.markdown(
    position_explanations[position_sidebar]
)

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
################################ first plot ################################
st.header('Top Technologies Plot')

# Provide details on how to use the plot
st.write("""
The plot below shows the top technologies for a specific work level and employee state.

Explanation of the plot:
- X-Axis: The X-axis represents the count of workers for each technology (if sorted by count) or the percentage of workers (if sorted by percentage).
- Y-Axis: The Y-axis represents the technology.

Each data point on the plot consists of a marker and a line:
- Marker: Represents the count of workers or the percentage of workers for a specific technology.
- Line: Connects the marker to the origin of the plot.

The plot is titled "Top Technologies for Role" and includes an appropriate title for the X-axis based on the chosen sorting option.

Please note that if there is no data available for the selected combination of work level, employee state, and position, an error message will be displayed.

""")


def create_plot(work_level, emp_state, sort_by):
    if position_sidebar == 'All':
        temp_df = df
        # Include 'work_level' and 'emp_state' in the pivot_table
        tech_pivot = pd.pivot_table(data=temp_df, index=['work_level', 'emp_state'], columns='first_word',
                                    values='yearly_salary', aggfunc='count')
        tech_pivot = tech_pivot[tech_names]
        filtered_df = tech_pivot.loc[work_level, emp_state].nlargest(10)
    else:
        temp_df = df_top10
        # Include 'work_level' and 'emp_state' in the pivot_table
        tech_pivot = pd.pivot_table(data=temp_df, index=['position', 'work_level', 'emp_state'], columns='first_word',
                                    values='yearly_salary', aggfunc='count')
        tech_pivot = tech_pivot[tech_names]
        filtered_df = tech_pivot.loc[position_sidebar, work_level, emp_state].nlargest(10)
    try:
        # Filter based on position from the sidebar, work_level, and emp_state and get the top 10 technologies

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
            xaxis=dict(
                title='Count' if sort_by == 'Count' else 'Percentage of workers' if sort_by == 'Percentage' else ''),
            yaxis=dict(title='Technology'),
            showlegend=False,
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)'
        )

        st.plotly_chart(fig)
    except KeyError:
        st.error(
            'No data available for the selected combination of Position, Work Level, and Employee State. Try a different combination.')


# st.header("Choose your future job")

# Create dropdown widgets with positions, work levels, and employee states
# dropdown = st.selectbox('Position:', top10_positions, key='position')
work_levels = df['work_level'].unique()
work_level_dropdown = st.selectbox('Work Level:', work_levels, key='work_level')
emp_states = df['emp_state'].unique()
emp_state_dropdown = st.selectbox('Employee State:', emp_states, key='emp_state')
sort_by_radio = st.radio('Sort By:', ['Name', 'Percentage'], key='sort_by')

# Call the create_plot function with the selected work level, employee state, and sort by option
create_plot(work_level_dropdown, emp_state_dropdown, sort_by_radio)
st.write("---------------------------------------")
# Create the sidebar box for position selection


################################### second plot #########################################
colors = pio.templates["plotly"].layout.colorway

st.header("Choose your gender and age")
st.write("You can see the average salary according to your details. "
         "Select your gender from the dropdown menu and adjust your age using the slider below.")
st.write("""
The plot below shows the trend of yearly salary over age for both men and women.

Explanation of the plot:
- X-Axis: The X-axis represents the age of individuals.
- Y-Axis: The Y-axis represents the yearly salary. It shows the average salary for each age group.
- Blue Markers and Lines: Represent the trend of yearly salary for men. Each marker represents the average salary at a specific age for men. The lines connect the markers to visualize the trend more smoothly.
- Orange Markers and Lines: Represent the trend of yearly salary for women. Each marker represents the average salary at a specific age for women, and the lines connect the markers.
- Annotation: The plot includes an annotation that dynamically updates based on the selected gender and age. It displays the specific age and salary for the selected point on the plot.
- Legend: The plot has a legend indicating which color corresponds to men and women.
""")

# Create the interactive widgets using Streamlit
gender_dropdown = st.selectbox('Gender:', ['Men', 'Women'])
age_slider = st.slider('Age:', min_value=22, max_value=int(df['age'].max()), value=22, step=1)


# Define the function to update the plot
def update_plot(position, age, gender):
    # Calculate the mean value per age and gender
    if position == 'All':
        df_filtered = df
    else:
        df_filtered = df[df['position'] == position]  # Filter the data for men and women
    df_men = df_filtered[df_filtered['gender'] == 'Male']
    df_women = df_filtered[df_filtered['gender'] == 'Female']

    mean_values_men = df_men.groupby('age')['yearly_salary'].mean()
    mean_values_women = df_women.groupby('age')['yearly_salary'].mean()

    # Create the scatter traces
    men_scatter = go.Scatter(x=mean_values_men.index, y=mean_values_men, name='Men', mode='markers+lines',
                             marker=dict(color=colors[0]))
    women_scatter = go.Scatter(x=mean_values_women.index, y=mean_values_women, name='Women', mode='markers+lines',
                               marker=dict(color=colors[1]))

    # Create the layout
    layout = go.Layout(
        title='Trend of Yearly Salary over Age (Men vs Women)',
        xaxis=dict(title='Age', range=[22, int(df_filtered['age'].max())]),
        yaxis=dict(title='Yearly Salary'),
        showlegend=True
    )

    if gender == 'Men':
        scatter = men_scatter
        mean_values = mean_values_men
    else:
        scatter = women_scatter
        mean_values = mean_values_women

    # Update annotation
    salary = mean_values.get(age, '')
    layout.update(dict(annotations=[
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
            font=dict(size=12),
            opacity=0.8
        )
    ]))

    return men_scatter, women_scatter, layout


# Display the plot using Streamlit's plotly_chart function
men_scatter, women_scatter, layout = update_plot(position_sidebar, age_slider, gender_dropdown)
fig = go.Figure(data=[men_scatter, women_scatter], layout=layout)
st.plotly_chart(fig)
st.write("---------------------------------------")

################################### third plot #########################################
# Assuming you have already loaded the dataframe 'df'

st.header("Choose your work experience")
st.write("""
The plot below shows the job levels based on required work experience.

Explanation of the plot:
- X-Axis: Represents the job levels.
- Y-Axis: Represents the required work experience for each job level.
- Color Gradient: The color of each bar represents the required work experience, ranging from low (lighter color) to high (darker color).

The plot is titled "Job Level Based on Required Experience.""")

# Add a 2-way slide bar to select the range of work experience
min_experience, max_experience = st.slider("Select the range of work experience", int(df['experience'].min()),
                                           int(df['experience'].max()), (0, int(df['experience'].max())))

df_filtered = df[(df['experience'] >= min_experience) & (df['experience'] <= max_experience)]

df_filtered = df_filtered[df_filtered['work_level'] != 'Working Student']


if position_sidebar == "All":
    avg_experience = df_filtered.groupby('work_level')['experience'].mean().reset_index()
    filtered_avg_experience = avg_experience
else:
    avg_experience = df_filtered.groupby(['position', 'work_level'])['experience'].mean().reset_index()

    filtered_avg_experience = avg_experience[avg_experience['position'] == position_sidebar]

job_levels = filtered_avg_experience["work_level"]
required_experience = filtered_avg_experience["experience"].astype(int)

sorted_indices = required_experience.argsort()
job_levels_sorted = job_levels.iloc[sorted_indices]
required_experience_sorted = required_experience.iloc[sorted_indices]

# Creating a color gradient

color_gradient = 'Viridis'  # use inbuilt Viridis colorscale
color_scale = 1 - np.interp(required_experience_sorted, (required_experience_sorted.min(), required_experience_sorted.max()), [0,1])

fig = go.Figure(data=go.Bar(
    x=job_levels_sorted,
    y=required_experience_sorted,
    marker=dict(
        color=color_scale,  # Adding color gradient
        colorscale=color_gradient,
        line=dict(color='rgb(8,48,107)', width=1.5),
    )
))

# Configure the layout
fig.update_layout(
    title={
        'text': 'Job Level Based on Required Experience',
        'y': 0.9,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    xaxis_title='Job Level',
    yaxis_title='Required Experience',
    showlegend=False
)

st.plotly_chart(fig)
st.write("---------------------------------------")
############################ fourth plot #########################################

st.header("Most popular job titles in Europe")
st.write(
    "As the job becomes more popular, there are more open positions. The bar chart below shows the percentage of each job title in Europe in 2020. Click on a bar to see the percentage of that job title.")
st.write("""The plot below shows the percentage of each job title in Europe in 2020.

Explanation of the plot:
- X-Axis: Represents the percentage of job titles.
- Y-Axis: Represents the job titles.
- Color: Each bar represents a job title, with a unique color for each title.
- Interactivity: Clicking on a bar displays the percentage of that job title.

The plot is titled "Most Popular Job Titles in Europe" and includes only job titles with a percentage of at least 1.5%.

Please note that the data used for both plots is based on the provided dataframe.

""")
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

st.sidebar.image('pic.jpeg', use_column_width=True, )
