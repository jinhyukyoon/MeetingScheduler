# Create Google Oauth2.0 credentials
1. Go to the **Google Cloud Console**.
2. Select your project *(e.g., meetingscheduler-424407)*.
3. Navigate to the **"IAM & Admin" > "Service accounts"**.
4. Click **"Create Service Account"**.
5. Fill in the required details and click **"Create"**.
6. Assign the **"Project" > "Editor"** role to the service account (or another role with necessary permissions for the Calendar API).
7. Click **"Continue"** and then **"Done"**.
8. Find the newly created service account in the list and click on it.
9. Go to the **"Keys"** tab, click **"Add Key"**, and select **"Create new key"**.
10. Choose **"JSON"** and click **"Create"**. This will download the service account key JSON file to your computer.

# MariaDB setup
1. installation: ``brew services start mariadb ``
2. `` mysql -u root -p ``
3. `` CREATE DATABASE schedule; ``
4. `` CREATE USER 'myuser'@'localhost' IDENTIFIED BY 'password' ``
5. `` GRANT ALL PRIVILEGES ON schedule.* TO 'myuser'@'localhost'; ``
6. ``FLUSH PRIVILEGES;``
6. ``exit``

# flask db initialization
1. ``flask db init``
2. ``flask db migrate -m "Initial migration"``
3. ``flask db upgrade``