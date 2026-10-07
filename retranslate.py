"""
Second pass: keep original layout (no dir=rtl), inject Heebo font only,
and translate the long paragraphs that were missed on pass 1.

Rationale: The Salient WordPress theme uses absolute/flex positioning that
breaks under dir=rtl. Keeping LTR layout + Hebrew text inside gives us
pixel-perfect fidelity to the Spanish original + readable Hebrew content.
"""
import os, re
from pathlib import Path

ROOT = Path.home() / "Desktop" / "ones-mayo-hebrew"

# Long paragraphs that need translating (missed in pass 1)
MORE_TRANS = [
    # Home page company intro paragraph
    ("Somos Onesmay Sabores, uno de los 4 grandes productivos del gran grupo familiar, GA Alimentaria, con más de 60 años de bagaje creando productos de alimentación con una sensible fórmula: experiencia e innovación nace a mediados del siglo XX, en el año 1960, y tres generaciones después seguimos con el mismo espíritu con el que nació este sueño",
     "אנחנו Onesmay Sabores, אחת מ-4 יחידות הייצור הגדולות של קבוצת GA Alimentaria המשפחתית, עם למעלה מ-60 שנה של ניסיון ביצירת מוצרי מזון תוך שילוב של ניסיון וחדשנות. החברה נולדה באמצע המאה ה-20, בשנת 1960, ושלושה דורות אחר כך אנחנו ממשיכים באותה רוח שבה נולד החלום הזה."),

    # In el año 2018 paragraph
    ("En el año 2018, después de 40 años de dedicación y con un gran proyecto de expansión, se constituye GA Alimentaria dando un salto de calidad importante y añadiendo una amplia oferta de productos a nuestro catálogo gracias a las 4 unidades productivas presentes en el grupo: Gracom",
     "בשנת 2018, לאחר 40 שנה של מסירות ועם פרויקט התרחבות משמעותי, הוקמה GA Alimentaria עם קפיצת איכות משמעותית, המוסיפה היצע רחב של מוצרים לקטלוג שלנו הודות ל-4 יחידות הייצור הנמצאות בקבוצה: Gracom"),

    # OnesMay Sabores R&D
    ("OnesMay Sabores es el resultado de la labor constante de investigación del grupo GA Alimentaria, para el que la cercanía en el trato al cliente y la proximidad son valores muy presentes",
     "OnesMay Sabores היא תוצאה של עבודת מחקר מתמדת של קבוצת GA Alimentaria, שעבורה היחס הקרוב ללקוחות והקרבה הם ערכים מרכזיים."),

    ("Contamos con equipos propios de I+D para la formulación de nuevos sabores, que disponen de una planta piloto propia en la que se realizan las mezclas y formulaciones.",
     "יש לנו צוותי מחקר ופיתוח (R&D) משלנו ליצירת טעמים חדשים, בעלי מפעל פיילוט בו מתבצעים הערבובים והנוסחאות."),

    # Lifestyle values
    ("Apoyamos firmemente un estilo de vida saludable con una dieta equilibrada y trabajamos para ello.",
     "אנחנו תומכים בהחלט באורח חיים בריא עם תזונה מאוזנת, ועובדים לקידום הנושא."),
    ("Una nutrición adecuada es muy importante para que el cuerpo obtenga los mejores resultados.",
     "תזונה נכונה חשובה מאוד כדי שהגוף יקבל את התוצאות הטובות ביותר."),
    ("Disponemos de distintos recursos y estrategias para asegurar que todos los alimentos sean seguros para el consumo.",
     "יש לנו משאבים ואסטרטגיות שונים כדי להבטיח שכל המזונות בטוחים לצריכה."),
    ("Nuestras salsas son responsables tanto en el proceso de fabricación como en todo su ciclo de vida. Las mercancías están en continuo movimiento y fabricamos bajo pedido siguiendo un modelo de “Stock Cero”.",
     "הרטבים שלנו אחראיים הן בתהליך הייצור והן לאורך כל מחזור החיים. הסחורות בתנועה מתמדת ואנחנו מייצרים לפי הזמנה במודל של \"מלאי אפס\"."),
    ("Nuestras salsas son responsables tanto en el proceso de fabricación como en todo su ciclo de vida. En nuestras instalaciones, las mercancías están en continuo movimiento. Fabricamos bajo pedido según las necesidades de cada cliente, siguiendo un modelo de “Stock Cero”. Con esta m",
     "הרטבים שלנו אחראיים הן בתהליך הייצור והן לאורך כל מחזור החיים. במתקנים שלנו הסחורות בתנועה מתמדת. אנחנו מייצרים לפי הזמנה בהתאם לצרכי כל לקוח, במודל של \"מלאי אפס\". בעזרת זה"),
    ("Con esta medida buscamos la mayor eficiencia con la consiguiente reducción del impacto ambiental que supone adquirir nuestros productos.",
     "באמצעות הצעד הזה אנחנו שואפים ליעילות מרבית תוך הפחתת ההשפעה הסביבתית הכרוכה ברכישת המוצרים שלנו."),
    ("Cuidar de nuestro entorno, así como de nuestros recursos tanto naturales como humanos, económicos y sociales.",
     "לשמור על הסביבה שלנו, כמו גם על המשאבים שלנו — טבעיים, אנושיים, כלכליים וחברתיים."),
    ("Ser la primera opción de los usuarios pasa por innovar y adecuarse a las necesidades reales a lo largo del tiempo, buscando fórmulas que nos hagan mejorar cada día.",
     "להיות הבחירה הראשונה של המשתמשים דורש חדשנות והתאמה לצרכים האמיתיים לאורך זמן, בחיפוש אחר נוסחאות שיגרמו לנו להשתפר כל יום."),
    ("A través de la transparencia, la honestidad y la confianza que trasladamos y hace que nuestros clientes lleven años colaborando con nosotros.",
     "באמצעות השקיפות, הכנות והאמון שאנחנו משדרים, הלקוחות שלנו משתפים איתנו פעולה כבר שנים."),
    ("Para nosotros cada cliente es más que un cliente… es un socio con el que compartimos inquietudes y sueños. La receta del éxito pasa por potenciar el talento colectivo a través de la cooperación.",
     "עבורנו כל לקוח הוא יותר מאשר לקוח — הוא שותף שאיתו אנחנו חולקים דאגות וחלומות. מתכון ההצלחה עובר דרך העצמת הכישרון הקולקטיבי באמצעות שיתוף פעולה."),
    ("Para nosotros cada cliente es más que un cliente… sí, pero cada miembro del equipo es mucho más que una parte del engranaje, las empresas como Onesmay, parte del grupo GA, creemos en que somos la suma del capital intelectual de nuestro equipo y que solo así podemos lograr nuestro",
     "עבורנו כל לקוח הוא יותר מלקוח… כן, אבל גם כל חבר צוות הוא הרבה יותר מחלק מהגלגלים. חברות כמו Onesmay, חלק מקבוצת GA, מאמינות שאנחנו סכום של ההון האינטלקטואלי של הצוות שלנו, ורק כך נוכל להשיג את"),
    ("Así que si quieres un reto, una motivación laboral y un futuro profesional, nos encantará conocerte.",
     "אז אם אתם מחפשים אתגר, מוטיבציה בעבודה ועתיד מקצועי — נשמח להכיר."),
    ("Como parte del Grupo GA Alimentaria centralizamos las ofertas de empleo en la web principal del grupo, si quieres optar a un puesto o enviarnos tu curriculum haz click en el botón y envíanos tu postulación.",
     "כחלק מקבוצת GA Alimentaria אנחנו מרכזים את הצעות העבודה באתר הראשי של הקבוצה. אם אתם מעוניינים במשרה או רוצים לשלוח קורות חיים — לחצו על הכפתור ושלחו לנו את מועמדותכם."),

    # Product descriptions
    ("Nuestras mayonesas… deliciosas, suaves y cremosas, elaboradas con los mejores ingredientes de alta calidad que marcan la diferencia con cada cucharada. Un sabor único y sin igual, pruébalas con tus comidas favoritas o prueba alguna de nuestras recetas.",
     "המיונז שלנו — טעים, רך וקרמי, מיוצר עם המרכיבים האיכותיים ביותר שעושים את ההבדל בכל כפית. טעם ייחודי ובלתי משתווה. נסו אותו עם המאכלים האהובים עליכם או במתכונים שלנו."),
    ("Nuestras mayonesas&#8230; deliciosas, suaves y cremosas, elaboradas con los mejores ingredientes de alta calidad que marcan la diferencia con cada cucharada. Un sabor único y sin igual, pruébalas con tus comidas favoritas o prueba alguna de nuestras recetas.",
     "המיונז שלנו — טעים, רך וקרמי, מיוצר עם המרכיבים האיכותיים ביותר שעושים את ההבדל בכל כפית. טעם ייחודי ובלתי משתווה. נסו אותו עם המאכלים האהובים עליכם או במתכונים שלנו."),
    ("Ketchup, Barbacoa, Brava… las mejores salsas con base de tomate elaboradas con una selección de productos de la huerta, frescos y llenos de nutrientes para conseguir un producto de sabor inigualable que hará que tus platos y recetas brillen todavía más.",
     "קטשופ, ברביקיו, ברווה... הרטבים הטובים ביותר על בסיס עגבנייה, מיוצרים מתוצרת גן קפדנית — טרייה ומלאת רכיבים תזונתיים — ליצירת מוצר בטעם שאין שני לו, שיאיר את המנות והמתכונים שלכם."),
    ("Ketchup, Barbacoa, Brava&#8230; las mejores salsas con base de tomate elaboradas con una selección de productos de la huerta, frescos y llenos de nutrientes para conseguir un producto de sabor inigualable que hará que tus platos y recetas brillen todavía más.",
     "קטשופ, ברביקיו, ברווה... הרטבים הטובים ביותר על בסיס עגבנייה, מיוצרים מתוצרת גן קפדנית — טרייה ומלאת רכיבים תזונתיים — ליצירת מוצר בטעם שאין שני לו, שיאיר את המנות והמתכונים שלכם."),
    ("Clasica, antigua o tipo dijon, tu eliges pero sin duda que tenemos las mejores recetas con un sabor inigualable, reconocidas en mercados de todo el mundo. No puede faltar en tu lista de salsas imprescindibles.",
     "קלאסי, גרגרים או סגנון דיז'ון — אתם בוחרים. ללא ספק יש לנו את המתכונים הטובים ביותר עם טעם ייחודי, מוכרים בשווקים ברחבי העולם. חייב להופיע ברשימת הרטבים ההכרחיים שלכם."),
    ("Nuestras recetas adaptables, deliciosas, suaves y cremosas, elaborada 100% con huevos camperos e ingredientes de alta calidad que marcan la diferencia con cada cucharada. Un sabor único y sin igual, pruébala con tus comidas favoritas o prueba alguna de nuestras recetas.",
     "המתכונים שלנו — ניתנים להתאמה, טעימים, רכים וקרמיים — מיוצרים 100% מביצי משק חופש ומרכיבים איכותיים שעושים את ההבדל בכל כפית. טעם ייחודי ובלתי משתווה. נסו עם המאכלים האהובים או במתכונים שלנו."),

    # El auténtico placer
    ("El auténtico placer está en el sabor, el sabor de nuestras salsas con base de tomate, elaboradas con concentrado de tomates de calidad extra cultivados en nuestras huertas. Perfectas en hamburgue",
     "העונג האמיתי נמצא בטעם — טעם רטבי העגבנייה שלנו, המיוצרים מרסק עגבניות באיכות עליונה שגדל בגינות שלנו. מושלמים להמבורגרים"),

    # Mustard - "give your dishes"
    ("Dale un toque especial a tus platos. Perfectas en carnes, hamburguesas, verduras, pescados, perritos, sándwiches, ensaladas… te sorprenderá.",
     "תן למנות שלך גיוון מיוחד. מושלמים לבשרים, המבורגרים, ירקות, דגים, נקניקיות, כריכים, סלטים — זה יפתיע אותך."),

    # 40 years intro
    ("De nuestra experiencia de más de 40 años en el sector de la alimentación, como parte de Grupo GA Alimentaria, disponemos de un amplio portfolio de recetas propias adaptadas a cada mercado de los diferentes paises de todo el mundo. Tenemos la receta perfecta y la mejor salsa del m",
     "מתוך הניסיון שלנו של למעלה מ-40 שנה בתחום המזון, כחלק מקבוצת GA Alimentaria, יש לנו פורטפוליו רחב של מתכונים משלנו המותאמים לכל שוק של המדינות השונות ברחבי העולם. יש לנו את המתכון המושלם ואת הרוטב הטוב ביותר"),
    ("De nuestra experiencia de más de 40 años en el sector de la alimentación, como parte de Grupo GA Alimentaria, disponemos de un amplio portfolio de recetas propias adaptadas a cada mercado de los diferentes países de todo el mundo. Tenemos la receta perfecta y la mejor salsa del m",
     "מתוך הניסיון שלנו של למעלה מ-40 שנה בתחום המזון, כחלק מקבוצת GA Alimentaria, יש לנו פורטפוליו רחב של מתכונים משלנו המותאמים לכל שוק של המדינות השונות ברחבי העולם. יש לנו את המתכון המושלם ואת הרוטב הטוב ביותר"),

    # "Disponemos de recetas propias"
    ("Disponemos de recetas propias adaptadas y elaboradas para todos los gustos. Recetas caseras, suaves, ligeras, con ese toque de sabor de toda la vida pero con frescura, de calidad",
     "יש לנו מתכונים משלנו המותאמים ומעובדים לכל טעם. מתכונים ביתיים, עדינים, קלים, עם אותו טעם של פעם אבל ברעננות ואיכות"),
    ("Disponemos de recetas propias adaptadas y elaboradas para todos los gustos. Recetas caseras, suaves, ligeras, con un toque de",
     "יש לנו מתכונים משלנו המותאמים ומעובדים לכל טעם. מתכונים ביתיים, עדינים, קלים, עם נגיעה של"),

    # Channels common
    ("Somos expertos en crear productos que aportan soluciones de calidad y a medida de tu empresa. Nuestro Know how de más de 60 años en el sector de la alimentación junto a nuestra inquietud por aportar innovación y expertise en el desarrollo de nuevos productos permiten que juntos l",
     "אנחנו מומחים ביצירת מוצרים המספקים פתרונות איכותיים ומותאמים לעסק שלך. ה-Know-how שלנו של למעלה מ-60 שנה בתחום המזון, יחד עם השאיפה שלנו להביא חדשנות ומומחיות בפיתוח מוצרים חדשים, מאפשרים לנו ביחד"),
    ("Conocemos el mercado, las necesidades y gustos de los consumidores finales, por ello disponemos de un amplio porfolio de productos y formatos para el canal retail. Trabajamos en aportar soluciones presentes y trabajamos para las tendencias futuras. Salsas de todos los sabores y c",
     "אנחנו מכירים את השוק, את הצרכים ואת הטעמים של הצרכנים הסופיים, ולכן יש לנו פורטפוליו רחב של מוצרים ופורמטים לערוץ הקמעונאי. אנחנו עובדים על מתן פתרונות להווה ועל טרנדים עתידיים. רטבים בכל הטעמים"),
    ("Marca Privada\nPodemos ayudarte a resolver cualquier problema, a desarrollar una idea o a mejorar tu producto actual. Tenemos la receta perfecta y la mejor salsa del mundo, la tuya, y nosotros te ayudamos a crearla. También disponemos de un amplio porfolio de recetas adaptadas a c",
     "מותג פרטי\nאנחנו יכולים לעזור לך לפתור כל בעיה, לפתח רעיון או לשפר את המוצר הנוכחי שלך. יש לנו את המתכון המושלם ואת הרוטב הטוב ביותר בעולם — שלך — ואנחנו עוזרים לך ליצור אותו. בנוסף, יש לנו פורטפוליו רחב של מתכונים מותאמים"),
    ("Nos caracterizamos por trabajar de manera muy flexible, adaptándose a las necesidades de cada uno de nuestros clientes. Podemos fabricar cualquier tipo de salsa, personalizando el color, gusto o textura en función de las tendencias de cada gusto, cada país y territorio. Nos adapt",
     "אנחנו מאופיינים בעבודה גמישה מאוד, המתאימה את עצמה לצרכים של כל אחד מהלקוחות שלנו. אנחנו יכולים לייצר כל סוג רוטב, בהתאמה אישית של צבע, טעם או מרקם לפי הטרנדים של כל טעם, מדינה וטריטוריה. אנחנו מתאימים"),
    ("Selección de productos pensados para facilitar la labor de los profesionales del sector Horeca, ofreciendo distintas preparaciones, soluciones y formatos de envases adaptados a las necesidades de su negocio con una garantía de calidad constante que cubre todas las necesidades de",
     "מבחר מוצרים שתוכננו להקל על עבודת אנשי המקצוע בסקטור ה-HoReCa, ומציעים הכנות, פתרונות ופורמטי אריזה מותאמים לצרכים של העסק עם ערובת איכות קבועה שמכסה את כל הצרכים של"),
    ("Podemos fabricar cualquier tipo de salsa, personalizando el color, gusto o textura en función de las tendencias de cada mercado, país y/o territorio. Nos adaptamos a ti, con el trato cercano y exclusivo que caracteriza a todas las unidades productivas del grupo GA Alimentaria tra",
     "אנחנו יכולים לייצר כל סוג רוטב, בהתאמה אישית של צבע, טעם או מרקם לפי הטרנדים של כל שוק, מדינה או טריטוריה. אנחנו מתאימים את עצמנו אליך, עם היחס הקרוב והבלעדי המאפיין את כל יחידות הייצור של קבוצת GA Alimentaria"),
    ("Disponemos de un gran equipo de profesionales con la más moderna tecnología disponible en nuestra planta de I+D+I porque apostamos por el futuro, un futuro altamente eficiente que aporta soluciones a los mercados en constante evolución con las tendencias actuales y futuras, llena",
     "יש לנו צוות גדול של אנשי מקצוע עם הטכנולוגיה המודרנית ביותר שזמינה במפעל ה-R&D+I שלנו — אנחנו משקיעים בעתיד, עתיד יעיל במיוחד שמביא פתרונות לשווקים בהתפתחות מתמדת עם הטרנדים הנוכחיים והעתידיים, מלא"),
    ("Somos expertos y podemos ayudarte a mejorar tu producto actual o a adaptarlo a las nuevas tendencias específicamente bajo tus criterios y necesidades de mercado. A través de nuestro servicio personalizado afrontamos el desafío de ayudar a nuestros clientes en el desarrollo de pro",
     "אנחנו מומחים ויכולים לעזור לך לשפר את המוצר הנוכחי או להתאים אותו לטרנדים חדשים, בדיוק לפי הקריטריונים והצרכים השיווקיים שלך. באמצעות השירות המותאם אישית שלנו, אנחנו מתמודדים עם האתגר של סיוע ללקוחותינו בפיתוח מוצרים"),
    ("Somos expertos en crear productos que permiten aportar sabores únicos, de calidad y a medida de tu negocio. Ofrecemos soluciones al sector de la alimentación gracias a una continua innovación y a nuestro amplio expertise y liderazgo de más de 60 años",
     "אנחנו מומחים ביצירת מוצרים המביאים טעמים ייחודיים, איכותיים ומותאמים לעסק שלך. אנחנו מציעים פתרונות לסקטור המזון הודות לחדשנות מתמדת ולמומחיות הרחבה והמנהיגות שלנו של למעלה מ-60 שנה."),
    ("Nuestra división para clientes industriales comercializa productos a medida conforme a las exigencias específicas, condiciones y objetivos de producto que nos solicitan. Para ello y cuando se nos requiere, ponemos a disposición de de los clientes nuestro departamento de I+D+i.",
     "האגף שלנו ללקוחות תעשייתיים משווק מוצרים מותאמים לפי הדרישות הספציפיות, התנאים ויעדי המוצר שהוגשו לנו. לשם כך, כאשר נדרש, אנחנו מעמידים לרשות הלקוחות את מחלקת ה-R&D שלנו."),
    ("Contacte con nosotros… ¿Cúal es tu necesidad? tenemos la solución perfecta.",
     "צרו איתנו קשר… מה הצורך שלך? יש לנו את הפתרון המושלם."),
    ("Estamos trabajando para obtener las mejores calificaciones de las certificaciones más estrictas en materia de calidad y seguridad alimentaria.",
     "אנחנו פועלים להשיג את התעודות המחמירות ביותר בתחום האיכות ובטיחות המזון."),
    ("Déjanos tus datos y tu consulta para cualquier de nuestros departamentos y nos pondremos en contacto contigo lo antes posible.",
     "השאירו פרטים ופנייה לכל אחת מהמחלקות שלנו, ונחזור אליכם בהקדם האפשרי."),

    # Final paragraph fragments (the "4 centros productivos" split across HTML spans)
    ("Somos Onesmay Sabores, uno de los", "אנחנו Onesmay Sabores, אחת מ-"),
    ("centros productivos del gran grupo familiar,", "יחידות הייצור הגדולות של קבוצת"),
    ("años de bagaje creando productos de alimentación con una sencilla fórmula",
     "שנות ניסיון ביצירת מוצרי מזון עם נוסחה פשוטה"),
    ("nace a mediados del siglo XX, en el año 1960, y tres generaciones después seguimos con el mismo espíritu con el que nació este sueño.",
     "נולדה באמצע המאה ה-20, בשנת 1960, ושלושה דורות אחר כך אנחנו ממשיכים באותה רוח שבה נולד החלום הזה."),
    # "valor diferencial" trailing part
    ("valor diferencial y exclusivo para las políticas de sostenibilidad de las empresas.",
     "ערך מבדל ובלעדי למדיניות הקיימות של החברות."),
    # Short Spanish bits
    ("experiencia e innovación", "ניסיון וחדשנות"),

    # Short labels sometimes missed
    ("y lo sabes", "ואתה יודע את זה"),
    ("Más info", "מידע נוסף"),
    ("Ver más", "למידע נוסף"),
    ("Leer más", "קרא עוד"),
    ("Enviar", "שלח"),
]

