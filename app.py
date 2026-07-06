import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
from datetime import datetime
import time
import os
from dotenv import load_dotenv
load_dotenv(override=True)
print(os.environ.get("DB_HOST"))
from dotenv import dotenv_values


st.set_page_config(page_title="Student Analytics Dashboard", layout="wide")

#chart container styling
st.markdown("""
            <style>
            div[data-testid="stPlotlyChart"]{
            background:white;
            padding:15px;
            border-radius:20px;
            box-shadow: 0px 8px 20px rgba(0,0,0,.12);
            }
            </style>
            """, unsafe_allow_html=True)

#chart layout update
#fig_course.update_layout(

#kpi card styling
st.markdown("""
            <style>
            div[data-testid="stMetricValue"]{
            background:white;
            padding:20px;
            border-radius:20px;
            border-left:8px solid #2563EB;
            box-shadow: 0px 8px 20px rgba(0,0,0,.15);
            }
            </style>
            """, unsafe_allow_html=True)


#background
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg,#EEF2FF,#FFFFFF,#E0F2FE);
    }
            
    div[data-testid="stPlotlyChart"]{
            background:white;
            padding:15px;
            border-radius:20px;
            border:none;
            outline:none;
            box-shadow: 0px 8px 20px rgba(0,0,0,0.08);
            }
    </style>
    """, unsafe_allow_html=True)


hide_menu = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""

#header
st.markdown("""
            <h1 style='font-size:48px; text-align: center; color: #1E3A8A;'>
            📊Student Analytics Dashboard
            </h1>
            <p style ='text-align: center;
            font-size: 20px; 
            color: gray;'>
            Real-Time Student Analytics using PostgresSQL and Streamlit
            </p>
            """, unsafe_allow_html=True)
st.markdown("""
            <p style ='text-align: center; 
            font-size: 18px;
            color: #555;
            margin-top: -5px;'>
            Welcome to the <b>Student Performance Dashboard</b>.<br>
            Analyze student records, placements, attendance and academic performance in real-time. 
            </p>
            """,
            unsafe_allow_html=True
            )


st.markdown(hide_menu, unsafe_allow_html=True)
with st.spinner("Fetching data from PostgreSQL ..."):
            print("HOST:", os.getenv("DB_HOST"))
            print("PORT:", os.getenv("DB_PORT"))
            print("NAME:", os.getenv("DB_NAME"))
            conn = psycopg2.connect(
    host= os.getenv("DB_HOST"),   
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT"),
    sslmode="require"
)
            
cur = conn.cursor()
cur.execute("SELECT current_database();")
print("Database:", cur.fetchone())

cur.execute("Select current_schema();")
print("Schema:", cur.fetchone())

cur.execute("SELECT tablename FROM pg_tables where schemaname ='public';")
print(cur.fetchall())  


query = "SELECT * FROM public.students"    
df = pd.read_sql(query, conn)
conn.close()

#sidebar filters
st.markdown("""
            <style>
            [data-testid="stSidebar"]{
            background-color: #F8FBFF;
            border-right: 1.5px solid #ADD8E6;}
            </style>
            """, unsafe_allow_html=True)

#sidebar title
st.sidebar.title("🎯 Dashboard Controls")
#st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style = "
    height: 2px;
    background-color: #ADD8E6;
    border-radius: 10px;
    margin-top: 15px 0 20px 0;
    "></div>
""", unsafe_allow_html=True)

#sidebar title

#city filter
st.sidebar.header("Filters")
selected_city = st.sidebar.selectbox("Select City", ["All"] + list(df['city'].unique()))

st.sidebar.write("")

selected_course = st.sidebar.multiselect("Select Course", df['course'].unique())
st.sidebar.write("")
placement_filter = st.sidebar.selectbox("Placement Status",["All","Placed", "Not Placed"])




st.sidebar.markdown("""
    <div style = "
    height: 2px;
    background-color: #ADD8E6;
    border-radius: 10px;
    margin-top: 15px 0 20px 0;
    "></div>
""", unsafe_allow_html=True)


#student name search
st.sidebar.subheader("🔍 Student Search")
search_student = st.sidebar.text_input("Search Student Name", placeholder="Enter student name...")

