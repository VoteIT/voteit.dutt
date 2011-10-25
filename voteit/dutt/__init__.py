from pyramid.i18n import TranslationStringFactory


DuttMF = TranslationStringFactory('voteit.dutt')


def includeme(config):
    from voteit.core.models.interfaces import IPoll
    from voteit.core.models.interfaces import IPollPlugin
    from voteit.dutt.plugin import DuttPoll
    
    config.registry.registerAdapter(DuttPoll, (IPoll,), IPollPlugin, DuttPoll.name)
   # config.add_translation_dirs('voteit.dutt:locale/')
