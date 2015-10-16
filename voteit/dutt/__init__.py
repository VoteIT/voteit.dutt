from pyramid.i18n import TranslationStringFactory


_ = TranslationStringFactory('voteit.dutt')


def includeme(config):
    config.include('voteit.dutt.models')
    config.add_translation_dirs('voteit.dutt:locale/')