#refresh button
if st.sidebar.button("Refresh Data"):st.rerun()
st.markdown("""
<style>
/* Refresh Data Button */
div.stButton > button {
    background-color: #3B82F6;
    color: white;
    width: 250px;
    border: none;
    border-radius: 12px;
    padding: 12px 20px;
    font-size: 15px;
    font-weight: 600;
    transition: all 0.3s ease;
}

/* Hover Effect */
div.stButton > button:hover {
    background-color: #1D4ED8;
    color: white;
    transform: scale(1.03);
    box-shadow: 0 4px 10px rgba(37,99,235,0.3);
}

/* Click Effect */
div.stButton > button:active {
    transform: scale(0.98);
}
</style>
""", unsafe_allow_html=True)




#filters
filtered_df = df.copy()
if selected_course : filtered_df = filtered_df[filtered_df['course'].isin(selected_course)]
if selected_city != "All":
    filtered_df = filtered_df[filtered_df['city'] == selected_city]
if placement_filter != "All": filtered_df = filtered_df[filtered_df["placement_status"]== placement_filter]
if search_student:
    filtered_df = filtered_df[filtered_df['sname'].str.contains(search_student, case=False, na=False)]

if not filtered_df.empty:
        topper = filtered_df.loc[filtered_df['marks'].idxmax()]
else:
    topper = None



st.info(
    f"📌 Current Filters → Course: {selected_course} | City: {selected_city}"
)

#kpi card
total_students = len(filtered_df)
average_marks = 0 if filtered_df.empty else round(filtered_df['marks'].mean(),2)
average_attendance = 0  if filtered_df.empty else round (filtered_df['attendance_perc'].mean() , 2)
if topper is not None:
    st.markdown(f"""
            <div style="
            background:white;
            padding:20px;
            border-radius:15px;
            box-shadow:0px 4px 12px rgba(0,0,0,0.08);
            border-left:6px solid gold;
            ">
            <h3 style="color: gold;">🏆Top Performer</h3>
            <p><b>Name:</b> {topper['sname']}</p>
            <p><b>Course:</b> {topper['course']}</p>
            <p><b>Marks:</b> {topper['marks']}</p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
            <p style="
            color:#d32f2f;
            font-size:18px;
            font-weight:bold;
            text-align:center;
            padding:25px;
            ">       
                ❌ No student found for the selected filters.
            </p>
            </div>
                """, unsafe_allow_html=True )
st.write("")
st.write("")

st.markdown("""
            <style>
            /* Metric card heading */
            [data-testid="stMetricLabel"]{
            font-size: 20px !important;
            font-weight: 800 !important;
            font-family: "Segoe UI", sans-serif !important;
            color: #2563EB !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;}
            
            /* Metric Value */
            [data-testid="stMetricValue"]{
            font-size: 38px !importsnt;
            font-weight: bold !important;
            font-family: :"Poppins", sans-serif !important;}
            </style>
            """, unsafe_allow_html=True)

#card display
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Students", total_students)
with col2:  
    st.metric("Average Marks", round(average_marks, 2))
with col3:
    st.metric("Average Attendance", round(average_attendance, 2))
    
st.divider()

#bar chart students by course
course_count = filtered_df['course'].value_counts().reset_index()
course_count.columns = ['course', 'Students']
fig_course = px.bar (
    course_count,
    x='course',
    y='Students',
    title = "Students by Course", 
    color = "course"
)
fig_course.update_traces(
    hovertemplate="<b>%{x}</b><br>Students: %{y}<extra></extra>")

#fig_course.update_layout(
#   transition_duration=500)

fig_course.update_layout(
    paper_bgcolor= "#F8FAFC",
    plot_bgcolor= "#F8FAFC",
    font=dict(color="#1E293B"),
    margin=dict(l=10, r=10, t=50, b=10)
)


#bar chart studnets by city
city_data = filtered_df['city'].value_counts().reset_index()
city_data.columns = ['city', 'Students']
fig_city = px.bar (
    city_data,
    x='city',
    y='Students',
    title = "Students by City", 
    #color = "city"
)

