from sentence_transformers import SentenceTransformer, util
from ..utils.transaction_data_utils import *
from ..tasks.make_company_database import *
import random


# transaction data with companies and locations
transaction_data_with_details = AugmentTransactionData().get_transaction_details(remove_sensitive_data=True)

# load the database and the summaries 
companies_and_summaries = retrieve_database_contents(db_path)


if __name__ == '__main__':

    # category = ['Cinema','Restaurant | Cafe', 'Grocery','Sports','Take out','Commute | Train | Plane',' miscellaneous','Housing | Rent','Person']
    categories = [
    "Cinema: Places where people watch movies or other forms of visual entertainment, such as theaters or multiplex cinemas.",
    "Restaurant | Cafe: Establishments where people dine, drink, or socialize, including restaurants, cafes, and coffee shops.",
    "Sports: Activities, events, or establishments related to physical exercise, games, or athletic competitions, such as gyms, stadiums, or sports clubs.",
    "Take out: Food or beverages delivered. Thuisbezorgd.nl, UberEats, Deliveroo, or other food delivery services.",
    "Commute | Train | Plane: Transportation services including trains, buses, airplanes. NS, OV-chipkaart, KLM, or other travel companies.",
    "miscellaneous: Entities or activities that do not fall into a specific category or are ambiguous in nature.",
    "Housing | Rent: Places or services related to accommodation, including apartments, rental properties, or housing agencies.",
    "Person: Transactions made to people and not companies."
    "Grocery: Convenience stores. Typically Albert Heijn, AH To Go, Jumbo, or other supermarkets.",
    ""
]


    model = SentenceTransformer('all-MiniLM-L6-v2')



    for i in range(15):
        # Pick a random company from the transaction data
        random_company = random.choice(transaction_data_with_details['company'][:119])

        # Retrieve the summary for the selected company from the in-memory data
        summary = next((item['summary'] for item in companies_and_summaries if item['company'] == random_company), None)
        
        # Check if a summary was found
        if not summary:
            print(f"No summary found for {random_company}")

        # check similarity
        sentence_embedding = model.encode(summary, convert_to_tensor=True)
        activity_embeddings = model.encode(categories, convert_to_tensor=True)

        matches = util.pytorch_cos_sim(sentence_embedding, activity_embeddings)
        if matches.argmax() < 0.8:
            best_match = "miscellaneous"
        else:
            best_match = categories[matches.argmax()]

        
        print("*"*100)
        print(f"{random_company} :{best_match.split(":")[0]}")


