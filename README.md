# **Boardgame Manager**

---
## **Description**

___
Boardgame Manager is a back-end application for managing a board game library. 
Board game information could be created manually or fetched from the BoardGameGeek (BGG) API.
The most important game information is stored in an SQL database using different related tables.
The application also provides user management with two roles: administrator and member.
Each role has different permissions and access to the application's features.
The application was built with Python, FastAPI, PostgreSQL, SQLAlchemy, and the BoardGameGeek API..
BoardGame Manager was developed as the final project for a Software Engineering Bootcamp at Masterschool.


## **Main features**
___

**User registration, login and JWT authentication**
  - Users can create an account and log in securely using JWT authentication.

**Admin/member roles**
  - The first user created is automatically assigned the administrator role. All subsequent users created are automatically assigned the member role.

**Game management**
  - Administrators can read, create, update, import and delete board games in the database, while members have read-only access.
  - Board game information is stored and managed in a PostgreSQL database.

**BGG API integration**
  - Board game information can be searched and imported from the BoardGameGeek API.



## Technologies

___

| Technology        | Purpose                           |
|:------------------|:----------------------------------|
| Python            | Core programming language         |
| FastAPI           | Web framework                     |
| PostgreSQL        | Relational database               |
| SQLAlchemy        | Database access and ORM           |
| Pydantic          | Data validation and serialization |
| JWT               | User authentication               |
| BoardGameGeek API | Retrieve Board game information   |


## **Project structure**

___
The application follows the **Repository Pattern**, a design pattern that acts as an intermediary between the application's business logic and its data access layer.
This structure makes the application easier to maintain, test, and extend.
```text
boardgame_manager/
│
├── app/
│   ├── auth/
│   │   ├── dependencies.py
│   │   └── security.py
│   ├── database/
│   │   ├── models/
│   │   │   └── models.py
│   │   └── database.py
│   ├── exceptions/
│   │   └── exceptions.py
│   ├── repositories/
│   │   ├── game_repository.py
│   │   ├── sqlalchemy_game_repository.py
│   │   ├── user_repository.py
│   │   └── sqlalchemy_user_repository.py
│   ├── schemas/
│   │   └── schemas.py
│   ├── services/
│   │   ├── bgg_service.py
│   │   ├── game_service.py
│   │   └── user_service.py
│   └── main.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

| Directory         | Purpose                                                                             |
|:------------------|:------------------------------------------------------------------------------------|
| auth              | Authentication and authorization logic, including JWT handling                      |
| database          | Database configuration and SQLAlchemy models used to define the database structure. |
| exceptions        | Custom application exceptions                                                       |
| repositories      | Repository interfaces and implementations responsible for database access           |
| schemas           | Pydantic schemas for request and response validation                                |
| services          | Business logic for users, board games, and BGG API requests.                        |

**main.py**: FastAPI application, endpoints and dependency configuration.

## **Installation**

___

1. Get a BGG token:
    
    Get a BoardGameGeek API token from the [BoardGameGeek Applications](https://boardgamegeek.com/applications)

3. Clone the repository:

    ```bash
        git clone https://github.com/esterplaza/BoardGame-Manager.git    
        cd BoardGame-Manager
    ```

3. Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    ```
    Activation for Windows PowerShell:
    ```Powershell
    .venv\Scripts\Activate.ps1
    ```
    Activation for Linux/macOS:
    ```bash
    source .venv/bin/activate
    ```
4. Install requirements:

    ```bash
    pip install -r requirements.txt
    ```
5. Set up PostgreSQL:

    Make sure PostgreSQL is installed and running locally, and that a database named boardgame_manager has been created.
    The database can be created using PostgreSQL/pgAdmin.
    ```SQL
    CREATE DATABASE boardgame_manager;
    ```
6. Create a .env file:

    Create a .env file in the project root directory. The file should follow this format:
    ```env
    DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/boardgame_manager
    
    BGG_TOKEN=YOUR_BGG_TOKEN
        
    SECRET_KEY=YOUR_SECRET_KEY
    ```
    Replace the placeholder values with your own PostgreSQL password, BoardGameGeek API token, and secret key.

5. Start the application  

    ```bash
      uvicorn app.main:app --reload
    ```
6. Open API documentation in your browser:
    
    ```text
    http://127.0.0.1:8000/docs
    ```
    The FastAPI Swagger documentation provides an interactive interface for exploring and testing the API endpoints.

## API Endpoints
___
| Method | Endpoint                 | Description                                  | Access        |
|:-------|:-------------------------|----------------------------------------------|---------------|
| POST   | /users                   | Register a new user                          | Public        |
| POST   | /login                   | Authenticate a user                          | Public        |
| GET    | /users/me                | Get current user information                 | Authenticated |
| GET    | /games                   | Get all games                                | Admin/Member  |
| GET    | /games/{game_id}         | Get a game by ID                             | Admin/Member  |
| POST   | /games                   | Create a game                                | Admin         |
| PUT    | /games/{game_id}         | Update a game                                | Admin         |
| DELETE | /games/{game_id}         | Delete a game                                | Admin         |
| GET    | /bgg/search              | Search for a game by title using the BGG API | Admin/Member  |
| GET    | /bgg/game/{bgg_id}       | Get game details by BGG ID using the BGG API | Admin/Member  |
| POST   | /games/import/{bgg_id}   | Import a game by BGG ID from BGG API         | Admin         |


## **Authentication**

___

The application uses JWT-based authentication. Users authenticate through
the `/login` endpoint and receive a JWT bearer token that must be provided
when accessing protected endpoints.


## **Authorization**

___

The application has two roles:

- Admin – full access to game management operations, including creating, updating importin, and deleting games.
- Member – read-only access to board games.

The first registered user is automatically assigned the Admin role.
All subsequent users are assigned the Member role.

## **Database Schema**

___
The following diagram shows the database structure and relationships between the tables.
![Database Schema](docs/dbdiagram.png)

## **Deployment**

___
The application was successfully deployed to Render with a PostgreSQL database. The deployed environment was tested for database connectivity, authentication, user roles and BGG game imports.

## **Acknowledgments**

___

BoardGame Manager uses the [BoardGameGeek API](https://boardgamegeek.com/using_the_xml_api)
to search for and retrieve board game information.

[![Powered by BGG](static/powered_by_BGG_01_SM.png)](https://boardgamegeek.com)