fig_city.update_traces(
    hovertemplate="<b>%{x}</b><br>Students: %{y}<extra></extra>")

#fig_city.update_layout(
#   transition_duration=500)

fig_city.update_layout(
    paper_bgcolor= "#F8FAFC",
    plot_bgcolor= "#F8FAFC",
    font=dict(color="#1E293B"),
    margin=dict(l=10, r=10, t=50, b=10)
)


#pie chart plaement status
placement_data = filtered_df['placement_status'].value_counts().reset_index()
placement_data.columns = ['placement_status', 'Students']
fig_placement = px.pie (
    placement_data,
    values='Students',
    names='placement_status',
    title = "Placement Status",
    hole=0.4
)

#fig_placement.update_layout(
#   transition_duration=500)

fig_placement.update_layout(                      
    paper_bgcolor= "#F8FAFC",
    plot_bgcolor= "#F8FAFC",
    font=dict(color="#1E293B"),
    margin=dict(l=10, r=10, t=50, b=10)
)

# average marks by course
marks_data = filtered_df.groupby('course')['marks'].mean().reset_index()
fig_marks = px.bar (
    marks_data,
    x='course',
    y='marks',
    title = "Average Marks by Course",
    color = "course"
)

#fig_marks.update_traces(
#    transition_duration=500)

fig_marks.update_layout(
    paper_bgcolor= "#F8FAFC",
    plot_bgcolor= "#F8FAFC",
    font=dict(color="#1E293B"),
    margin=dict(l=10, r=10, t=50, b=10)
)

placement_course = filtered_df.groupby(["course", "placement_status"]).size().reset_index(name="Students")
fig_stack = px.bar(
    placement_course,
    x="course",
    y="Students",
    color="placement_status",
    barmode="stack",
    title="Placement Status by Course",
    color_discrete_sequence=["#2563EB","#60A5FA"]
)
fig_stack.update_layout(
    paper_bgcolor= "#F8FAFC",
    plot_bgcolor= "#F8FAFC",
    font=dict(color="#1E293B"),
    margin=dict(l=10, r=10, t=50, b=10)
)
#heatmap
heatmap_data = filtered_df.pivot_table(
    values="marks",
    index="course",
    columns="city",
    aggfunc="mean"
)
fig_heat = px.imshow(
    heatmap_data,
    text_auto=".1f",
    color_continuous_scale="Blues",
    title="Average Marks Heatmap"
)
fig_heat.update_layout(
    paper_bgcolor= "#F8FAFC",
    plot_bgcolor= "#F8FAFC",
    font=dict(color="#1E293B",size=14),
    margin=dict(l=80, r=40, t=60, b=40),
    height =500,
    autosize=True,
    #font=dict(size=14)
)
fig_heat.update_xaxes(side="bottom",tickangle=-45)
fig_heat.update_yaxes(automargin=True)
st.subheader("📊Average Marks Heatmap")
st.plotly_chart(fig_heat,use_container_width=True)

#Treemap
treemap_data = filtered_df.groupby(
    ["course","placement_status"]).size().reset_index(name="Students")
fig_tree = px.treemap(
    treemap_data,
    path=["course", "placement_status"],
    values="Students",
    color="Students",
    color_continuous_scale="Blues",
    title="Students Distribution by Course & Placement"
)
fig_tree.update_layout(
    paper_bgcolor= "#F8FAFC",
    plot_bgcolor= "#F8FAFC",
    font=dict(color="#1E293B"),
    margin=dict(l=10, r=10, t=50, b=10),
    height=450
)


line_data = filtered_df.groupby('course').agg(
    avg_marks=('marks', 'mean'),
    avg_attendance=('attendance_perc', 'mean'),
    placement_perc=('placement_status', lambda x: (x == 'Placed').sum() / len(x) * 100)
).reset_index()

fig_multi = px.line(
    line_data,
    x = 'course',
    y = ["avg_marks","avg_attendance","placement_perc"],
    markers=True,
    title="Course Performance Analysis"
)

col5, col6 =st.columns(2)
with col5:
    st.plotly_chart(fig_multi,use_container_width=True)
with col6:
    st.plotly_chart(fig_stack,use_container_width=True)

