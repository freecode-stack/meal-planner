import pandas
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os
from langchain_chroma import Chroma

load_dotenv()
os.environ["GOOGLE_API_KEY"]=os.getenv("GOOGLE_API_KEY")


# def data_parsing(data_file_path : str) -> list[Document]:        
#     # df = pandas.read_csv("rag/meals.csv")
#     df = pandas.read_csv(data_file_path)
#     # print(df)
#     df["Ingredients"] = df["Ingredients"].apply(lambda x : [i.strip() for i in x.split(",")])
#     df["Nutrients"] = df["Nutrients"].apply(lambda x : [i.strip() for i in x.split(",")])
#     # print("**************************************")
#     # print(df)
#     documents= [
#         Document (
#             page_content=f"{row['Dish_name']}: {', '.join(row['Ingredients'])} :  {', '.join(row['Nutrients'])}",
#             metadata={"Dish_name":row["Dish_name"], "Nutrients":row["Nutrients"]}
#         )
#         for _, row in df.iterrows()
#         ]
#     # print(documents[0])
#     return documents
def data_parsing(data_file_path : str) -> list[Document]:        
    # df = pandas.read_csv("rag/meals.csv")
    df = pandas.read_csv(data_file_path)
    # print(df)
    df["Ingredients"] = df["Ingredients"].apply(lambda x : [i.strip() for i in x.split(",")])
    df["Nutrients"] = df["Nutrients"].apply(lambda x : [i.strip() for i in x.split(",")])
    df["micro_nutrients"] = df["micro_nutrients"].apply(lambda x : [i.strip() for i in x.split(",")])
    # print("**************************************")
    # print(df)
    documents= [
        Document (
            page_content=f"{row['Dish_name']}: {', '.join(row['Ingredients'])} :  {', '.join(row['Nutrients'])} : {row['portion_g']} : {row['protein_g']} : {row['carbs_g']} : {row['fat_g']} : {row['fiber_g']} : {', '.join(row['micro_nutrients'])}",
            metadata={"Dish_name":row["Dish_name"], "Nutrients":row["Nutrients"],  "micro_nutrients":row["micro_nutrients"]}
        )
        for _, row in df.iterrows()
        ]
    # print(documents[0])
    return documents

def embedding_and_store(document_list : list[Document], vector_store_path: str) -> Chroma:
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    if os.path.exists(vector_store_path):
        return Chroma(persist_directory=vector_store_path, embedding_function=embeddings)
    else:
        vector_store=Chroma.from_documents(documents=document_list, embedding=embeddings, persist_directory=vector_store_path)
        return vector_store

def retreival(vector_db: Chroma, user_query:str, total_meals_required:int=10) -> list[Document]:
    # results = vector_db.similarity_search(query=user_query)
    results= vector_db.max_marginal_relevance_search(
        query=user_query,
        k=total_meals_required,
        fetch_k=total_meals_required+6,
        lambda_mult=0.5
    )
    return results

def main():
    csv_file_path="rag/meals-copy.csv"
    vector_path="rag/chroma_receipes_db"
    docs = data_parsing(data_file_path=csv_file_path)
    vector_store = embedding_and_store(document_list=docs,vector_store_path=vector_path)
    results = retreival(vector_store,user_query="fiber dishes")
    for r in results:
        print(r.page_content)

if __name__=="__main__":
    main()