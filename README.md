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

You will need to create a gmail app password (EMAIL_HOST_PASSWORD in env) from this link:  

https://myaccount.google.com/apppasswords?pli=1&rapt=AEjHL4NrXmNPNO-Si6UDjeAeXrtarYomuS5lAU3cMsmRQyALsybGA_p19Cd-CBH8stb00nM2JUfiT-aRkQJN832iUUkehVodm_I9-K9_X71QeDlehQkSPH0

**Set up the database:**

You will need to download a MySQL server from this link: 

https://www.oracle.com/mysql/technologies/mysql-enterprise-edition-downloads.html.

After installation, run the following command to set up the database.
```bash
mysql -u root -p < database_creation_query.sql
```

**Run the application:**
```bash
python src/main.py
```

### Features

- Supports PDF and CSV bank statements from multiple UK banks (Lloyds, HSBC, Monzo, Santander, and it should theoretically for other banks too)
- Automatically standardises transaction data across different bank formats
- Searchable and filterable transaction table
- Smart auto-categorisation that updates as changes are made
- Nine types of interactive charts and graphs
- Export everything as CSV, PDF, or PNG
- Instant transaction stamtements processing
- Files are encrypted on disk and passwords are hashed
- Password can be updated (via Password-based key hierarchy with key wrapping)
  
  - Password-based key hierarchy (key wrapping)
    - Password + salt → derives Key Encryption Key (KEK)
    - KEK → encrypts (wraps) Data Encryption Key (DEK)
    - DEK → encrypts files (data)
      
- Account recovery, including access to previously uploaded files (via RSA cryptography)
- User verification via email
- User information validity check (email validity, password requirement, username uniqueness)

### How to Use:

When the app starts, the login page is displayed.

<img width="398" height="525" alt="Login page" src="https://github.com/user-attachments/assets/6b621124-966b-4df6-ba89-e7d2dea0c1fb" />

#### Creating an account

If you don't have an account, click "Create new account" to go to the signup page. An account is created if:
- The password satisfies the safety requirements
- The email is valid
- The username is unique

After successful signup, or by clicking "Already have an account?", you will be taken back to the login page.

<img width="420" height="528" alt="Account creation" src="https://github.com/user-attachments/assets/50b24f3b-b99d-41fe-8916-a4c8f080483f" />

#### Resetting a forgotten password

If you've forgotten your password,  enter your username and click "Forgotten Password?". 
A verification code will be sent to your registered email, and you will be taken to the verification page to enter it within 90 seconds.

<img width="1014" height="317" alt="Verification code email" src="https://github.com/user-attachments/assets/cc2e8fa4-102b-499d-8bb7-a5819bb02692" />

<img width="394" height="525" alt="Verification page" src="https://github.com/user-attachments/assets/9bdb78f4-1d5e-4663-abcd-18e94178738e" />

- If the code isn't entered in time, a new code will be sent automatically.
- If an incorrect code is entered, a warning message will appear.
- Once the correct code is entered, you will be taken to the password reset page.

<img width="398" height="519" alt="Password reset page" src="https://github.com/user-attachments/assets/a0406abb-d21c-4335-bc36-19d6ad7a7eff" />

After setting a new password that meets the requirements, you will be returned to the login page.

#### Logging in

Enter your credentials and click "Login."

- If the details are incorrect, a warning message appears.

<img width="398" height="529" alt="Incorrect login warning" src="https://github.com/user-attachments/assets/753ecf25-cf7c-411e-86a4-6171e0faa65a" />

- If the details are correct, you're redirected to the home page. (In this state, no account has been added yet.)

<img width="1068" height="629" alt="Home page" src="https://github.com/user-attachments/assets/ccd92b3d-d359-481c-9a0a-4774aed4d99d" />

#### Account Creation and Selection

You can manage accounts by clicking the button with wallet icon, which allows you to choose which account to display if you have more than one.

If you don't have an account yet, click "Add Account" to open a new window and create one.

<img width="1075" height="628" alt="Screenshot 2026-06-16 at 14 19 15" src="https://github.com/user-attachments/assets/5229728d-7fa1-4b09-afb2-80e3583a571b" />

<img width="1168" height="634" alt="Screenshot 2026-06-16 at 14 19 57" src="https://github.com/user-attachments/assets/ff812a3c-026d-44a8-a195-82a172695725" />

- The account is created if all the information is provided in the form. If not, corresponding warning message will appear.
- The below is the state of home page after the first account is created.
  
<img width="1065" height="631" alt="Screenshot 2026-06-16 at 14 22 56" src="https://github.com/user-attachments/assets/8bd66631-5802-4e60-a30a-9924e39ae83d" />

#### Transaction upload

<img width="1068" height="628" alt="Screenshot 2026-06-16 at 14 25 46" src="https://github.com/user-attachments/assets/cf9c8497-3826-4a94-a07f-ce92fbf9411f" />

- You can upload transaction statements in PDF and CSV formats via "upload" button, which will then allow you to select the files.
- The progress window shows the state of the files uploaded:
  -  If the files are uploaded successfully:
  <img width="1071" height="628" alt="Screenshot 2026-06-16 at 14 29 33" src="https://github.com/user-attachments/assets/94407c4c-fe84-4df5-bd0b-7ce80d65052f" />
  
  - If the files with the same content aleady exists:
  <img width="1071" height="630" alt="Screenshot 2026-06-16 at 14 34 50" src="https://github.com/user-attachments/assets/08f1703c-8241-4d4f-9f5e-2197768929b4" />
  
  - You can preview the duplicate files by clicking on the link in the progress window.

