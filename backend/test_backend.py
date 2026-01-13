import requests
import time
import sys

def test_api():
    base_url = "http://127.0.0.1:5000/api"
    retries = 10
    
    print("Waiting for server...")
    for i in range(retries):
        try:
            r = requests.get(f"{base_url}/status")
            if r.status_code == 200:
                print("Server is UP!")
                print(f"Status: {r.json()}")
                break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            if i == retries - 1:
                print("Server failed to start.")
                sys.exit(1)

    print("\nTesting /api/latest...")
    try:
        r = requests.get(f"{base_url}/latest")
        if r.status_code == 200:
            print(f"Latest: {r.json()}")
        else:
            print(f"Latest Failed: {r.status_code} {r.text}")
    except Exception as e:
        print(f"Latest Exception: {e}")

    print("\nTesting /api/history...")
    try:
        r = requests.get(f"{base_url}/history?limit=5")
        if r.status_code == 200:
            data = r.json()
            print(f"History Total: {data.get('total')}")
            print(f"History Data (First item): {data['data'][0] if data['data'] else 'No Data'}")
        else:
            print(f"History Failed: {r.status_code}")
    except Exception as e:
        print(f"History Exception: {e}")

    print("\nTesting /api/prediction...")
    try:
        r = requests.get(f"{base_url}/prediction")
        if r.status_code == 200:
            print(f"Prediction: {r.json()}")
        else:
            print(f"Prediction Failed: {r.status_code} {r.text}")
    except Exception as e:
        print(f"Prediction Exception: {e}")

if __name__ == "__main__":
    test_api()
