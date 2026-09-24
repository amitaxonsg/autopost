# AutoPost V1 Product Blueprint

Developed by **Axon 1Pro** — https://axon.com.sg — support@axon.com.sg

## Objective

A non-technical WebUI where a client or SEO agency can manage WordPress content automation without using n8n or editing scripts.

## Client journey

1. Login
2. View dashboard
3. Connect WordPress
4. Connect OpenAI
5. Add topics
6. Edit, schedule, enable or disable topics
7. Set posting frequency
8. AutoPost generates article and image
9. AutoPost sends the post to WordPress
10. Draft Only by default
11. Client reviews
12. Client publishes, or optionally enables Auto Publish

## Dashboard

Displays:

- WordPress connection
- OpenAI connection
- automation on/off
- publishing mode
- ready count
- scheduled count
- drafts count
- failures
- next topic
- recent topics
- activity log

## Topics & schedule

Fields:

- topic
- keywords
- category
- notes
- scheduled date/time
- enabled
- status

Actions:

- edit
- enable/disable
- generate now
- retry
- open WordPress result
- publish a draft
- delete

## Automation

Modes:

- Manual only
- Posts per week
- Posts per month

Automatic topics without an explicit date are selected from the ready queue based on cadence. Explicit scheduled topics take priority when due.

## AI generation

Per topic, AutoPost requests:

- title
- excerpt
- meta description
- category
- tags
- image prompt
- image alt text
- WordPress-ready HTML

## Images

When enabled:

1. generate image
2. upload image to WordPress Media Library
3. set alt text
4. assign as featured image

## WordPress

Uses WordPress REST API and a dedicated Application Password.

Default post status is draft.

## Memory

The client memory is editable in the WebUI and included with article-generation instructions.

It should hold approved facts, tone, concepts, SEO direction, CTA wording, restrictions and image guidance.

## Security

- HTTPS
- CSRF
- secure sessions
- encrypted client credentials
- .env excluded from Git
- database excluded from Git
- dedicated WordPress integration credentials

## Deployment

- German Ubuntu server
- Gunicorn web service
- separate scheduling worker
- Nginx reverse proxy
- Certbot SSL
- domain: autopost.chezsuzette.sg

## Commercial outline

- Setup: USD 200 one time
- Hosting: USD 150/year
- OpenAI API: client purchases directly; suggested starting credit USD 5-10
