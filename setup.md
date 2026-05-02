# Project Setup Guide: Food Delivery Website

Follow these steps to set up and run the Food Delivery Website on your local machine.

## Prerequisites
Before you begin, ensure you have the following installed:
*   Python 3.x
*   pip (Python package installer)
*   A MySQL database (Local or remote like Railway)

---

## Step 1: Download or Clone the Project
Open your terminal and navigate to the project folder. If you haven't created it yet:
```bash
cd /home/tanvi/Desktop/food_delivery_website
```

## Step 2: Set up a Virtual Environment
It's best practice to use a virtual environment so the project's libraries don't interfere with your system-wide Python installation.

Create the virtual environment:
```bash
python3 -m venv venv
```

Activate the virtual environment:
*   **On Linux/macOS:**
    ```bash
    source venv/bin/activate
    ```
*   **On Windows:**
    ```bash
    venv\Scripts\activate
    ```

You should now see `(venv)` at the start of your terminal prompt.

## Step 3: Install Required Packages
Install all necessary Python libraries (like Flask and the MySQL connector) by running:
```bash
pip install -r requirements.txt
```

## Step 4: Configure the Database
This application is designed to connect to a MySQL database (e.g., hosted on Railway).

1.  Open the `.env` file in the root of the project.
2.  Update the file with your actual database credentials:
    ```env
    DB_USER=your_db_username
    DB_PASSWORD=your_db_password
    DB_HOST=your_db_host
    DB_PORT=your_db_port
    DB_NAME=your_db_name
    SECRET_KEY=a_random_secure_string_for_flask_sessions
    ```
3.  Open your preferred database management tool (e.g., MySQL Workbench, DBeaver).
4.  Connect to your database using the same credentials.
5.  Execute the SQL script located in `database/schema.sql` to create the necessary tables (`users`, `menu_items`, `orders`, `order_items`).

*(Note: For academic simulation purposes, the provided codebase currently runs with in-memory Python lists to demonstrate UI flow quickly. Step 7 in the code guides you to swap this out for the real `models.py` database connection).*

## Step 5: Run the Server
With the virtual environment activated, start the Flask development server:
```bash
python run.py
```

## Step 6: View the Website
Once the server is running, open your web browser and go to:
**`http://127.0.0.1:5000`**

To stop the server, press `Ctrl + C` in your terminal.
