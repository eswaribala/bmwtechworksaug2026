import json

def lambda_handler(event, context):
    vehicle_id = event.get("vehicle_id", "BMW001")
    model = event.get("model", "iX")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "BMW vehicle processed successfully",
            "vehicle_id": vehicle_id,
            "model": model
        })
    }