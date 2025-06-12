from home_budget.apps.category.models import Category


def create_predefined_categories(db, user_id):
    predefined_categories = [
        {"name": "Groceries", "description": "Food and household items"},
        {"name": "Utilities", "description": "Electricity, water, gas bills"},
        {"name": "Entertainment", "description": "Movies, games, and leisure activities"},
    ]

    for c in predefined_categories:
        category_name = c["name"]
        category_description = c.get("description", "")
        if not db.query(Category).filter(Category.name == category_name, Category.user_id == user_id).first():
            new_category = Category(name=category_name, user_id=user_id, description=category_description)
            db.add(new_category)

    db.commit()
