# Toshstat.uz — Telegram bot

Toshkent shahar statistika boshqarmasi uchun rasmiy Telegram bot: bilim sinovi
(test) tizimi va rasmiy hujjatlar manbai.

**Stek:** Python 3.11+, aiogram 3.x, SQLite (aiosqlite).

## Loyiha tuzilishi

```
tashstat_bot/
├── bot.py                   # kirish nuqtasi (polling)
├── config.py                 # .env / muhit o'zgaruvchilaridan sozlamalarni o'qiydi
├── Dockerfile                 # konteyner image
├── docker-compose.yml         # Dokploy/Docker Compose orqali joylashtirish
├── .dockerignore
├── handlers/
│   ├── start.py              # /start, asosiy menyu, "Bot haqida"
│   ├── tests.py              # testlar ro'yxati, savol-javob FSM, natijalar, reyting
│   └── sources.py            # "Manbalar" bo'limi (hujjatlar ro'yxati va yuklab olish)
├── keyboards/                 # inline keyboard generatorlari
├── database/db.py             # SQLite: users, results jadvallari
├── states/quiz.py             # FSM holatlari (aiogram StatesGroup)
├── utils/
│   ├── quiz_logic.py          # savol/variantlarni aralashtirish, hisoblash
│   └── ui.py                  # matn dizayni: ajratuvchilar, harflar, medal/daraja belgilari
└── data/
    ├── questions.json         # test savollari bazasi (6 ta test, 102 ta haqiqiy savol)
    ├── sources.json           # "Manbalar" bo'limidagi hujjatlar ro'yxati
    ├── files/                  # shu yerga haqiqiy PDF/DOCX fayllarni joylang
    └── banner.jpg              # (ixtiyoriy) /start banneri — mavjud bo'lmasa, matn bilan davom etadi
```

## O'rnatish va ishga tushirish

1. Python 3.11+ o'rnatilganini tekshiring:

   ```bash
   python --version
   ```

2. Virtual muhit yaratib, kutubxonalarni o'rnating:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. `.env.example` faylidan nusxa olib `.env` yarating va tokeningizni kiriting:

   ```bash
   copy .env.example .env
   ```

   `.env` ichida:

   ```
   BOT_TOKEN=<BotFather'dan olingan token>
   WEBSITE_URL=https://toshstat.uz
   DB_PATH=database/bot.db
   SHOW_LEADERBOARD=true
   LEADERBOARD_SHOW_NAMES=false
   ```

4. Botni ishga tushiring:

   ```bash
   python bot.py
   ```

   Birinchi ishga tushishda `database/bot.db` SQLite fayli avtomatik yaratiladi.

## Savollar bazasi

`data/questions.json` faylida **6 ta test, jami 102 ta haqiqiy savol** bor —
`Biznes_perepisi_test.docx` va `Biznes_perepisi_test_TOLIQ.2.docx`
fayllaridagi savol-javob banki asosida tuzilgan (mavzular bo'yicha
guruhlangan, dublikatlar olib tashlangan):

| Test | Mavzu | Savollar soni |
|---|---|---|
| 1-test | Asosiy qaror | 18 |
| 2-test | Ro'yxatga olish tartibi (Nizom) | 21 |
| 3-test | Chora-tadbirlar rejasi | 17 |
| 4-test | Dastur va ma'muriy ma'lumotlar | 19 |
| 5-test | Aholi soni va respondentlar toifalari | 16 |
| 6-test | Komissiya tarkibi | 11 |

Savollar soni testlar bo'yicha 11–21 oralig'ida — bu haqiqiy hujjatlardagi
mavzular hajmiga mos keladi (asl talabdagi "har biri 20 ta" shartini
sun'iy ravishda savol qo'shib yoki kesib bajarish o'rniga, mavjud haqiqiy
kontent saqlab qolindi). Har bir savol uchun `explanation` maydonida manba
hujjat/ilova nomi ko'rsatilgan.

Yangi savol qo'shish yoki tahrirlash uchun format:

```json
{
  "id": "t1_q1",
  "question": "Savol matni",
  "options": ["A varianti", "B varianti", "C varianti", "D varianti"],
  "correct_index": 0,
  "explanation": "To'g'ri javob nima uchun to'g'ri ekanligi haqida qisqa izoh"
}
```

- `correct_index` — `options` massividagi to'g'ri javobning indeksi (0 = A, 1 = B, ...).
- Bot har safar savol va variantlar tartibini **avtomatik aralashtiradi** — JSON'da
  tartib muhim emas.
