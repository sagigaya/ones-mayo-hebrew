# ONES Mayo · Hebrew Site — Handoff Summary · 7.10.2026

## 2 גרסאות חיות — תבחר מה שעובד לך

### 🟢 גרסה 1 — **מירור סטטי** (ההמלצה שלי)
- **URL פעיל:** 🟢 **https://ones-mayo.vercel.app** ← השתמש בזה
- **URL ישן:** ~~https://ones-mayo-hebrew.vercel.app~~ (תקוע ב-Vercel Challenge · ייפתר תוך שעות)
- **מה זה:** העתק 1:1 של האתר הספרדי onesmay.com, רק עם טקסטים בעברית
- **איך זה נבנה:** הורדתי את כל ה-WordPress של onesmay.com (531 קבצים · HTML/CSS/JS/תמונות/פונטים) ותרגמתי טקסטואלית לעברית. הפריסה, התמונות, הפונטים והאנימציות **זהים לחלוטין** למקור
- **פרויקט מקומי:** `~/Desktop/ones-mayo-hebrew/`
- **מה חסר:**
  - 3 עמודים משפטיים (aviso-legal · politica-de-privacidad · politica-de-cookies) עדיין בספרדית — צריך להחליף בטקסט ישראלי
  - פיסקאות קצרות בעברית/ספרדית מעורבות בעמודי מוצר/ערוץ (כ-5-10% מהטקסט)

### 🟡 גרסה 2 — **Lovable (React/TanStack)**
- **URL:** https://id-preview--d9dac04d-24f3-4871-ab79-426b4ff2fb96.lovable.app
- **Editor:** https://lovable.dev/projects/d9dac04d-24f3-4871-ab79-426b4ff2fb96
- **מה זה:** נבנה ב-Lovable עם פרומפט שהעברתי + 10 screenshots פיקסל-פיקסל של הדפים הספרדיים
- **יתרון:** קוד נקי, יכול להתחבר ל-GitHub לפי בקשת אוהד, יש Supabase backend לטופס קשר
- **חסרון:** נבנה מאפס → קטנים הבדלים בפריסה (לא פיקסל-פיקסל)
- **עלות עד כה:** ~12 Lovable credits

---

## השוואה
כשתפתח את 2 הקישורים ליד https://onesmay.com — תראה שהמירור הסטטי קרוב יותר ל-1:1. ה-Lovable הוא תחליף נקי.

## ההמלצה שלי
**לך עם המירור הסטטי כנקודת פתיחה** (זה הכי מהיר להציג לאוהד — זה *האתר הספרדי בעברית*). אחר כך, אם מישהו רוצה לפתח ולהוסיף פיצ'רים — מעבירים ל-Lovable.

## מה אני ממליץ שתעשה
1. **פתח את https://ones-mayo-hebrew.vercel.app** ותראה
2. **פתח את https://onesmay.com לידו** ותשווה
3. אם נראה טוב → נעלה לדומיין (ones-foods.co.il / something)
4. אם נראה פחות — נגיד לי מה לשפר

## קבצים
- `~/Desktop/ones-mayo-hebrew/` — פרויקט המירור הסטטי
- `~/Desktop/ones-mayo-hebrew/mirror.py` — סקריפט הורדת האתר הספרדי
- `~/Desktop/ones-mayo-hebrew/translate.py` + `retranslate.py` + `word_sweep.py` — סקריפטי התרגום
- `~/Desktop/ones-mayo-hebrew/vercel.json` — קונפיג deploy

## מידע מתכוני
- יבואן בישראל: גאיה פודס · office@gaya-foods.com
- מפעל בוולנסיה, ספרד: Calle Seis Nº 33, Polígono Industrial Picassent, Valencia 46220
- טלפון המפעל: +34 961 232 938
- מייל המפעל: info@onesmay.com
- קבוצת האם: GA Alimentaria (4 חברות: Gracom, Doccas Food, Onesmay Sabores, Anker Food)
- מוצרים: מיונז · בסיסי עגבנייה (קטשופ, ברביקיו, ברווה) · חרדל (דיז׳ון, גרגרים, קלאסי) · רטבים נוספים
- 4 ערוצים: HoReCa (מוסדי) · קמעונאי · מותג פרטי · פרויקט תעשייתי
- 6 פורמטים: מנה בודדת · טופ-דאון · קריסטל · בקבוק · ג׳ריקן · דלי
- גדלים: 250ml · 300ml · 500ml · 750ml
