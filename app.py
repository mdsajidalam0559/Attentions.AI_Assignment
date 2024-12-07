import streamlit as st
import datetime
import sys
from crewai import Crew
from agents import TripAgents, StreamToExpander
from tasks import TripTasks

st.set_page_config(page_icon="🌍", layout="wide")


class VacationPlanner:
    def __init__(self, start_location, destinations, travel_dates, preferences):
        self.start_location = start_location
        self.destinations = destinations
        self.travel_dates = travel_dates
        self.preferences = preferences
        self.output_section = st.empty()

    def execute(self):
        # Initialize agents and tasks
        agent_manager = TripAgents()
        task_manager = TripTasks()

        city_agent = agent_manager.city_selection_agent()
        expert_agent = agent_manager.local_expert()
        concierge_agent = agent_manager.travel_concierge()

        # Define tasks
        task1 = task_manager.identify_task(
            city_agent,
            self.start_location,
            self.destinations,
            self.preferences,
            self.travel_dates
        )
        task2 = task_manager.gather_task(
            expert_agent,
            self.start_location,
            self.preferences,
            self.travel_dates
        )
        task3 = task_manager.plan_task(
            concierge_agent,
            self.start_location,
            self.preferences,
            self.travel_dates
        )

        # Combine agents and tasks
        trip_crew = Crew(
            agents=[city_agent, expert_agent, concierge_agent],
            tasks=[task1, task2, task3],
            verbose=True
        )

        # Execute the plan and display results
        result = trip_crew.kickoff()
        self.output_section.markdown(result)
        return result


if __name__ == "__main__":
    st.title("AI Vacation Planner")
    st.subheader("Plan your dream trip with AI!", anchor=False)

    # Set up date variables
    current_date = datetime.datetime.now().date()
    next_year_date = datetime.date(current_date.year + 1, 1, 10)

    # Sidebar for user inputs
    with st.sidebar:
        st.header("📝 Trip Details")
        with st.form("trip_form"):
            origin = st.text_input("Where are you starting from?", placeholder="E.g., San Francisco, CA")
            destination_list = st.text_input("Where do you want to go?", placeholder="E.g., Paris, France")
            travel_dates = st.date_input(
                "Select your travel dates",
                min_value=current_date,
                value=(current_date, next_year_date + datetime.timedelta(days=5))
            )
            preferences = st.text_area(
                "Tell us more about your interests or trip details",
                placeholder="E.g., Family trip, hiking, beach activities"
            )
            form_submitted = st.form_submit_button("Plan My Trip")

    # Process form submission
    if form_submitted:
        with st.spinner("✨ Planning your trip..."):
            sys.stdout = StreamToExpander(st)
            planner = VacationPlanner(origin, destination_list, travel_dates, preferences)
            trip_plan = planner.execute()
        
        st.success("✅ Your Trip Plan is Ready!")
        st.subheader("Here’s Your Customized Itinerary", anchor=False)
        st.markdown(trip_plan)