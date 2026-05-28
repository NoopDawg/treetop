# Changelog

## 2.0.0

Initial open-source release.

- All AWS resource IDs are now user-configured (no hardcoded defaults)
- `treetop init` provides a full interactive setup flow including launch template creation
- `treetop create-template` is now a first-class command
- AWS region is configurable per environment
- Modern Python packaging (hatchling, PEP 621)
- Removed GCP-era artifacts (suspend_on_idle)
- Added IAM permissions documentation
- Added setup guide for new AWS environments
