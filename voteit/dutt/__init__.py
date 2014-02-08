from pyramid.i18n import TranslationStringFactory


DuttMF = TranslationStringFactory('voteit.dutt')


def includeme(config):
    config.include('voteit.dutt.models')
    config.include('voteit.dutt.fanstaticlib')
    from voteit.core.deform_bindings import append_search_path
    from pkg_resources import resource_filename
    append_search_path(resource_filename('voteit.dutt', 'templates/deform'))
    config.add_translation_dirs('voteit.dutt:locale/')
