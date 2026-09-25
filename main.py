import streamlit as sl
from graph import *
import csv
import random

def read_paratha_data() -> list:
    file_name="rag/paratha.csv"
    with open(file=file_name, mode='r', encoding='utf-8', newline='') as f:
        reader = (csv.reader(f))
        header = next(reader)
        csv_data=list(reader)
    return csv_data
def get_random_paratha(list_paratha:list) -> str:

        # for d in csv_data:
        #     print(d)
        # print("Random paratha")
    return random.choice(list_paratha)[0]
    
def print_meal_plan(state: MealPlannerState, paratha_list:list):
    week_plan=state["weekly_plan"]
    shop_list=state["shopping_list"]
    tab1, tab2 = sl.tabs(["Weekly Plan", "Shopping List"])

    with tab1:
        tab1.header("Weekly plan")
        for day in week_plan.per_day_plan:
            sl.markdown(f"## Day {day.day_number}")
            for meal in day.meals:
                sl.markdown(f"#### {meal.meal_type}")
                sl.text(f" {meal.dish_name} and {get_random_paratha(paratha_list)}. Portion: {meal.portion}")
                # for nutri in meal.nutrients:
                sl.text(f"Protien:{meal.nutrients.protein}. Carb:{meal.nutrients.carbs}. Fats:{meal.nutrients.fats}. Micro-nutrients: {meal.nutrients.micro}")
                # with sl.expander("Ingredients", expanded=False):
                #     for item in meal.ingredients:
                #         sl.write(item)
                
    
    with tab2:
        tab2.header("Shopping List")
        for item in shop_list.items:
            sl.text(item.name)


def main():
    sl.title("Meal Planner application")
    graph = build_graph()
    paratha_list=read_paratha_data()
    days = sl.number_input("How many number of days you need meal plan ?", min_value=1, max_value=7)
    meals_everyday = sl.number_input("How many meals per day you will take?", min_value=1, max_value=3)
    sl.subheader("Food Preferences")
    selected=[]
    preferences=["High Protein", "Fiber"]

    for pref in preferences:
        select=sl.checkbox(pref, key=pref)
        if select:
            selected.append(pref)
    
    initial_state = MealPlannerState(
        meals_per_day=meals_everyday,
        days=days,
        needs_retry=False,
        retry_count=3,
        preferences=", ".join(selected)
    )
    plan_button= sl.button("Generate Plan")
    # print("plan_button: ", plan_button)
    if plan_button:
        final_state= graph.invoke(initial_state)
        print_meal_plan(final_state, paratha_list)



if __name__=="__main__":
    main()
