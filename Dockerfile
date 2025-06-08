# Use Miniconda as the base image for conda + pip support
FROM continuumio/miniconda3

# Set working directory
WORKDIR /app

# Copy environment and requirements files
COPY environment.yml .
COPY requirements.in .
COPY requirements.txt .
COPY .env .

# Create the conda environment
RUN conda env create -f environment.yml

# Make sure the environment is activated by default
SHELL ["conda", "run", "-n", ".conda_flexiai", "/bin/bash", "-c"]

# Copy the rest of the application code
COPY . .

# Expose the port your Quart app runs on
EXPOSE 8000

# Run the Quart app
CMD ["conda", "run", "-n", ".conda_flexiai", "python", "app.py"]
