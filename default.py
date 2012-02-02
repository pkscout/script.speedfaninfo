import os, sys, datetime
import xbmcaddon
import xbmc, xbmcgui

### get addon info and set globals
__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__addonname__    = __addon__.getAddonInfo('name')
__author__       = __addon__.getAddonInfo('author')
__version__      = __addon__.getAddonInfo('version')
__addonpath__    = __addon__.getAddonInfo('path')
__addondir__     = xbmc.translatePath( __addon__.getAddonInfo('profile') )
__icon__         = __addon__.getAddonInfo('icon')
__localize__     = __addon__.getLocalizedString
__log_preamble__ = '[speedfaninfo] '

#this is the class for creating and populating the window 
class SpeedFanInfoWindow(xbmcgui.WindowXMLDialog): 
    
    def __init__(self, *args, **kwargs): pass
        # and define it as self

    def onInit(self): self.populateFromLog()
        #tell the object to go read the log file, parse it, and put it into listitems for the XML

    def populateFromLog(self):        
        #get all this stuff into list info items for the window
        #create a new log parser obeject
        lp = LogParser()
        #get the information from the SpeedFan Log
        temps, speeds, voltages, percents = lp.parseLog()
        xbmc.log(__log_preamble__ + 'starting to convert output for window')
        #show some additional information if advanced logging is turned on
        lp.logDatatoXBMC (temps, speeds, voltages, percents)
        #now parse all the data and get it into ListIems for display on the page
        self.getControl(120).reset()
        #this allows for a line space *after* the first one so the page looks pretty
        firstline_shown = 'false'
        if(len(temps) > 0):
            self.populateList('Temperature Information', temps, firstline_shown)
            firstline_shown = 'true'
        if(len(speeds) > 0):
            #please don't ask why this is so complicated, the simple way caused a fatal error on Windows
            if(len(speeds) == len(percents)):
                en_speeds = []
                for i in range(len(speeds)):
                    en_speeds.append((speeds[i][0], speeds [i][1] + ' (' + percents[i][1] + ')'))
            else:
                en_speeds = speeds
            self.populateList('Fan Speed Information', en_speeds, firstline_shown)
            firstline_shown = 'true'
        if(len(voltages) > 0):
            self.populateList('Voltage Information', voltages, firstline_shown)
        #log that we're done and ready to show the page
        xbmc.log(__log_preamble__ + 'completed putting information into lists, displaying window')
            
    def populateList(self, title, things, titlespace):
        #this takes an arbitrating list of readings and gets them into the ListItems
        if(titlespace == 'true'):
            item = xbmcgui.ListItem()
            self.getControl(120).addItem(item) #this adds an empty line
        item = xbmcgui.ListItem(label=title)
        item.setProperty('istitle','true')
        self.getControl(120).addItem(item)
        #we want two columns to make good use of the page
        nextside = 'left'
        for  onething in things:
            if(nextside == 'left'):
                left_label = onething[0]
                left_value = onething[1]
                nextside = 'right'
            else:
                item = xbmcgui.ListItem(label=left_label,label2=onething[0])
                item.setProperty('value',left_value)
                item.setProperty('value2',onething[1])
                nextside = 'left'
                self.getControl(120).addItem(item)
        if(nextside == 'right'):
            item = xbmcgui.ListItem(label=left_label,label2='')
            item.setProperty('value',left_value)
            self.getControl(120).addItem(item)

