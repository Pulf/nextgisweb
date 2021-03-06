# -*- coding: utf-8 -*-
from collections import namedtuple

from ..resource import Widget, resource_factory
from ..dynmenu import DynItem, Label, Link

from .model import WebMap
from .plugin import WebmapPlugin, WebmapLayerPlugin
from .adapter import WebMapAdapter
from .util import _
import urllib


class ExtentWidget(Widget):
    resource = WebMap
    operation = ('create', 'update')
    amdmod = 'ngw-webmap/ExtentWidget'


class ItemWidget(Widget):
    resource = WebMap
    operation = ('create', 'update')
    amdmod = 'ngw-webmap/ItemWidget'


def setup_pyramid(comp, config):

    def display(obj, request):
        request.resource_permission(WebMap.scope.webmap.display)

        MID = namedtuple('MID', ['adapter', 'basemap', 'plugin'])

        display.mid = MID(
            set(),
            set(),
            set(),
        )

        # Map level plugins
        plugin = dict()
        for pcls in WebmapPlugin.registry:
            p_mid_data = pcls.is_supported(obj)
            if p_mid_data:
                plugin.update((p_mid_data, ))

        def traverse(item):
            data = dict(
                id=item.id,
                type=item.item_type,
                label=item.display_name
            )

            if item.item_type == 'layer':
                style = item.style
                layer = style.parent

                # If there are no necessary permissions skip web-map element
                # so it won't be shown in the tree

                # TODO: Security

                # if not layer.has_permission(
                #     request.user,
                #     'style-read',
                #     'data-read',
                # ):
                #     return None

                # Main element parameters
                data.update(
                    layerId=style.parent_id,
                    styleId=style.id,
                    visibility=bool(item.layer_enabled),
                    transparency=item.layer_transparency,
                    minScaleDenom=item.layer_min_scale_denom,
                    maxScaleDenom=item.layer_max_scale_denom,
                )

                data['adapter'] = WebMapAdapter.registry.get(
                    item.layer_adapter, 'image').mid
                display.mid.adapter.add(data['adapter'])

                # Layer level plugins
                plugin = dict()
                for pcls in WebmapLayerPlugin.registry:
                    p_mid_data = pcls.is_layer_supported(layer, obj)
                    if p_mid_data:
                        plugin.update((p_mid_data, ))

                data.update(plugin=plugin)
                display.mid.plugin.update(plugin.keys())

            elif item.item_type in ('root', 'group'):
                # Recursively run all elements excluding those
                # with no permissions
                data.update(
                    expanded=item.group_expanded,
                    children=filter(
                        None,
                        map(traverse, item.children)
                    )
                )

            return data

        tmp = obj.to_dict()

        config = dict(
            extent=tmp["extent"],
            rootItem=traverse(obj.root_item),
            mid=dict(
                adapter=tuple(display.mid.adapter),
                basemap=tuple(display.mid.basemap),
                plugin=tuple(display.mid.plugin)
            ),
            webmapPlugin=plugin,
            bookmarkLayerId=obj.bookmark_resource_id,
            tinyDisplayUrl=request.route_url('webmap.display.tiny', id=obj.id),
            testEmbeddedMapUrl=request.route_url('webmap.display.shared.test', id=obj.id),
        )

        return dict(
            obj=obj,
            display_config=config,
            custom_layout=True
        )

    config.add_route(
        'webmap.display', '/resource/{id:\d+}/display',
        factory=resource_factory, client=('id',)
    ).add_view(display, context=WebMap, renderer='nextgisweb:webmap/template/display.mako')

    config.add_route(
        'webmap.display.tiny', '/resource/{id:\d+}/display/tiny',
        factory=resource_factory, client=('id',)
    ).add_view(display, context=WebMap, renderer='nextgisweb:webmap/template/tinyDisplay.mako')

    def shared_map_test(request):
        iframe = request.POST['iframe']
        request.response.headerlist.append(("X-XSS-Protection", "0"))
        return dict(
            iframe=urllib.unquote(urllib.unquote(iframe))
        )

    config.add_route(
        'webmap.display.shared.test', '/embedded/test.html'
    ).add_view(shared_map_test, renderer='nextgisweb:webmap/template/embeddedMapTest.mako')

    class DisplayMenu(DynItem):
        def build(self, args):
            if isinstance(args.obj, WebMap):
                yield Label('webmap', _("Web map"))

                yield Link(
                    'webmap/display', _("Display"),
                    self._url())

        def _url(self):
            return lambda (args): args.request.route_url(
                'webmap.display', id=args.obj.id)

    WebMap.__dynmenu__.add(DisplayMenu())
