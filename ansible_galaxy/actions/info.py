
import logging

from ansible_galaxy import display
from ansible_galaxy.utils.content_name import parse_content_name
from ansible_galaxy.utils.text import to_text

from ansible_galaxy.flat_rest_api.content import GalaxyContent

log = logging.getLogger(__name__)

SKIP_INFO_KEYS = ("name", "description", "readme_html", "related", "summary_fields", "average_aw_composite", "average_aw_score", "url")


# FIXME: format?
def _repr_content_info(content_info):
    log.debug('content_info: %s', content_info)
    print(content_info)
    return content_info


# TODO: move to a repr for Role?
def _repr_role_info(role_info):

    text = [u"", u"Role: %s" % to_text(role_info['name'])]
    text.append(u"\tdescription: %s" % role_info.get('description', ''))

    for k in sorted(role_info.keys()):

        if k in SKIP_INFO_KEYS:
            continue

        if isinstance(role_info[k], dict):
            text.append(u"\t%s:" % (k))
            for key in sorted(role_info[k].keys()):
                if key in SKIP_INFO_KEYS:
                    continue
                text.append(u"\t\t%s: %s" % (key, role_info[k][key]))
        else:
            text.append(u"\t%s: %s" % (k, role_info[k]))

    return u'\n'.join(text)


def info_content_specs(galaxy_context,
                       api,
                       content_specs,
                       content_path,
                       display_callback=None,
                       offline=None):

    data = ''
    display_callback = display_callback or display.display_callback

    offline = offline or False
    for content_spec in content_specs:

        content_username, repo_name, content_name = parse_content_name(content_spec)

        log.debug('content_spec=%s', content_spec)
        log.debug('content_username=%s', content_username)
        log.debug('repo_name=%s', repo_name)
        log.debug('content_name=%s', content_name)

        repo_name = repo_name or content_name
        log.debug('repo_name2=%s', repo_name)

        content_info = {'path': content_path}
        gr = GalaxyContent(galaxy_context, content_spec)

        install_info = gr.install_info
        if install_info:
            if 'version' in install_info:
                install_info['intalled_version'] = install_info['version']
                del install_info['version']
            content_info.update(install_info)

        remote_data = False
        if not offline:
            remote_data = api.lookup_content_by_name(content_username, repo_name, content_name)

        if remote_data:
            content_info.update(remote_data)

        if gr.metadata:
            content_info.update(gr.metadata)

        # role_spec = yaml_parse({'role': role})
        # if role_spec:
        #     role_info.update(role_spec)

        data = _repr_content_info(content_info)
        display_callback(data)
        # data = self._display_role_info(content_info)
        # FIXME: This is broken in both 1.9 and 2.0 as
        # _display_role_info() always returns something
        if not data:
            data = u"\n- the content %s was not found" % content_spec

    display_callback(data)
    return data
    # self.display(data)