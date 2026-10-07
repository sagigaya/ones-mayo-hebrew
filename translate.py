"""
Translate all Spanish text in mirrored onesmay.com HTML files to Hebrew,
set dir=rtl, inject minimal RTL CSS override.

Strategy:
- Find/replace of textual Spanish → Hebrew (ordered longest-first to avoid partial matches).
- Preserve all HTML structure, CSS, JS, images, fonts, layout.
- Add <style> override for RTL body + font fallback stack with Heebo.
"""
import os, re, sys
from pathlib import Path

ROOT = Path.home() / "Desktop" / "ones-mayo-hebrew"

# ─── Translations, ordered by length (longest first) to prevent sub-match corruption ───
TRANS = [
    # Hero / home taglines
    ("En la salsa está el gusto", "בטעם של הרוטב"),
    ("Ven a descubrirlo", "בואו לגלות"),
    ("CREAMOS LAS MEJORES SALSAS", "אנחנו יוצרים את הרטבים הטובים ביותר"),
    ("Y PRODUCTOS TOTALMENTE PERSONALIZADOS PARA TI", "ומוצרים מותאמים אישית במלואם בשבילך"),
    ("TODOS LOS PRODUCTOS. TODOS LOS CANALES.", "כל המוצרים. כל הערוצים."),
    ("LA REVOLUCIÓN DE LAS SALSAS", "המהפכה של הרטבים"),
    ("Mucho más que salsas", "הרבה יותר מרטבים"),
    ("PRODUCTOS DE CALIDAD", "מוצרי איכות"),
    ("COMPROMISO DE CALIDAD", "מחויבות לאיכות"),
    ("CALIDAD GA ALIMENTARIA", "איכות GA Alimentaria"),
    ("CALIDAD GARANTIZADA", "איכות מובטחת"),
    ("CALIDAD INDUSTRIAL", "איכות תעשייתית"),
    ("RECETAS ÚNICAS", "מתכונים ייחודיים"),
    ("TODOS LOS FORMATOS", "כל הפורמטים"),
    ("NUESTROS CANALES", "הערוצים שלנו"),
    ("NUESTRAS RECETAS", "המתכונים שלנו"),
    ("NUESTRO CONTACTO", "יצירת קשר"),
    ("NUESTRAS MARCAS", "המותגים שלנו"),
    ("SOBRE ONESMAY", "אודות ONES"),
    ("ContactA\nCON ONESMAY", "צרו קשר\nעם ONES"),
    ("Contacta con ONESMAY", "צרו קשר עם ONES"),
    ("MÁS DE 40 AÑOS CREANDO", "למעלה מ-40 שנה של יצירה"),
    ("PARA GARANTIZAR RESULTADOS Y CONFIANZA", "להבטחת תוצאות ואמון"),
    ("No te conformes con una salsa estándar, creamos la que necesites",
     "אל תסתפק ברוטב סטנדרטי — אנחנו יוצרים את זה שאתה צריך"),

    # Product category names
    ("Bases de tomate", "בסיסי עגבנייה"),
    ("Base de tomate", "בסיס עגבנייה"),
    ("Otras salsas", "רטבים נוספים"),
    ("Otras Salsas", "רטבים נוספים"),
    ("Mayonesas", "מיונז"),
    ("Mayonesa", "מיונז"),
    ("Mostazas", "חרדל"),
    ("Mostaza", "חרדל"),
    ("TIPOS DE MAYONESAS", "סוגי מיונז"),
    ("TIPOS DE MOSTAZAS", "סוגי חרדל"),
    ("TIPOS DE SALSAS CON TOMATE", "סוגי רטבי עגבנייה"),
    ("MÁS TIPOS DE SALSAS", "עוד סוגי רטבים"),
    ("TIPOS Y FORMATOS DISPONIBLES", "סוגים ופורמטים זמינים"),
    ("FORMATOS DISPONIBLES", "פורמטים זמינים"),
    ("salsas", "רטבים"),

    # Mayo types
    ("MAYONESA ORIGINAL", "מיונז קלאסי"),
    ("MAYONESA CASERA", "מיונז ביתי"),
    ("MAYONESA AJONESA", "מיונז עם שום"),
    ("MAYONESA SUAVE", "מיונז עדין"),
    ("MAYONESA LIGERA", "מיונז קל"),

    # Tomato
    ("KETCHUP ORIGINAL", "קטשופ קלאסי"),
    ("SALSA BARBACOA", "רוטב ברביקיו"),
    ("SALSA BRAVA", "סלסה בראווה"),

    # Mustard
    ("MOSTAZA DIJÓN", "חרדל דיז׳ון"),
    ("MOSTAZA ANTIGUA", "חרדל גרגרים"),
    ("MOSTAZA CLÁSICA", "חרדל קלאסי"),

    # Formats
    ("MONODOSIS", "מנה בודדת"),
    ("TOPDOWN", "טופ-דאון"),
    ("CRISTAL", "קריסטל"),
    ("BOTELLA", "בקבוק"),
    ("GARRAFA", "ג׳ריקן"),
    ("CUBOS", "דלי"),
    ("TODOS LOS QUE NECESITES", "כל מה שתצטרך"),

    # "Your own" sections
    ("TU PROPIA MAYONESA", "המיונז שלך"),
    ("TU PROPIA MOSTAZA", "החרדל שלך"),
    ("TU PROPIA SALSA", "הרוטב שלך"),
    ("TU RECETA PERSONALIZADA", "המתכון המותאם שלך"),
    ("CREAMOS LOS PRODUCTOS QUE NECESITE TU MARCA",
     "אנחנו יוצרים את המוצרים שהמותג שלך צריך"),
    ("CREADA Y  PERSONALIZADA PARA TI", "נוצר ומותאם אישית בשבילך"),
    ("CREADA Y PERSONALIZADA PARA TI", "נוצר ומותאם אישית בשבילך"),
    ("CON BASE DE TOMATE PERSONALIZADA", "עם בסיס עגבנייה מותאם"),
    ("Crea tu marca", "צור את המותג שלך"),
    ("IDEAS", "רעיונות"),

    # Channels - top-level
    ("Llegamos a todos los canales", "מגיעים לכל הערוצים"),
    ("Creamos soluciones personalizadas, trabajadas y basadas en más de 60 años de experiencia con todos los canales.",
     "אנחנו יוצרים פתרונות מותאמים אישית, מעובדים ומבוססים על למעלה מ-60 שנות ניסיון עם כל הערוצים."),
    ("Canal horeca", "ערוץ HoReCa"),
    ("Canal industrial", "ערוץ תעשייתי"),
    ("Canal retail", "ערוץ קמעונאי"),
    ("Marca Privada", "מותג פרטי"),
    ("MARCA PRIVADA", "מותג פרטי"),
    ("Y A TU GUSTO", "לפי טעמך"),
    ("SALSAS RESPONSABLES", "רטבים אחראיים"),
    ("Adquirir nuestros productos supone reducir el impacto ambiental.",
     "רכישת המוצרים שלנו מפחיתה את ההשפעה הסביבתית."),

    # HoReCa page
    ("Distribución canal HORECA", "הפצה בערוץ HoReCa"),
    ("CANAL HORECA", "ערוץ HoReCa"),
    ("Flexibilidad y adaptación a cada cliente… lo tenemos todo",
     "גמישות והתאמה לכל לקוח — יש לנו הכל"),
    ("Flexibilidad y adaptación a cada cliente", "גמישות והתאמה לכל לקוח"),
    ("EXPERIENCIA EN HORECA", "ניסיון ב-HoReCa"),
    ("DE MÁS DE 50 AÑOS", "של למעלה מ-50 שנה"),
    ("Es muy fácil, dinos lo que necesitas y nosotros lo haremos para ti.",
     "זה פשוט — תגיד לנו מה אתה צריך ואנחנו נייצר בשבילך."),
    ("TODAS LAS SALSAS Y FORMATOS", "כל הרטבים והפורמטים"),
    ("SOLUCIONES DE HOY, SABORES Y TENDENCIAS DEL MAÑANA", "פתרונות היום, טעמים וטרנדים של מחר"),
    ("Nuestras marcas o tu marca propia", "המותגים שלנו או המותג שלך"),
    ("SOLUCIONES", "פתרונות"),
    ("FORMATOS", "פורמטים"),

    # Retail
    ("Distribución canal RETAIL", "הפצה בערוץ קמעונאי"),
    ("CANAL RETAIL", "ערוץ קמעונאי"),
    ("Tradición a la vanguardia de las nuevas tendencias", "מסורת בחזית הטרנדים החדשים"),
    ("EXPERTOS EN LLEGAR A TI", "מומחים להגיע אליך"),
    ("PORQUE SOMOS COMO TU", "כי אנחנו כמוך"),
    ("Mejoramos el presente mirando al futuro.", "אנחנו משפרים את ההווה במבט לעתיד."),
    ("Damos forma al sabor", "אנחנו נותנים צורה לטעם"),

    # Private label
    ("Distribución de tu MARCA PRIVADA", "הפצת המותג הפרטי שלך"),
    ("UN KNOW HOW DE MÁS DE 60 AÑOS", "Know-how של למעלה מ-60 שנה"),
    ("AL SERVICIO DEL SECTOR PRIVADO", "בשירות הסקטור הפרטי"),
    ("Disponemos de un amplio porfolio de formatos para que que crees tu propia marca",
     "יש לנו פורטפוליו רחב של פורמטים כדי שתוכל ליצור את המותג שלך"),
    ("Disponemos de un amplio porfolio de formatos para que crees tu propia marca",
     "יש לנו פורטפוליו רחב של פורמטים כדי שתוכל ליצור את המותג שלך"),
    ("Nuestra planta piloto y equipo de expertos a tu servicio.",
     "מפעל הפיילוט שלנו וצוות המומחים לשירותך."),
    ("Tu pides y nosotros le damos forma", "אתה מבקש, אנחנו נותנים צורה"),

    # Industrial
    ("Distribución de tu PROYECTO INDUSTRIAL", "הפצת הפרויקט התעשייתי שלך"),
    ("PROYECTO INDUSTRIAL", "פרויקט תעשייתי"),
    ("Soluciones a medida y cero problemas", "פתרונות מותאמים ללא בעיות"),
    ("COOPERAMOS CON EN EL SECTOR INDUSTRIAL", "משתפים פעולה עם הסקטור התעשייתי"),
    ("DESDE HACE MÁS DE 60 AÑOS", "מעל 60 שנה"),
    ("¿Cual es su necesidad? tenemos la solución perfecta.", "מה הצורך שלך? יש לנו את הפתרון המושלם."),
    ("¿Cúal es tu necesidad? tenemos la solución perfecta.", "מה הצורך שלך? יש לנו את הפתרון המושלם."),
    ("¿TE ASESORAMOS PARA TU MEJOR SOLUCIÓN?", "נייעץ לך לפתרון הטוב ביותר?"),
    ("Tecnología y Know how para hacer tu proyecto", "טכנולוגיה ו-Know-how לפרויקט שלך"),

    # Company / About
    ("Compromiso con la innovación y el sabor", "מחויבות לחדשנות ולטעם"),
    ("Nuestra historia", "ההיסטוריה שלנו"),
    ("SOMOS PARTE DE GRUPO GA ALIMENTARIA", "אנחנו חלק מקבוצת GA Alimentaria"),
    ("Y MOLAMOS MUCHO Y LO SABES", "ואתה יודע את זה"),
    ("EL CAMINO PARA SER DISRUPTIVOS EN EL MUNDO DE LAS SALSAS",
     "הדרך להיות פורצי דרך בעולם הרטבים"),
    ("INNOVACIÓN Y DESARROLLO", "חדשנות ופיתוח"),
    ("TU NEGOCIO, TU PRODUCTO", "העסק שלך, המוצר שלך"),
    ("Comprometidos", "מחויבים"),
    ("LOS VALORES DE ONESMAY", "הערכים של ONES"),
    ("SON LOS VALORES DE GA ALIMENTARIA", "הם הערכים של GA Alimentaria"),
    ("Sostenibilidad", "קיימות"),
    ("Liderazgo", "מנהיגות"),
    ("Integridad", "יושרה"),
    ("Colaboración", "שיתוף פעולה"),
    ("Vida saludable", "אורח חיים בריא"),
    ("Nutrición", "תזונה"),
    ("Seguridad", "בטיחות"),

    # Recipes
    ("Tenemos las mejores recetas para ti", "יש לנו את המתכונים הטובים ביותר בשבילך"),
    ("Nachos con guacamole", "נאצ׳וס עם גואקמולי"),
    ("Patatas Animal Style", "תפוחי אדמה בסטייל אנימל"),
    ("Tacos estilo Onesmay", "טאקו בסטייל Onesmay"),
    ("Tacos estilo onesmay", "טאקו בסטייל Onesmay"),

    # News
    ("Noticias Onesmay &amp; GA Alimentaria", "חדשות Onesmay ו-GA Alimentaria"),
    ("Noticias Onesmay & GA Alimentaria", "חדשות Onesmay ו-GA Alimentaria"),
    ("SECCIÓN EN PLENO DESARROLLO, PRONTO VERÁS NUESTRAS NOTICIAS",
     "המדור בפיתוח — בקרוב תראו את החדשות שלנו"),

    # Contact
    ("ESTAMOS AQUÍ", "אנחנו כאן"),
    ("DATOS DE CONTACTO", "פרטי התקשרות"),
    ("ESCRÍBENOS", "כתבו לנו"),
    ("Déjanos tus datos y tu consulta para cualquier de nuestros departamentos y nos pondremos en contacto contigo lo antes posible.",
     "השאירו פרטים ופנייה לכל אחת מהמחלקות שלנו, ונחזור אליכם בהקדם האפשרי."),
    ("Calle Seis Nº 33(poligono Industrial Picassent) PARC. A-B-4 12.\nPicassent, 46220. Valencia",
     "Calle Seis Nº 33 (Polígono Industrial Picassent) PARC. A-B-4 12\nPicassent 46220, Valencia, ספרד"),
    ("Picassent, 46220. Valencia", "Picassent 46220, ספרד"),

    # Navigation / menu
    ("Aviso Legal", "תנאי שימוש"),
    ("Política de Privacidad", "מדיניות פרטיות"),
    ("Política de cookies", "מדיניות עוגיות"),
    ("Compromiso", "ערכים"),
    ("Productos", "מוצרים"),
    ("Canales", "ערוצים"),
    ("Recetas", "מתכונים"),
    ("Noticias", "חדשות"),
    ("Contacto", "קשר"),
    ("Horeca", "HoReCa"),
    ("Retail", "קמעונאי"),
    ("Proyecto Industrial", "פרויקט תעשייתי"),
    ("Empresa", "חברה"),
    ("nosotros", "אודות"),
    ("trabaja con nosotros", "עבוד איתנו"),
    ("ABOUT", "אודות"),

    # Longer about-page paragraphs (verbatim)
    ("Los orígenes en la actividad se remontan al año 1960 con la creación de dos empresas familiares en Valencia dedicadas a la producción de productos para otras industrias del sector para la industria de la alimentación.",
     "המקורות של הפעילות חוזרים לשנת 1960, עם הקמתן של שתי חברות משפחתיות בוולנסיה שהתמחו בייצור מוצרים לתעשיות המזון."),
    ("Somos fabricantes de salsas, tus salsas, personalizadas para las principales cadenas y empresas del canal industrial, la alimentación profesional y el sector Horeca. Nos distinguimos en el mercado por ofrecer un producto único, con un trato cercano y personalizado, que aporta un",
     "אנחנו יצרני רטבים — הרטבים שלך, בהתאמה אישית לרשתות ולחברות המובילות בערוץ התעשייתי, במזון המקצועי ובסקטור ה-HoReCa. אנחנו בולטים בשוק בכך שאנחנו מציעים מוצר ייחודי, עם יחס קרוב ואישי, שמוסיף ערך."),
    ("Estamos orgullosos de saber y contar que nuestros productos destacan entre los profesionales y los consumidores finales en más de 60 países de todo el mundo.",
     "אנחנו גאים לדעת ולספר שהמוצרים שלנו בולטים בקרב המקצוענים והצרכנים הסופיים ביותר מ-60 מדינות ברחבי העולם."),

    # Country / lang hint
    ("es-ES", "he"),
    ("es_ES", "he_IL"),
]

