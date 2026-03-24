import requests
from bs4 import BeautifulSoup


def internshala_scraper(skill):
    skill_normalized = str(skill).lower().strip().replace(" ", "-")
    if not skill_normalized:
        return []

    url = f"https://internshala.com/internships/{skill_normalized}-internship/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/116.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    response = requests.get(url, headers=headers, timeout=15)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    data = []

    cards = soup.find_all("div", class_="individual_internship")

    for card in cards:
        try:
            title_tag = card.find("h3")
            title = title_tag.get_text(strip=True) if title_tag else "N/A"

            company_tag = card.find("p", class_="company-name") or card.find("h4")
            company = company_tag.get_text(strip=True) if company_tag else "N/A"

            location_tag = (
                card.find("div", class_="locations")
                or card.find("div", class_="row-1-item locations")
                or card.find("a", class_="location_link")
            )
            location = location_tag.get_text(separator=" ", strip=True) if location_tag else "N/A"


            apply_href = card.get("data-href") or card.find("a", class_="job-title-href") and card.find("a", class_="job-title-href").get("href")
            if apply_href and apply_href.startswith("/"):
                apply_href = "https://internshala.com" + apply_href

            data.append({
                "title": title,
                "company": company,
                "location": location,
                "skills_required": skill_normalized,
                "apply_link": apply_href or "#",
                "source": "Internshala",
            })
        except Exception:
            continue

    return data


def remoteok_scraper(skill):
    if not skill or not str(skill).strip():
        return []

    skill_lower = str(skill).strip().lower()

    url = "https://remoteok.com/api"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/116.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "application/json",
        "Referer": "https://remoteok.com/",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return []

        jobs = response.json()
        if not isinstance(jobs, list):
            return []

    except Exception:
        return []

    data = []
    for job in jobs:
        if not isinstance(job, dict):
            continue

        # skip the first metadata object if present
        if job.get("id") is None:
            continue

        tags = [t.lower() for t in job.get("tags", []) if isinstance(t, str)]
        position = str(job.get("position") or job.get("title") or "").strip()
        company = str(job.get("company") or "").strip()
        location = str(job.get("location") or job.get("geo") or "Remote").strip() or "Remote"

       
        if skill_lower not in position.lower() and skill_lower not in company.lower() and skill_lower not in " ".join(tags):
            continue

        apply_link = str(job.get("url") or job.get("link") or "").strip()
        if apply_link and apply_link.startswith("/"):
            apply_link = "https://remoteok.com" + apply_link

        data.append({
            "title": position or "N/A",
            "company": company or "N/A",
            "location": location or "Remote",
            "skills_required": skill_lower,
            "apply_link": apply_link or "#",
            "source": "RemoteOK",
        })

    # Fallback: if no items matched the exact skill, return first few internship API results
    if not data:
        fallback = []
        for job in jobs:
            if not isinstance(job, dict) or job.get("id") is None:
                continue

            position = str(job.get("position") or job.get("title") or "").strip()
            company = str(job.get("company") or "").strip()
            location = str(job.get("location") or job.get("geo") or "Remote").strip() or "Remote"
            apply_link = str(job.get("url") or job.get("link") or "").strip()
            if apply_link and apply_link.startswith("/"):
                apply_link = "https://remoteok.com" + apply_link

            fallback.append({
                "title": position or "N/A",
                "company": company or "N/A",
                "location": location or "Remote",
                "skills_required": skill_lower,
                "apply_link": apply_link or "#",
                "source": "RemoteOK",
            })
            if len(fallback) >= 10:
                break

        return fallback

    return data



def get_all_internships(skill):
    if not skill or not str(skill).strip():
        return []

    all_data = []

    try:
        data1 = internshala_scraper(skill)
        print("Internshala:", len(data1))
        all_data.extend(data1)
    except Exception as e:
        print("Internshala error:", e)

    try:
        data2 = remoteok_scraper(skill)
        print("remote:", len(data2))
        all_data.extend(data2)
    except Exception as e:
        print("remote error:", e)

    return all_data