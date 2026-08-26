# VIC.ir Company Scraper

A Python-based web scraper that extracts company information from the VIC.ir website, organized by Iranian provinces.

## Features

- **Automated Login**: Handles authentication using credentials from environment variables
- **Province-based Scraping**: Processes companies province by province
- **Resume Capability**: Can resume scraping from where it left off using existing CSV data
- **Configurable Output**: Option to save data in separate CSV files per province or a single combined file
- **Company Data Extraction**: Extracts company details including:
  - Province name
  - Company name
  - Company URL
  - Address information
  - Contact details (phone, postal code, etc.)
- **Robust Error Handling**: Retry logic with configurable attempts and timeouts
- **Session Management**: Automatically handles session expiration and re-login

## Prerequisites

- Python 3.8 or higher
- Firefox browser installed
- GeckoDriver (Firefox WebDriver)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Download [GeckoDriver](https://github.com/mozilla/geckodriver/releases) and place it in the project directory.

## Configuration

Create a `.env` file in the project root with your VIC.ir credentials:

```env
VIC_USERNAME=your_username
VIC_PASSWORD=your_password
```

### Script Configuration

The script includes configurable parameters at the top of `final.py`:

```python
MAX_COMPANIES_PER_PROVINCE = 1000        # Maximum companies per province
start_Provincy = 1                        # Starting province (1-based)
separate_Provinces = True                 # True: separate CSV per province, False: single combined CSV
file_template = "province_$"             # CSV filename template ($ replaced with province number)
MAX_RETRIES = 3                          # Maximum retries for page loads
PAGE_TIMEOUT = 30                        # Page load timeout in seconds
RETRY_WAIT = 5                           # Wait between retries in seconds
```

## Usage

Run the script:
```bash
python final.py
```

### Output Files

- When `separate_Provinces = True`: Creates `province_1.csv`, `province_2.csv`, etc.
- When `separate_Provinces = False`: Creates a single `province_1.csv` file

### Resume Feature

The script automatically detects existing CSV files and resumes scraping from where it left off:
- If a province already has `MAX_COMPANIES_PER_PROVINCE` companies, it skips that province
- It skips companies that have already been saved to CSV
- Existing data is preserved when files are updated

## CSV Output Format

Each CSV file includes the following columns (dynamic based on available data):
- `province`: Province name
- `company_name`: Company name
- `company_url`: Company URL
- `استان`: Province (from page data)
- `نشانی پستی`: Postal address
- `کد پستی`: Postal code
- `تلفن`: Phone number
- Additional fields as found on the page

## Error Handling

The script includes comprehensive error handling:
- Automatic retry for failed page loads
- Session expiration detection and automatic re-login
- Graceful handling of missing elements
- Individual company processing failures don't stop the entire script
- Data is saved after each successful company extraction

## File Structure

```
project/
├── final.py           # Main script
├── geckodriver.exe    # Firefox WebDriver
├── .env               # Environment variables (credentials)
├── province_1.csv     # Output CSV files
├── province_2.csv     # (etc.)
└── requirements.txt   # Python dependencies
```

## Requirements

Create a `requirements.txt` file with:

```
selenium==4.15.2
python-dotenv==1.0.0
```

## Known Limitations

- The script is configured for Firefox browser only
- Company extraction relies on specific page structure (div.Title and aside.CompanyRigth elements)
- First 1000 companies per province are scraped (configurable)
- Some company pages may lack certain data fields

## Notes

- The script includes a 1-second delay after page loads to ensure content is populated
- JavaScript is used to scroll elements into view and perform clicks
- UTF-8 with BOM encoding is used for CSV files for better Excel compatibility

## License

MIT

# اسکریپر شرکت‌های وب‌سایت VIC.ir

ابزار پایتون برای استخراج اطلاعات شرکت‌ها از وب‌سایت VIC.ir، سازمان‌دهی شده بر اساس استان‌های ایران.

## قابلیت‌ها

- **ورود خودکار**: مدیریت احراز هویت با استفاده از اعتبارنامه‌های ذخیره شده در متغیرهای محیطی
- **اسکرپینگ بر اساس استان**: پردازش شرکت‌ها به صورت استان‌به‌استان
- **قابلیت ادامه از نقطه قطع**: امکان ادامه اسکرپینگ از جایی که قبلاً متوقف شده با استفاده از داده‌های CSV موجود
- **خروجی قابل تنظیم**: امکان ذخیره داده‌ها در فایل‌های CSV جداگانه برای هر استان یا یک فایل ترکیبی واحد
- **استخراج اطلاعات شرکت**: دریافت اطلاعات شرکت شامل:
  - نام استان
  - نام شرکت
  - آدرس شرکت
  - اطلاعات تماس (تلفن، کد پستی و ...)
- **مدیریت خطاهای قدرتمند**: منطق تکرار مجدد با تعداد تلاش‌ها و زمان‌های انتظار قابل تنظیم
- **مدیریت نشست**: تشخیص خودکار انقضای نشست و ورود مجدد

## پیش‌نیازها

- پایتون نسخه 3.8 یا بالاتر
- مرورگر فایرفاکس نصب شده
- GeckoDriver (درایور وب فایرفاکس)

## نصب و راه‌اندازی

1. کلون کردن مخزن:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. نصب پکیج‌های مورد نیاز:
```bash
pip install -r requirements.txt
```

3. دانلود [GeckoDriver](https://github.com/mozilla/geckodriver/releases) و قرار دادن آن در پوشه پروژه.

## تنظیمات

یک فایل `.env` در پوشه پروژه با اطلاعات ورود به VIC.ir ایجاد کنید:

```env
VIC_USERNAME=نام_کاربری_شما
VIC_PASSWORD=رمز_عبور_شما
```

### تنظیمات اسکریپت

اسکریپت شامل پارامترهای قابل تنظیم در ابتدای فایل `final.py` است:

```python
MAX_COMPANIES_PER_PROVINCE = 1000        # حداکثر شرکت در هر استان
start_Provincy = 1                        # شروع از استان شماره (یک‌پایه)
separate_Provinces = True                 # True: CSV جداگانه برای هر استان، False: یک CSV ترکیبی
file_template = "province_$"             # الگوی نام فایل CSV ($ با شماره استان جایگزین می‌شود)
MAX_RETRIES = 3                          # حداکثر تلاش برای بارگذاری صفحات
PAGE_TIMEOUT = 30                        # زمان انتظار برای بارگذاری صفحه بر حسب ثانیه
RETRY_WAIT = 5                           # زمان انتظار بین تلاش‌های مجدد بر حسب ثانیه
```

## نحوه اجرا

اجرای اسکریپت:
```bash
python final.py
```

### فایل‌های خروجی

- وقتی `separate_Provinces = True`: فایل‌های `province_1.csv`، `province_2.csv` و ... ایجاد می‌شوند.
- وقتی `separate_Provinces = False`: یک فایل `province_1.csv` واحد ایجاد می‌شود.

### قابلیت ادامه از نقطه قطع

اسکریپت به صورت خودکار فایل‌های CSV موجود را تشخیص می‌دهد و اسکرپینگ را از جایی که متوقف شده ادامه می‌دهد:
- اگر یک استان قبلاً به `MAX_COMPANIES_PER_PROVINCE` شرکت رسیده باشد، آن استان را نادیده می‌گیرد.
- شرکت‌هایی که قبلاً در CSV ذخیره شده‌اند را اسکرپ نمی‌کند.
- داده‌های موجود هنگام بروزرسانی فایل‌ها حفظ می‌شوند.

## فرمت خروجی CSV

هر فایل CSV شامل ستون‌های زیر است (پویا بر اساس داده‌های موجود):
- `province`: نام استان
- `company_name`: نام شرکت
- `company_url`: آدرس شرکت
- `استان`: نام استان (از داده‌های صفحه)
- `نشانی پستی`: آدرس پستی
- `کد پستی`: کد پستی
- `تلفن`: شماره تلفن
- فیلدهای اضافی بر اساس داده‌های موجود در صفحه

## مدیریت خطاها

اسکریپت شامل مدیریت جامع خطاها است:
- تلاش مجدد خودکار برای بارگذاری ناموفق صفحات
- تشخیص انقضای نشست و ورود مجدد خودکار
- مدیریت مناسب عناصر موجود نبوده در صفحه
- خرابی پردازش یک شرکت باعث توقف کل اسکریپت نمی‌شود
- ذخیره داده‌ها پس از استخراج موفق هر شرکت

## ساختار پوشه پروژه

```
project/
├── final.py           # اسکریپت اصلی
├── geckodriver.exe    # درایور وب فایرفاکس
├── .env               # متغیرهای محیطی (اعتبارنامه‌ها)
├── province_1.csv     # فایل‌های CSV خروجی
├── province_2.csv     # (و غیره)
└── requirements.txt   # وابستگی‌های پایتون
```

## وابستگی‌ها

فایل `requirements.txt`:

```
selenium==4.15.2
python-dotenv==1.0.0
```

## محدودیت‌های شناخته شده

- اسکریپت فقط برای مرورگر فایرفاکس پیکربندی شده است.
- استخراج اطلاعات شرکت وابسته به ساختار خاص صفحه (عناصر div.Title و aside.CompanyRigth) است.
- حداکثر ۱۰۰۰ شرکت اول هر استان اسکرپ می‌شود (قابل تنظیم).
- ممکن است برخی صفحات شرکت فاقد برخی فیلدهای داده باشند.

## نکات

- اسکریپت پس از بارگذاری صفحات، ۱ ثانیه تاخیر دارد تا محتوای صفحه کاملاً بارگذاری شود.
- از جاوااسکریپت برای اسکرول به عناصر و کلیک روی آنها استفاده می‌شود.
- برای سازگاری بهتر با اکسل، از کدگذاری UTF-8 با BOM برای فایل‌های CSV استفاده شده است.
