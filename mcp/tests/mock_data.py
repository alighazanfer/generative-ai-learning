async def mock_resume_data():
    return {
        "candidate": {
            "first_name": "Alice",
            "last_name": "Johnson",
            "email": "alice.johnson@example.com",
            "phone": "+1234567890",
            "address": "123 Main St",
            "city": "New York",
            "gender": "",
            "linkedin": "",
            "skills": [
                {"id": 1, "title": "Python"},
                {"id": 2, "title": "FastAPI"},
                {"id": 3, "title": "Machine Learning"},
            ],
        },
        "job": 101,
        "cv": "https://example.com/resume/alice_johnson.pdf",
        "requirement_values": [
            {
                "employer": "TechCorp",
                "title": "Software Engineer",
                "start": "2019-06-01",
                "end": "2022-08-31",
            },
            {
                "school": "MIT",
                "major": "Computer Science",
                "start": "2015-09-01",
                "end": "2019-06-01",
            },
        ],
        "source_type": "socialmedia",
        "source_value": "",
    }