- Transaction can also be uploaded manually by entering all the required information in the form and clicking "Add Transaction" button, if not, corresponding warning message will be shown.

<img width="1068" height="628" alt="Screenshot 2026-06-16 at 14 26 15" src="https://github.com/user-attachments/assets/7c8d83f3-00d9-47ca-9b0e-7ac87a66ec50" />

- Duplicate transactions (which may appear across different files or entered twice) are automatically ignored, keeping the data in a consistent state.

#### Transactions and Files Management

You can remove transactions either by deleting the associated file, which removes all related transactions, or by deleting them individually from the transaction table on the home page.

<img width="1067" height="630" alt="Screenshot 2026-06-16 at 15 11 34" src="https://github.com/user-attachments/assets/d0462889-47f9-4797-96a1-f48142169946" />

<img width="1064" height="630" alt="Screenshot 2026-06-16 at 15 11 24" src="https://github.com/user-attachments/assets/a8aea369-631f-4b98-a52a-81743193084b" />

#### Graphs

There are various options of graphs available for you to understand your spending pattern, each  having their unique filters.

The below are examples of graphs:

<img width="1070" height="628" alt="Screenshot 2026-06-16 at 15 13 38" src="https://github.com/user-attachments/assets/0f083703-380d-4aa4-a2f2-2f6b9ecc9860" />
<img width="1073" height="629" alt="Screenshot 2026-06-16 at 15 17 28" src="https://github.com/user-attachments/assets/2f0e0b72-fcad-4ea6-8141-d655e829f81b" />

You can also increase the size of the graph without setting full screen by cliking on the "Graphs" text.
<img width="1070" height="625" alt="Screenshot 2026-06-16 at 15 20 14" src="https://github.com/user-attachments/assets/6f84c199-06a7-46c2-83cf-82c796dd2a1e" />

#### Export

The transaction table, including filtered views, can be exported in CSV or PDF format. Graphs can be downloaded as PNG files, including any that have been filtered.

You can see the downloaded files in your downloads folder.

- Exported Transaction Table in CSV format.
[View CSV](./Export_exmaples/lloyds_financial_report_2026-06-16.csv)

- Exported Transaction Table in PDF format.
[View PDF](./Export_exmaples/lloyds_financial_report_2026-06-16.pdf)

- Exported Graph in PNG format (example).
![Top Expense Sources](./Export_exmaples/lloyds_Top%20Expense%20Sources_2026-06-16.png)

#### Categorisation

You can define and customise transaction categories either through the Category subpage in Settings, or directly from the transaction table. 

<img width="1074" height="630" alt="Transaction categorisation" src="https://github.com/user-attachments/assets/f37b3fa8-9d91-4162-ad23-2062e3218e51" />

From the table, you can update a transaction's category in two ways: by changing its description, which automatically assigns the closest matching category (or "Undefined" if no match is found), or by directly changing its category, which updates all related transactions to reflect the new category.

<img width="1072" height="627" alt="Screenshot 2026-06-16 at 15 44 41" src="https://github.com/user-attachments/assets/80b1413d-dc4d-43fe-a38c-7ab921c79ed6" />

From the Category subpage, you can add new categories or edit existing ones, with changes automatically reflected across all related transactions.

If a category is deleted, affected transactions are reassigned to the next closest matching category, based on a defined hierarchy of similarity, or marked "Undefined" if no match is found.

Category matching is based on keywords found in the transaction description, and works hierarchically: the system tries to find the most specific matching category first, falling back to broader categories if no specific match exists.

#### Account Management

<img width="1063" height="627" alt="Screenshot 2026-06-16 at 15 39 10" src="https://github.com/user-attachments/assets/71ca9019-9b28-4a53-ab67-c12ad991462f" />

<img width="1071" height="632" alt="Screenshot 2026-06-16 at 15 41 29" src="https://github.com/user-attachments/assets/b6e292d9-9853-4b63-97a8-eb3575c30c84" />

Account information can be managed by clicking the account button or visiting the Profile page. From there, details can be edited and saved.

You can also delete your account from this page. Deleting action will result in a warning message appearing, asking you to confirm or cancel before proceeding.

<img width="1071" height="627" alt="Screenshot 2026-06-16 at 15 42 38" src="https://github.com/user-attachments/assets/26676a98-6f76-4cf0-8cfb-ac511ad8fc79" />

#### User Profile Management

<img width="1072" height="631" alt="Screenshot 2026-06-16 at 15 46 08" src="https://github.com/user-attachments/assets/b1f6e77d-da8d-47d0-8cd2-dc2d59ba95aa" />

User information can be edited through the Profile page. 
Changing the registered email requires verification: a code is sent to confirm the change before it takes effect.

- The verfication window:
<img width="1075" height="633" alt="Screenshot 2026-06-16 at 15 48 44" src="https://github.com/user-attachments/assets/1ffe7396-b6cb-4701-aca7-709d9e54a6a5" />

- The state after verification:
<img width="1076" height="628" alt="Screenshot 2026-06-16 at 15 49 15" src="https://github.com/user-attachments/assets/33154e55-c07b-49f8-9a38-25586e117ca2" />

<img width="1068" height="630" alt="Screenshot 2026-06-16 at 15 51 33" src="https://github.com/user-attachments/assets/bc6a9312-1ee5-4d13-8f9d-af86a9349cec" />

User password can be changed via the Password Change subpage in Settings.

<img width="1076" height="629" alt="Screenshot 2026-06-16 at 15 52 31" src="https://github.com/user-attachments/assets/6963a3cc-5171-43ea-8cf6-c615006b7603" />

User Account can also be deleted via the Account Deletion subpage in Settings, which requires the current password.


