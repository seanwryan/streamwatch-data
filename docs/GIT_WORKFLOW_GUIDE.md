# Git Branching Workflow Guide

**For:** StreamWatch Data Project  
**Purpose:** Understanding how to work with branches and merge changes

---

## 🎯 Quick Answer: What Should You Do?

**Current Situation:**
- You're on `main` branch (the main/production code)
- Angelo created a `sites-table` branch with his sites table work
- You've created scripts to complete the missing pieces

**What to Do:**
1. **Option A (Recommended):** Merge Angelo's branch into main first, then add your scripts
2. **Option B:** Add your scripts to Angelo's branch, then merge everything to main

---

## 📚 Understanding Git Branches

### What is a Branch?

Think of branches like **parallel universes** of your code:
- `main` = the "official" version everyone uses
- `sites-table` = a separate copy where Angelo worked on sites table changes
- You can switch between branches to see different versions

### Why Use Branches?

- **Isolation**: Work on features without breaking main
- **Collaboration**: Multiple people can work on different things
- **Safety**: Test changes before merging to main

---

## 🔄 Common Git Workflows

### Scenario 1: You Want to See Angelo's Work

```bash
# Switch to Angelo's branch
git checkout sites-table

# Look at files, test things
# ...

# Switch back to main when done
git checkout main
```

### Scenario 2: Merge Angelo's Branch into Main

```bash
# Make sure you're on main
git checkout main

# Get latest changes from remote
git fetch origin

# Merge Angelo's branch into main
git merge origin/sites-table

# Push to remote
git push origin main
```

### Scenario 3: Add Your Scripts to Angelo's Branch First

```bash
# Switch to Angelo's branch
git checkout sites-table

# Add your new scripts
git add scripts/schema/complete_sites_requirements.sql
git add scripts/schema/complete_sites_requirements.py
git add docs/SITES_TABLE_REVIEW.md

# Commit
git commit -m "Add scripts to complete sites table requirements"

# Push to remote (creates/updates remote branch)
git push origin sites-table

# Now merge to main
git checkout main
git merge sites-table
git push origin main
```

### Scenario 4: Add Scripts to Main (After Merging)

```bash
# Make sure you're on main
git checkout main

# Merge Angelo's branch first
git merge origin/sites-table

# Add your scripts
git add scripts/schema/complete_sites_requirements.sql
git add scripts/schema/complete_sites_requirements.py
git add docs/SITES_TABLE_REVIEW.md

# Commit
git commit -m "Add scripts to complete sites table requirements"

# Push
git push origin main
```

---

## 🚨 Important: Check Current Branch

**Always check which branch you're on:**

```bash
git branch
# Shows: * main  (the * means you're on main)
# Or:   * sites-table
```

**Or check status:**

```bash
git status
# Shows current branch at the top
```

---

## 📋 Step-by-Step: Recommended Workflow

### Step 1: Review Angelo's Work

```bash
# Switch to his branch
git checkout sites-table

# Look at what he did
ls scripts/schema/
cat scripts/schema/align_sites_with_requirements.sql

# Switch back
git checkout main
```

### Step 2: Merge Angelo's Branch

```bash
# Make sure you're on main
git checkout main

# Get latest from remote
git fetch origin

# Merge (this combines his changes into main)
git merge origin/sites-table

# If there are conflicts, Git will tell you
# Resolve them, then:
git add .
git commit -m "Merge sites-table branch"
```

### Step 3: Add Your Scripts

```bash
# You're already on main (from step 2)
# Add your new files
git add scripts/schema/complete_sites_requirements.sql
git add scripts/schema/complete_sites_requirements.py
git add docs/SITES_TABLE_REVIEW.md
git add docs/GIT_WORKFLOW_GUIDE.md

# Commit
git commit -m "Complete sites table requirements implementation"

# Push to remote
git push origin main
```

---

## 🔀 Understanding Merge vs Rebase

### Merge (What We're Doing)
- **Creates a merge commit** that combines two branches
- **Preserves history** - you can see when branches diverged
- **Safe** - doesn't rewrite history

```bash
git merge sites-table
# Creates a commit that says "merged sites-table into main"
```

### Rebase (Advanced - Don't Use Yet)
- **Replays commits** on top of another branch
- **Linear history** - looks like everything happened in order
- **Can be dangerous** if others are using the branch

**For now, stick with merge!**

---

## 🐛 Common Issues & Solutions

### Issue: "Your branch is ahead of 'origin/main'"

**Meaning:** You have local commits that aren't pushed yet

**Solution:**
```bash
git push origin main
```

### Issue: "Please commit your changes or stash them"

**Meaning:** You have uncommitted changes

**Solution:**
```bash
# Option 1: Commit them
git add .
git commit -m "Your message"

# Option 2: Stash them (save for later)
git stash
# Do your work
git stash pop  # Get them back
```

### Issue: Merge Conflicts

**Meaning:** Git can't automatically combine changes

**Solution:**
1. Git will mark conflicts in files with `<<<<<<<` markers
2. Open the file and look for conflicts
3. Edit to resolve (keep what you want)
4. Save file
5. `git add filename`
6. `git commit -m "Resolve merge conflicts"`

---

## 📖 Git Commands Cheat Sheet

```bash
# See current branch
git branch

# Switch branches
git checkout branch-name

# See what's changed
git status

# See commit history
git log --oneline

# Get latest from remote
git fetch origin

# Merge a branch
git merge branch-name

# Add files
git add filename
git add .  # All files

# Commit
git commit -m "Your message"

# Push to remote
git push origin main

# Pull latest (fetch + merge)
git pull origin main
```

---

## ✅ Checklist Before Pushing to Main

- [ ] You're on the `main` branch (`git branch`)
- [ ] You've tested your changes
- [ ] You've committed your changes (`git status` shows "nothing to commit")
- [ ] You've pulled latest from remote (`git pull origin main`)
- [ ] No merge conflicts
- [ ] You're ready to share with the team

---

## 🎓 Best Practices

1. **Always check your branch** before making changes
2. **Pull before you push** - get latest changes first
3. **Write clear commit messages** - describe what you did
4. **Test before merging** - make sure things work
5. **Communicate** - let team know when you're merging

---

## 💡 For This Specific Project

**Recommended Approach:**

1. **Merge Angelo's branch first:**
   ```bash
   git checkout main
   git merge origin/sites-table
   git push origin main
   ```

2. **Then add your completion scripts:**
   ```bash
   git add scripts/schema/complete_sites_requirements.*
   git add docs/SITES_TABLE_REVIEW.md
   git commit -m "Complete sites table requirements"
   git push origin main
   ```

This way:
- Angelo's work is in main
- Your completion scripts are added on top
- Everything is in one place
- History is clear

---

**Questions?** Check Git documentation or ask for help!
