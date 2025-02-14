import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="History - AI Fitness Trainer",
    page_icon="🏋️‍♂️",
    layout="wide"
)

# Initialize workout history in session state if it doesn't exist
if 'workout_history' not in st.session_state:
    st.session_state.workout_history = []

def format_duration(minutes):
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0:
        return f"{int(hours)}h {int(mins)}m"
    return f"{int(mins)}m"

def main():
    st.markdown("""
        <div style='text-align: center; padding: 0.5rem;'>
            <h1 style='color: #FF4B2B; font-size: 1.75rem;'>History</h1>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.workout_history:
        df = pd.DataFrame(st.session_state.workout_history)
        
        # Summary Statistics in 2x2 grid
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
                <div class="stats-card">
                    <h3>Total Workouts</h3>
                    <h2>{}</h2>
                </div>
            """.format(len(df)), unsafe_allow_html=True)
            
            total_calories = df['calories'].sum()
            st.markdown("""
                <div class="stats-card">
                    <h3>Total Calories</h3>
                    <h2>{:.0f}</h2>
                </div>
            """.format(total_calories), unsafe_allow_html=True)
            
        with col2:
            total_reps = df['reps'].sum()
            st.markdown("""
                <div class="stats-card">
                    <h3>Total Reps</h3>
                    <h2>{}</h2>
                </div>
            """.format(total_reps), unsafe_allow_html=True)
            
            total_duration = df['duration_mins'].sum()
            st.markdown("""
                <div class="stats-card">
                    <h3>Duration</h3>
                    <h2>{}</h2>
                </div>
            """.format(format_duration(total_duration)), unsafe_allow_html=True)

        # Graphs in tabs
        tab1, tab2 = st.tabs(["Calories", "Exercises"])
        
        with tab1:
            fig_calories = px.line(df, x='time', y='calories',
                                 title='Calories Burned',
                                 labels={'calories': 'kcal', 'time': 'Date'})
            fig_calories.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=40, b=10),
                plot_bgcolor='rgba(22, 27, 34, 0.8)',
                paper_bgcolor='rgba(22, 27, 34, 0.8)',
                font_color='white',
                font_size=10
            )
            st.plotly_chart(fig_calories, use_container_width=True)

        with tab2:
            exercise_dist = df['exercise_type'].value_counts()
            fig_pie = go.Figure(data=[go.Pie(labels=exercise_dist.index, 
                                           values=exercise_dist.values,
                                           hole=.3)])
            fig_pie.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=40, b=10),
                title='Exercise Types',
                plot_bgcolor='rgba(22, 27, 34, 0.8)',
                paper_bgcolor='rgba(22, 27, 34, 0.8)',
                font_color='white',
                font_size=10
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # Recent Workouts
        st.markdown("""
            <div style='background: rgba(22, 27, 34, 0.8); padding: 1rem; border-radius: 12px; margin: 1rem 0;'>
                <h2 style='color: #FF4B2B; font-size: 1.2rem;'>Recent Workouts</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Show only last 5 workouts by default
        display_df = df.copy().tail(5)
        display_df['time'] = pd.to_datetime(display_df['time']).dt.strftime('%m/%d %H:%M')
        display_df['duration'] = display_df['duration_mins'].apply(format_duration)
        display_df['calories'] = display_df['calories'].round(0).astype(int).astype(str) + ' kcal'
        
        # Reorder and rename columns
        display_df = display_df[['time', 'exercise_type', 'reps', 'calories', 'duration']]
        display_df.columns = ['Date', 'Exercise', 'Reps', 'Cal', 'Time']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        if st.button("Clear History", type="secondary", use_container_width=True):
            st.session_state.workout_history = []
            st.experimental_rerun()

    else:
        st.markdown("""
            <div style='background: rgba(22, 27, 34, 0.8); padding: 1.5rem; border-radius: 12px; text-align: center;'>
                <h2 style='color: #FF4B2B; font-size: 1.2rem;'>No Workouts Yet</h2>
                <p style='color: white; font-size: 0.9rem;'>Start your first workout!</p>
                <br>
                <a href='1_Workout' class='mobile-button primary'>Start Workout</a>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 