- Yangi test qo'shish uchun `tests` massiviga yangi obyekt qo'shing (`id`, `title`,
  `description`, `questions`) — u avtomatik ravishda testlar ro'yxatida chiqadi.

## Manbalar (hujjatlar) bo'limini to'ldirish

1. Haqiqiy PDF/DOCX fayllarni `data/files/` papkasiga joylang.
2. `data/sources.json` faylida har bir hujjat uchun `file` maydonida fayl nomini
   ko'rsating (masalan `"file": "qaror_loyihasi.pdf"`). Fayl hali yuklanmagan bo'lsa,
   bot foydalanuvchiga "Fayl hali yuklanmagan" xabarini avtomatik ko'rsatadi.

## Banner rasmi

`/start` bosilganda `data/banner.jpg` fayli mavjud bo'lsa, u birinchi bo'lib
yuboriladi. Fayl topilmasa, bot xatosiz — banner rasmisiz, faqat matn bilan
davom etadi. **Muhim:** rasmiy davlat ramzlari/yubiley logotipini
Toshkent shahar statistika boshqarmasi matbuot xizmati bilan kelishib,
tasdiqlangan versiyasini shu yerga joylang.

## Buyruqlar

| Buyruq | Vazifasi |
|---|---|
| `/start` | Botga kirish, banner, tabrik, asosiy menyu |
| `/testlar` | Testlar ro'yxati |
| `/manbalar` | Rasmiy hujjatlar ro'yxati |
| `/mynatijalar` | Foydalanuvchining o'z natijalari tarixi |
| `/reyting` | Eng yaxshi natijalar reytingi (`.env`da `SHOW_LEADERBOARD=false` bilan o'chirish mumkin) |
| `/yordam` | Bot haqida qisqa ma'lumot |

## Dokploy orqali shaxsiy serverga joylashtirish

Loyihada `Dockerfile` va `docker-compose.yml` tayyor — Dokploy panelida
quyidagicha joylashtiring:

1. Dokployda **Create Project → Application → Docker Compose** turini tanlang
   (yoki alohida "Compose" xizmati sifatida qo'shing).
2. **Source**: shu GitHub repozitoriysini ulang
   (`shaxzodabdisamadov-dev/toshstatquiz_bot`), branch — `main`.
   Dokploy `docker-compose.yml` faylini avtomatik topadi.
3. **Environment Variables** bo'limida quyidagilarni kiriting (`.env.example`
   bilan bir xil nomlar, qiymatlar Dokploy panelida saqlanadi, repoga
   yuklanmaydi):

   ```
   BOT_TOKEN=<BotFather'dan olingan haqiqiy token>
   WEBSITE_URL=https://toshstat.uz
   DB_PATH=database/bot.db
   SHOW_LEADERBOARD=true
   LEADERBOARD_SHOW_NAMES=false
   ```

   `BOT_TOKEN` — majburiy, qolganlari ixtiyoriy (standart qiymatlar
   `docker-compose.yml` ichida bor).
4. **Deploy** tugmasini bosing. Dokploy image'ni qurib, konteynerni polling
   rejimida (portsiz, tashqi trafik kerak emas) ishga tushiradi.
5. SQLite baza (`/app/database`) va yuklangan fayllar (`/app/data/files`)
   nomlangan Docker volume'larda saqlanadi (`bot_database`, `bot_files`) —
   qayta deploy qilinganda ma'lumotlar yo'qolmaydi.
6. `data/files/` papkasiga haqiqiy PDF/DOCX hujjatlarni qo'shish uchun ularni
   repoga commit qilib qayta deploy qiling (eng oddiy yo'l), yoki Dokployning
   konteyner terminali/volume boshqaruvidan foydalanib to'g'ridan-to'g'ri
   volume ichiga joylang.

Kodni yangilagach, GitHub'ga push qiling — Dokployda **auto-deploy** yoqilgan
bo'lsa, u avtomatik qayta qurib ishga tushiradi; aks holda panelda **Redeploy**
bosing.

## Eslatma

Bu rasmiy davlat idorasi nomidan ishlaydigan bot bo'lgani uchun ishga
tushirishdan oldin barcha matnlar va vizual materiallar (ayniqsa Mustaqillik
35 yilligi bilan bog'liq tabrik va banner) Toshkent shahar statistika
boshqarmasining matbuot xizmati yoki rahbariyati tomonidan tasdiqlanishi
tavsiya etiladi.
