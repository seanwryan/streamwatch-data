# Digital Forms Options & Database Hosting Information

**Date:** December 2025

---

## Part 1: Options for Creating Digital Forms

PostgreSQL does **not** have built-in form creation capabilities like FileMaker Pro. You'll need a separate tool to create forms that connect to your PostgreSQL database.

### Recommended Options

#### **Softr** ⭐ Best for Quick Setup
- **Direct PostgreSQL connection** (no data duplication)
- **Pricing:** Free tier available, paid from $29/month
- **Best for:** Building forms that directly interact with PostgreSQL
- **Pros:** User-friendly, can build full applications, modern design
- **Cons:** Learning curve for complex forms

#### **Retool** ⭐ Best for Internal Tools
- **Direct PostgreSQL connection**
- **Pricing:** Free for up to 5 users, paid from $10/user/month
- **Best for:** Staff/admin forms for volunteer management
- **Pros:** Powerful form builder, direct queries, complex workflows
- **Cons:** More technical, primarily for internal use

#### **Budibase** ⭐ Best Budget Option
- **Direct PostgreSQL connection**
- **Pricing:** Free (open-source, self-hosted) or $8/month cloud
- **Best for:** Budget-friendly option with PostgreSQL integration
- **Pros:** Free, direct connection, full applications
- **Cons:** More setup if self-hosting

#### **Airtable**
- **PostgreSQL Integration:** Via Zapier (not direct)
- **Pricing:** Free tier, paid from $20/month
- **Best for:** Excel-like interface
- **Cons:** Data stored in Airtable, requires integration

#### **Custom Web Application** (Django/Next.js)
- **Direct PostgreSQL connection**
- **Pricing:** Free (open-source)
- **Best for:** Long-term, fully custom solution
- **Cons:** Requires programming knowledge and development time

### Other Options (Require Integration)
- **Jotform, Typeform, Zoho Forms:** Require Zapier to connect to PostgreSQL (adds cost and complexity)

### Quick Recommendations

- **Quick Setup (Non-Technical):** Softr or Retool
- **Long-Term Solution:** Custom Django or Next.js
- **Budget-Conscious:** Budibase (free, open-source)

---

## Part 2: Database Hosting Information

### Current Setup

**Provider:** Neon (neon.tech)  
**Type:** Cloud-hosted PostgreSQL (serverless)  
**Host:** `ep-wild-rice-ad71vs5v-pooler.c-2.us-east-1.aws.neon.tech`  
**Database:** `neondb`  
**Region:** US East (AWS)

### Is It Free?

**Yes, Neon offers a free tier:**

**Free Tier (Hobby Plan):**
- 0.5 GB storage
- Shared compute (may pause after inactivity)
- 7-day backup retention
- **Cost:** Free forever

**Paid Plans:**
- Launch: $19/month (10 GB, dedicated compute)
- Scale: $69/month (50 GB, higher performance)

**Check your plan:** Log into https://console.neon.tech → Your project → Billing/Plan section

### Is It Public?

**Yes, publicly accessible** but secured with:
- SSL/TLS encryption (required for all connections)
- Username/password authentication
- Two user accounts: `streamwatch_edit` (full access) and `streamwatch_readonly` (read-only)

### Database Status

- **Tables:** 19 tables
- **Records:** ~31,700 records
- **Status:** Fully operational
- **Access:** Via DBeaver, pgAdmin, command line, Python scripts, or form builders

### Important Notes

- Cloud-hosted (not local server)
- Publicly accessible but secure (requires authentication)
- Likely on free tier unless upgraded
- Auto-backups (7 days on free tier)
- May pause after inactivity on free tier (auto-resumes on connection)

---

## Summary

**Forms:** PostgreSQL has no built-in forms. Use **Softr** or **Retool** for quick setup, or **Django/Next.js** for custom development.

**Database:** Hosted on **Neon** (likely free tier), publicly accessible but secured, fully operational.

**Next Steps:**
1. Check Neon account for current plan/usage
2. Choose form-building option (Softr recommended for quick start)
3. Test with a simple form before building full system
