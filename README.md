# AutoPost

**AutoPost** is a lightweight WebUI for AI-assisted WordPress content automation. A client or SEO agency can add topics, schedule them, generate an article and featured image, and send the result to WordPress.

**Default publishing mode: Draft Only.**

Developed by **Axon 1Pro**  
Website: https://axon.com.sg  
Support: support@axon.com.sg

## Commercial outline

- One-time setup: **USD 200**
- AutoPost hosting: **USD 150/year**
- OpenAI API: purchased and billed directly by the client
- Suggested initial OpenAI credit: **USD 5-10**

## V1 features implemented

- Secure client/admin login
- Professional responsive WebUI
- Dashboard with connection, queue, draft and failure status
- WordPress REST API connection
- OpenAI API connection
- Encrypted API key / WordPress Application Password storage
- Add topics
- Edit topics
- Disable / re-enable topics
- Delete topics
- Manual Generate Now
- Scheduled topics
- Automatic weekly/monthly queue
- Manual-only mode
- Article generation
- Title, excerpt, meta description, category, tags and image prompt generation
- Featured image generation
- WordPress Media Library upload
- Featured image assignment
- WordPress draft creation
- Optional Auto Publish
- Manual Publish button for created drafts
- Retry failed items
- Client brand memory editor
- Activity log
- Dedicated background worker
- Gunicorn + Nginx deployment
- Let's Encrypt / Certbot deployment instructions
- Axon 1Pro branding and support links

## How it works

~~~text
Client Login
    ↓
Add / Schedule Topics
    ↓
AutoPost checks the queue
    ↓
OpenAI creates article + SEO content + image
    ↓
Image uploads to WordPress Media Library
    ↓
Article goes to WordPress
    ↓
DRAFT by default
    ↓
Client reviews / edits
    ↓
Publish
~~~

## Publishing modes

### Draft Only
Recommended default. AutoPost creates a WordPress draft. Nothing goes live automatically.

### Approval Required
AutoPost creates a draft. The user can review it and use the AutoPost Publish action when ready.

### Auto Publish
AutoPost publishes directly according to the configured schedule. This must be explicitly enabled.

## Topic controls

Every topic can be:

- edited
- scheduled
- generated immediately
- disabled without deleting
- re-enabled later
- deleted
- retried after failure

Statuses include:

- ready
- scheduled
- generating
- draft_created
- failed
- published

## Brand memory

The initial client memory file is:

~~~text
clients/chezsuzette/MEMORY.md
~~~

It can contain:

- business description
- approved facts
- brand tone
- target audience
- preferred concepts
- keywords
- calls to action
- image style
- internal link guidance
- claims/topics to avoid

The WebUI includes a **Brand Memory** page so the client or administrator can update these instructions.

## Recommended initial settings

- Frequency: 2 posts per week
- Publishing: Draft Only
- Featured image: ON
- SEO content: ON
- Auto Publish: OFF

## Stack

- Python / Flask
- Flask-SQLAlchemy
- Flask-WTF CSRF protection
- SQLite for the first client
- OpenAI API
- WordPress REST API
- Gunicorn
- Nginx
- systemd
- Let's Encrypt / Certbot

For larger multi-client use, move the database to PostgreSQL and add per-tenant user/role management.

## Production deployment

Pilot domain:

~~~text
autopost.chezsuzette.sg
~~~

Target path:

~~~text
/var/www/autopost.chezsuzette.sg
~~~

### 1. DNS

Create an A record:

~~~text
Host: autopost
Type: A
Value: <German server public IP>
~~~

Wait until:

~~~bash
dig +short autopost.chezsuzette.sg
~~~

returns the German server IP.

### 2. Clone

~~~bash
cd /var/www
git clone https://github.com/amitaxonsg/autopost.git autopost.chezsuzette.sg
cd autopost.chezsuzette.sg
~~~

### 3. Run deployment helper

Run as root:

~~~bash
bash scripts/deploy_ubuntu.sh autopost.chezsuzette.sg support@axon.com.sg
~~~

The script installs Python, Nginx, Certbot and Git, creates the virtual environment, installs dependencies, creates systemd services, configures Nginx and generates secure Flask/Fernet keys.

### 4. Edit environment

Before client use:

~~~bash
nano /var/www/autopost.chezsuzette.sg/.env
~~~

Set at minimum:

~~~text
ADMIN_EMAIL=<login email>
ADMIN_PASSWORD=<strong unique password>
~~~

Do not paste client OpenAI or WordPress credentials into Git. Enter them through the AutoPost WebUI after login.

### 5. Restart

~~~bash
systemctl restart autopost autopost-worker
systemctl status autopost --no-pager
systemctl status autopost-worker --no-pager
~~~

### 6. Verify HTTP

~~~bash
curl -i http://autopost.chezsuzette.sg/healthz
~~~

Expected:

~~~json
{"app":"AutoPost","status":"ok"}
~~~

### 7. Activate SSL

Only after DNS resolves to this server:

~~~bash
certbot --nginx -d autopost.chezsuzette.sg \
  --email support@axon.com.sg \
  --agree-tos --no-eff-email --redirect
~~~

Then test:

~~~bash
curl -I https://autopost.chezsuzette.sg/healthz
certbot renew --dry-run
~~~

## WordPress setup

Create a dedicated WordPress integration account.

Recommended:

- username: autopost
- role: Editor for the pilot, so category/tag/media/post operations work
- create a WordPress Application Password for AutoPost
- do not use the client's normal WordPress password

Then open **Connections & Settings** in AutoPost and enter:

- WordPress website URL
- username
- Application Password
- Test Connection

## OpenAI setup

The client should use their own OpenAI API project and billing.

In AutoPost:

- enter the client's API key
- choose a low-cost text model available to their project
- choose the configured image model
- click Test Connection

The model names are configurable; the application is not tied to an expensive model.

## Security

Implemented:

- CSRF protection
- secure session cookie settings
- API/Application Password encryption using Fernet
- .env excluded from Git
- database excluded from Git
- dedicated WordPress Application Password support
- Draft Only default

Operational requirements:

- use HTTPS in production
- use a strong unique admin password
- protect the server and SSH access
- keep the generated CREDENTIAL_ENCRYPTION_KEY backed up securely
- never change the encryption key after credentials are saved unless credentials are re-entered
- do not commit .env or the production database

## Services

WebUI:

~~~bash
systemctl status autopost
journalctl -u autopost -f
~~~

Scheduler worker:

~~~bash
systemctl status autopost-worker
journalctl -u autopost-worker -f
~~~

## Updating from Git

~~~bash
cd /var/www/autopost.chezsuzette.sg
git pull --ff-only
source venv/bin/activate
pip install -r requirements.txt
systemctl restart autopost autopost-worker
~~~

## Important V1 note about SEO plugins

AutoPost generates a title, excerpt, meta description, category, tags and article structure. WordPress core does not expose every third-party SEO plugin's private meta fields through the same generic REST interface. Plugin-specific Yoast/RankMath field mapping should be added only if the client's chosen SEO plugin requires it.

## Repository status

V1 is coded for server deployment and UAT. Recommended rollout:

1. deploy on the German server
2. activate SSL
3. configure login
4. connect OpenAI
5. connect WordPress
6. add one test topic
7. confirm Draft Only workflow
8. confirm featured image
9. test scheduling
10. keep Auto Publish OFF until UAT is complete
