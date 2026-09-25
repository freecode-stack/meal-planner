from pydantic import BaseModel, Field
from typing import Optional, Literal
from prompt import get_flatten_list_prompt,get_meal_plan_prompt
from langchain_google_genai import ChatGoogleGenerativeAI
import json
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
import os
from models import *
from rag.chroma import *

load_dotenv()
os.environ["GOOGLE_API_KEY"]=os.getenv("GOOGLE_API_KEY")


def get_weekly_plan_json() -> WeeklyPlan:
    with open("weekly-meal-plan.json", "r") as f:
        content = json.load(f)
        weekly_plan = WeeklyPlan(**content)
    return weekly_plan

def get_shopping_list_json() -> ShoppingList:
    with open("shopping_list.json", 'r') as f:
        content = json.load(f)
        shop_list = ShoppingList(**content)
    return shop_list

def retrieve_recipes(state:MealPlannerState) -> MealPlannerState:
    docs = data_parsing(data_file_path=os.getenv("MEAL_CSV_PATH"))
    total_meals_needed=state.days*state.meals_per_day
    vector_store = embedding_and_store(document_list=docs,vector_store_path=os.getenv("VECTOR_PATH"))
    results = retreival(vector_store, user_query=state.preferences, total_meals_required=total_meals_needed)
    recipes = [result.page_content for result in results]
    state.retrieved_recipes=recipes
    print("Completed retrieve_recipes ----------")
    return state


def critique_plan(state:MealPlannerState) -> MealPlannerState:
    """For now, checking if any duplicate dish names. We can change this later for any different criterias as well."""
    days = state.weekly_plan.per_day_plan
    state.needs_retry=False
    dishes=[]
    for day in days:
        meals = day.meals
        for meal in meals:
            dishes.append(meal.dish_name)
    # print("len(dishes):", len(dishes))
    for dish in dishes:
        if dishes.count(dish)>1 :
            state.needs_retry=True
            state.retry_count+=1
            break
    return state

def route_after_critique(state:MealPlannerState)->str:
    if state.needs_retry and state.retry_count<3:
        return "generate_meal_plan"
    return "generate_shopping_list"

def generate_meal_plan(state:MealPlannerState) -> MealPlannerState:
    print("Inside generate_meal_plan----")
    # instruction=get_meal_plan_prompt(state.days,state.meals_per_day, state.preferences) # old code before RAG added.
    instruction=get_meal_plan_prompt(state.days,state.meals_per_day, state.retrieved_recipes)
    #region 
    # model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    # model_with_structure = model.with_structured_output(WeeklyPlan)
    # response = model_with_structure.invoke(instruction)

    response=get_weekly_plan_json()

    #endregion
    state.weekly_plan=response
    print("Leaving generate_meal_plan----")
    return state

def flatten_ingredients(plan : WeeklyPlan) -> list[str]:
    all_ingredients = []
    for day in plan.per_day_plan:
        for meal in day.meals:
            for item in meal.ingredients:
                all_ingredients.append(item)

    ingredients = set(all_ingredients)
    return ingredients

def generate_shopping_list(state:MealPlannerState) -> MealPlannerState:
    flatten_items = flatten_ingredients(state.weekly_plan)
    instruct= get_flatten_list_prompt(flatten_items)
    #region
    # model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    # model_with_structure = model.with_structured_output(ShoppingList)
    # result=model_with_structure.invoke(instruct)
    
    result=get_shopping_list_json()
    #endregion
    state.shopping_list=result
    return state

def build_graph():
    gb= StateGraph(MealPlannerState)
    gb.add_node("retrieved_recipes", retrieve_recipes)
    gb.add_node("meal_plan", generate_meal_plan)
    gb.add_node("shopping_list", generate_shopping_list)
    gb.add_node("critique_plan", critique_plan)
    gb.add_edge(START,"retrieved_recipes")
    gb.add_edge("retrieved_recipes", "meal_plan")
    gb.add_edge("meal_plan","critique_plan")
    gb.add_conditional_edges("critique_plan",
                             route_after_critique,
                             {
                                 "generate_meal_plan":"meal_plan",
                                 "generate_shopping_list":"shopping_list"
                             })
    gb.add_edge("shopping_list", END)
    graph = gb.compile()
    return graph

def print_MealPlannerState(state:MealPlannerState):
    # print("Total dishes: ", len())
    print("*"*30)
    print("\t Meal Plan")
    print("*"*30)
    print("meals_per_day: ", state['meals_per_day'])
    print("number of days: ", state['days'])
    weekly_plan = state['weekly_plan']
    for day in weekly_plan.per_day_plan :
        print("Day ", day.day_number)
        for meal in day.meals:
            print(f"\t {meal.meal_type} : {meal.dish_name}")
    print("*"*30)
    print("\t Shopping List")
    print("*"*30)
    shop_list=state['shopping_list']
    for item in shop_list.items :
        print(item.name)


    

def main():
    # csv_file_path="rag/meals-copy.csv"
    # vector_path="rag/chroma_receipes_db"
    # docs = data_parsing(data_file_path=csv_file_path)
    # vector_store = embedding_and_store(document_list=docs,vector_store_path=vector_path)
    # results = retreival(vector_store,user_query="fiber dishes")
    # # ********
    new_graph = build_graph()
    initial_state=MealPlannerState(
        days=2,
        preferences="fiber",
        meals_per_day=2,
        needs_retry=False,
        retry_count=3
    )
    final_state:MealPlannerState
    final_state=new_graph.invoke(initial_state)
    print_MealPlannerState(final_state)
    # print(final_state['preferences'])
    # print(type(final_state))
    # for x in final_state.values:
    #     print(x)

if __name__=="__main__":
    main()