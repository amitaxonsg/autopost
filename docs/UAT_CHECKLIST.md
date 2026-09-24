# AutoPost UAT Checklist

Developed by **Axon 1Pro**  
https://axon.com.sg  
support@axon.com.sg

Use this checklist after deploying to the German server.

## Server

- [ ] DNS for autopost.chezsuzette.sg resolves to the German server
- [ ] Nginx configuration passes nginx -t
- [ ] autopost.service is active
- [ ] autopost-worker.service is active
- [ ] /healthz returns HTTP 200
- [ ] Let's Encrypt certificate is active
- [ ] HTTP redirects to HTTPS
- [ ] certbot renew --dry-run succeeds

## Login

- [ ] Login page loads
- [ ] Correct credentials work
- [ ] Incorrect credentials fail
- [ ] Logout works
- [ ] Axon 1Pro footer, axon.com.sg and support@axon.com.sg are visible

## WordPress

- [ ] Dedicated AutoPost WordPress account exists
- [ ] Application Password created
- [ ] Test WordPress Connection succeeds
- [ ] No normal WordPress password is stored in AutoPost

## OpenAI

- [ ] Client owns the API project/billing
- [ ] API key entered in WebUI
- [ ] Low-cost supported text model selected
- [ ] Image model selected
- [ ] Test OpenAI Connection succeeds

## Topic workflow

- [ ] Add topic
- [ ] Edit topic
- [ ] Add keywords
- [ ] Add category
- [ ] Add notes
- [ ] Schedule a date/time
- [ ] Disable topic
- [ ] Re-enable topic
- [ ] Delete test topic
- [ ] Generate Now works
- [ ] Failed job displays an error
- [ ] Retry returns failed job to queue

## Article / image

- [ ] Article title generated
- [ ] Body formatting is acceptable
- [ ] No invented business claims
- [ ] Featured image generated
- [ ] Image uploads to WordPress Media Library
- [ ] Image alt text is present
- [ ] Category/tags are applied when WordPress permissions allow
- [ ] Post appears as DRAFT

## Publishing safety

- [ ] Default publishing mode is Draft Only
- [ ] Test generation does not publish live
- [ ] Manual Publish action requires deliberate click
- [ ] Auto Publish remains OFF during pilot UAT

## Automation

- [ ] Manual mode does not process queue automatically
- [ ] Weekly mode processes at the expected cadence
- [ ] Monthly mode processes at the expected cadence
- [ ] Preferred time works
- [ ] Timezone is correct
- [ ] Explicit scheduled topic takes priority when due
- [ ] Disabled topic is never processed

## Brand memory

- [ ] Brand Memory page loads
- [ ] Memory can be edited and saved
- [ ] Generated article follows approved brand tone
- [ ] Restricted claims are avoided
- [ ] Approved CTA / concepts are followed

## Final pilot approval

- [ ] Client has reviewed at least 3 generated drafts
- [ ] Client approves article quality
- [ ] Client approves image quality
- [ ] Client approves scheduling
- [ ] Backup of .env and encryption key stored securely
- [ ] Auto Publish remains disabled unless explicitly approved
