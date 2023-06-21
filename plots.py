import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import random
import numpy as np
import plotly.express as px
import plotly.io as pio

# Add the map to the sidebar
st.set_page_config(page_title="Help for the  high tech worker", layout="wide")
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child{
        width: 400px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child{
        width: 400px;
        margin-left: -400px;
    }

    """,
    unsafe_allow_html=True,
)
st.title("Help for the high tech worker")


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
st.header('Top Technologies(Programming Languages)')

# Provide details on how to use the plot
st.markdown("""The visualization displays the prevalence of each technology for every job, represented as percentages indicating the proportion of employees in each job who deal with each technology.
Upon selecting the desired features, the corresponding graph will be presented.
There are two options available for sorting the data:
Sort by technology name (alphabetically): This allows the user to observe the relevance of their known technologies in comparison to others. For instance, if the user is interested in a junior Backend developer job with a full-time employment status, this sorting option helps in understanding the prominence of various technologies.
Sort by technology frequency (percentages): This option enables the user to identify the most common technologies associated with the job they are seeking.
""")


def create_plot(work_level, emp_state, sort_by):
    try:

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
            tech_pivot = pd.pivot_table(data=temp_df, index=['position', 'work_level', 'emp_state'],
                                        columns='first_word',
                                        values='yearly_salary', aggfunc='count')
            tech_pivot = tech_pivot[tech_names]
            filtered_df = tech_pivot.loc[position_sidebar, work_level, emp_state].nlargest(10)
        # Filter based on position from the sidebar, work_level, and emp_state and get the top 10 technologies

        if sort_by == 'Name':
            total_workers = filtered_df.sum()  # Calculate the total number of workers
            filtered_df = (filtered_df / total_workers) * 100  # Calculate the percentage
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
            width=1000,
            xaxis=dict(
                title='Percentage of workers' if sort_by == 'Name' else 'Percentage of workers' if sort_by == 'Percentage' else ''),
            yaxis=dict(title='Technology'),
            showlegend=False,
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)'
        )

        st.plotly_chart(fig)
    except KeyError:
        st.error(
            'No data available for the selected combination of Position, Work Level, and Employee State. Try a different combination.')


work_levels = df['work_level'].unique()
work_level_dropdown = st.selectbox('Work Level:', work_levels, key='work_level')
emp_states = df['emp_state'].unique()
emp_state_dropdown = st.selectbox('Employee State:', emp_states, key='emp_state')
sort_by_radio = st.radio('Sort By:', ['Percentage', 'Name'], key='sort_by')

# Call the create_plot function with the selected work level, employee state, and sort by option
create_plot(work_level_dropdown, emp_state_dropdown, sort_by_radio)
st.write("---------------------------------------")


################################### second plot #########################################

st.header("Average Yearly Salary")

st.write("""
The visualization displays the average annual salary for each job based on the employee's age, gender, and company size.

You can choose whether to view the salary specifically for women, men, or both genders combined.
""")

gender_dropdown = st.selectbox('Gender:', ['Men', 'Women'])
company_size_dropdown = st.selectbox('Company Size:', ['All'] + df['company_size'].unique().tolist())
age_slider = st.slider('Age:', min_value=22, max_value=int(df['age'].max()), value=22, step=1)
colors = pio.templates["plotly"].layout.colorway


# Define the function to update the plot
def update_plot(position, age, gender, company_size, df):
    # Filter the data according to company size
    if company_size != 'All':
        df = df[df['company_size'] == company_size]

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
        width=1000,
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

    # Update annotation if salary value is available
    salary = mean_values.get(age)
    annotations = []
    if salary is not None:
        annotations.append(
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
        )
    layout.update(dict(annotations=annotations))

    return men_scatter, women_scatter, layout


men_scatter, women_scatter, layout = update_plot(position_sidebar, age_slider, gender_dropdown, company_size_dropdown,
                                                 df)
fig = go.Figure(data=[men_scatter, women_scatter], layout=layout)
st.plotly_chart(fig)
st.write("---------------------------------------")

################################### third plot #########################################

st.header("Years of Experience vs. Job Level ")
st.write("""The visualization depicts the number of years of experience required for each position 
level within a company. You have the option to select your own years of experience and receive 
corresponding recommendations 
on why you should consider competing for specific positions""")

# Calculate average experience for all possible job levels


# Add a 2-way slide bar to select the range of work experience
min_experience, max_experience = st.slider("Select the range of work experience", int(df['experience'].min()),
                                           15, (0, 15))

# Filter the data based on the selected range of work experience
df_filtered = df[(df['experience'] >= min_experience) & (df['experience'] <= max_experience)]
df_filtered = df_filtered[df_filtered['work_level'] != 'Working Student']

# Assuming position_sidebar is defined elsewhere in your code
if position_sidebar == "All":
    avg_experience_all = df.groupby('work_level')['experience'].mean().reset_index()
    avg_experience = avg_experience_all
else:
    temp_df = df[df['position'] == position_sidebar]
    avg_experience_all = temp_df.groupby('work_level')['experience'].mean().reset_index()
    avg_experience = avg_experience_all

# Sort both fields together, keeping their alignment
avg_experience_sorted = avg_experience.sort_values('experience')

job_levels_sorted = avg_experience_sorted['work_level']
required_experience_sorted = avg_experience_sorted['experience'].astype(int)

# Remove bars above or below the specified line
indices_to_remove = (required_experience_sorted > max_experience) | (required_experience_sorted < min_experience)
job_levels_sorted = job_levels_sorted[~indices_to_remove]
required_experience_sorted = required_experience_sorted[~indices_to_remove]

# Creating a color gradient
color_gradient = 'Viridis'  # use inbuilt Viridis colorscale
color_scale = 1 - np.interp(required_experience_sorted,
                            (required_experience_sorted.min(), required_experience_sorted.max()), [0, 1])

fig = go.Figure(data=go.Bar(

    x=job_levels_sorted,
    y=required_experience_sorted,

))

# Configure the layout
fig.update_layout(
    width=1000,
    title={
        'text': 'Job Level Based on Required Experience',
        'y': 0.9,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    xaxis_title='Job Level',
    yaxis_title='Required Experience(years)',
    showlegend=False
)

st.plotly_chart(fig)
st.write("---------------------------------------")
############################ fourth plot #########################################

st.header("Top High-Tech Jobs in 2020")
st.write("""The purpose of this visualization is to display the user of the 
application the percentages of the most common jobs in the high-tech field for the year 2020. 
This information will assist high-tech employees in making informed decisions regarding 
their field of focus based on their preferences and considerations.

""")
# Filter to only include data from Europe in 2020
df_europe_2020 = df[(df['city'].isin(['Berlin', 'London', 'Paris']))]

# Count the occurrences of each job title
job_title_counts = df_europe_2020['position'].value_counts().reset_index()

# Rename the columns to 'position' and 'count'
job_title_counts.columns = ['position', 'count']

columns_to_exclude = ['temp']

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
    width=1100,
    height=600,
    hovermode='y',
    xaxis=dict(title='Percentage'),
    yaxis=dict(title='Job Title', automargin=True, side='right'),  # Align y-axis labels to the right
    showlegend=False
)

st.plotly_chart(fig)

st.sidebar.image('pic.jpeg', use_column_width=True, )