# Pre-compile for speed
TRANS_SORTED = sorted(TRANS, key=lambda x: -len(x[0]))

RTL_CSS_OVERRIDE = """
<style id="hebrew-rtl-override">
  html, body { direction: rtl !important; }
  body, * { font-family: 'Heebo', 'Assistant', 'Montserrat', 'Lato', sans-serif !important; }
  .nectar-slider-wrap, .swiper-wrapper, .vc_row { direction: rtl; }
  /* keep latin for brand names */
  .brand, .logo, [data-latin], .no-rtl { direction: ltr; }
  /* small typographic tweaks for Hebrew legibility */
  h1, h2, h3, h4, h5, h6 { letter-spacing: 0 !important; font-weight: 700 !important; }
  p, li, a, span { letter-spacing: 0 !important; }
</style>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800;900&family=Assistant:wght@300;400;500;600;700;800&display=swap">
"""

def inject_rtl(html: str) -> str:
    # Set html dir=rtl, lang=he
    html = re.sub(r'<html([^>]*)>', lambda m: f'<html lang="he" dir="rtl"{strip_lang_dir(m.group(1))}>', html, count=1, flags=re.IGNORECASE)
    # Inject override CSS right before </head>
    if "hebrew-rtl-override" not in html and "</head>" in html:
        html = html.replace("</head>", RTL_CSS_OVERRIDE + "\n</head>", 1)
    return html

def strip_lang_dir(attrs: str) -> str:
    attrs = re.sub(r'\s*lang="[^"]*"', '', attrs)
    attrs = re.sub(r'\s*dir="[^"]*"', '', attrs)
    return attrs

def translate_file(path: Path):
    try:
        txt = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ✗ {path}: {e}")
        return 0
    original = txt
    # Apply translations (longest first)
    for es, he in TRANS_SORTED:
        if es in txt:
            txt = txt.replace(es, he)
    # Inject RTL + fonts
    txt = inject_rtl(txt)
    if txt != original:
        path.write_text(txt, encoding="utf-8")
        return 1
    return 0

def main():
    htmls = sorted(ROOT.rglob("*.html"))
    print(f"Processing {len(htmls)} HTML files...")
    changed = 0
    for p in htmls:
        # skip wp-json / feed / comment feed junk
        rel = str(p.relative_to(ROOT))
        if any(seg in rel for seg in ("wp-json", "feed", "comments", "oembed")):
            continue
        if translate_file(p):
            changed += 1
    print(f"\n✓ {changed} files updated.")

if __name__ == "__main__":
    main()
