# -*- coding: utf-8 -*-
from ..component import Component
from ..security import SecurityProvider

from .models import LayerGroup
from . import views


@Component.registry.register
@SecurityProvider.registry.register
class LayerGroupComponent(object):

    # Component
    # =================================

    @classmethod
    def setup_routes(cls, config):
        config.add_route('layer_group', '/layer_group/')

        config.add_route('layer_group.show', '/layer_group/{id}')
        config.add_route('layer_group.edit_security', '/layer_group/{id}/edit-security')
        config.add_route('layer_group.show_security', '/layer_group/{id}/show-security')

        config.add_route('layer_group.new_group', '/layer_group/{id}/new-group')
        config.add_route('layer_group.new_layer', '/layer_group/{id}/new-layer')
        config.add_route('layer_group.delete', '/layer_group/{id}/delete')

    # SecurityProvider
    # =================================

    @classmethod
    def permission_scopes(cls):
        return (
            ('layer_group', u"Группа слоёв"),
        )

    @classmethod
    def permission_categories(cls):
        return (
            ('layer_group', u"Группа слоёв", ('layer_group', )),
        )

    @classmethod
    def permissions(cls):
        return (
            ('layer_group', 'read', u"Чтение"),
            ('layer_group', 'group-add', u"Добавлять группы"),
            ('layer_group', 'layer-add', u"Добавлять слои"),
            ('layer_group', 'security', u"Управление доступом")
        )