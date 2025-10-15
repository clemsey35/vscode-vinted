import aiohttp
from bs4 import BeautifulSoup

async def get_latest_vinted_items(brand_name):
    # On récupère le flux RSS de Vinted pour la marque donnée
    url = f"https://www.vinted.fr/vetements?search_text={brand_name}&order=newest_first&format=rss"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"⚠️ Erreur HTTP {resp.status} pour {brand_name}")
                return []
            xml = await resp.text()

    soup = BeautifulSoup(xml, "xml")
    items = []
    for item in soup.find_all("item")[:5]:  # On prend les 5 plus récentes
        title = item.title.text
        link = item.link.text
        desc = item.description.text

        # Petits nettoyages de texte
        desc = desc.replace("<br>", "\n").replace("&nbsp;", " ").strip()

        items.append({
            "title": title,
            "link": link,
            "description": desc,
            "photos": [],  # Les flux RSS ne contiennent pas toujours d’images
        })
    return items
