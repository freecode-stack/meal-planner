from pydantic import BaseModel, Field
from typing import Literal, Optional

class Nutrients(BaseModel):
    protein:int = Field(description="Total protein in gm in the meal")
    carbs:int = Field(description="Total carbohydrate in gm in the meal")
    fats:int = Field(description="Total fats in gm in the meal.")
    micro:list[str] = Field(description="Other micro nutrients in the meal.")

class Meal(BaseModel):
    dish_name:str = Field(description="Name of the dish, e.g paneer burji, aloo palak,..")
    meal_type: Literal["Breakfast", "Lunch", "Dinner"] = Field(description="Type of meal, e.g Lunch, Dinner, Breakfast")
    ingredients: list[str] = Field("List of ingredients needed for the dish.")
    energy:str = Field(description="Total energy in calories of the meal.")
    portion:int = Field(description="Total portion or weight of dish in gm")
    nutrients:Nutrients = Field(description="Micro and Macro nutrients in meal.")

class Day(BaseModel):
    day_number:int = Field(description="The number of day in a weekly plan, e.g 1, 2, ..")
    meals:list[Meal] = Field(description="All the meals for this particular day.")

class WeeklyPlan(BaseModel):
    per_day_plan:list[Day] = Field(description="Per day meal plan in a weekly plan")
    # user_preference:str = Field(description="User's preference e.g vegiterian only, no dairy, etc.")

class ShoppingItem(BaseModel):
    name:str = Field(description="Normalized item name, merging duplicates or variants, e.g 'Rice' and 'Basmati rice' should be one item.")
    category:Literal["Dairy", "Vegetable", "Pulses", "Spices", "Flour", "Poultry", "Grains", "Fruits", "Sauces", "Other"] = Field(description="Type of shopping item e.g egg is poultry. If any item can't be categorized then mark Other.")

class ShoppingList(BaseModel):
    items:list[ShoppingItem] = Field(description="List of all shopping items.")

class MealPlannerState(BaseModel):
    meals_per_day:int
    days:int
    preferences:str
    weekly_plan: Optional[WeeklyPlan]=None
    shopping_list: Optional[ShoppingList]=None
    needs_retry:bool
    retry_count:int
    retrieved_recipes:Optional[list[str]]=None