<img src="synbiosource/static/assets/images/SBS_Logo_transparentbg_notext.png" alt="SynBioSource Logo" width="100">

# SynBioSource

SynBio Source is an open-source platform designed for the Synthetic Biology community, enabling easy sharing and management of datasets. It offers intuitive uploading and searching capabilities, with the goal of fostering a unified metadata standard to enhance accessibility and collaboration within the field. 

This README provides a comprehensive guide to setting up and running the application locally or otherwise. 

## Table of Contents

- [Setup](#setup)
- [File Structure](#file-structure)
- [Environment Variables](#environment-variables)
- [Database Configuration](#database-configuration)
- [AWS S3 Configuration](#aws-s3-configuration)
- [Local Storage Configuration](#local-storage-configuration)

## Setup

1. **Clone the Repository**
    ```bash
    git clone https://github.com/AatishDA1/SynBioSource.git
    cd SynBioSource
    ```

2. **Create a Virtual Environment and Install Dependencies**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3. **Apply Migrations**
    ```bash
    python manage.py migrate
    ```

4. **Create a Superuser**
    ```bash
    python manage.py createsuperuser
    ```

5. **Run the Server**
    ```bash
    python manage.py runserver
    ```

## File Structure

- **synbiosource/**: Main Django application
- **dashboard/**: Contains views and templates for the user dashboard
- **dataset/**: Manages data upload and dataset-related functionalities
- **api/**: Provides REST API endpoints for the application

## Environment Variables

Create a `.env` file in the root directory and include the following variables:

```plaintext
SECRET_KEY='your_secret_key'
USE_S3=True  # Set to False if not using AWS S3
AWS_ACCESS_KEY_ID='your_aws_access_key_id'
AWS_SECRET_ACCESS_KEY='your_aws_secret_access_key'
AWS_STORAGE_BUCKET_NAME='your_s3_bucket_name'
SCREATE='your_secret'
EMAIL_HOST_USER='your_email_host_user'
EMAIL_HOST_PASSWORD='your_email_host_password'

DB_NAME='your_db_name'
DB_USER='your_db_user'
DB_PORT='your_db_port'
DB_PASSWORD='your_db_password'
DB_HOST='your_db_host'

TEST_DATABASE_URL='your_test_database_url'
```

## Database Configuration
SynBioSource uses a PostgreSQL database. Update the .env file with your PostgreSQL credentials:
```plaintext
DB_NAME='your_db_name'
DB_USER='your_db_user'
DB_PORT='your_db_port'
DB_PASSWORD='your_db_password'
DB_HOST='your_db_host'
```

## AWS S3 Configuration
To enable AWS S3 for storage, ensure the following variables are set in your .env file:

```plaintext
USE_S3=True
AWS_ACCESS_KEY_ID='your_aws_access_key_id'
AWS_SECRET_ACCESS_KEY='your_aws_secret_access_key'
AWS_STORAGE_BUCKET_NAME='your_s3_bucket_name'
```

## Local Storage Configuration
If not using AWS S3, set USE_S3=False in your .env file. Datasets will be stored in the local file system.


