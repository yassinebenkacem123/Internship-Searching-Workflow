# Skill: notion-sync

## Purpose

Use Notion as the internship CRM.

## One internship = one Notion record

Recommended properties:

```text
Position
Company
Status
Match Score
Location
Work Mode
Posted Date
Found Date
Source
Main Job Link
LinkedIn Job
LinkedIn Post
Indeed
ReKrute
Company Careers
ATS URL
Recruiter
Recruiter LinkedIn
Contact Email
Required Skills
Missing Skills
Internship Type
Notes
```

## Existing record

Update:

- newly discovered source URLs
- missing recruiter information
- required skills
- description
- posted date if newly verified

Do NOT overwrite:

- Status
- Notes
- application history
- interview notes
- user decisions

## New record

Default:

```text
Status = New
```

## Lookup

Prefer:

```text
normalized_company + normalized_position
```

Also consider direct URL matches.

## Failure handling

One failed Notion write must not corrupt the entire workflow.
