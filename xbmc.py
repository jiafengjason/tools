# -*- coding: utf-8 -*-
import sys, urlparse, urllib2, xbmcplugin, xbmcgui
import xml.dom.minidom

plugin_url = sys.argv[0]
handle = int(sys.argv[1])
params = dict(urlparse.parse_qsl(sys.argv[2].lstrip('?')))

def get_dom():
    return xml.dom.minidom.parse(
            urllib2.urlopen('http://www.hdpfans.com/live/unamenew/wenl'))

def find_element(dom, tag, attr_name, attr_val):
    return [e for e in dom.getElementsByTagName(tag)
                if e.getAttribute(attr_name) == attr_val][0]

def index():
    for node in get_dom().getElementsByTagName('class'):
        li = xbmcgui.ListItem(node.getAttribute('classname'))
        url = plugin_url + '?act=channel&id=' + node.getAttribute('id')

        xbmcplugin.addDirectoryItem(handle, url, li, True)

    xbmcplugin.endOfDirectory(handle)

def list_channel():
    class_node = find_element(get_dom(), 'class', 'id', params['id'])
    for channel in class_node.getElementsByTagName('channel'):
        tvlinks = channel.getElementsByTagName('tvlink')
        if not tvlinks: #没有视频源，则不显示
            continue

        if len(tvlinks) == 1: #单源直接播放
            url = tvlinks[0].getAttribute('link')
        else:
            url = plugin_url + '?act=choice&id=' + channel.getAttribute('id')

        li = xbmcgui.ListItem(channel.getAttribute('name'))
        li.setProperty('mimetype', 'video/x-msvideo') #防止列出视频时获取mime type
        li.setProperty('IsPlayable', 'true') #setResolvedUrl前必需

        xbmcplugin.addDirectoryItem(handle, url, li)

    xbmcplugin.endOfDirectory(handle)

def choice_tvlink():
    node = find_element(get_dom(), 'channel', 'id', params['id'])
    tvlinks = [(tvlink.getAttribute('source'), tvlink.getAttribute('link'))
                    for tvlink in node.getElementsByTagName('tvlink')]
    choice = xbmcgui.Dialog().select('选择信号源', [s[0] for s in tvlinks])
    li = xbmcgui.ListItem(node.getAttribute('name'), path=tvlinks[choice][1])
    xbmcplugin.setResolvedUrl(handle, True, li)


{
    'index': index,
    'channel': list_channel,
    'choice': choice_tvlink,
}[params.get('act', 'index')]()
