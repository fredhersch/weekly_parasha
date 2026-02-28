# tools/sepharia_tools.py
from agno.tools import tool
import datetime
import hdate

PARSHA_MAP = {
    "בראשית": "Bereishit", "נח": "Noach", "לך לך": "Lech Lecha",
    "וירא": "Vayera", "חיי שרה": "Chayei Sarah", "תולדות": "Toldot",
    "ויצא": "Vayetzei", "וישלח": "Vayishlach", "וישב": "Vayeshev",
    "מקץ": "Miketz", "ויגש": "Vayigash", "ויחי": "Vayechi",
    "שמות": "Shemot", "וארא": "Vaera", "בא": "Bo",
    "בשלח": "Beshalach", "יתרו": "Yitro", "משפטים": "Mishpatim",
    "תרומה": "Terumah", "תצוה": "Tetzaveh", "כי תשא": "Ki Tisa",
    "ויקהל": "Vayakhel", "פקודי": "Pekudei", "ויקרא": "Vayikra",
    "צו": "Tzav", "שמיני": "Shemini", "תזריע": "Tazria",
    "מצורע": "Metzora", "אחרי מות": "Acharei Mot", "קדושים": "Kedoshim",
    "אמור": "Emor", "בהר": "Behar", "בחוקותי": "Bechukotai",
    "במדבר": "Bamidbar", "נשא": "Naso", "בהעלותך": "Beha'alotcha",
    "שלח": "Shelach", "קרח": "Korach", "חקת": "Chukat",
    "בלק": "Balak", "פינחס": "Pinchas", "מטות": "Matot",
    "מסעי": "Masei", "דברים": "Devarim", "ואתחנן": "Vaetchanan",
    "עקב": "Eikev", "ראה": "Re'eh", "שופטים": "Shoftim",
    "כי תצא": "Ki Teitzei", "כי תבוא": "Ki Tavo", "נצבים": "Nitzavim",
    "וילך": "Vayeilech", "האזינו": "Haazinu", "וזאת הברכה": "Vezot Habracha"
}

@tool
def get_parsha_info() -> dict:
    """Returns the current week's parsha name for study."""
    today = datetime.date.today()
    h = hdate.HDateInfo(today)
    hebrew_name = str(h.parasha).strip()
    english_name = PARSHA_MAP.get(hebrew_name, hebrew_name)

    return {
        "parsha": english_name,
        "hebrew": hebrew_name,
        "date": str(today),
        "description": f"This week's Torah portion is {english_name} ({hebrew_name}). Use your knowledge of the text, Rashi, Ramban, and other commentaries to analyze it."
    }