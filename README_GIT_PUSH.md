# Git Push Guide — Week 2 (Shrinivas)

**Milestone**: Week 2 &bull; Phase 2 — Authentication, Multi-Tenancy & Engine REST Client  
**Author**: Shrinivas (Dev-B / Dev-2) &bull; Roll: `01fe24bca311`  
**Repository**: `Product-Catalogue-Ranked-Search`  
**Target Branch**: `week2-tenant`  

---

## 1. Overview of Delivered Files

Extract the contents of this zip file directly into your local **`Product-Catalogue-Ranked-Search`** repository root directory.

The following files are packaged in this update:
- `app/admin/__init__.py`
- `app/admin/forms.py`
- `app/templates/admin/company_list.html`
- `app/templates/admin/company_form.html`
- `app/templates/admin/platform_dashboard.html`
- `knowledgebase.md`
- `function_map.md`

---

## 2. Step-by-Step GitHub Push Instructions

### Step 1: Open repository and ensure `main` is clean
```bash
cd /path/to/Product-Catalogue-Ranked-Search
git checkout main
git pull origin main
```

### Step 2: Create and checkout the feature branch `week2-tenant`
```bash
git checkout -b week2-tenant
```

### Step 3: Copy packaged files into repository
Extract this zip file into your `Product-Catalogue-Ranked-Search` folder, preserving the relative folder paths (`app/`, `docs/`, `tests/`, etc.).

### Step 4: Stage, commit, and push to GitHub
```bash
git add "app/admin/__init__.py" "app/admin/forms.py" "app/templates/admin/company_list.html" "app/templates/admin/company_form.html" "app/templates/admin/platform_dashboard.html" "knowledgebase.md" "function_map.md"
git commit -m "[Dev-B] P2: Add company CRUD, tenant isolation"
git push -u origin week2-tenant
```

### Step 5: Merge into `main` and synchronize remote
```bash
git checkout main
git merge week2-tenant
git push origin main
```

---

*Package verified and generated automatically for BCA Mini-Project.*
