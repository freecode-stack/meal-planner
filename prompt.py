
# def get_meal_plan_prompt(num_of_days:int, meals_per_day:int, meal_preferences:str) -> str:
#     prompt=f"""
#         I need to plan my Indian eggiterian meals for next {num_of_days} days. 
#         Meals per day: {meals_per_day}, lunch and dinner.
#         Requirements:
#         - Meal will be for family of 4. 2 adults and 2 kids.
#         - You will be provided with a list of dishes. You need to create a meal plan from these dishes only. The format will be
#         [Dish name] : [Ingredients] : [Nutrients]
#         - Keep nutrition balanced, so kids gets all daily vital nutrients.
#         - Make sure meals remain varied and not repeated.
#         - For each meal list dish name and main ingredients.
#         - For each meal, also note down the macro nutrients and total energy in calories.

#         Preferences:
#         {meal_preferences}
#         Format your response like this:

#         Day 1:
#         - Lunch: [Dish name] - Ingredients:[ingredient1, ingredient2, ...]
#         - Dinner: [Dish name] - Ingredients:[ingredient1, ingredient2, ...]

#         Day 2:
#         ...
#         """
#     return prompt

def get_meal_plan_prompt(num_of_days:int, meals_per_day:int, meals:list[str]) -> str:
    meal_text="\n".join(f"{meal}" for meal in meals)
    prompt=f"""
        I need to plan my Indian eggiterian meals for next {num_of_days} days. 
        Meals per day: {meals_per_day}, lunch and dinner.
        Requirements:
        - Meal will be for family of 4. 2 adults and 2 kids.
        - You will be provided with a list of dishes. You need to create a meal plan from these dishes only. 
        There will more columns and hence more information available along with the dish names but you need to ignore rest of the information
        and just use the dish names. The dish name will likely be the first column. For your understanding, the format will be similar to
        the one mentioned below -
        [Dish name] : [Ingredients] : [Nutrients] .....
        - Make sure meals remain varied and not repeated.
        - For each meal list dish name and main ingredients.

        List of dishes:
        {meal_text}
        """
    return prompt

def get_flatten_list_prompt(items: list[str]) -> str:
    prompt=f""" Remove the duplicates and near duplicates or variants from the provided list.
    Categorize the items as per the provided structure.
    List of items={items}"""
    return prompt