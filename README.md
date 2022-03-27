# papers-tracker

## Introduction
This is a python application which collects follow-up papers of registered papers.


## Run
### 1. Clone repository
```
git clone https://github.com/respect5716/papers-tracker.git
```

### 2. Register papers
Write the arxiv ids of papers which you want to follow on the `papers.txt`.

```
2004.04906
2012.15828
```

### 3. Set variables
This application sends you the results by email. Thus you need to set you email information as environment variables.
Only google gmail was tested, so if you want to send to other emails, you need to test it.
The EMAIL_PASSWORD is an [app password](https://support.google.com/accounts/answer/185833?hl=en), which doesn't mean your google password.

```
export EMAIL_ADDRESS=my_email_address
export EMAIL_PASSWORD=my_email_password
```

### 4. Run the script
Install the required libraries and run the python script. Then, you will receive the follow-up papers.

```
pip install -r requirements.txt
python main.py
```

### (Optional) Github Action
I registered github action which run this script at every 6 am (KST). If you want this function either, just fork this repository and add your email information to [github secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets).
