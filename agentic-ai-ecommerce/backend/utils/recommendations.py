import random

def get_user_recommendations(user_id, catalog, n=5):
    """
    VERY SIMPLE: Just recommend random products for now.
    For real use: filter based on user activity, similarity, analytics, etc.
    """
    all_products = catalog.get("products", [])
    if len(all_products) <= n:
        return all_products
    return random.sample(all_products, n)
