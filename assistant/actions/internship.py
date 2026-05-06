"""
MAZE — Internship Finder (Internshala Scraper)
Scrapes Internshala for internship listings by keyword.
Voice: "find internship cybersecurity" or "search internship python remote"
Telegram: /internship <keyword>
"""

import urllib.parse
from assistant.actions.helpers import contains_any, extract_after


def find_internships(keyword: str = "cybersecurity", remote: bool = False) -> list:
    """Scrape Internshala for internship listings.
    Returns a list of dicts: [{title, company, stipend, location, link}, ...]"""
    try:
        import requests
        from bs4 import BeautifulSoup

        # Build URL
        slug = keyword.lower().strip().replace(" ", "-")
        if remote:
            url = f"https://internshala.com/internships/work-from-home-{slug}-internships"
        else:
            url = f"https://internshala.com/internships/{slug}-internship"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

        page = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(page.content, "html.parser")

        results = []

        # Internshala listing structure
        internships = soup.find_all("div", class_="individual_internship")
        if not internships:
            # Try alternate selector
            internships = soup.find_all("div", {"class": lambda c: c and "internship_meta" in c})

        for job in internships[:5]:
            try:
                # Title
                title_tag = job.find("h3", class_="heading_4_5") or job.find("a", class_="job-title-href") or job.find("h3")
                title = title_tag.text.strip() if title_tag else "Unknown Role"

                # Company
                company_tag = job.find("h4", class_="heading_6") or job.find("p", class_="company-name") or job.find("h4")
                company = company_tag.text.strip() if company_tag else "Unknown Company"

                # Stipend
                stipend_tag = job.find("span", class_="stipend") or job.find("span", {"class": lambda c: c and "stipend" in str(c)})
                stipend = stipend_tag.text.strip() if stipend_tag else "Not specified"

                # Location
                loc_tag = job.find("a", class_="location_link") or job.find("span", {"id": lambda i: i and "location" in str(i)})
                location = loc_tag.text.strip() if loc_tag else ("Remote" if remote else "See listing")

                # Link
                link_tag = job.find("a", class_="view_detail_button") or job.find("a", href=True)
                if link_tag and link_tag.get("href"):
                    href = link_tag["href"]
                    if not href.startswith("http"):
                        href = f"https://internshala.com{href}"
                    link = href
                else:
                    link = url

                results.append({
                    "title": title,
                    "company": company,
                    "stipend": stipend,
                    "location": location,
                    "link": link,
                })
            except Exception:
                continue

        return results

    except ImportError:
        return [{"error": "Missing dependencies. Run: pip install requests beautifulsoup4"}]
    except Exception as e:
        return [{"error": f"Scraping failed: {str(e)[:100]}"}]


def format_internships(results: list) -> str:
    """Format internship results as a readable string (for voice/text output)."""
    if not results:
        return "I couldn't find any internships for that keyword. Try a different search term."

    if "error" in results[0]:
        return results[0]["error"]

    output = f"Found {len(results)} internships:\n\n"
    for i, r in enumerate(results, 1):
        output += f"{i}. {r['title']} at {r['company']}\n"
        output += f"   💰 Stipend: {r['stipend']}\n"
        output += f"   📍 Location: {r['location']}\n"
        output += f"   🔗 {r['link']}\n\n"
    return output.strip()


def format_internships_telegram(results: list) -> str:
    """Format internship results for Telegram (with clickable links)."""
    if not results:
        return "❌ No internships found. Try a different keyword."

    if "error" in results[0]:
        return f"⚠️ {results[0]['error']}"

    lines = [f"🔍 Found {len(results)} internships:\n"]
    for i, r in enumerate(results, 1):
        lines.append(
            f"**{i}. {r['title']}**\n"
            f"🏢 {r['company']}\n"
            f"💰 {r['stipend']}\n"
            f"📍 {r['location']}\n"
            f"[Apply Here]({r['link']})\n"
        )
    return "\n".join(lines)


def format_internships_voice(results: list) -> str:
    """Format internship results for voice output (concise)."""
    if not results:
        return "I couldn't find any internships for that keyword. Try a different search term."

    if "error" in results[0]:
        return results[0]["error"]

    parts = [f"I found {len(results)} internships."]
    for i, r in enumerate(results, 1):
        parts.append(f"Number {i}: {r['title']} at {r['company']}, stipend {r['stipend']}.")
    return " ".join(parts)


def handle_internship(command: str) -> str:
    """Handle internship search commands.
    Voice: 'find internship cybersecurity' or 'search internship python remote'"""

    # Check if this is an internship command
    if not contains_any(command, ["internship", "intern"]):
        return None

    # Don't trigger for "open internshala" (website open handled elsewhere)
    if contains_any(command, ["open internshala", "launch internshala"]):
        return None

    # Extract keyword
    keyword = command
    for remove in ["find", "search", "get", "show", "look", "for", "me",
                    "internship", "internships", "intern", "interns",
                    "on", "internshala", "please", "can you", "could you"]:
        keyword = keyword.replace(remove, " ")
    keyword = " ".join(keyword.split()).strip()

    # Check for "remote"
    remote = False
    if "remote" in keyword or "work from home" in command:
        remote = True
        keyword = keyword.replace("remote", "").replace("work from home", "").strip()

    if not keyword:
        keyword = "python"  # Default keyword

    print(f"   🔍 Searching internships for: {keyword} {'(remote)' if remote else ''}")
    results = find_internships(keyword, remote=remote)
    return format_internships_voice(results)
