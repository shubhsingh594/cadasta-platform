from django.core.urlresolvers import reverse
from rest_framework_tmp_scoped_token import TokenManager

from tasks.celery import app


@app.task(name='export.export')
def export(org_slug, project_slug, api_key, output_type):
    pass


@app.task(name='msg.email')
def email(task, to_address):
    pass


@app.task(name='msg.email_err')
def email_err(task, to_address):
    pass


def schedule_export(organization, project, user, output_type, project_name):
    endpoint = reverse(
        'api:v1:organization:project_detail',
        kwargs={'organization': organization, 'project': project})
    token = TokenManager(
        user=user,
        endpoints={'GET': [endpoint]},
        max_age=60 * 60 * 12,  # 12 hr expiration,
        recipient='export-service')
    token = token.generate_token()

    payload = {
        'org_slug': organization,
        'project_slug': project,
        'api_key': token,
        'output_type': output_type,
    }
    job = "export of {}".format(project_name)
    return export.apply_async(
        kwargs=payload,
        link=email.s(job, user.email),
        link_error=email_err.s(job, user.email)
    )
