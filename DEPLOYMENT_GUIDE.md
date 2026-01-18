# GITHUB DEPLOYMENT GUIDE
## Orthogonal Engineering Repository

---

## STEP 1: CREATE GITHUB REPOSITORY

1. Go to: **https://github.com/new**
2. Repository name: **`orthogonal-engineering`**
3. Description: **"A constraint-first methodology for extracting reliable outputs from unreliable AI systems"**
4. Select: **Public** (so GitHub Pages works for free)
5. **DO NOT** check "Add a README file" (we already have one)
6. Click: **Create repository**

---

## STEP 2: UPLOAD FILES

### Option A: Web Upload (Easiest)

1. On the empty repository page, click: **"uploading an existing file"**
2. Drag and drop the entire **`orthogonal-engineering`** folder from your outputs
3. Wait for upload to complete
4. Scroll down, enter commit message: **"Initial commit: Orthogonal Engineering methodology"**
5. Click: **Commit changes**

### Option B: GitHub Desktop (If you have it)

1. Open GitHub Desktop
2. File → Add Local Repository
3. Choose the `orthogonal-engineering` folder
4. Click "Publish repository"
5. Make sure "Keep this code private" is **unchecked**
6. Click "Publish Repository"

---

## STEP 3: ENABLE GITHUB PAGES

1. In your repository, click: **Settings** (top right)
2. Scroll down left sidebar, click: **Pages**
3. Under "Source", select: **Deploy from a branch**
4. Branch: **`main`** (or `master`)
5. Folder: **`/ (root)`**
6. Click: **Save**
7. Wait 1-2 minutes for deployment

---

## STEP 4: GET YOUR LIVE URL

After deployment completes, GitHub will show:
**"Your site is live at https://[your-username].github.io/orthogonal-engineering/"**

Example:
- If username is `tony_dev`: https://tony_dev.github.io/orthogonal-engineering/
- Theory page: https://tony_dev.github.io/orthogonal-engineering/theory/
- Workbench: https://tony_dev.github.io/orthogonal-engineering/workbench/

---

## STEP 5: UPDATE README (OPTIONAL)

The README has placeholder URLs like:
```
https://yourusername.github.io/orthogonal-engineering/
```

Replace `yourusername` with your actual GitHub username:

1. Click on `README.md` in the repository
2. Click the pencil icon (edit)
3. Find/replace all instances of `yourusername` with your actual username
4. Scroll down, commit changes

---

## VERIFICATION CHECKLIST

✅ Repository created and public
✅ All files uploaded (5 files total: 3 HTML, 1 README, 1 .gitignore)
✅ GitHub Pages enabled
✅ Live URL accessible
✅ All 3 pages load correctly:
   - Main guide (index.html)
   - Theory (theory/index.html)
   - Workbench (workbench/index.html)

---

## TROUBLESHOOTING

**Problem: "404 Page Not Found"**
- Solution: Wait 2-3 minutes, GitHub Pages takes time to build
- Check Settings → Pages to see deployment status

**Problem: "Files not showing up"**
- Solution: Make sure you uploaded the folder CONTENTS, not the folder itself
- The repo root should have `index.html`, not `orthogonal-engineering/index.html`

**Problem: "Pages not enabled in Settings"**
- Solution: Make sure repository is public (Settings → General → Change visibility)

---

## WHAT YOU'LL HAVE

📦 **Repository Structure:**
```
orthogonal-engineering/
├── .gitignore
├── README.md
├── index.html              (Main guide)
├── theory/
│   └── index.html         (Theory paper v3)
└── workbench/
    └── index.html         (Workbench tool v4)
```

🌐 **Live URLs:**
- Main: `https://[username].github.io/orthogonal-engineering/`
- Theory: `https://[username].github.io/orthogonal-engineering/theory/`
- Workbench: `https://[username].github.io/orthogonal-engineering/workbench/`

---

## NEXT STEPS

1. **Share the main URL** - Send to DeepSeek or whoever needs to see it
2. **Star your own repo** - Click the star button (makes it easier to find later)
3. **Add topics** - Settings → General → Topics: add `llm`, `ai`, `methodology`, `engineering`
4. **Tweet it** (optional) - Share your methodology with the AI engineering community

---

**Built with Kingdom OS principles: Deterministic, inspectable, ideology-agnostic.**
