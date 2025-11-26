# 📧 HTML Email Preview - Interest Form Notification

## Email Features

✅ **Professional HTML Design** with gradient header  
✅ **Organized Table Layout** for easy reading  
✅ **Color-Coded Sections** with emoji icons  
✅ **Clickable Links** for email, phone, LinkedIn, and GitHub  
✅ **Resume File Attachment** (if provided)  
✅ **Responsive Design** that works on all email clients  
✅ **Plain Text Fallback** for non-HTML email clients  

---

## What the Email Looks Like

### Header Section
- **Gradient purple header** with submission date
- Subject line: `🎯 New Interest Submission - [First Name] [Last Name]`

### 1. 👤 Candidate Information (Table)
| Field | Value |
|-------|-------|
| Full Name | [First Name] [Last Name] (bold) |
| Email Address | [email@example.com] (clickable) |
| Phone Number | [phone] (clickable) |

### 2. 🎓 Education Details (Table)
| Field | Value |
|-------|-------|
| University | [University Name] |
| Degree | [Bachelor's/Master's/PhD] |
| Major | [Major/Field of Study] |
| Graduation Date | [MM/YYYY] |

### 3. 🌍 Visa & Employment Status (Table)
| Field | Value |
|-------|-------|
| Visa Status | [F1-OPT/H1B/etc.] (badge style) |
| OPT End Date | [Date or N/A] |

### 4. 📋 Additional Information (Table)
| Field | Value |
|-------|-------|
| Referral Source | [Google/LinkedIn/Friend/etc.] |
| LinkedIn Profile | [URL] (clickable link) |
| GitHub Profile | [URL] (clickable link) |
| Resume | ✓ Attached (green badge) or Not provided |
| Additional Notes | [Free text or None] |

### Footer
- Automated notification message
- Submission ID (UUID)

---

## Color Scheme

- **Primary Color**: Purple gradient (#667eea to #764ba2)
- **Section Titles**: Purple (#667eea)
- **Table Headers**: Light gray (#f8f9fa)
- **Borders**: Light gray (#e0e0e0)
- **Success Badge**: Green (#d4edda)
- **Warning Badge**: Yellow (#fff3cd)
- **Text**: Dark gray (#333)

---

## Email Clients Compatibility

✅ **Gmail** - Full support  
✅ **Outlook** - Full support  
✅ **Apple Mail** - Full support  
✅ **Yahoo Mail** - Full support  
✅ **Mobile Clients** - Responsive design  
✅ **Plain Text** - Fallback version included  

---

## Resume Attachment

When a resume file is uploaded:
- ✅ **Automatically attached** to the email
- ✅ Preserves original filename (e.g., `john_doe_resume.pdf`)
- ✅ Works with PDF and DOCX formats
- ✅ Shows "✓ Attached to this email" badge in the table

---

## Testing the Email

Run the test script to see the actual email:

```bash
python test_email.py
```

For console output (without sending):
```env
# In .env file
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

For real email sending:
```env
# In .env file
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## Example Email Preview

```
Subject: 🎯 New Interest Submission - Jane Smith

┌─────────────────────────────────────────────────────┐
│  🎯 New Interest Form Submission                    │
│  Submission received on November 26, 2025 at 2:30 PM│
│  [Gradient Purple Background]                        │
└─────────────────────────────────────────────────────┘

👤 Candidate Information
┌─────────────────────┬─────────────────────────────┐
│ Full Name           │ Jane Smith                   │
│ Email Address       │ jane.smith@example.com       │
│ Phone Number        │ (555) 123-4567              │
└─────────────────────┴─────────────────────────────┘

🎓 Education Details
┌─────────────────────┬─────────────────────────────┐
│ University          │ Stanford University          │
│ Degree              │ Master's                     │
│ Major               │ Computer Science             │
│ Graduation Date     │ 2026-05-01                  │
└─────────────────────┴─────────────────────────────┘

🌍 Visa & Employment Status
┌─────────────────────┬─────────────────────────────┐
│ Visa Status         │ [F1-OPT]                    │
│ OPT End Date        │ 2027-05-01                  │
└─────────────────────┴─────────────────────────────┘

📋 Additional Information
┌─────────────────────┬─────────────────────────────┐
│ Referral Source     │ LinkedIn                     │
│ LinkedIn Profile    │ linkedin.com/in/janesmith    │
│ GitHub Profile      │ github.com/janesmith         │
│ Resume              │ ✓ Attached to this email    │
│ Additional Notes    │ Passionate about backend dev │
└─────────────────────┴─────────────────────────────┘

───────────────────────────────────────────────────────
This is an automated notification from the 
Hyrind Interest Form System
Submission ID: 550e8400-e29b-41d4-a716-446655440000
```

---

## Key Improvements Over Plain Text

1. **Visual Hierarchy** - Easy to scan and find information
2. **Professional Appearance** - Makes a great impression
3. **Clickable Elements** - One-click access to email, phone, profiles
4. **Resume Attached** - No need to log into the admin panel
5. **Color Coding** - Important info stands out
6. **Mobile Friendly** - Looks great on all devices
7. **Branded** - Consistent with professional email standards

---

## Technical Details

- Uses `EmailMultiAlternatives` for HTML + plain text
- Inline CSS for maximum compatibility
- Failsafe design (email errors won't break form submission)
- Automatic file attachment handling
- UTF-8 encoding for international characters
- Proper MIME type handling

---

The email system is now production-ready with professional HTML formatting! 🎉
