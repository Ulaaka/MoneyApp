## Money Manager Application

### Overview

A personal finance app that reads bank statements and turns them into clear, interactive charts and reports, helping you better understand your financial patterns.

### Setup

**Install the dependencies:**
```bash
pip install -r requirements.txt
```

**Set up the environment variables:**
```bash
cp .env.example .env
```
Fill in the required values in your `.env` file.

**Set up the database:**
```bash
mysql -u root -p < database_creation_query.sql
```

**Run the application:**
```bash
python src/main.py
```

### Features

- Supports PDF and CSV bank statements from multiple UK banks (Lloyds, HSBC, Monzo, Santander, etc.)
- Automatically standardises transaction data across different bank formats
- Searchable and filterable transaction table
- Smart auto-categorisation that updates as changes are made
- Nine types of interactive charts and graphs
- Export everything as CSV, PDF, or PNG
- Files are encrypted on disk and passwords are hashed
- Account recovery, including access to previously uploaded files

### How to Use

When the app starts, the login page is displayed.

<img width="398" height="525" alt="Login page" src="https://github.com/user-attachments/assets/6b621124-966b-4df6-ba89-e7d2dea0c1fb" />

**Creating an account**

If you don't have an account, click "Create New Account" to go to the signup page. An account is created if:
- The password satisfies the safety requirements
- The email is valid
- The username is unique

After successful signup, or by clicking "Already have an account?", you will be taken back to the login page.

<img width="420" height="528" alt="Account creation" src="https://github.com/user-attachments/assets/50b24f3b-b99d-41fe-8916-a4c8f080483f" />

**Resetting a forgotten password**

If you've forgotten your password,  enter your username and click "Forgotten Password?". 
A verification code will be sent to your registered email, and you will be taken to the verification page to enter it within 90 seconds.

<img width="1014" height="317" alt="Verification code email" src="https://github.com/user-attachments/assets/cc2e8fa4-102b-499d-8bb7-a5819bb02692" />

<img width="394" height="525" alt="Verification page" src="https://github.com/user-attachments/assets/9bdb78f4-1d5e-4663-abcd-18e94178738e" />

- If the code isn't entered in time, a new code will be sent automatically.
- If an incorrect code is entered, a warning message will appear.
- Once the correct code is entered, you will be taken to the password reset page.

<img width="398" height="519" alt="Password reset page" src="https://github.com/user-attachments/assets/a0406abb-d21c-4335-bc36-19d6ad7a7eff" />

After setting a new password that meets the requirements, you will be returned to the login page.

**Logging in**

Enter your credentials and click "Login."

- If the details are incorrect, a warning message appears.

<img width="398" height="529" alt="Incorrect login warning" src="https://github.com/user-attachments/assets/753ecf25-cf7c-411e-86a4-6171e0faa65a" />

- If the details are correct, you're redirected to the home page. (In this state, no account has been added yet.)

<img width="1068" height="629" alt="Home page" src="https://github.com/user-attachments/assets/ccd92b3d-d359-481c-9a0a-4774aed4d99d" />

**Account Creation and Selection**

You can manage accounts by clicking the button with wallet icon, which allows you to choose which account to display if you have more than one. If you don't have an account yet, click "Add Account" to open a new window and create one.

<img width="1075" height="628" alt="Screenshot 2026-06-16 at 14 19 15" src="https://github.com/user-attachments/assets/5229728d-7fa1-4b09-afb2-80e3583a571b" />

<img width="1168" height="634" alt="Screenshot 2026-06-16 at 14 19 57" src="https://github.com/user-attachments/assets/ff812a3c-026d-44a8-a195-82a172695725" />

- The account is created if all the information is provided in the form. If not, corresponding warning message will appear.
- The below is the state of home page after the first account is created.
  
<img width="1065" height="631" alt="Screenshot 2026-06-16 at 14 22 56" src="https://github.com/user-attachments/assets/8bd66631-5802-4e60-a30a-9924e39ae83d" />

**Transaction upload**

<img width="1068" height="628" alt="Screenshot 2026-06-16 at 14 25 46" src="https://github.com/user-attachments/assets/cf9c8497-3826-4a94-a07f-ce92fbf9411f" />

- You can upload transaction statements in PDF and CSV formats via "upload" button, which will then allow you to select the files.
- The progress window shows the state of the files uploaded
  -  If the files are uploaded successfully:
  <img width="1071" height="628" alt="Screenshot 2026-06-16 at 14 29 33" src="https://github.com/user-attachments/assets/94407c4c-fe84-4df5-bd0b-7ce80d65052f" />
  - If the files with the same content aleady exists:
  <img width="1071" height="630" alt="Screenshot 2026-06-16 at 14 34 50" src="https://github.com/user-attachments/assets/08f1703c-8241-4d4f-9f5e-2197768929b4" />
  - You can preview the duplicate files by cliking on the link in the progress window


- Transaction can also be uploaded manually by entering all the required information in the form and clicking "Add Transaction" button, if not, corresponding warning message will be shown.

<img width="1068" height="628" alt="Screenshot 2026-06-16 at 14 26 15" src="https://github.com/user-attachments/assets/7c8d83f3-00d9-47ca-9b0e-7ac87a66ec50" />





