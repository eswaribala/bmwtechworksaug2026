def create_mapper(users, projects):
    for (x,y) in zip(users, projects):
        print(f"User: {x}, Project: {y}")