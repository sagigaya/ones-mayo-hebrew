"""
Mega-sweep: catch all remaining hybrid Spanish/Hebrew paragraphs.
Each entry targets the EXACT current state of the HTML (with partial Hebrew already injected).
"""
import re
from pathlib import Path

ROOT = Path.home() / "Desktop" / "ones-mayo-hebrew"

MEGA = sorted([
    # ─── Base-tomate (ketchup, barbacoa, brava…) ───
    ("Ketchup, Barbacoa, Brava... las mejores רטבים con base de tomate elaboradas con una selección de productos de la huerta, frescos y llenos de nutrientes para",
     "קטשופ, ברביקיו, סלסה בראווה — הרטבים הטובים ביותר על בסיס עגבנייה, מיוצרים מתוצרת גן קפדנית — טרייה ומלאה ברכיבים תזונתיים — כדי"),
    ("Ketchup, Barbacoa, Brava... las mejores רטבים con base de tomate",
     "קטשופ, ברביקיו, סלסה בראווה — הרטבים הטובים ביותר על בסיס עגבנייה"),
    ("Ketchup, Barbacoa, Brava",
     "קטשופ, ברביקיו, סלסה בראווה"),
    ("las mejores רטבים con base de tomate elaboradas con una selección de productos de la huerta, frescos y llenos de nutrientes para conseguir un producto de sabor inigualable que hará que tus platos y recetas brillen todavía יותר.",
     "הרטבים הטובים ביותר על בסיס עגבנייה, מיוצרים מתוצרת גן קפדנית — טרייה ומלאה ברכיבים תזונתיים — ליצירת מוצר בטעם ללא תחרות שיאיר את המנות והמתכונים שלך עוד יותר."),
    ("las mejores רטבים con base de tomate elaboradas con una selección de productos de la huerta, frescos y llenos de nutrientes para",
     "הרטבים הטובים ביותר על בסיס עגבנייה, מיוצרים מתוצרת גן קפדנית — טרייה ומלאה ברכיבים תזונתיים — כדי"),
    ("las mejores רטבים con base de tomate", "הרטבים הטובים ביותר על בסיס עגבנייה"),
    ("elaboradas con una selección de productos de la huerta, frescos y llenos de nutrientes para conseguir un producto de sabor inigualable que hará que tus platos y recetas brillen todavía יותר",
     "מיוצרים מתוצרת גן קפדנית — טרייה ומלאה ברכיבים תזונתיים — ליצירת מוצר בטעם ללא תחרות שיאיר את המנות והמתכונים שלך עוד יותר"),

    # ─── Base-tomate: TIPOS DE SALSAS CON TOMATE paragraph ───
    ("TIPOS DE SALSAS CON TOMATE El auténtico placer está en el sabor, el sabor de nuestras רטבים con base de tomate, elaboradas con concentrado de tomates de calidad extra cultivados en nuestras huertas",
     "סוגי רטבי עגבנייה · העונג האמיתי נמצא בטעם — טעם רטבי העגבנייה שלנו, מיוצרים מרסק עגבניות באיכות עליונה שגדל בגינות שלנו"),
    ("El auténtico placer está en el sabor, el sabor de nuestras רטבים con base de tomate, elaboradas con concentrado de tomates de calidad extra cultivados en nuestras huertas",
     "העונג האמיתי נמצא בטעם — טעם רטבי העגבנייה שלנו, מיוצרים מרסק עגבניות באיכות עליונה שגדל בגינות שלנו"),
    ("El auténtico placer está en el sabor, el sabor de nuestras",
     "העונג האמיתי נמצא בטעם — טעם ה"),
    ("con base de tomate, elaboradas con concentrado de tomates de calidad extra cultivados en nuestras huertas",
     "על בסיס עגבנייה, מיוצרים מרסק עגבניות באיכות עליונה שגדל בגינות שלנו"),
    ("Perfectas en hamburguesas, patatas, perritos, bocatas, pasta, carnes… ¡dónde tú quieras!",
     "מושלמים להמבורגרים, תפוחי אדמה, נקניקיות, כריכים, פסטה, בשרים — איפה שתרצה!"),

    # ─── Base-tomate: product descriptions ───
    ("1 Procedente de plantaciones de tomate seleccionadas y un color rojo que lo hace inconfundible",
     "קטשופ קלאסי · ממטעי עגבנייה נבחרים בצבע אדום בלתי משתווה"),
    ("Procedente de plantaciones de tomate seleccionadas y un color rojo que lo hace inconfundible",
     "ממטעי עגבנייה נבחרים בצבע אדום בלתי משתווה"),
    ("Sin colorantes artificiales ni demasiada sal y poco azucar para que disfrutes plenamente del auténtico sabor del ketchup americano",
     "ללא צבעי מאכל מלאכותיים, מעט מלח ומעט סוכר — כדי שתוכל ליהנות באמת מהטעם האותנטי של הקטשופ האמריקאי"),
    ("Sin colorantes artificiales ni demasiada sal y poco azúcar para que disfrutes plenamente del auténtico sabor del ketchup americano",
     "ללא צבעי מאכל מלאכותיים, מעט מלח ומעט סוכר — כדי שתוכל ליהנות באמת מהטעם האותנטי של הקטשופ האמריקאי"),

    # ─── Mayonesa: list of mayo types + "ligera" ───
    ("MAYONESA ORIGINAL MAYONESA CASERA MAYONESA AJONESA MAYONESA SUAVE MAYONESA LIGERA TU RECETA PERSONALIZADA TIPOS DE MAYONESAS Disponemos de recetas propias adaptadas y elaboradas para todos los gustos",
     "מיונז קלאסי · מיונז ביתי · מיונז עם שום · מיונז עדין · מיונז קל · המתכון המותאם שלך · סוגי מיונז · יש לנו מתכונים משלנו המותאמים ומעובדים לכל טעם"),
    ("2 Ligera, cremosa, con menos calorías pero con la misma textura que una mayonesa convencional siendo muy fácil de aplicar",
     "מיונז קל · קרמי, פחות קלוריות אבל אותה טקסטורה של מיונז רגיל — קל מאוד למריחה"),
    ("Ligera, cremosa, con menos calorías pero con la misma textura que una mayonesa convencional siendo muy fácil de aplicar",
     "קרמי, פחות קלוריות אבל אותה טקסטורה של מיונז רגיל — קל מאוד למריחה"),

    # ─── Otras salsas: types + descriptions ───
    ("MÁS TIPOS DE SALSAS Nuestras recetas adaptables, deliciosas, suaves y cremosas, elaborada 100% con huevos camperos e ingredientes de alta calidad que marcan la diferencia con cada cucharada",
     "עוד סוגי רטבים · המתכונים שלנו — ניתנים להתאמה, טעימים, רכים וקרמיים — מיוצרים 100% מביצי משק חופש ומרכיבים איכותיים שעושים את ההבדל בכל כפית"),
    ("Nuestras recetas adaptables, deliciosas, suaves y cremosas, elaborada 100% con huevos camperos e ingredientes de alta calidad que marcan la diferencia con cada cucharada",
     "המתכונים שלנו — ניתנים להתאמה, טעימים, רכים וקרמיים — מיוצרים 100% מביצי משק חופש ומרכיבים איכותיים שעושים את ההבדל בכל כפית"),
    ("Ofrece un aroma muy agradable y un sabor suave que combina estupendamente con carnes, pescados e incluso ensaladas",
     "מציעה ארומה נעימה וטעם רך שמשתלב מצוין עם בשרים, דגים ואפילו סלטים"),
    ("Para disfrutar sin duda con unas buenas patatas fritas pero esta deliciosa salsa גם es un buen complemento para ensaladas, pescados y mariscos, incorporando en cada plato un toque de sabor muy peculiar",
     "להנאה מובטחת עם צ'יפס טוב — אבל הרוטב הטעים הזה גם משלים נהדר לסלטים, דגים ופירות ים, מוסיף נגיעת טעם ייחודית לכל מנה"),
    ("Un sabor suave y refrescante que dará vida a muchos de tus platos",
     "טעם רך ומרענן שיעניק חיים למנות שלכם"),
    ("Suave, cremosa y ligera, una sabrosa salsa que dará un toque fresco a tus ensaladas, kebabs o como acompañamiento con verduras",
     "רכה, קרמית וקלה — רוטב טעים שיעניק נגיעה רעננה לסלטים, קבבים או כליווי לירקות"),

    # ─── HoReCa paragraph ───
    ("Selección de productos pensados para facilitar la labor de los profesionales del sector HoReCa, ofreciendo distintas preparaciones, soluciones y formatos de envases adaptados a las necesidades de su negocio con una garantía de calidad constante que cubre todas las necesidades de",
     "מבחר מוצרים שתוכננו להקל על עבודת אנשי המקצוע בסקטור ה-HoReCa — מציעים הכנות, פתרונות ופורמטי אריזה מותאמים לצרכי העסק, עם ערובת איכות קבועה שמכסה את כל הצרכים של"),
    ("ערוץ HoReCa Selección de productos pensados para facilitar la labor de los profesionales del sector HoReCa, ofreciendo distintas preparaciones, soluciones y formatos de envases adaptados a las necesidades de su negocio con una garantía de calidad constante que cubre todas las nec",
     "ערוץ HoReCa · מבחר מוצרים שתוכננו להקל על עבודת אנשי המקצוע בסקטור ה-HoReCa — מציעים הכנות, פתרונות ופורמטי אריזה מותאמים לצרכי העסק, עם ערובת איכות קבועה שמכסה את הצרכים"),

    # ─── Canales/index.html — Marca Privada card ───
    ("מותג פרטי Podemos ayudarte a resolver cualquier problema, a desarrollar una idea o a mejorar tu producto actual",
     "מותג פרטי · אנחנו יכולים לעזור לך לפתור כל בעיה, לפתח רעיון או לשפר את המוצר הנוכחי שלך"),
    ("Podemos ayudarte a resolver cualquier problema, a desarrollar una idea o a mejorar tu producto actual",
     "אנחנו יכולים לעזור לך לפתור כל בעיה, לפתח רעיון או לשפר את המוצר הנוכחי שלך"),

    # ─── Industrial — mixed sentence ───
    ("אנחנו מפתחים מוצרים מותאמים בהתאם לדרישות הספציפיות , condiciones y objetivos de producto que nos solicitan",
     "אנחנו מפתחים מוצרים מותאמים בהתאם לדרישות הספציפיות, לתנאים וליעדי המוצר שהוגשו לנו"),
    ("condiciones y objetivos de producto que nos solicitan",
     "לתנאים וליעדי המוצר שהוגשו לנו"),

    # ─── Recipes ───
    ("Mezcla en un bol el resto de ingredientes y mezcla bien",
     "ערבבו בקערה את שאר המרכיבים ובחשו היטב"),
    ("Añade la cantidad de queso que quieras sobre las patatas y lo hornea",
     "הוסיפו את כמות הגבינה הרצויה על תפוחי האדמה ואפו"),
    ("Espera a que el queso se derrita sobre las patatas",
     "חכו עד שהגבינה נמסה על תפוחי האדמה"),
    ("Saca del horno las patatas cubiertas de queso y sírvelas en un plato grande",
     "הוציאו מהתנור את תפוחי האדמה המכוסים בגבינה והגישו בצלחת גדולה"),
    ("Añade la salsa por", "הוסיפו את הרוטב מעל"),

    # ─── Trailing partials ───
    (" todavía יותר", " עוד יותר"),
    (" todavía más", " עוד יותר"),
    ("¡dónde tú quieras", "איפה שתרצה"),
    ("¡Qué rico", "איזה טעים"),
], key=lambda x: -len(x[0]))

def process(path: Path):
    try: txt = path.read_text(encoding="utf-8")
    except: return False
    orig = txt
    for es, he in MEGA:
        if es in txt:
            txt = txt.replace(es, he)
    if txt != orig:
        path.write_text(txt, encoding="utf-8")
        return True
    return False

def main():
    htmls = sorted(ROOT.rglob("*.html"))
    print(f"Mega-sweep over {len(htmls)}...")
    n = 0
    for p in htmls:
        rel = str(p.relative_to(ROOT))
        if any(s in rel for s in ("wp-json","feed","oembed","comments")): continue
        if process(p): n += 1
    print(f"✓ {n} files updated.")

if __name__ == "__main__":
    main()
