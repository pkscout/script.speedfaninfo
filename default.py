from kodi_six import xbmc, xbmcaddon, xbmcgui
from threading import Thread
from resources.common.kodisettings import getSettingBool, getSettingString
from resources.common.xlogger import Logger
from resources.lib.spid import Main, updateWindow

addon        = xbmcaddon.Addon()
addonversion = addon.getAddonInfo( 'version' )
addonpath    = addon.getAddonInfo( 'path' )
preamble     = '[SpeedFan Info]'
logdebug     = addon.getSetting( 'logging' )

lw = Logger( preamble = preamble, logdebug = logdebug )

if ( __name__ == "__main__" ):
    lw.log( ['script version %s started' % addonversion], xbmc.LOGNOTICE )
    lw.log( ['debug logging set to %s' % logdebug], xbmc.LOGNOTICE )
    if xbmcgui.Window( 10000 ).getProperty( "speedfan.running" ) == "true":
        lw.log( ['script already running, aborting subsequent run attempts'] )
    else:
        xbmcgui.Window( 10000 ).setProperty( "speedfan.running",  "true" )
        if getSettingBool( addon, 'show_compact' ):
            transparency_image = 'speedfan-panel-compact-%s.png' % getSettingString( addon, 'transparency', default='70' )
            xbmcgui.Window( 10000 ).setProperty( 'speedfan.panel.compact',  transparency_image )
            w = Main( "speedfaninfo-compact.xml", addonpath )
        else:
            w = Main( "speedfaninfo-main.xml", addonpath )
        t1 = Thread( target=updateWindow,args=("thread 1", w) )
        t1.setDaemon( True )
        t1.start()
        w.doModal()
        del t1
        del w
        xbmcgui.Window(10000).setProperty( "speedfan.running",  "false" )
lw.log( ['script stopped'], xbmc.LOGNOTICE )