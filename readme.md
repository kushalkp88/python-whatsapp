# WhatsApp Scheduler API (Minimal Version)

A minimal REST API for sending WhatsApp messages (text or image) using Python Flask and Node.js with [@open-wa/wa-automate](https://github.com/open-wa/wa-automate-nodejs).

---

## Features

- Send WhatsApp text or image messages via a simple API
- Get WhatsApp QR code for authentication
- Reset WhatsApp session
- Rate limiting for API security
- Clean, minimal codebase

---

## Folder Structure

```
whatsapp_scheduler/
├── app.py                      # Flask API (Python)
├── node_whatsapp/
│   └── send_message.cjs        # Node.js WhatsApp worker script
│   └── package.json            # Node.js dependencies for node_whatsapp
├── uploads/                    # Temporary image uploads (auto-deleted)
├── session/                    # WhatsApp session data (persisted)
└── requirements.txt            # Python dependencies
```

---

## Setup

### 1. Clone the Repository from GitHub

```
git clone https://github.com/yourusername/whatsapp_scheduler.git
cd whatsapp_scheduler
```

### 2. Set Up Python Environment with Conda

```f
conda create -n whatsapp-api python=3.12ff
conda activate whatsapp-api
pip install -r requirements.txt
```

### 3. Set Up Node.js Environment

Make sure you have **Node.js v18+** installed.

```
cd node_whatsapp
npm install
cd ..
```

### 4. Run the Flask API

```
python app.py
```

The API will start on [http://localhost:3000](http://localhost:3000)

---

## API Endpoints

| Endpoint         | Method | Description                                 |
|------------------|--------|---------------------------------------------|
| `/`              | GET    | Health check                                |
| `/qrcode`        | GET    | Get QR code for WhatsApp authentication     |
| `/send`          | POST   | Send text/image (form-data or base64)       |
| `/changesession` | POST   | Reset WhatsApp session                      |

---

### Example: Send a Message

```
curl -X POST http://localhost:3000/send \
  -F "phone=919900000000" \
  -F "message=Hello from API"
```

### Example: Send an Image

```
curl -X POST http://localhost:3000/send \
  -F "phone=919900000000" \
  -F "image=@/path/to/image.jpg"
```

### Example: Get QR Code

```
curl http://localhost:3000/qrcode
```

---

## WhatsApp Authentication

On first run, call `/qrcode` and scan the QR code with your WhatsApp mobile app.

---

## Security Notes

- **Do not expose this API publicly without authentication.**
- **Add HTTPS and authentication before production deployment.**
- **Adjust rate limits in `app.py` as needed.**

---

## License

Private repository. For internal or invited collaborator use only.
```
