# ONES Mayo · Hebrew Static Mirror

אתר שיווקי בעברית של **ONES** — יצרן רטבים ספרדי מוולנסיה (חלק מקבוצת GA Alimentaria), שגאיה פודס מייבאת לישראל.

🟢 **חי:** https://ones-mayo.vercel.app

## איך בנוי

מירור סטטי מלא של https://onesmay.com (ה-WordPress Divi/Salient מקורי) + תרגום מלא לעברית — כדי לקבל מראה פיקסל-פיקסל זהה למקור.

- **HTML** · 20 דפים (14 ציבוריים: בית, חברה, 4 מוצרים, 5 ערוצים, מתכונים, חדשות, קשר + 3 משפטיים)
- **CSS/JS/תמונות/פונטים** · 430+ קבצים נגזרים מה-WordPress המקורי
- **ללא backend** · סטטי לחלוטין, מתארח ב-Vercel

## מבנה הפרויקט

```
.
├── index.html                 # דף הבית
├── empresa/                   # חברה
├── productos/                 # 4 דפי מוצרים
│   ├── mayonesa/
│   ├── base-tomate/
│   ├── mostazas/
│   └── otras-salsas/
├── canales/                   # ערוצים
│   ├── horeca/
│   ├── retail/
│   ├── marca-privada/
│   └── proyecto-industrial/
├── recetas/                   # מתכונים
├── noticias/                  # חדשות
├── contacto/                  # יצירת קשר
├── wp-content/                # כל ה-CSS/JS/תמונות מהמקור
├── vercel.json                # הגדרות Vercel
├── HANDOFF.md                 # סיכום לאוהד
│
├── mirror.py                  # הורדת onesmay.com → קבצים מקומיים
├── translate.py               # פאס תרגום ראשון (DNA + headings)
├── retranslate.py             # פאס שני (long paragraphs)
├── word_sweep.py              # פאס שלישי (fragments)
├── final_sweep.py             # פאס רביעי (product descriptions)
├── finalest_sweep.py          # פאס חמישי (fix mistranslations)
├── mega_sweep.py              # פאס שישי (hybrid Spanish-Hebrew)
└── fix_broken_urls.py         # תיקון URL-ים שנשברו בתרגום
```

## דברים לדעת

- **~5% מהטקסטים** בעמודי המוצר/ערוץ עדיין בעברית-ספרדית מעורב (קטעים קצרים שנתפסו בין פאסים של התרגום) — ניתן להמשיך לנקות ע״י הוספה למילוני הסקריפטים ו-redeploy
- **3 דפים משפטיים** (`aviso-legal/`, `politica-de-privacidad/`, `politica-de-cookies/`) עדיין בספרדית — ממילא נדרש להחליף בנוסח ישראלי מאושר
- **פרטי יבואן** של גאיה טרם הוזנו בדף יצירת הקשר — עדיין מוצגת כתובת וטלפון של המפעל בוולנסיה בלבד
- **פטי GitHub Pages / vercel integration** — דורש הגדרה נוספת

## Deploy

```bash
# פריסה ל-preview
vercel

# promote ל-production
vercel ls ones-mayo | head -1 | xargs vercel promote
```

הפרויקט מקושר ל-Vercel project `ones-mayo` (team `sagi-s-projects2`).

## רישיונות / קניין

- **תוכן, לוגו ותמונות:** בבעלות Onesmay Sabores / GA Alimentaria (ספרד)
- **קוד HTML/CSS/JS בפרויקט זה:** מירור של האתר המקורי + תרגום לעברית — למטרת שיווק של גאיה פודס כיבואן בלעדי בישראל
- **לא לפרסום/שימוש חיצוני** ללא אישור של גאיה פודס + Onesmay
