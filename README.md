# E-commerce Backend Project

Welcome to the E-commerce Backend project repository! This project is structured using Flask, SQLAlchemy, and Flask-Migrate for database migrations, and it is containerized with Docker for consistent and portable deployment.

This README will guide you through setting up the project locally, including environment setup, pulling the repository, running migrations, and working collaboratively.

---

## **Project Overview**
This project implements the backend services for an e-commerce platform. So far, we have:

1. A `Customers` service that includes:
   - API to register a customer.
   - API to delete a customer.
2. Database migrations for the `customers` table.
3. Dockerized configuration for the Flask app and MySQL database.

---

## **How to Pull and Set Up the Project Locally**

### **Step 1: Clone the Repository**
1. Open your terminal or Git Bash and navigate to the directory where you want to clone the project.
2. Run the following command:
   ```bash
   git clone <repository_url>
   ```
   Replace `<repository_url>` with the actual GitHub repository URL.

3. Navigate into the project directory:
   ```bash
   cd ecommerce_project
   ```

### **Step 2: Set Up the Environment**
1. Ensure Python 3.9 or above is installed on your system. You can check your Python version with:
   ```bash
   python --version
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### **Step 3: Set Up the Database**
The project uses MySQL and Flask-Migrate for database migrations. Follow these steps to set up the database:

1. Ensure you have MySQL installed and running. Alternatively, you can use the Dockerized version (explained in Step 6 below).
2. Open MySQL Workbench or a terminal and create a database:
   ```sql
   CREATE DATABASE ecommerce_db;
   ```

3. Update the `.env` file in the root directory (or ensure the `database/db_config.py` is correctly configured). The database URI format should be:
   ```plaintext
   mysql+pymysql://root:<yourpassword>@localhost:3306/ecommerce_db
   ```
   Replace `<yourpassword>` with your MySQL root password. **If using Dockerized MySQL, update the host to `mysql-container` in the URI**:
   ```plaintext
   mysql+pymysql://root:<yourpassword>@mysql-container:3306/ecommerce_db
   ```

4. Run the migrations to create the database schema:
   ```bash
   flask db upgrade
   ```

### **Step 4: Run the Flask App Locally**
To run the Flask application locally, use:
```bash
python app.py
```
The API will be available at `http://127.0.0.1:5000`.

### **Step 5: Test the Existing APIs**
1. Use Postman or any API client to test the existing endpoints:
   - **Register a Customer**: `POST /customers/register`
   - **Delete a Customer**: `DELETE /customers/<customer_id>`
2. Check the database to ensure changes are reflected.

### **Step 6: Use Docker for the Project**
To run the project using Docker, follow these steps:

1. Ensure Docker is installed and running on your machine.
2. Build and start the services:
   ```bash
   docker-compose build
   docker-compose up
   ```
3. The Flask app will be available at `http://localhost:5000`, and the MySQL database will be accessible at `localhost:3306`.
4. Run migrations inside the Docker container (if needed):
   ```bash
   docker exec -it flask-container flask db upgrade
   ```

### **Important Notes on Database Configuration**
- **Local MySQL vs Dockerized MySQL**: If you are using the Dockerized MySQL, ensure your Flask app's `SQLALCHEMY_DATABASE_URI` points to `mysql-container` as the host, like this:
  ```plaintext
  mysql+pymysql://root:<yourpassword>@mysql-container:3306/ecommerce_db
  ```
  If you're using a local MySQL instance (e.g., with MySQL Workbench), set the host to `localhost`.

- **Data Migration**: The Dockerized MySQL instance starts as a fresh environment. If you previously created tables in your local MySQL, you need to apply migrations in the Dockerized setup to recreate the schema (see Step 6, point 4).

- **Testing Connections**: To test database connections inside the Flask container, use:
  ```bash
  docker exec -it flask-container bash
  flask db upgrade
  ```

---

## **How to Work Collaboratively**

### **Step 1: Pull the Latest Changes**
1. Before starting work, pull the latest changes from the repository:
   ```bash
   git pull origin main
   ```

### **Step 2: Create a New Branch**
1. Create a branch for the feature or bug fix you’re working on:
   ```bash
   git checkout -b <branch_name>
   ```
   Replace `<branch_name>` with a descriptive name, such as `add-inventory-service`.

2. Work on your changes and commit them locally:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

3. Push your branch to the remote repository:
   ```bash
   git push origin <branch_name>
   ```

### **Step 3: Create a Pull Request**
1. Go to the GitHub repository and create a pull request (PR) from your branch to `main`.
2. Add a description of the changes and assign the PR to your teammate for review.

### **Step 4: Resolve Conflicts (if any)**
If there are conflicts when merging, coordinate with your teammate to resolve them.

### **Step 5: Run Migrations After Pulling Changes**
If a teammate has added new migrations, ensure you apply them locally:
```bash
flask db upgrade
```

---

## **Next Steps**
1. Extend the project by working on the other services (“Inventory”, “Sales”, “Reviews”).
2. Follow the same structure for models, routes, and migrations for consistency.
3. Regularly commit and push changes to avoid conflicts.

---

## **Helpful Commands**

### **Database Migrations**
- Initialize migrations (only needed once):
  ```bash
  flask db init
  ```
- Create a new migration:
  ```bash
  flask db migrate -m "Migration description"
  ```
- Apply migrations:
  ```bash
  flask db upgrade
  ```

### **Docker Commands**
- Build the containers:
  ```bash
  docker-compose build
  ```
- Start the services:
  ```bash
  docker-compose up
  ```
- Stop the services:
  ```bash
  docker-compose down
  ```



