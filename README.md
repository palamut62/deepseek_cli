# deepseek-cli

![Python](https://img.shields.io/badge/python-3.8%2B-blue?logo=python)
![License](https://img.shields.io/badge/license-MIT-green)

## 🚀 Proje Hakkında
Bu proje, **Claude Code** benzeri gelişmiş kod üretim ve yönetim özelliklerini terminal üzerinden sunmak amacıyla geliştirilmiş bir Python CLI uygulamasıdır. Uygulama, **DeepSeek LLM** altyapısını kullanır ve görev odaklı bir **CrewAI** agent akışını uygular:

1. **PlannerAgent** → Kullanıcı prompt’unu adım adım görevlere böler.
2. **TodoAgent** → İsteği yapılacaklar listesine dönüştürür (`todo.md`).
3. **CoderAgent** → İstenen kodu üretir.
4. **ReviewerAgent** → Kodu analiz eder, riskleri ve iyileştirme alanlarını çıkarır.
5. **FixerAgent** → Tespit edilen sorunları giderir ve nihai kodu verir.

---

## 📦 Kurulum

```bash
# Repoyu klonlayın
git clone <repo-url>
cd deepseek_cli

# Sanal ortam (opsiyonel fakat tavsiye edilir)
python -m venv venv
# Linux/MacOS:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt
# veya
pip install click rich openai python-dotenv
```

> **Not:** `python-dotenv` API anahtarını yerel `.env` dosyasına kaydetmek için kullanılır.

---

## ⚙️ Ortam Değişkenleri
Aşağıdaki değişkenler `.env` dosyası ya da kabuk ortamınıza eklenmelidir:

| Değişken            | Açıklama                                              |
|---------------------|------------------------------------------------------|
| `DEEPSEEK_API_KEY`  | DeepSeek API anahtarınız **(zorunlu)**               |
| `DEEPSEEK_MODEL`    | Kullanılacak model adı *(varsayılan: deepseek-coder)*|
| `DEEPSEEK_API_BASE` | API uç noktası *(varsayılan: https://api.deepseek.com/v1)* |
| `PYTHON_ENV`        | Geliştirme/üretim ayrımı *(varsayılan: development)*  |

`.env` dosyası örneği:

```dotenv
DEEPSEEK_API_KEY=your_deepseek_key_here
DEEPSEEK_MODEL=deepseek-coder
```

---

## 🛠️ Kullanım
Proje kökünde aşağıdaki gibi çalıştırın:

```bash
python -m deepseek_cli.cli "jwt authentication içeren fastapi backend"
```

### Opsiyonlar

| Bayrak                | Açıklama                                      |
|-----------------------|-----------------------------------------------|
| `--save <file.py>`    | Nihai kodu dosyaya kaydeder                   |
| `--plan / --no-plan`  | Görev planı çıktısı üretir/üretmez            |
| *(bayrak gerekmez)*   | TODO listesi **her zaman** `data/todo.md`'ye kaydedilir |

#### Örnekler

Kod + plan (TODO otomatik oluşturulur) ve dosyaya kaydet:
```bash
python -m deepseek_cli.cli "build a flask todo api" --plan --save todo_api.py
```

Sadece kod (TODO otomatik):
```bash
python -m deepseek_cli.cli "jwt authentication fastapi backend"
```

---

## 🔍 Özellikler
- Doğal dilden **kod üretimi**
- **Kod analizi** ve iyileştirme önerileri
- **Hata düzeltme** (sentaktik & mantıksal)
- **Plan modu**: Görev kırılımı (isteğe bağlı bayrak)
- **TODO listesi**: Her zaman oluşturulur ve kaydedilir
- Renkli terminal çıktıları (**rich**)

---

## 📂 Klasör Yapısı

```text
deepseek_cli/
├── cli.py           # CLI giriş noktası
├── config.py        # API & genel ayarlar
├── crew_runner.py   # Tüm agent akışını yönetir
│
├── agents/          # Agent sınıfları
│   ├── base_agent.py
│   ├── planner_agent.py
│   ├── todo_agent.py
│   ├── coder_agent.py
│   ├── reviewer_agent.py
│   └── fixer_agent.py
│
├── tools/           # Yardımcı fonksiyonlar
│   ├── file_tools.py
│   └── todo_writer.py
│
└── data/
    └── todo.md      # Oluşturulan TODO listesi
```

---

## 🧭 Kullanım Akışı (Arayüz)

Aşağıdaki adımlar CLI arayüzünde kullanıcıya gösterilir:

1. **Özellik Seçimi**
   - Kullanıcıdan bir özellik/fonksiyon seçmesi istenir:
     ```
     Lütfen bir özellik seçin:
     1 - auth
     2 - api
     3 - db
     4 - ui
     5 - test
     6 - ci
     7 - cache
     8 - logging
     9 - config
     10 - utils
     11 - other
     Seçiminiz (numara veya isim): _
     ```
   - Hiçbir seçim yapılmazsa veya yanlış seçim yapılırsa:
     ```
     [bold red]Hiçbir özellik seçilmedi! Çıkılıyor...
     veya
     [bold red]Geçersiz seçim: ...
     ```

2. **Prompt Girişi**
   - Seçilen özellik için kullanıcıdan açıklama istenir:
     ```
     Lütfen bu özellik için ne yapılacağını yazın: _
     ```
   - Boş bırakılırsa:
     ```
     [bold red]Prompt girilmedi! Çıkılıyor...
     ```

3. **Plan Oluşturma ve Onay**
   - Eğer `--plan` seçiliyse, plan oluşturulup gösterilir:
     ```
     📝 Plan oluşturuluyor...
     1. ...
     2. ...
     ...
     Devam edilsin mi? (e/h): _
     ```
   - Kullanıcı "h" derse:
     ```
     [bold red]İşlem iptal edildi.
     ```

4. **Kod ve TODO Üretimi**
   - Plan onaylanırsa veya plan yoksa, TODO ve kod üretimi başlar.
   - Kod üretimi sonrası kaydetme sorusu:
     ```
     Kodu dosyaya kaydetmek ister misiniz? [e]vet / [h]ayır / [a]lways
     ```

---

## ⚡ Kısaca Kullanım

1. Komutu başlatın:
   ```bash
   python -m deepseek_cli.cli
   ```
2. Özellik seçin (menüden numara veya isim girin):
   ```
   Lütfen bir özellik seçin:
   1 - auth
   2 - api
   ...
   Seçiminiz (numara veya isim): 2
   # veya: api
   ```
3. Seçilen özellik için ne yapılacağını yazın:
   ```
   Lütfen bu özellik için ne yapılacağını yazın: JWT tabanlı kimlik doğrulama ekle
   ```
4. (Varsa) Planı inceleyin ve devam etmek için onay verin:
   ```
   📝 Plan oluşturuluyor...
   1. ...
   Devam edilsin mi? (e/h): e
   ```
5. Kod ve TODO otomatik üretilir. Son olarak kaydetmek isteyip istemediğiniz sorulur:
   ```
   Kodu dosyaya kaydetmek ister misiniz? [e]vet / [h]ayır / [a]lways
   ```

---

## ✨ Genişletme Önerileri
- [ ] Web arayüzü (Streamlit)
- [ ] GitHub Issue & PR entegrasyonu
- [ ] Kod geçmişi/loglama
- [ ] Farklı LLM modelleri ile karşılaştırma

---

## 📝 Lisans

MIT