TRANS_SORTED = sorted(MORE_TRANS, key=lambda x: -len(x[0]))

def process(path: Path):
    try:
        txt = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ✗ {path}: {e}")
        return False
    original = txt

    # Remove dir="rtl" + lang="he" overrides — revert to Spanish layout
    # (keeps hero/grid/absolute positions working, Hebrew text still renders RTL inside paragraphs)
    txt = re.sub(r'<html lang="he" dir="rtl"', '<html lang="he"', txt)
    # Remove the earlier override block
    txt = re.sub(r'<style id="hebrew-rtl-override">.*?</style>', '', txt, flags=re.DOTALL)
    # Keep the Google Fonts Heebo link + add minimal LTR-friendly font override
    new_override = """<style id="hebrew-font-only">
  body, p, h1, h2, h3, h4, h5, h6, a, span, li, td, label, input, textarea, button, .btn {
    font-family: 'Heebo', 'Assistant', inherit, sans-serif !important;
  }
  /* give Hebrew text proper rtl direction *within* its container,
     but keep the overall page layout as original Spanish LTR */
  body { unicode-bidi: plaintext; }
  p, h1, h2, h3, h4, h5, h6, li, td, span { unicode-bidi: plaintext; }
</style>"""
    # Deduplicate injection
    txt = re.sub(r'<style id="hebrew-font-only">.*?</style>', '', txt, flags=re.DOTALL)
    if "</head>" in txt:
        txt = txt.replace("</head>", new_override + "\n</head>", 1)

    # Apply additional translations
    for es, he in TRANS_SORTED:
        if es in txt:
            txt = txt.replace(es, he)

    if txt != original:
        path.write_text(txt, encoding="utf-8")
        return True
    return False

def main():
    htmls = sorted(ROOT.rglob("*.html"))
    print(f"Reprocessing {len(htmls)} HTML files...")
    n = 0
    for p in htmls:
        rel = str(p.relative_to(ROOT))
        if any(seg in rel for seg in ("wp-json", "feed", "oembed", "comments")):
            continue
        if process(p):
            n += 1
    print(f"\n✓ {n} files updated.")

if __name__ == "__main__":
    main()
