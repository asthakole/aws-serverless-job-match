# AWS Serverless Job Match Tracker

A serverless backend project that matches job descriptions against resume keywords, stores job descriptions in AWS S3, saves match results, and exposes REST API endpoints through AWS API Gateway.

## Tech Stack

- Python
- AWS Lambda
- API Gateway
- S3
- DynamoDB
- REST APIs
- AWS CLI
- VS Code

## Features

- Submits job descriptions through an API endpoint
- Calculates match score based on resume/job keyword overlap
- Stores job descriptions in S3
- Saves job metadata, match score, matched keywords, and missing keywords
- Retrieves saved jobs through a GET API endpoint

## Example API Response

```json
{
  "company": "Google",
  "match_score": 72,
  "recommendation": "Medium match - tailor resume",
  "matched_keywords": ["aws", "python", "linux", "networking"],
  "missing_keywords": ["java", "mysql", "rds"]
}