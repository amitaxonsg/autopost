# AutoPost

AutoPost is a simple WebUI for clients and SEO agencies to plan AI-assisted WordPress content, generate articles and featured images, and send them to WordPress as **drafts by default**.

## Commercial Outline

- One-time setup: **USD 200**
- AutoPost hosting: **USD 150/year**
- OpenAI API: client purchases directly from OpenAI; suggested initial top-up **USD 5-10**
- OpenAI usage is paid directly by the client.

## Recommended Starting Mode

- 2 posts per week
- Featured image generation: ON
- SEO metadata: ON
- Publishing mode: **Draft Only**
- Auto-publish: OFF

## Non-Technical Workflow

```text
Client Login
    ↓
Add Topic / Schedule Topics
    ↓
AutoPost Generates Article + SEO + Image
    ↓
Send to WordPress
    ↓
DRAFT
    ↓
Client Reviews / Edits
    ↓
Publish
```

## WebUI

### Dashboard
Shows:
- WordPress connection status
- OpenAI connection status
- Automation ON/OFF
- Posts per week/month
- Drafts ready
- Next scheduled article
- Recent activity
- Failed jobs

### Topics & Schedule
Client can:
- Add a topic
- Edit a topic
- Enable/disable a topic
- Delete a topic
- Add keywords
- Select category
- Add notes
- Set target date/time
- Generate immediately
- View all scheduled topics
- View all completed drafts
- Retry failed items

Suggested statuses:
- `ready`
- `disabled`
- `scheduled`
- `generating`
- `draft_created`
- `failed`
- `published`

### Automation
Modes:
- Manual only
- Posts per week
- Posts per month
- Custom schedule

Settings:
- Frequency
- Preferred weekdays
- Preferred time
- Timezone
- Generate featured image ON/OFF
- SEO metadata ON/OFF
- Publishing mode

### Publishing Modes

#### Draft Only
Default and recommended. Nothing goes live automatically.

#### Approval Required
Generate first, then wait for user approval before publishing.

#### Auto Publish
Optional. Must be explicitly enabled by the client.

## WordPress Connection

Use:
- Website URL
- Dedicated WordPress username
- WordPress Application Password
- Test Connection button

Do **not** use the client's normal WordPress password.

## OpenAI Connection

Use:
- Provider: OpenAI
- Client's API key
- Recommended low-cost model
- Test Connection button

The client purchases API credits directly from OpenAI.

## Client Memory / Brand Preferences

Each client gets a memory file, e.g.:

`clients/chezsuzette/MEMORY.md`

It can contain:
- Business description
- Brand voice
- Target audience
- Important facts
- Preferred wording
- Topics to emphasize
- Topics to avoid
- Prohibited claims
- CTA wording
- SEO priorities
- Image direction
- Preferred internal links

AutoPost should include this memory when generating future content.

## Initial Stack

- Python 3.12+
- Flask
- SQLAlchemy
- SQLite for V1
- APScheduler for V1
- OpenAI API
- WordPress REST API
- Gunicorn
- Nginx
- Let's Encrypt

For multiple clients later, move the database to PostgreSQL and encrypt per-client secrets.

## Initial Deployment

Pilot domain:

`autopost.chezsuzette.sg`

Suggested server path:

`/var/www/autopost.chezsuzette.sg`

## Build Phases

### Phase 1
- DNS
- Server directory
- Python virtual environment
- Flask app
- Login
- Dashboard
- SSL

### Phase 2
- WordPress connection
- OpenAI connection
- Test Connection buttons

### Phase 3
- Topic CRUD
- Edit/disable/delete
- Scheduling
- Queue/status view

### Phase 4
- AI article generation
- SEO title
- Excerpt
- Meta description
- Tags/categories
- Client memory injection

### Phase 5
- AI featured image generation
- Upload to WordPress Media Library
- Assign featured image

### Phase 6
- WordPress Draft creation
- Approval mode
- Optional auto-publish
- Activity logs
- Retry failed jobs

## Security

Before public production:
- HTTPS only
- Secure session cookies
- CSRF protection
- Rate limiting
- Encrypted API keys and WordPress credentials
- Dedicated WordPress integration account
- WordPress Application Passwords
- Audit log for publishing actions
- Never commit real secrets to Git

## V1 Status

This repository starts as a V1 scaffold and product blueprint. The first live deployment should remain **Draft Only** until the workflow is fully tested.
