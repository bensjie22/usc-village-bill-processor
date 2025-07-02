# USC Village Bill Processor Web App

A complete web application for automatically separating batch utility bills into individual PDFs with proper naming conventions.

## 🚀 Quick Start for LJ

### What This App Does
- Upload a batch PDF with multiple utility bills
- Automatically separates each bill into individual PDF files
- Uses proper naming: `USC Village - [Suite#]-[Tenant] [Type] - [Month Year].pdf`
- Downloads a ZIP file with all separated bills + summary report

### Deploy to Vercel (Easy!)

1. **Upload to GitHub:**
   - Create a new repository on GitHub
   - Upload all the files from this folder to your repo

2. **Connect to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will automatically detect it's a React app

3. **Deploy:**
   - Click "Deploy" 
   - Wait 2-3 minutes
   - Your app will be live at a URL like `your-app-name.vercel.app`

That's it! No technical setup needed.

## 🛠️ Technical Details

### Frontend
- **React + Vite** - Modern, fast web framework
- **Tailwind CSS + shadcn/ui** - Beautiful, responsive design
- **Drag & drop file upload** - Easy to use interface
- **Real-time progress tracking** - Shows processing status

### Backend API
- **Python Flask** - Handles PDF processing
- **PyPDF2** - PDF manipulation library
- **CORS enabled** - Works with frontend

### Key Features
- ✅ **Smart extraction** - Uses the perfected patterns we developed
- ✅ **Electric vs Water bills** - Handles both types correctly
- ✅ **Duplicate handling** - Adds sequence numbers for multiple bills per tenant
- ✅ **Error handling** - Graceful fallbacks and user-friendly messages
- ✅ **ZIP download** - Packages everything neatly
- ✅ **Summary report** - Detailed processing results

## 📁 Project Structure

```
usc-village-app/
├── src/                    # Frontend React code
│   ├── App.jsx            # Main application
│   ├── components/ui/     # UI components
│   └── ...
├── api/                   # Backend Python API
│   ├── process.py         # Main processing logic
│   └── requirements.txt   # Python dependencies
├── package.json           # Frontend dependencies
├── vercel.json           # Vercel deployment config
└── README.md             # This file
```

## 🔧 Local Development (Optional)

If you want to run locally for testing:

1. **Install dependencies:**
   ```bash
   npm install --legacy-peer-deps
   cd api && pip install -r requirements.txt
   ```

2. **Start backend:**
   ```bash
   cd api && python process.py
   ```

3. **Start frontend:**
   ```bash
   npm run dev
   ```

4. **Open browser:**
   - Go to `http://localhost:5173`

## 🎯 How to Use the App

1. **Select Bill Type:** Electric or Water
2. **Enter Billing Period:** e.g., "May 2025"
3. **Upload PDF:** Drag & drop or click to browse
4. **Process:** Click "Process Bills" and wait
5. **Download:** Get your ZIP file with separated bills

## 🔍 Processing Logic

### Electric Bills
- Looks for suite-tenant info in the **SECOND line** after USC header
- Ignores utility codes like "UVIB4-MHC-Electric"
- Extracts actual tenant names like "344A-Amazon Electric Bill"

### Water Bills
- Finds suite-tenant info embedded in consumption data
- Patterns like "276.58344A-Amazon" or "$2,778.34344C-CafeDulce"

### Validation
- Checks if extracted names are real businesses (not utility codes)
- Uses fallback naming for unreadable bills
- Handles duplicates with sequence numbers

## 📦 Output

Creates individual PDFs with naming convention:
```
USC Village - 344A-Amazon Electric - May 2025.pdf
USC Village - 348C-Starbucks Electric - May 2025.pdf
USC Village - 347F-City Tacos Electric - May 2025.pdf
...
```

Plus a summary report with processing details.

## 🚨 Troubleshooting

**If deployment fails:**
- Make sure all files are uploaded to GitHub
- Check that `vercel.json` is in the root directory
- Vercel should auto-detect the Python API

**If processing fails:**
- Check that the PDF is a valid utility bill batch
- Make sure bill type (Electric/Water) is correct
- Try a smaller file first

**If download doesn't work:**
- The download should start automatically
- Check your browser's download folder
- Try right-clicking the download button

## 💡 Tips for LJ

- **Test with a small batch first** - Upload a 2-3 page PDF to test
- **Check the naming** - Make sure extracted tenant names look right
- **Save the URL** - Bookmark your deployed app for easy access
- **Share with team** - Anyone can use the web app once deployed

## 🎉 Success!

You now have a professional web app that:
- Saves hours of manual work
- Ensures consistent naming
- Works from any device with internet
- Processes bills automatically
- Provides detailed reports

No more manual PDF splitting! Just upload, process, and download. 🚀

