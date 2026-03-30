# OCR Models Installation Guide

The SCAN page now supports three OCR models for text extraction:

## 1. **Tesseract OCR** (Default)
- Lightweight and fast
- Good for basic text recognition
- Already installed

### Installation:
```bash
pip install pytesseract
```

Also requires Tesseract system installation:
- **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

---

## 2. **PaddleOCR** (Recommended)
- High accuracy multi-language OCR
- Faster than Tesseract for complex text
- Better with multiple languages
- Downloads model automatically (first use ~200MB)

### Installation:
```bash
pip install paddleocr
```

### Features:
- Supports 80+ languages
- Handles rotated text well
- Higher accuracy than Tesseract

---

## 3. **Docext** (Document Text Recognition)
- Specialized for document OCR
- Excellent for structured text
- Higher precision on clean documents
- Requires more resources

### Installation:
```bash
pip install python-doctr
```

### Features:
- Document layout analysis
- Better word spacing
- Handles complex layouts

---

## How to Use

1. Open the **SCAN** tab in the app
2. Select your preferred OCR model from the dropdown: **Tesseract**, **PaddleOCR**, or **Docext**
3. Set your capture area using the **SELECTOR** button
4. Click **EXTRACT** to test single extraction or start continuous capture
5. The app will use the selected model for text extraction

## Performance Comparison

| Feature | Tesseract | PaddleOCR | Docext |
|---------|-----------|-----------|-------|
| Speed | Fast | Medium | Slow |
| Accuracy | Good | Excellent | Excellent |
| Languages | Multiple | 80+ | English |
| Memory | Low | High | Very High |
| First Run | Instant | ~200MB download | ~500MB download |

## Installation All at Once

```bash
pip install pytesseract paddleocr python-doctr
```

## Troubleshooting

**PaddleOCR not found:**
- Make sure it's installed: `pip install paddleocr`
- First run will download the model automatically

**Docext not found:**
- Make sure it's installed: `pip install python-doctr`
- First run will download the model automatically

**Fallback behavior:**
- If your selected model fails, the app automatically falls back to Tesseract
- Check console output for error messages

## Recommendations

- **For speed**: Use **Tesseract**
- **For accuracy**: Use **PaddleOCR** (recommended)
- **For documents**: Use **Docext**
