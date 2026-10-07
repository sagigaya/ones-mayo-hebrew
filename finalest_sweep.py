"""Last cleanup — target the specific stuck fragments found by the audit."""
import re
from pathlib import Path

ROOT = Path.home() / "Desktop" / "ones-mayo-hebrew"

FIXES = sorted([
    # ─── Fix remaining wrong "אודות" / mixed sentences ───
    ("Para אודות cada cliente es יותר que un cliente… es un socio con el que compartimos inquietudes y sueños",
     "אצלנו כל לקוח הוא יותר מלקוח — הוא שותף שאיתו אנחנו חולקים דאגות וחלומות"),
    ("Para אודות cada cliente es יותר que un cliente… sí, pero cada miembro del equipo es mucho יותר que una parte del engranaje",
     "אצלנו כל לקוח הוא יותר מלקוח… כן, אבל כל חבר צוות הוא הרבה יותר מגלגל במכונה"),
    ("Para אודות cada cliente es más que un cliente",
     "אצלנו כל לקוח הוא יותר מלקוח"),
    ("Trabaja con אודות", "עבוד איתנו"),
    ("Trabaja con nosotros", "עבוד איתנו"),
    ("por eso ponemos a tu disposición nuestras habilidades y tecnología",
     "לכן אנחנו מעמידים לרשותך את היכולות והטכנולוגיה שלנו"),
    ("tu reto profesional", "האתגר המקצועי שלך"),

    # ─── "Tenemos la receta perfecta" tail ───
    ("Tenemos la receta perfecta y la mejor salsa del mundo, la tuya, ואנחנו עוזרים לך ליצור אותו",
     "יש לנו את המתכון המושלם ואת הרוטב הטוב ביותר בעולם — שלך — ואנחנו עוזרים לך ליצור אותו"),
    ("Tenemos la receta perfecta y la mejor salsa del mundo, la tuya",
     "יש לנו את המתכון המושלם ואת הרוטב הטוב ביותר בעולם — שלך"),

    # ─── "Recetas caseras" trailing ───
    ("מתכונים caseras, suaves, ligeras, con ese toque de sabor de toda la vida pero con frescura, de calidad&#8230; ¿Cuál prefieres tú",
     "מתכונים ביתיים, עדינים, קלים, עם אותו טעם של פעם אבל בטריות ואיכות — איזה אתה מעדיף?"),
    ("¿Cuál prefieres tú", "איזה אתה מעדיף?"),

    # ─── Channel pages mixed intros ───
    ("ערוץ תעשייתי Somos expertos en crear productos que aportan soluciones de calidad y a medida de tu empresa",
     "ערוץ תעשייתי · אנחנו מומחים ביצירת מוצרים המספקים פתרונות איכותיים ומותאמים לעסק שלך"),
    ("ערוץ קמעונאי Conocemos el mercado, las necesidades y gustos de los consumidores finales, por ello disponemos de un amplio porfolio de productos y formatos para el canal retail",
     "ערוץ קמעונאי · אנחנו מכירים את השוק, את הצרכים ואת הטעמים של הצרכנים הסופיים — ולכן יש לנו פורטפוליו רחב של מוצרים ופורמטים לערוץ הקמעונאי"),
    ("מותג פרטי Podemos ayudarte a resolver cualquier problema, a desarrollar una idea o a mejorar tu producto actual",
     "מותג פרטי · אנחנו יכולים לעזור לך לפתור כל בעיה, לפתח רעיון או לשפר את המוצר הנוכחי שלך"),
    ("También disponemos de un amplio porfolio de recetas adaptadas a cada mercado de los diferentes países del mundo",
     "בנוסף יש לנו פורטפוליו רחב של מתכונים המותאמים לכל שוק של המדינות השונות בעולם"),
    ("Para ello la personalización es esencial ya que permite al fabricante expresar su propia personalidad y aumentar el éxito de sus productos",
     "לשם כך ההתאמה האישית חיונית — היא מאפשרת ליצרן לבטא את האישיות שלו ולהגדיל את הצלחת המוצרים"),
    ("Somos expertos y podemos ayudarte a mejorar tu producto actual o a adaptarlo a las nuevas tendencias específicamente bajo tus criterios y necesi",
     "אנחנו מומחים ויכולים לעזור לך לשפר את המוצר הנוכחי או להתאים אותו לטרנדים חדשים — בדיוק לפי הקריטריונים והצרכים שלך"),
    ("A través de nuestro servicio personalizado afrontamos el desafío de ayudar a nuestros clientes en el desarrollo de productos para que sus marcas crezcan y sean un referente en sus canales de venta",
     "באמצעות השירות המותאם אישית שלנו אנחנו מתמודדים עם האתגר של סיוע ללקוחות בפיתוח מוצרים — כדי שהמותגים שלהם יצמחו ויהיו מובילים בערוצי המכירה שלהם"),

    # ─── "Nuestras רטבים son responsables" ───
    ("Nuestras רטבים son responsables tanto en el proceso de fabricación como en todo su ciclo de vida",
     "הרטבים שלנו אחראיים הן בתהליך הייצור והן לאורך כל מחזור החיים"),
    ("Nuestras salsas son responsables tanto en el proceso de fabricación como en todo su ciclo de vida",
     "הרטבים שלנו אחראיים הן בתהליך הייצור והן לאורך כל מחזור החיים"),

    # ─── R&D mixed sentence ───
    ("אנחנו מעמידים לרשותך, אם תרצה, צוות מחקר ופיתוח ומפעל פיילוט לפיתוח הרטבים שלך, כי אנחנו יודעים שהמתכון הטוב ביותר הוא שלך — וביחד נוכל ליצור אותו, הרטבים שהכי מתאימים לדרישות שלך, criterio y a tu mer",
     "אנחנו מעמידים לרשותך, אם תרצה, צוות מחקר ופיתוח ומפעל פיילוט לפיתוח הרטבים שלך — כי אנחנו יודעים שהמתכון הטוב ביותר הוא שלך, וביחד נוכל ליצור אותו: הרטבים שהכי מתאימים לדרישות ולשוק שלך"),

    # ─── "referencias adaptadas" ───
    ("referencias adaptadas a todas las necesidades sea cual sea tu negocio",
     "פניות מותאמות לכל הצרכים — יהיה אשר יהיה העסק שלך"),

    # ─── "כל הרטבים והפורמטים פתרונות" mixed ───
    ("כל הרטבים והפורמטים פתרונות אתה מבקש, אנחנו נותנים צורה Somos expertos y podemos ayudarte a mejorar tu producto actual o a adaptarlo a las nuevas tendencias específicamente bajo tus criterios y necesi",
     "כל הרטבים והפורמטים · פתרונות · אתה מבקש, אנחנו נותנים צורה · אנחנו מומחים ויכולים לעזור לך לשפר את המוצר הנוכחי או להתאים אותו לטרנדים חדשים — בדיוק לפי הקריטריונים והצרכים שלך"),

    # ─── Jobs page ───
    ("tu reto profesional Como parte del קבוצת GA Alimentaria centralizamos las ofertas de empleo en la web principal del grupo, אם רוצים optar a un puesto o enviarnos tu curriculum haz click en el botón y",
     "האתגר המקצועי שלך — כחלק מקבוצת GA Alimentaria אנחנו מרכזים את הצעות העבודה באתר הראשי של הקבוצה. אם אתם מעוניינים במשרה או רוצים לשלוח קורות חיים — לחצו על הכפתור"),

    # ─── Short mid-sentence word hybrids ───
    ("ponemos a tu disposición nuestras habilidades y tecnología",
     "מעמידים לרשותך את היכולות והטכנולוגיה שלנו"),
    ("optar a un puesto o enviarnos tu curriculum",
     "להגיש מועמדות למשרה או לשלוח קורות חיים"),

], key=lambda x: -len(x[0]))

def process(path: Path):
    try: txt = path.read_text(encoding="utf-8")
    except: return False
    original = txt
    for es, he in FIXES:
        if es in txt:
            txt = txt.replace(es, he)
    if txt != original:
        path.write_text(txt, encoding="utf-8"); return True
    return False

def main():
    htmls = sorted(ROOT.rglob("*.html"))
    print(f"Sweep over {len(htmls)}...")
    n = 0
    for p in htmls:
        rel = str(p.relative_to(ROOT))
        if any(s in rel for s in ("wp-json","feed","oembed","comments")): continue
        if process(p): n += 1
    print(f"✓ {n} files updated.")

if __name__ == "__main__":
    main()
