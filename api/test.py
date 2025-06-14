def handler(request):
    """Simple test handler to verify Vercel Python functions work."""
    return {
        "statusCode": 200,
        "headers": {
            "content-type": "application/json",
            "access-control-allow-origin": "*"
        },
        "body": '{"message": "Test function works!", "request_method": "' + request.get("httpMethod", "unknown") + '"}'
    } 