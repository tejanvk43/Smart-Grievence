#!/bin/bash
cd /workspaces/Smart-Grievence
git add .
git commit -m "feat: Enhanced Django backend with admin seeding and officer creation

Features:
- Add default admin user (admin@smartgriev.com/Admin@123) in seed_db command
- Block ADMIN/OFFICER registration via public endpoint (403 forbidden)
- Force all public registrations to CITIZEN role only
- Add POST /api/admin/users endpoint for admin to create officers
- Update GET /api/departments to return string array instead of objects

Frontend Updates:
- Add officer creation UI in AdminDashboard with modal form
- Disable role selector during registration in LandingPage
- Add createOfficer() method in API service
- Department dropdown auto-populated from backend

Configuration:
- Remove *.db and *.sqlite3 from .gitignore to track seeded database
- Add comprehensive documentation (CHANGES_SUMMARY.md, QUICK_TEST_GUIDE.md)

Security:
- Role-based registration restrictions
- Admin-controlled officer account creation
- JWT authentication for admin operations"
git push origin main