fig_multi.for_each_trace(
    lambda t: t.update(
        name = t.name.replace("avg_marks","Average Marks")
        .replace("avg_attendance","Average Attendance")
        .replace("placement_perc","Placement %")
    )
)

st.plotly_chart(fig_multi, use_container_width = True)

fig_multi.update_traces(line=dict(width=4),
                        marker=dict(size=8),
                        textposition="top center",
                        mode="lines+markers+text",
                        text=line_data["avg_marks"].round(1))

fig_multi.data[0].line.color ="#2563EB"
fig_multi.data[1].line.color ="#10B981"
fig_multi.data[2].line.color ="#EF4444"
fig_multi.update_layout(
    title="Course Performance Analysis",
    title_x=0.5,
    margin=dict(l=10, r=10, t=50, b=10),
    legend_title="", 
    xaxis_title="Course",
    yaxis_title="Values"
)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_course,
use_container_width=True)
with col2:
    st.plotly_chart(fig_placement,
use_container_width=True)
     
#Treemap
#st.plotly_chart(fig_tree,use_container_width=True)
#treemap

col3,col4 = st.columns(2)
with col3:
    st.plotly_chart(fig_city,
use_container_width=True)
with col4:
    st.plotly_chart(fig_marks,
use_container_width=True)
    
#FEE STATUS
fee_data = filtered_df["fee_status"].value_counts().reset_index()
fee_data.columns = ["Status", "Students"]
fig_fee = px.pie(
    fee_data,
    names = "Status",
    values = "Students",
    hole = 0.6,
    color = "Status",
    color_discrete_map={
        "Paid": "#22C55E",
        "Pending": "#EF4444"
    },
    title= "Fee Status"
)
fig_fee.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(color="#1E293B"),
    margin=dict(l=10, r=10, t=50, b=10)
)
st.subheader("💳 Fees Status")
st.plotly_chart(fig_fee,use_container_width=True) 

st.markdown('## 🌐 3D Student Performance Analysis')
import plotly.express as px
fig3d = px.scatter_3d(
    filtered_df,
    x = "marks",
    y = "attendance_perc",
    z = "age",
    color = "placement_status",
    size = "attendance_perc",
    symbol = "placement_status",
    hover_name = "sname",
    hover_data = {
        "course": True,
        "city": True,
        "semester" : True,
        "marks" : True,
        "attendance_perc": True,
        "age":True
    },
    title="3d Student Performance Analysis",
)
fig3d.update_traces(
    marker=dict(
        opacity = 0.85,
        sizemin = 5
    )
)
fig3d.update_layout(
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=0.5
    ),
    height=700,
    title = {
        "text": "🌐 3D Student Performance",
        "x": 0.5,
        "font": {"size": 24}
    },
    scene=dict(
        xaxis_title="Marks",
        yaxis_title="Attendance (%)",
        zaxis_title="Age",
        camera=dict(
            eye=dict(x=1.7, y=1.7, z=1.2)
        )
    ),
    legend_title="Placement Status",
    margin=dict(l=0, r=0, b=0, t=60)
)
st.plotly_chart(fig3d, use_container_width=True)

st.subheader("📋 Student Records")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

csv = filtered_df.to_csv(index=False).encode('utf-8')
filename = f"student_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
st.download_button(
    label="📥 Download Filtered Data",
    data=csv,
    file_name=filename,
    mime='text/csv',
)

#real time update
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ")

#database statistics
st.divider()
st.subheader("🗄️ Database Statistics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Students", len(df))
with col2:
    st.metric("Courses",df["course"].nunique())
with col3:
    st.metric("Cities",df["city"].nunique())
st.success("✅ PostgreSQL Connected")

st.divider()
#footer
st.markdown("""
            <div style="text-align:center;
            color:gray;">
            <h4>Student Analytics Dashboard v1.0</h4>
            
            Developed by <b>AARSH VASHISHT</b><br>
            
            Python • Streamlit • PostgreSQL • Plotly
            </div>
            """, unsafe_allow_html=True)
#st.caption("Developed by AARSH VASHISHT using Python • Streamlit • PostgreSQL • Plotly")