class LogParser():
    def __init__(self): pass
        # and define it as self

    def logDatatoXBMC (self, temps, speeds, voltages, percents):
        #if advanced logging is set in the plugin, this logs extra data to the XBMC log
        #mostly for troubleshooting
        if(__addon__.getSetting('advanced_log') == "true"):
            for onetemp in temps:
                xbmc.log(__log_preamble__ + ' temp: ' + onetemp[0] + ' value: ' + onetemp[1])
            for onespeed in speeds:
                xbmc.log(__log_preamble__ + ' speed: ' + onespeed[0] + ' value: ' + onespeed[1])
            for onevoltage in voltages:
                xbmc.log(__log_preamble__ + ' voltage: ' + onevoltage[0] + ' value: ' + onevoltage[1])
            for onepercent in percents:
                xbmc.log(__log_preamble__ + ' percent: ' + onepercent[0] + ' value: ' + onepercent[1])
        return

    def readLogFile(self):
        #try and open the log file
        #SpeedFan rolls the log every day, so we have to look for the log file based on the date
        #SpeedFan also does numerics if it has to roll the log during the day
        #but in my testing it only uses the numeric log for a couple of minutes and then goes
        #back to the main dated log, so I only read the main log file for a given date
        log_file_date = datetime.date(2011,1,29).today().isoformat().replace('-','')
        log_file_raw = __addon__.getSetting('log_location') + 'SFLog' + log_file_date
        log_file = log_file_raw + '.csv'
        xbmc.log(__log_preamble__ + 'trying to open logfile ' + log_file)
        try:
            f = open(log_file, 'rb')
        except IOError:
            xbmc.log(__log_preamble__ + 'no log file found')
            return
        xbmc.log(__log_preamble__ + 'opened logfile ' + log_file)                
        #get the first and last line of the log file
        #the first line has the header information, and the last line has the last log entry
        #Speedfan updates the log every three seconds, so I didn't want to read the whole log
        #file in just to get the last line
        first = next(f).decode()
        read_size = 1024
        offset = read_size
        f.seek(0, 2)
        file_size = f.tell()
        while 1:
            if file_size < offset:
                offset = file_size
            f.seek(-1*offset, 2)
            read_str = f.read(offset)
            # Remove newline at the end
            if read_str[offset - 1] == '\n':
                read_str = read_str[0:-1]
            lines = read_str.split('\n')
            if len(lines) > 1:  # Got a line
                last = lines[len(lines) - 1]
                break
            if offset == file_size:   # Reached the beginning
                last = read_str
                break
            offset += read_size
        f.close()
        #some additional information for advanced logging
        if(__addon__.getSetting('advanced_log') == 'true'):
            xbmc.log(__log_preamble__ + 'first line: ' + first)
            xbmc.log(__log_preamble__ + 'last line: ' + last)
        return first, last

    def parseLog(self):
        xbmc.log(__log_preamble__ + 'started parsing log');
        #I can't log something with unicode, so if I want to log I don't set the degree symbol
        if(__addon__.getSetting('advanced_log') == 'true'):
            degree_symbol = ''
        else:
            degree_symbol = unichr(176).encode("latin-1")
        if(__addon__.getSetting('temp_scale') == '0' or __addon__.getSetting('temp_scale') == '00'):
            temp_scale = 'C'
        else:
            temp_scale = 'F'
        #read the log file
        first, last = self.readLogFile()
        #pair up the heading with the value
        temps = []
        speeds = []
        voltages = []
        percents = []
        for s_item, s_value in map(None, first.split('\t'), last.split('\t')):
            item_type = s_item.split('.')[-1].rstrip().lower()
            item_text = os.path.splitext(s_item)[0].rstrip().replace('.', ' ')
            #round the number, drop the decimal and then covert to a string
            #skip the rounding for the voltage reading
            if(item_type == 'voltage'):
                s_value = s_value.rstrip()
            else:
                s_value = str(int(round(float(s_value.rstrip()))))
            if(item_type == "temp"):
                #put this info in the temperature array
                temps.append([item_text + ':', s_value + degree_symbol + temp_scale])
            elif(item_type == "speed"):
                #put this info in the speed array
                speeds.append([item_text + ':', s_value + 'rpm'])
            elif(item_type == "voltage"):
                #put this info in the voltage array
                voltages.append([item_text + ':', s_value + 'v'])
            elif(item_type == "percent"):
                #put this info to the percent array
                percents.append([item_text, s_value + '%'])
        #log some additional data if advanced logging is one
        self.logDatatoXBMC (temps, speeds, voltages, percents)
        #log that we're done parsing the file
        xbmc.log(__log_preamble__ + 'ended parsing log, displaying results');
        return temps, speeds, voltages, percents

#run the script
w = SpeedFanInfoWindow("speedfaninfo-main.xml", __addonpath__, "Default")
w.doModal()
del w