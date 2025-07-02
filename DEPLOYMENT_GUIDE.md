# 🚀 Deployment Guide for LJ

## Step-by-Step Vercel Deployment

### Prerequisites
- A GitHub account (free)
- A Vercel account (free) - sign up at [vercel.com](https://vercel.com)

### Step 1: Upload to GitHub

1. **Create a new repository:**
   - Go to [github.com](https://github.com)
   - Click the green "New" button
   - Name it something like `usc-village-bill-processor`
   - Make it Public (easier for deployment)
   - Click "Create repository"

2. **Upload your files:**
   - Click "uploading an existing file"
   - Drag and drop ALL the files from the `usc-village-app` folder
   - Write a commit message like "Initial upload"
   - Click "Commit changes"

### Step 2: Deploy to Vercel

1. **Connect GitHub to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "Sign up" and choose "Continue with GitHub"
   - Authorize Vercel to access your GitHub

2. **Import your project:**
   - Click "New Project"
   - Find your `usc-village-bill-processor` repository
   - Click "Import"

3. **Configure deployment:**
   - **Project Name:** Keep the default or change it
   - **Framework Preset:** Should auto-detect "Vite"
   - **Root Directory:** Leave as `./`
   - **Build Command:** Should be `npm run build`
   - **Output Directory:** Should be `dist`

4. **Deploy:**
   - Click "Deploy"
   - Wait 2-3 minutes for deployment to complete
   - You'll get a live URL like `your-app-name.vercel.app`

### Step 3: Test Your App

1. **Visit your live app:**
   - Click the URL Vercel provides
   - You should see the USC Village Bill Processor interface

2. **Test with a small file:**
   - Upload a 2-3 page PDF
   - Select "Electric" bill type
   - Enter "May 2025" as billing period
   - Click "Process Bills"
   - Download should work automatically

### Step 4: Bookmark and Share

- **Save the URL** - This is your permanent web app
- **Share with team** - Anyone can use this URL
- **No maintenance needed** - Vercel handles everything

## 🔧 If Something Goes Wrong

### Common Issues and Fixes

**"Build failed" error:**
- Make sure all files were uploaded to GitHub
- Check that `package.json` is in the root directory
- Try deploying again (sometimes it's just a temporary issue)

**"Function timeout" error:**
- This happens with very large PDF files
- Try with smaller files first
- The free Vercel plan has a 10-second timeout

**API not working:**
- Make sure `vercel.json` was uploaded
- Check that the `api` folder is in your GitHub repo
- Vercel should automatically detect Python functions

**Download not working:**
- This might happen on the free plan with large files
- Try with smaller PDFs first
- The processing works, but download might timeout

### Alternative: Local Hosting

If Vercel doesn't work perfectly, you can run it locally:

1. **Download the files** to your computer
2. **Install Python** (if not already installed)
3. **Run the backend:**
   ```
   cd api
   pip install -r requirements.txt
   python process.py
   ```
4. **Run the frontend:**
   ```
   npm install --legacy-peer-deps
   npm run dev
   ```
5. **Use at** `http://localhost:5173`

## 🎯 Pro Tips

1. **Test incrementally:**
   - Start with a 2-page PDF
   - Then try 5 pages
   - Then your full batch

2. **Check the extraction:**
   - Look at the summary report
   - Make sure tenant names look right
   - If they're wrong, the PDF might need the corrected patterns

3. **Bookmark everything:**
   - Your GitHub repo
   - Your Vercel dashboard
   - Your live app URL

4. **Share wisely:**
   - The app is public once deployed
   - Only share the URL with people who need it
   - No sensitive data is stored

## 🎉 You're Done!

Once deployed, you have:
- ✅ A professional web application
- ✅ Accessible from anywhere with internet
- ✅ No software to install or maintain
- ✅ Automatic bill processing
- ✅ Professional results every time

Your USC Village bill processing just got 100x easier! 🚀

