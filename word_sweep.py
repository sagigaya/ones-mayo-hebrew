"""
Third pass: word/phrase level sweep for Spanish fragments that survived.
These are shorter spans inside paragraphs that got split by HTML tags.
"""
import os, re
from pathlib import Path

ROOT = Path.home() / "Desktop" / "ones-mayo-hebrew"

# Longest first for correct matching
WORD_TRANS = sorted([
    # Mid-paragraph Spanish fragments that commonly appear
    ("En el año 2018, después de 40 años de dedicación y con un gran proyecto de expansión, se constituye",
     "בשנת 2018, לאחר 40 שנה של מסירות ועם פרויקט התרחבות משמעותי, הוקמה"),
    ("Alimentaria dando un salto de calidad importante y añadiendo una amplia oferta de productos a nuestro catálogo gracias a las",
     "Alimentaria, עם קפיצת איכות משמעותית, המוסיפה היצע רחב של מוצרים לקטלוג שלנו הודות ל-"),
    ("Somos una de las unidades productivas de",
     "אנחנו אחת מיחידות הייצור של"),
    ("español con origen en Valencia, compite con grandes actores del mercado internacional con productos alimentarios de gran consumo como son las",
     "ספרדי במקור מוולנסיה, מתחרה בשחקנים הגדולים של השוק הבינלאומי עם מוצרי מזון לצריכה המונית כמו"),
    ("son responsables tanto en el proceso de fabricación como en todo su ciclo de vida. Las mercancías están en continuo movimiento y fabricamos bajo pedido siguiendo un",
     "אחראיים הן בתהליך הייצור והן לאורך כל מחזור החיים. הסחורות בתנועה מתמדת ואנחנו מייצרים לפי הזמנה במודל של"),
    ("través de la transparencia, la honestidad y la confianza que trasladamos y hace que nuestros clientes lleven años colaborando con",
     "באמצעות שקיפות, כנות ואמון שאנחנו משדרים — הלקוחות שלנו משתפים איתנו פעולה כבר שנים"),
    ("sí, pero cada miembro del equipo es mucho más que una parte del engranaje",
     "כן, אבל כל חבר צוות הוא הרבה יותר מגלגל במכונה"),
    ("las empresas como Onesmay, parte del grupo",
     "חברות כמו Onesmay, חלק מקבוצת"),
    ("creemos en que somos la suma del capital intelectual de nuestro equipo y que solo así podemos lograr nuestros",
     "מאמינות שאנחנו סכום של ההון האינטלקטואלי של הצוות שלנו, ורק כך נוכל להשיג את יעדינו"),
    ("Alimentaria centralizamos las ofertas de empleo en la web principal del grupo, si quieres optar a un puesto o enviarnos tu curriculum haz click en el botón y enví",
     "Alimentaria מרכזים את הצעות העבודה באתר הראשי של הקבוצה. אם אתם מעוניינים במשרה או רוצים לשלוח קורות חיים — לחצו על הכפתור ושלחו"),

    # Common partial sentences
    ("Onesmay Skip to main content Close Search Menu",
     "Onesmay · דלגו לתוכן · סגור · חיפוש · תפריט"),
    ("Skip to main content", "דלגו לתוכן"),
    ("Close Search", "סגור חיפוש"),
    ("Close Menu", "סגור תפריט"),
    ("Menu", "תפריט"),
    ("Search", "חיפוש"),
    ("Comments", "תגובות"),

    # Shorter mid-paragraph fragments (from channels pages)
    ("Flexibilidad y adaptación", "גמישות והתאמה"),
    ("Nos adaptamos a ti", "אנחנו מתאימים את עצמנו אליך"),
    ("con el trato cercano y exclusivo que caracteriza a todas las unidades productivas del grupo GA Alimentaria",
     "עם היחס הקרוב והבלעדי המאפיין את כל יחידות הייצור של קבוצת GA Alimentaria"),
    ("GA Alimentaria", "GA Alimentaria"),  # keep as-is (brand)
    ("Grupo GA Alimentaria", "קבוצת GA Alimentaria"),

    # Legal page phrases (less critical but still)
    ("Política de Privacidad y Protección de Datos", "מדיניות פרטיות והגנה על מידע"),
    ("Política de Cookies", "מדיניות עוגיות"),
    ("Aviso Legal", "תנאי שימוש"),
    ("Términos y Condiciones", "תנאים והגבלות"),
    ("Acepto", "מאשר"),
    ("Rechazar", "דחייה"),
    ("Guardar preferencias", "שמירת העדפות"),

    # Common tiny ones (CAREFUL: these can over-match; keep short list)
    ("más", "יותר"),
    ("años", "שנים"),
    ("año", "שנה"),
    ("además", "בנוסף"),
    ("también", "גם"),
    ("porque", "כי"),
    ("si quieres", "אם רוצים"),
    ("Siguiente", "הבא"),
    ("Anterior", "הקודם"),
    ("Enviar", "שלח"),
    ("Suscríbete", "הירשם"),

    # Months
    ("Enero", "ינואר"), ("Febrero", "פברואר"), ("Marzo", "מרץ"), ("Abril", "אפריל"),
    ("Mayo", "מאי"), ("Junio", "יוני"), ("Julio", "יולי"), ("Agosto", "אוגוסט"),
    ("Septiembre", "ספטמבר"), ("Octubre", "אוקטובר"), ("Noviembre", "נובמבר"), ("Diciembre", "דצמבר"),

    # Alt labels (for images / aria)
    ("Nos encanta ver crecer tu marca", "אנחנו אוהבים לראות את המותג שלכם גדל"),
    ("Innovación en salsas", "חדשנות ברטבים"),
    ("Experiencia", "ניסיון"),
    ("Innovación", "חדשנות"),
    ("Calidad", "איכות"),
    ("Sabores", "טעמים"),
    ("Sabor", "טעם"),

    # Button labels
    ("Más info", "מידע נוסף"),
    ("Ver más", "לפרטים נוספים"),
    ("Leer más", "קרא עוד"),
    ("Descargar", "הורדה"),
    ("Contactar", "לקשר"),

    # "Nuestras marcas"
    ("MOTO SALSAS", "MOTO רטבים"),
    ("MARCAS", "מותגים"),
], key=lambda x: -len(x[0]))

def process(path: Path):
    try:
        txt = path.read_text(encoding="utf-8")
    except: return False
    original = txt
    for es, he in WORD_TRANS:
        if es in txt:
            txt = txt.replace(es, he)
    if txt != original:
        path.write_text(txt, encoding="utf-8")
        return True
    return False

def main():
    htmls = sorted(ROOT.rglob("*.html"))
    print(f"Word-sweep over {len(htmls)} files...")
    n = 0
    for p in htmls:
        rel = str(p.relative_to(ROOT))
        if any(seg in rel for seg in ("wp-json", "feed", "oembed", "comments")):
            continue
        if process(p): n += 1
    print(f"\n✓ {n} files updated.")

if __name__ == "__main__":
    main()
