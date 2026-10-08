
import os
import requests
import pandas as pd

API_KEY = "AIzaSyCvRPYrZWJKJCAH5mLxyj1XeC_dcsb4LQw"

URL = "https://places.googleapis.com/v1/places:searchText"

FIELDS = [
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.nationalPhoneNumber",
    "places.websiteUri",
    "places.rating",
    "places.userRatingCount",
    "places.location",
    "places.googleMapsUri",
    "nextPageToken"
]

headers = {
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": ",".join(FIELDS),
    "Content-Type": "application/json"
}

query = input("Enter business and location: ").strip()

if not query:
    raise ValueError("Search query cannot be empty")

rows = []
page_token = None

while True:
    payload = {
        "textQuery": query,
        "pageSize": 20
    }

    if page_token:
        payload["pageToken"] = page_token

    response = requests.post(
        URL, json=payload, headers=headers, timeout=30
    )
    response.raise_for_status()

    data = response.json()

    for place in data.get("places", []):
        location = place.get("location", {})

        rows.append({
            "Place ID": place.get("id"),
            "Name": place.get("displayName", {}).get("text"),
            "Address": place.get("formattedAddress"),
            "Phone": place.get("nationalPhoneNumber"),
            "Website": place.get("websiteUri"),
            "Rating": place.get("rating"),
            "Review Count": place.get("userRatingCount"),
            "Latitude": location.get("latitude"),
            "Longitude": location.get("longitude"),
            "Google Maps": place.get("googleMapsUri")
        })

    page_token = data.get("nextPageToken")
    if not page_token:
        break

df = pd.DataFrame(rows)

if not df.empty:
    df = df.drop_duplicates(subset=["Place ID"])
    df = df.sort_values("Review Count", ascending=False)

df.to_csv("stores.csv", index=False, encoding="utf-8-sig")
df.to_excel("stores.xlsx", index=False)

print(f"Found {len(df)} stores")
print("Export complete")
