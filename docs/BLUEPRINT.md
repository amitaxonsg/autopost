# AutoPost V1 Blueprint

## Goal

A very simple WebUI for a non-technical client or SEO agency.

## User Experience

1. Login.
2. See dashboard.
3. Connect WordPress.
4. Connect OpenAI.
5. Add topics.
6. View, edit, schedule, disable, or delete topics.
7. Set how many posts per week/month.
8. AutoPost creates article, SEO data, and optional image.
9. Send to WordPress as Draft.
10. Review and publish.

## Dashboard Cards

- WordPress: Connected / Not Connected
- OpenAI: Connected / Not Connected
- Automation: On / Off
- Ready Topics
- Drafts Created
- Next Scheduled Post
- Failed Jobs

## Topic Fields

- Topic
- Keywords
- Category
- Notes
- Scheduled date/time
- Enabled
- Status

## Schedule Views

Client should be able to view:
- All upcoming scheduled topics
- Weekly schedule
- Monthly schedule
- Drafts already created
- Disabled topics
- Failed jobs

Every scheduled topic should be editable or disable-able without deleting it.

## Memory

Use client memory to keep content consistent.

Memory should be editable later from the WebUI. V1 may read from a Markdown file on the server.

## V1 Defaults

- Draft Only
- 2 posts/week
- Images ON
- SEO ON
- Auto Publish OFF
