# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy the env file to the container
COPY .env /app/.env

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install SQLite3
RUN apt-get update && apt-get install -y sqlite3

# Add shell script and SQL files for database creation
COPY ./sql/create_db.sh /app/sql/create_db.sh
COPY ./sql/create_users_table.sql /app/sql/create_users_table.sql
COPY ./sql/create_portfolio_table.sql /app/sql/create_portfolio_table.sql

RUN chmod +x /app/sql/create_db.sh
RUN chmod +x /app/entrypoint.sh


# Define a volume for persisting the database
VOLUME ["/app/db"]

# Make port 5000 available to the world outside this container
EXPOSE 5001

# Run the entrypoint script when the container launches
CMD ["/app/entrypoint.sh"]