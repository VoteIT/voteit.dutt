from pyramid.i18n import TranslationStringFactory


DuttMF = TranslationStringFactory('voteit.dutt')


def includeme(config):
    #Include poll plugin
    from voteit.core.models.interfaces import IPoll
    from voteit.core.models.interfaces import IPollPlugin
    from voteit.dutt.plugin import DuttPoll
    config.registry.registerAdapter(DuttPoll, (IPoll,), IPollPlugin, DuttPoll.name)

    #Include current dir in search path for deform templates
    from voteit.core.patches import append_search_path
    from pkg_resources import resource_filename
    CURRENT_PATH = resource_filename('voteit.dutt', '')
    append_search_path(CURRENT_PATH)

    #Include translations
    #config.add_translation_dirs('voteit.dutt:locale/')