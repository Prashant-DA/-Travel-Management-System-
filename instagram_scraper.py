#!/usr/bin/env python3
"""
100% FREE Instagram Verified Creator Scraper
No subscriptions, no API keys, no paid tools
"""

import instaloader
import pandas as pd
import sqlite3
import time
import re
import random
from datetime import datetime

print("=" * 60)
print("🚀 FREE Instagram Verified Creator Scraper")
print("=" * 60)

# ⚠️ CHANGE THESE SETTINGS
USERNAME = "your_instagram_username"  # Your Instagram login
PASSWORD = "your_instagram_password"  # Your Instagram password

KEYWORDS = [
    "fitness",
    "vegan",
    "wellness",
    "yoga",
    "nutrition",
]

MAX_PROFILES_PER_KEYWORD = 500  # Adjust as needed

# Initialize Instaloader (free, no API key needed)
L = instaloader.Instaloader(
    download_pictures=False,
    download_videos=False,
    download_comments=False,
    save_metadata=False,
    compress_json=False,
)

# Initialize SQLite database for deduplication (free, local)
conn = sqlite3.connect("instagram_leads.db")
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS profiles (
        username TEXT PRIMARY KEY,
        full_name TEXT,
        bio TEXT,
        followers INTEGER,
        is_verified INTEGER,
        email TEXT,
        website TEXT,
        profile_url TEXT,
        scraped_at TEXT,
        keyword TEXT
    )
"""
)
conn.commit()

print("✅ Database initialized")

# Login to Instagram
print(f"🔐 Logging in as {USERNAME}...")
try:
    L.login(USERNAME, PASSWORD)
    print("✅ Login successful\n")
    time.sleep(10)  # Wait after login
except Exception as e:
    print(f"❌ Login failed: {e}")
    print("💡 Tips:")
    print("   - Check username/password are correct")
    print("   - Use a dedicated Instagram account (not personal)")
    print("   - Complete CAPTCHA in browser first if needed")
    exit(1)

# Storage for all profiles
all_profiles = []
total_verified = 0

# Scrape each keyword
for i, keyword in enumerate(KEYWORDS):
    print(f"📊 Keyword {i+1}/{len(KEYWORDS)}: #{keyword}")
    print("-" * 60)

    keyword_verified = 0

    try:
        hashtag = instaloader.Hashtag.from_name(L.context, keyword)

        for post in hashtag.get_posts():
            if keyword_verified >= MAX_PROFILES_PER_KEYWORD:
                break

            try:
                profile = post.owner_profile

                # Skip if not verified
                if not profile.is_verified:
                    continue

                # Check if already in database
                cursor.execute(
                    "SELECT username FROM profiles WHERE username = ?",
                    (profile.username,),
                )
                if cursor.fetchone():
                    print(f"⏭️  Skipping duplicate: {profile.username}")
                    continue

                # Extract email from bio
                email = None
                if profile.biography:
                    email_match = re.search(
                        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                        profile.biography,
                    )
                    if email_match:
                        email = email_match.group(0)

                # Build profile data
                profile_data = {
                    "username": profile.username,
                    "full_name": profile.full_name,
                    "bio": profile.biography[:500] if profile.biography else "",
                    "followers": profile.followers,
                    "is_verified": 1,
                    "email": email,
                    "website": profile.external_url,
                    "profile_url": f"https://instagram.com/{profile.username}",
                    "scraped_at": datetime.now().isoformat(),
                    "keyword": keyword,
                }

                # Save to database
                cursor.execute(
                    """
                    INSERT INTO profiles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        profile_data["username"],
                        profile_data["full_name"],
                        profile_data["bio"],
                        profile_data["followers"],
                        profile_data["is_verified"],
                        profile_data["email"],
                        profile_data["website"],
                        profile_data["profile_url"],
                        profile_data["scraped_at"],
                        profile_data["keyword"],
                    ),
                )
                conn.commit()

                all_profiles.append(profile_data)
                keyword_verified += 1
                total_verified += 1

                print(f"✅ @{profile.username} ({profile.followers:,} followers)")

                # Rate limiting (important to avoid bans)
                time.sleep(random.uniform(3, 6))

            except Exception:
                continue

        print(f"\n✅ Completed #{keyword}: {keyword_verified} verified creators\n")

        # Wait between keywords (important!)
        if i < len(KEYWORDS) - 1:
            wait_time = random.uniform(90, 150)
            print(f"⏳ Waiting {wait_time:.0f}s before next keyword...\n")
            time.sleep(wait_time)

    except Exception as e:
        print(f"❌ Error scraping #{keyword}: {e}\n")

# Export to CSV (free, no Google Sheets needed)
output_file = f"verified_creators_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

df = pd.DataFrame(all_profiles)
df.to_csv(output_file, index=False)

# Get statistics
cursor.execute("SELECT COUNT(*) FROM profiles")
total_in_db = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM profiles WHERE email IS NOT NULL")
with_email = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM profiles WHERE website IS NOT NULL")
with_website = cursor.fetchone()[0]

conn.close()

# Print final results
print("=" * 60)
print("📊 FINAL RESULTS")
print("=" * 60)
print(f"✅ Total verified creators found: {total_verified}")
print(f"✅ Total in database (all time): {total_in_db}")
print(f"✅ With email: {with_email}")
print(f"✅ With website: {with_website}")
print(
    f"✅ Contact rate: {(with_email / total_in_db * 100):.1f}%"
    if total_in_db > 0
    else "0%"
)
print(f"\n📁 Saved to: {output_file}")
print("=" * 60)
