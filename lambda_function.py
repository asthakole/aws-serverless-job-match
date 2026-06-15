import re
import json
import uuid
import boto3
from decimal import Decimal
from datetime import datetime, timezone

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("JobMatches")

s3 = boto3.client("s3", region_name="us-east-1")
BUCKET_NAME = "astha-job-match-descriptions"

RESUME_KEYWORDS = {
    "python",
    "java",
    "c",
    "flask",
    "aws",
    "s3",
    "rds",
    "mysql",
    "linux",
    "rest api",
    "tcp/ip",
    "dns",
    "networking",
    "cloud",
    "debugging",
    "systems",
    "operating systems",
    "multithreading",
}


def clean_text(text):
    return re.sub(r"[^a-zA-Z0-9+.#/ ]", " ", text.lower())


def calculate_match(job_description):
    cleaned = clean_text(job_description)

    matched = []
    missing = []

    for keyword in RESUME_KEYWORDS:
        if keyword in cleaned:
            matched.append(keyword)
        else:
            missing.append(keyword)

    score = round((len(matched) / len(RESUME_KEYWORDS)) * 100)

    if score >= 75:
        recommendation = "Strong match - apply"
    elif score >= 50:
        recommendation = "Medium match - tailor resume"
    else:
        recommendation = "Low match - skip or heavily tailor"

    return {
        "match_score": score,
        "matched_keywords": sorted(matched),
        "missing_keywords": sorted(missing),
        "recommendation": recommendation,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def save_job_description_to_s3(job_id, company, title, job_description):
    safe_company = clean_text(company).replace(" ", "-").strip("-")
    safe_title = clean_text(title).replace(" ", "-").strip("-")

    s3_key = f"job-descriptions/{safe_company}/{job_id}-{safe_title}.txt"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=job_description,
        ContentType="text/plain",
    )

    return s3_key

def convert_decimal(obj):
    if isinstance(obj, list):
        return [convert_decimal(item) for item in obj]

    if isinstance(obj, dict):
        return {key: convert_decimal(value) for key, value in obj.items()}

    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)

    return obj

def get_all_jobs():
    response = table.scan()
    jobs = response.get("Items", [])

    jobs = convert_decimal(jobs)

    return {
        "statusCode": 200,
        "body": json.dumps(jobs),
    }

def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method")

    if method == "GET":
        return get_all_jobs()

    body = event.get("body", event)

    if isinstance(body, str):
        body = json.loads(body)

    company = body.get("company", "Unknown Company")
    title = body.get("title", "Unknown Title")
    job_description = body.get("job_description", "")

    if not job_description:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "job_description is required"}),
        }

    match_result = calculate_match(job_description)
    job_id = str(uuid.uuid4())

    s3_key = save_job_description_to_s3(
        job_id,
        company,
        title,
        job_description,
    )

    job_result = {
        "job_id": job_id,
        "company": company,
        "title": title,
        "status": "saved",
        "s3_bucket": BUCKET_NAME,
        "s3_key": s3_key,
        **match_result,
    }

    table.put_item(Item=job_result)

    return {
        "statusCode": 200,
        "body": json.dumps(job_result),
    }


if __name__ == "__main__":
    with open("test_event.json", "r") as file:
        sample_event = json.load(file)

    response = lambda_handler(sample_event, None)
    print(json.dumps(json.loads(response["body"]), indent=2))