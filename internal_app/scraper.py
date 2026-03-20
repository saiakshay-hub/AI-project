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


def indeed_scraper(skill):
    skill_query = skill.replace(" ", "+")
    url = f"https://in.indeed.com/jobs?q={skill_query}+internship"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    data = []

    jobs = soup.find_all("a", attrs={"data-hide-spinner": "true"})

    print("Indeed jobs found:", len(jobs))  # DEBUG

    for job in jobs:
        try:
            title = job.find("span").text.strip() if job.find("span") else "N/A"

            company_tag = job.find_next("span", class_="companyName")
            company = company_tag.text.strip() if company_tag else "N/A"

            location_tag = job.find_next("div", class_="companyLocation")
            location = location_tag.text.strip() if location_tag else "N/A"

            link = "https://in.indeed.com" + job["href"]

            data.append({
                "title": title,
                "company": company,
                "location": location,
                "skills_required": skill,
                "apply_link": link,
                "source": "Indeed"
            })

        except Exception as e:
            print("Indeed error:", e)
            continue

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
        data2 = indeed_scraper(skill)
        print("Indeed:", len(data2))
        all_data.extend(data2)
    except Exception as e:
        print("Indeed error:", e)

    return all_data