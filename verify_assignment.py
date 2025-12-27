import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def print_pass(msg):
    print(f"✅ PASS: {msg}")

def print_fail(msg):
    print(f"❌ FAIL: {msg}")
    sys.exit(1)

def verify_assignment():
    print("Starting Comprehensive Verification...")

    # 1. Registration
    print("\n[1] Testing Registration")
    phone = "1234567890"
    user_name = "Test User"
    register_data = {"name": user_name, "phone_number": phone, "password": "password123"}
    
    # Clean up potentially existing user from previous runs (cannot easily do via API without admin, assuming fresh DB or ignoring error)
    # Actually, let's use a random phone each time to ensure clean run
    import random
    phone = f"9{random.randint(100000000, 999999999)}"
    register_data["phone_number"] = phone
    
    resp = requests.post(f"{BASE_URL}/register/", json=register_data)
    if resp.status_code == 201:
        print_pass("User registered successfully")
        token = resp.json().get("token")
        if token:
            print_pass("Token received in registration response")
        else:
            print_fail("Token missing in register response")
    else:
        print_fail(f"Registration failed: {resp.text}")

    headers = {"Authorization": f"Token {token}"}

    # 2. Login (for completeness, though we have token)
    print("\n[2] Testing Login")
    login_data = {"username": phone, "password": "password123"}
    resp = requests.post(f"{BASE_URL}/login/", json=login_data)
    if resp.status_code == 200 and "token" in resp.json():
        print_pass("Login successful")
    else:
        print_fail(f"Login failed: {resp.text}")

    # 3. Add Review (New Place)
    print("\n[3] Testing Add Review (New Place)")
    place_name = f"Test Place {random.randint(1, 1000)}"
    address = "123 Test St"
    review_data = {
        "place_name": place_name,
        "address": address,
        "rating": 5,
        "review_text": "Great place!"
    }
    resp = requests.post(f"{BASE_URL}/reviews/", json=review_data, headers=headers)
    if resp.status_code == 201:
        print_pass("Review added for new place")
        # Verify review content
        data = resp.json()
        if data['user_name'] == user_name:
            print_pass("Review has correct user name")
    else:
        print_fail(f"Add review failed: {resp.text}")

    # 4. Add Review (Existing Place - Different User)
    print("\n[4] Testing Add Review (Existing Place, Different User)")
    # Create another user
    phone2 = f"8{random.randint(100000000, 999999999)}"
    headers2 = {"Authorization": f"Token {requests.post(f'{BASE_URL}/register/', json={'name': 'User 2', 'phone_number': phone2, 'password': 'password'}).json()['token']}"}
    
    review_data2 = {
        "place_name": place_name, # Same place
        "address": address,
        "rating": 3,
        "review_text": "Average place."
    }
    resp = requests.post(f"{BASE_URL}/reviews/", json=review_data2, headers=headers2)
    if resp.status_code == 201:
        print_pass("Review added for existing place by User 2")
    else:
        print_fail(f"Add review 2 failed: {resp.text}")

    # 5. Search
    print("\n[5] Testing Search")
    # Exact match
    resp = requests.get(f"{BASE_URL}/places/search/?query={place_name}", headers=headers)
    if resp.status_code != 200:
        import re
        error_msg = "Unknown Error"
        match = re.search(r'<pre class="exception_value">(.*?)</pre>', resp.text)
        if match:
            error_msg = match.group(1)
        print_fail(f"Search request failed with status {resp.status_code}. Exception: {error_msg}")
    
    results = resp.json()
    if len(results) > 0 and results[0]['name'] == place_name:
        print_pass("Exact match search successful")
        # Check average rating: (5+3)/2 = 4.0
        if results[0]['average_rating'] == 4.0:
            print_pass("Average rating calculation correct (4.0)")
        else:
            print_fail(f"Incorrect average rating: {results[0]['average_rating']}")
    else:
        print_fail(f"Search failed or empty: {resp.text}")

    # Min rating filter
    resp = requests.get(f"{BASE_URL}/places/search/?min_rating=4.5", headers=headers)
    # Should not find it (rating is 4.0)
    found = any(r['name'] == place_name for r in resp.json())
    if not found:
        print_pass("Min rating filter excluded lower rated place")
    else:
        print_fail("Min rating filter failed (included lower rated place)")

    resp = requests.get(f"{BASE_URL}/places/search/?min_rating=3.5", headers=headers)
    found = any(r['name'] == place_name for r in resp.json())
    if found:
        print_pass("Min rating filter included higher rated place")
    else:
        print_fail("Min rating filter failed (excluded higher rated place)")

    # 6. Place Details & Ordering
    print("\n[6] Testing Place Details & Ordering")
    # Get ID of the place
    place_id = results[0]['id']
    
    # Request as User 2. User 2's review (3 stars) should be top. User 1's (5 stars) should be second.
    # Wait, "If the current user has left a review... that review must appear at the top... followed by all other reviews sorted by newest first."
    # User 2 just left the LAST review. So it would be newest anyway.
    # Let's add a OLDER review by User 3 to test "newest" sorting properly vs "my review".
    # But we can't easily backdate without direct DB access. 
    # Logic: User 1 posted first. User 2 posted second.
    # If User 1 views: User 1's review (oldest) should be first. Then User 2's.
    # If User 2 views: User 2's review (newest) should be first. Then User 1's.
    
    # View as User 1
    resp = requests.get(f"{BASE_URL}/places/{place_id}/", headers=headers)
    details = resp.json()
    reviews = details['reviews']
    if reviews[0]['user_name'] == user_name:
        print_pass("User 1 saw their review at the top")
    else:
        print_fail(f"User 1 did NOT see their review at top. First was: {reviews[0]['user_name']}")

    # View as User 2
    resp = requests.get(f"{BASE_URL}/places/{place_id}/", headers=headers2)
    details = resp.json()
    reviews = details['reviews']
    if reviews[0]['user_name'] == "User 2":
        print_pass("User 2 saw their review at the top")
    else:
        print_fail(f"User 2 did NOT see their review at top. First was: {reviews[0]['user_name']}")

    print("\nAll Tests Passed! 🚀")

if __name__ == "__main__":
    verify_assignment()
