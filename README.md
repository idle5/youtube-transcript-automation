# YouTube Playlist Transcript Automation

> **Purpose:** Automated bulk transcript extraction tool built to support technical certification study and knowledge base management.

A Python-based automation solution that demonstrates practical systems thinking, API integration, and process optimization skills applicable to IT operations and infrastructure roles.

## 🎯 Objective

Developed as part of CCNA certification preparation to automate the conversion of video-based technical content into searchable text documentation. Solves the operational challenge of managing large-scale educational content by implementing a resilient, optionally proxy-enabled scraping workflow.

**Real-World Application:** Transformed 100+ hours of network engineering video content into a searchable knowledge base, reducing study material lookup time from minutes to seconds.

## 🛠️ Technologies & Skills Demonstrated

- **Python 3** - Core automation scripting
- **API Integration** - YouTube Transcript API implementation with error handling
- **Optional Proxy Management** - Webshare proxy configuration for rate-limit mitigation (when needed)
- **Secure Configuration** - Environment-based credential management (dotenv)
- **Error Handling** - Multi-level exception handling with graceful degradation and retry logic
- **Virtual Environment Management** - Isolated dependency management following Python best practices
- **File System Operations** - Dynamic directory management and filename sanitization

## ⚙️ Key Features

- **Bulk Processing**: Iterates through playlists of any size with progress tracking
- **Idempotent Operations**: Automatically skips existing files to enable resume capability
- **Fallback Logic**: Attempts multiple transcript sources (manual → auto-generated → generic)
- **Configurable Rate Limiting**: Implements polite delays to respect API constraints
- **Optional Proxy Support**: Can run with or without proxy service based on playlist size
- **Clean Output**: Formats transcripts as plain text with sanitized filenames
- **Professional Logging**: Creates detailed log files for troubleshooting and audit trails

## 🏠 Lab Environment Context

Built and tested in a home lab environment as part of hands-on skill development for:
- **CCNA Certification** (currently pursuing)
- Systems administration fundamentals
- Automation and scripting best practices
- Understanding API interactions and network constraints

This project reflects a systematic approach to filling knowledge gaps through self-directed learning and practical tool-building—core competencies for technical support and infrastructure roles.

## 🚀 Quick Start

### Prerequisites
- Python 3.7+ (tested with Python 3.13)
- Optional: Webshare proxy account (only needed for very large playlists or if you hit rate limits)

### Installation

#### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/youtube-transcript-automation.git
cd youtube-transcript-automation
```

#### Step 2: Set Up Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# On Windows (CMD):
venv\Scripts\activate.bat

# Upgrade pip (optional but recommended)
pip install --upgrade pip
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root with your settings:

#### Option A: Without Proxy (Recommended Starting Point)
**Best for playlists under 50-100 videos**

```ini
# Basic configuration - no proxy needed
USE_PROXY=false
PLAYLIST_URL=https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID
OUTPUT_FOLDER=transcripts
```

**Note:** Without a proxy, you may hit YouTube's rate limits on very large playlists (100+ videos). If this happens, you'll see errors and can then enable proxy support.

#### Option B: With Proxy (For Large Playlists or Rate Limiting)
**Use this if you're processing 100+ videos or encountering rate limit errors**

```ini
# Proxy configuration for high-volume processing
USE_PROXY=true
PROXY_USER=your_webshare_username
PROXY_PASS=your_webshare_password
PLAYLIST_URL=https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID
OUTPUT_FOLDER=transcripts
```

**Getting Webshare Proxy (if needed):**
1. Sign up at [webshare.io](https://www.webshare.io/)
2. Free tier includes 10 proxies (sufficient for most use cases)
3. Get credentials from your dashboard

### Usage

#### Basic Usage
```bash
# 1. Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# 2. Update PLAYLIST_URL in .env file with your target playlist

# 3. Run the script
python main.py
```

Transcripts are saved to the `transcripts/` directory with format: `[video_id] - title.txt`

#### Advanced Configuration (Optional)

You can customize behavior through additional `.env` variables:

```ini
# Custom output directory
OUTPUT_FOLDER=my_transcripts

# Adjust retry attempts (default: 3)
RETRY_ATTEMPTS=5

# Adjust rate limit delay in seconds (default: 0.5)
RATE_LIMIT_DELAY=1.0
```

### Troubleshooting

#### Issue: "No transcript available" errors
**Cause:** Video doesn't have transcripts enabled, or you're hitting rate limits

**Solutions:**
1. Check if the video actually has captions on YouTube
2. If processing 100+ videos without proxy, enable proxy support
3. Increase `RATE_LIMIT_DELAY` in .env to slow down requests

#### Issue: Rate limit errors (429)
**Cause:** Too many requests without proxy

**Solution:** Enable proxy in .env:
```ini
USE_PROXY=true
PROXY_USER=your_credentials
PROXY_PASS=your_credentials
```

#### Issue: Virtual environment not activating
**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

#### Issue: Dependencies won't install
**Solution:** Upgrade pip first:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 📊 Performance Metrics

- Processes 100+ videos in ~15 minutes (with rate limiting and proxy)
- 95%+ success rate on publicly available transcripts
- Handles playlist updates incrementally (skip existing files)
- Idempotent operations allow resume after interruption

## 🔄 Future Enhancements

- [ ] CLI argument support for playlist URL and output directory
- [ ] Configurable retry logic with exponential backoff (partially implemented)
- [ ] Structured logging with rotation
- [ ] Multi-threading for improved throughput
- [ ] Database integration for metadata tracking
- [ ] Support for additional video platforms

## 📝 Use Case: CCNA Study Workflow

1. **Extraction**: Bulk download transcripts from comprehensive video courses (Jeremy's IT Lab, NetworkChuck, etc.)
2. **Indexing**: Build searchable text corpus of 100+ hours of content
3. **Analysis**: Use LLM tools to generate summaries and extract key concepts
4. **Validation**: Cross-reference generated content with personal flashcard deck
5. **Result**: Reduced time to locate specific concepts (OSPF, STP, subnetting) from 10+ minutes to <30 seconds

This workflow demonstrates practical problem-solving and process optimization mindset applicable to IT operations.

## ⚠️ Disclaimer

This tool is intended for personal educational use. Users are responsible for ensuring compliance with YouTube's Terms of Service and applicable copyright laws. Only download transcripts from content you have the right to access for personal study purposes.

## 🤝 Contributing

This is a personal learning project built as part of my CCNA certification preparation. Feel free to fork or use as reference for your own projects.
---

**Author:** idle5 
**Context:** Built during career transition from fitness/personal training to IT infrastructure roles

