from models.users import create_users
from models.projects import create_projects
from models.mapper import create_mapper


if __name__ == "__main__":    
    users = create_users()
    projects = create_projects()
    create_mapper(users, projects)