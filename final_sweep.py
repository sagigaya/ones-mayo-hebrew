"""
Final sweep: fix mistranslations + add product descriptions + quality paragraphs.
"""
import re
from pathlib import Path

ROOT = Path.home() / "Desktop" / "ones-mayo-hebrew"

FINAL_TRANS = sorted([
    # ─── Fix the wrong "אודות" (I had nosotros → אודות; should be אנחנו) ───
    ("y אודות te ayudamos a crearla", "ואנחנו עוזרים לך ליצור אותו"),
    ("Sabemos que si tú ganas אודות גם lo hacemos", "אנחנו יודעים שאם אתה מרוויח, גם אנחנו מרוויחים"),
    ("también lo hacemos", "גם אנחנו מרוויחים"),
    ("אודות te ayudamos", "אנחנו עוזרים לך"),
    ("אודות גם ", "ואנחנו גם "),

    # ─── Product descriptions ───
    # Mayo
    ("Un delicioso sabor neutro con su punto exacto de cremosidad lista para acompañar cualquier plato",
     "טעם ניטרלי טעים עם רמת קרמיות מושלמת, מוכן ללוות כל מנה"),
    ("El sabor clásico, auténtico, ese sabor casero que recordamos todos",
     "הטעם הקלאסי, האותנטי — אותו טעם ביתי שכולנו זוכרים"),
    ("Una mayonesa con una consistencia ideal para aplicar en múltiples recetas ya que potencia sus rasgos",
     "מיונז בעל טקסטורה אידיאלית לשימוש במתכונים מגוונים — מעצים את התכונות שלהם"),
    ("Sabemos que la mejor receta es la tuya y por eso ponemos a tu disposición a nuestro equipo de I+D para que juntos elaboremos esa mayonesa ideal, la que mejor se acopla a tus exigencias y a tu mercado",
     "אנחנו יודעים שהמתכון הטוב ביותר הוא שלך — ולכן אנחנו מעמידים לרשותך את צוות המחקר ופיתוח שלנו, כדי שביחד נייצר את המיונז המושלם, זה שהכי מתאים לדרישות שלך ולשוק שלך"),
    ("Sabemos que la mejor receta es la tuya y por eso ponemos a tu disposición a nuestro equipo de I+D para que juntos elaboremos esa salsa con tomate ideal, la que mejor se acopla a tus exigencias y a tu mercado",
     "אנחנו יודעים שהמתכון הטוב ביותר הוא שלך — ולכן אנחנו מעמידים לרשותך את צוות המחקר ופיתוח שלנו, כדי שביחד נייצר את רוטב העגבנייה המושלם, זה שהכי מתאים לדרישות שלך ולשוק שלך"),
    ("Sabemos que la mejor receta es la tuya y por eso ponemos a tu disposición a nuestro equipo de I+D para que juntos elaboremos esa mostaza ideal, la que mejor se acopla a tus exigencias y a tu mercado",
     "אנחנו יודעים שהמתכון הטוב ביותר הוא שלך — ולכן אנחנו מעמידים לרשותך את צוות המחקר ופיתוח שלנו, כדי שביחד נייצר את החרדל המושלם, זה שהכי מתאים לדרישות שלך ולשוק שלך"),
    ("Sabemos que la mejor receta es la tuya y por eso ponemos a tu disposición a nuestro equipo de I+D para que juntos elaboremos esa salsa ideal, la que mejor se acopla a tus exigencias y a tu mercado",
     "אנחנו יודעים שהמתכון הטוב ביותר הוא שלך — ולכן אנחנו מעמידים לרשותך את צוות המחקר ופיתוח שלנו, כדי שביחד נייצר את הרוטב המושלם, זה שהכי מתאים לדרישות שלך ולשוק שלך"),
    ("Sabemos que la mejor receta es la tuya",
     "אנחנו יודעים שהמתכון הטוב ביותר הוא שלך"),

    # Tomato
    ("Una salsa genuina, perfecta para acompañar tus platos de carne, pollo, pizzas o una deliciosas patatas fritas",
     "רוטב אותנטי, מושלם ללוות מנות בשר, עוף, פיצה או צ'יפס טעים"),
    ("Picante y sabrosa ideal para acompañar con patatas, carnes o lo que tu prefieras",
     "חריף וטעים, אידיאלי להגשה עם תפוחי אדמה, בשרים או כל מה שתעדיף"),
    ("Nuestra receta יותר hot", "המתכון הכי חריף שלנו"),
    ("Nuestra receta más hot", "המתכון הכי חריף שלנו"),
    ("Perfectas en hamburguesas, patatas, perritos, bocatas, pasta, carnes… ¡dónde tú quieras",
     "מושלמים להמבורגרים, תפוחי אדמה, נקניקיות, כריכים, פסטה, בשרים — איפה שתרצה"),
    ("Proporciona un delicioso sabor a barbacoa incomparable",
     "מעניק טעם ברביקיו טעים ובלתי משתווה"),

    # Mustard
    ("Un toque picante, una suave textura cremosa, sabor intenso y toques sofisticados",
     "נגיעה חריפה, מרקם רך וקרמי, טעם עז עם נגיעות מתוחכמות"),
    ("Procedente de una receta ancestral hecha a base de semillas de mostaza amarilla y negra con un toque de vinagre, vino blanco y un sabor suave no demasiado picante",
     "ממתכון עתיק המבוסס על גרגרי חרדל צהוב ושחור, עם נגיעה של חומץ, יין לבן וטעם רך לא חריף מדי"),
    ("Suave y con un clásico color amarillo al יותר puro estilo americano que combina perfectamente con tus patatas, carnes, pescados y verduras",
     "רך וצבע צהוב קלאסי בסטייל אמריקאי טהור — משתלב מצוין עם תפוחי אדמה, בשרים, דגים וירקות"),
    ("Suave y con un clásico color amarillo al más puro estilo americano que combina perfectamente con tus patatas, carnes, pescados y verduras",
     "רך וצבע צהוב קלאסי בסטייל אמריקאי טהור — משתלב מצוין עם תפוחי אדמה, בשרים, דגים וירקות"),

    # Other sauces
    ("Deliciosa y original, el aderezo perfecto para ensaladas de todo tipo",
     "טעים ומקורי — הרוטב המושלם לכל סוגי הסלטים"),
    ("Elaborada a partir de la receta tradicional", "מיוצר לפי המתכון המסורתי"),
    ("Elaborada con 3 tipos de pimientas (blanca, negra y verde)",
     "מיוצר עם 3 סוגי פלפל (לבן, שחור וירוק)"),
    ("Estupenda para acompañar y dar sabor a tus pescados azules, blancos pero liga muy bien con algunas carnes",
     "מעולה ללוות ולהעניק טעם לדגים כחולים ולבנים, מתאימה גם לבשרים מסוימים"),
    ("Ideal para hacer mucho יותר sabrosos muchos de los platos que comemos diariamente",
     "אידיאלי לעשות הרבה יותר טעימים את המנות שאנחנו אוכלים ביומיום"),
    ("Ideal para hacer mucho más sabrosos muchos de los platos que comemos diariamente",
     "אידיאלי לעשות הרבה יותר טעימים את המנות שאנחנו אוכלים ביומיום"),
    ("La salsa cocktail o salsa rosa liga perfectamente con ensaladas y pastas pero combina perfectamente con una amplia variedad de platos fríos dándoles un toque especial",
     "רוטב קוקטייל (רוטב ורוד) משתלב מצוין עם סלטים ופסטות, ומתאים למגוון רחב של מנות קרות — מוסיף להן נגיעה מיוחדת"),

    # ─── Quality / Calidad paragraphs (shared across pages) ───
    ("Onesmay טעמים, como empresa del קבוצת GA Alimentaria, reconoce como un pilar inherente su compromiso de garantizar que siempre estarán a la vanguardia de los últimos adelantos en materia de gestión de la",
     "Onesmay Sabores, כחברה בקבוצת GA Alimentaria, מכירה כעמוד תווך בלתי נפרד את מחויבותה להבטיח שתעמוד תמיד בחזית ההתפתחויות האחרונות בתחום ניהול"),
    ("Onesmay Sabores, como empresa del Grupo GA Alimentaria, reconoce como un pilar inherente su compromiso de garantizar que siempre estarán a la vanguardia de los últimos adelantos en materia de gestión de la",
     "Onesmay Sabores, כחברה בקבוצת GA Alimentaria, מכירה כעמוד תווך בלתי נפרד את מחויבותה להבטיח שתעמוד תמיד בחזית ההתפתחויות האחרונות בתחום ניהול"),
    ("El servicio de calidad es innato y bajo la supervisión de un equipo especializado que garantiza la tranquilidad de nuestros clientes",
     "שירות האיכות הוא מהותי, תחת פיקוח של צוות מומחים המבטיח ללקוחותינו שקט נפשי"),
    ("Para ello disponemos de un departamento de I+D+i a su disposición que le asesorarán en todo el proceso",
     "לשם כך יש לנו מחלקת מחקר-ופיתוח (R&D) העומדת לרשותך ומייעצת לאורך כל התהליך"),
    ("Desarrollamos productos a medida conforme a las exigencias específicas",
     "אנחנו מפתחים מוצרים מותאמים בהתאם לדרישות הספציפיות"),
    ("A través de nuestro servicio personalizado afrontamos el desafío de ayudar a nuestros clientes en el desarrollo de productos para que sus marcas crezcan y sean un referente en sus canales de venta",
     "באמצעות השירות המותאם אישית שלנו אנחנו מתמודדים עם האתגר של סיוע ללקוחותינו בפיתוח מוצרים — כדי שהמותגים שלהם יצמחו ויהיו מובילים בערוצי המכירה שלהם"),
    ("Conscientes de ello, en Onesmay somos expertos en el desarrollo de productos adaptados a tus necesidades y hemos conseguido una mezcla perfecta entre el saber hacer de יותר de 60 שנים de trayectoria exitosa y un gran equ",
     "מודעים לכך, ב-Onesmay אנחנו מומחים בפיתוח מוצרים המותאמים לצרכים שלך, ויצרנו שילוב מושלם בין Know-how של למעלה מ-60 שנות הצלחה לבין צוות גדול"),

    # ─── Channels page remaining ───
    ("Con esta medida conseguimos una mayor eficiencia en logística y reducir los costes que suponen el almacenaje",
     "באמצעות הצעד הזה אנחנו משיגים יעילות גדולה יותר בלוגיסטיקה ומקטינים את עלויות האחסון"),
    ("En nuestras instalaciones, las mercancías están en continuo movimiento",
     "במתקנים שלנו, הסחורות בתנועה מתמדת"),
    ("Fabricamos bajo pedido según las necesidades de cada cliente, siguiendo un modelo de “Stock Cero”",
     "אנחנו מייצרים לפי הזמנה בהתאם לצרכי כל לקוח, במודל של \"מלאי אפס\""),
    ("Fabricamos bajo pedido según las necesidades de cada cliente, siguiendo un modelo de \"Stock Cero\"",
     "אנחנו מייצרים לפי הזמנה בהתאם לצרכי כל לקוח, במודל של \"מלאי אפס\""),
    ("Salsas de todos los sabores y colores", "רטבים בכל הטעמים והצבעים"),
    ("Nuestro Know how de יותר de 60 שנים en el sector de la alimentación junto a nuestra inquietud por aportar innovación y expertise en el desarrollo de nuevos productos permiten que juntos lideremos el mercado",
     "ה-Know-how שלנו של למעלה מ-60 שנה בתחום המזון, יחד עם השאיפה שלנו להביא חדשנות ומומחיות בפיתוח מוצרים חדשים, מאפשרים לנו ביחד להוביל את השוק"),
    ("trabajando de manera muy flexible y escuchando a nuestros clientes",
     "אנחנו עובדים בגמישות רבה ומקשיבים ללקוחותינו"),
    ("Disponemos de un amplio porfolio de formatos y trabajamos conjuntamente con nuestros proveedores para aportar las mejores soluciones disponibles y las mejoramos día a día para hacerlas יותר sostenibles y respetuosas con",
     "יש לנו פורטפוליו רחב של פורמטים, ואנחנו עובדים בשיתוף עם הספקים שלנו כדי להציע את הפתרונות הטובים ביותר — משפרים אותם מדי יום כדי שיהיו יותר בני-קיימא ומכבדים את"),
    ("Disponemos, si así lo prefieres, de un equipo de I+D y planta piloto para el desarrollo de tus רטבים",
     "אנחנו מעמידים לרשותך, אם תרצה, צוות מחקר ופיתוח ומפעל פיילוט לפיתוח הרטבים שלך"),
    ("כי sabemos que la mejor receta es la tuya y juntos podemos hacerlo, las רטבים que mejor se acopla a tus exigencias",
     "כי אנחנו יודעים שהמתכון הטוב ביותר הוא שלך — וביחד נוכל ליצור אותו, הרטבים שהכי מתאימים לדרישות שלך"),
    ("Adquirir nuestros productos supone reducir el impacto ambiental",
     "רכישת המוצרים שלנו מפחיתה את ההשפעה הסביבתית"),

    # Nav / breadcrumb cleanup
    ("CALIDAD HORECA", "איכות ל-HoReCa"),
    ("CALIDAD INDUSTRIAL", "איכות תעשייתית"),
    ("CALIDAD RETAIL", "איכות לקמעונאות"),
    ("CALIDAD GARANTIZADA", "איכות מובטחת"),

    # Lingering short Spanish words
    (" más ", " יותר "),
    ("Sabores", "טעמים"),
], key=lambda x: -len(x[0]))

def process(path: Path):
    try:
        txt = path.read_text(encoding="utf-8")
    except: return False
    original = txt
    for es, he in FINAL_TRANS:
        if es in txt:
            txt = txt.replace(es, he)
    if txt != original:
        path.write_text(txt, encoding="utf-8")
        return True
    return False

def main():
    htmls = sorted(ROOT.rglob("*.html"))
    print(f"Final sweep over {len(htmls)} files...")
    n = 0
    for p in htmls:
        rel = str(p.relative_to(ROOT))
        if any(seg in rel for seg in ("wp-json","feed","oembed","comments")):
            continue
        if process(p): n += 1
    print(f"✓ {n} files updated.")

if __name__ == "__main__":
    main()
