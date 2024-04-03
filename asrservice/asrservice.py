#!/usr/bin/env python
#-*- coding:utf-8 -*-

###############################################################
# Service configuration file for CLAM
###############################################################

#Consult the CLAM documentation at https://clam.readthedocs.io/

from clam.common.parameters import ChoiceParameter, BooleanParameter, IntegerParameter
from clam.common.formats import *
from clam.common.converters import *
from clam.common.viewers import *
from clam.common.data import *
from clam.common.digestauth import pwhash
import clam
import sys
import os

#The minimum version of CLAM that is required by this service
REQUIRE_VERSION = 3.2

CLAMDIR = clam.__path__[0] #directory where CLAM is installed, detected automatically
WEBSERVICEDIR = os.path.dirname(os.path.abspath(__file__)) #directory where this webservice is installed, detected automatically

# ======== GENERAL INFORMATION ===========

# General metadata concerning your system.

#The System ID, a short alphanumeric identifier for internal use only (mandatory!)
SYSTEM_ID = "asrservice"
#System name, the way the system is presented to the world
SYSTEM_NAME = "Automatic Speech Recognition Service"

#An informative description for this system (this should be fairly short, about one paragraph, and may not contain HTML)
SYSTEM_DESCRIPTION = "An Automatic Speech Recognition Service for a variety of languages, powered by WhisperX"

#A version label of the underlying tool and/or this CLAM wrapper
#(If you can derive this dynamically then that is strongly recommended! It should be the same as in your setup.py)
SYSTEM_VERSION = 0.2

#The author(s) of the underlying tool and/or this CLAM wrapper
#(If you can derive this dynamically then that is strongly recommended!)
SYSTEM_AUTHOR = "Maarten van Gompel"

#How to reach the authors?
SYSTEM_EMAIL = "proycon@anaproy.nl"

#Does this system have a homepage (or possibly a source repository otherwise)
#SYSTEM_URL = ""

#Is this webservice embedded in a larger system? Like part of an institution or particular portal site. If so, mention the URL here.
#SYSTEM_PARENT_URL = ""

#The URL of a cover image to prominently display in the header of the interface. You may also want to set INTERFACEOPTIONS="centercover" to center it horizontally.
#SYSTEM_COVER_URL = ""

#URL to a website where users can register an account for use with this webservice. This link is only for human end
#users, not an API endpoint.
#SYSTEM_REGISTER_URL = ""

#Amount of free memory required prior to starting a new process (in MB!), Free Memory + Cached (without swap!). Set to 0 to disable this check (not recommended)
REQUIREMEMORY = 100


# ======== EXTERNAL CONFIGURATION ===========

#specify these variables in an external yaml file
#called $hostname.yaml or config.yaml and use the loadconfig() mechanism.
#Such an external file will be looked for my default and is the recommended way.

#This invokes the automatic loader, do not change it;
#it will try to find a file named $system_id.$hostname.yml or just $hostname.yml, where $hostname
#is the auto-detected hostname of this system. Alternatively, it tries a static $system_id.config.yml or just config.yml .
#You can also set an environment variable CONFIGFILE to specify the exact file to load at run-time.
#It will look in several paths including the current working directory and the path this settings script is loaded from.
#Such an external configuration file simply defines variables that will be imported here. If it fails to find
#a configuration file, an exception will be raised.
loadconfig(__name__)


#Allow Asynchronous HTTP requests from **web browsers** in following domains (sets Access-Control-Allow-Origin HTTP headers), by default this is unrestricted
#ALLOW_ORIGIN = "*"

# ======== WEB-APPLICATION STYLING =============

#Choose a style (has to be defined as a CSS file in clam/style/ ). You can copy, rename and adapt it to make your own style
STYLE = 'classic'

# ======== ENABLED FORMATS ===========

#In CUSTOM_FORMATS you can specify a list of Python classes corresponding to extra formats.
#You can define the classes first, and then put them in CUSTOM_FORMATS, as shown in this example:

#class MyXMLFormat(CLAMMetaData):
#    attributes = {}
#    name = "My XML format"
#    mimetype = 'text/xml'


class MP4AudioFormat(CLAMMetaData):
    attributes = {}
    name ="MP4 Audio File"
    mimetype = 'audio/mpeg'
    schemaorg_type = "AudioObject"

class SubRipTextFormat(CLAMMetaData):
    attributes = {}
    name ="SubRip Text"
    mimetype = 'application/x-subrip'
    schemaorg_type = "TextDigitalDocument"

class WebVTTFormat(CLAMMetaData):
    attributes = {}
    name ="WebVTT"
    mimetype = 'text/vtt'
    schemaorg_type = "TextDigitalDocument"

class TSVFormat(CLAMMetaData):
    attributes = {}
    name ="Tab Separated Values"
    mimetype = "text/tab-separated-values"
    schemaorg_type = "Dataset"

CUSTOM_FORMATS = [ SubRipTextFormat, WebVTTFormat, TSVFormat]

# CUSTOM_FORMATS = [ MyXMLFormat ]

# ======== ENABLED VIEWERS ===========

#In CUSTOM_VIEWERS you can specify a list of Python classes corresponding to extra viewers.
#You can define the classes first, and then put them in CUSTOM_VIEWERS, as shown in this example:

# CUSTOM_VIEWERS = [ MyXMLViewer ]

# ======= INTERFACE OPTIONS ===========

#Here you can specify additional interface options (space separated list), see the documentation for all allowed options
#INTERFACEOPTIONS = "inputfromweb" #allow CLAM to download its input from a user-specified url
INTERFACEOPTIONS = "disableliveinput"

# ======== PROJECTS: PREINSTALLED DATA ===========

#INPUTSOURCES = [
#    InputSource(id='sampledocs',label='Sample texts',path=ROOT+'/inputsources/sampledata',defaultmetadata=PlainTextFormat(None, encoding='utf-8') ),
#]

# ======== PROJECTS: PROFILE DEFINITIONS ===========

#Define your profiles here. This is required for the project paradigm, but can be set to an empty list if you only use the action paradigm.

PROFILES = [
    Profile(
        InputTemplate('InputWavFile',WaveAudioFormat,"Wav file",
            extension='.wav',
            multi=True #set unique=True if the user may only upload a file for this input template once. Set multi=True if you the user may upload multiple of such files
        ),
        #------------------------------------------------------------------------------------------------------------------------
        OutputTemplate('Transcription',PlainTextFormat,'Plain text transcriptions without time stamps and speaker attribution',
            SetMetaField('encoding','utf-8'),
            removeextension=".wav",
            extension='.txt',
            multi=True
        ),
        OutputTemplate('JSON',JSONFormat,'Transcription with full word segmentation/alignment and speaker attribution',
            SetMetaField('encoding','utf-8'),
            removeextension=".wav",
            extension='.json',
            multi=True
        ),
        OutputTemplate('SRT',SubRipTextFormat,'Timed transcriptions with speaker attribution (srt)',
            removeextension=".wav",
            extension='.srt',
            multi=True
        ),
        OutputTemplate('WebVTT',WebVTTFormat,'Timed transcriptions with speaker attribution (WebVTT)',
            removeextension=".wav",
            extension='.vtt',
            multi=True
        ),
        OutputTemplate('TSV', TSVFormat,'Timed transcriptions with speaker attribution (TSV)',
            removeextension=".wav",
            extension='.tsv',
            multi=True
        )
    ),
    Profile(
        InputTemplate('InputMP3File',MP3AudioFormat,"MP3 file",
            extension='.mp3',
            multi=True #set unique=True if the user may only upload a file for this input template once. Set multi=True if you the user may upload multiple of such files
        ),
        #------------------------------------------------------------------------------------------------------------------------
        OutputTemplate('Transcription',PlainTextFormat,'Plain text transcriptions without time stamps and speaker attribution',
            SetMetaField('encoding','utf-8'),
            removeextension=".mp3",
            extension='.txt',
            multi=True
        ),
        OutputTemplate('JSON',JSONFormat,'Transcription with full word segmentation/alignment and speaker attribution',
            SetMetaField('encoding','utf-8'),
            removeextension=".mp3",
            extension='.json',
            multi=True
        ),
        OutputTemplate('SRT',SubRipTextFormat,'Timed transcriptions with speaker attribution (srt)',
            removeextension=".mp3",
            extension='.srt',
            multi=True
        ),
        OutputTemplate('WebVTT',WebVTTFormat,'Timed transcriptions with speaker attribution (WebVTT)',
            removeextension=".mp3",
            extension='.vtt',
            multi=True
        ),
        OutputTemplate('TSV', TSVFormat,'Timed transcriptions with speaker attribution (TSV)',
            removeextension=".mp3",
            extension='.tsv',
            multi=True
        )
    ),
]

# ======== PROJECTS: COMMAND ===========

#The system command for the project paradigm.
#It is recommended you set this to small wrapper
#script around your actual system. Full shell syntax is supported. Using
#absolute paths is preferred. The current working directory will be
#set to the project directory.
#
#You can make use of the following special variables,
#which will be automatically set by CLAM:
#     $INPUTDIRECTORY  - The directory where input files are uploaded.
#     $OUTPUTDIRECTORY - The directory where the system should output
#                        its output files.
#     $TMPDIRECTORY    - The directory where the system should output
#                        its temporary files.
#     $STATUSFILE      - Filename of the .status file where the system
#                        should output status messages.
#     $DATAFILE        - Filename of the clam.xml file describing the
#                        system and chosen configuration.
#     $USERNAME        - The username of the currently logged in user
#                        (set to "anonymous" if there is none)
#     $PARAMETERS      - List of chosen parameters, using the specified flags
#
COMMAND = WEBSERVICEDIR + "/asrservice_wrapper.sh $STATUSFILE $INPUTDIRECTORY $OUTPUTDIRECTORY $PARAMETERS"

#Or if you only use the action paradigm, set COMMAND = None

# ======== PARAMETER DEFINITIONS ===========

#The global parameters (for the project paradigm) are subdivided into several
#groups. In the form of a list of (groupname, parameters) tuples. The parameters
#are a list of instances from common/parameters.py

PARAMETERS =  [
    ('Global', [
        ChoiceParameter(id='language',name='Language',description='The language to recognize', choices=[ ('nl','Dutch  / Nederlands'), ('en', 'English'),('de','German / Deutsch'),('fr', 'French / Français'), ('it', 'Italian / Italiano'), ('ja', 'Japanese / 日本語'), ('zh', 'Mandarin Chinese / 普通话'), ('es', 'Spanish / Español'), ('pt', 'Portuguese / Português'), ('uk', 'Ukrainian / Українська') ],default='nl',paramflag='-l'),
        ChoiceParameter(id='model',name='Model',description='The ASR model to use', choices=['tiny','small','medium','large','large-v2', 'large-v3',],default='large-v2',paramflag='-m')
    ]),
    ( 'Diarization', [
        BooleanParameter(id='diarization',name="Diarization", description="Enable speaker diarization?",paramflag="-d"),
        IntegerParameter(id='minspeakers',name="Minimum speakers", description="Minimum number of speakers (this helps diarization)",paramflag="-s"),
        IntegerParameter(id='maxspeakers',name="Maximum speakers", description="Minimum number of speakers (this helps diarization)",paramflag="-S"),
    ])
]


# ======= ACTIONS =============

#The action paradigm is an independent Remote-Procedure-Call mechanism that
#allows you to tie scripts (command=) or Python functions (function=) to URLs.
#It has no notion of projects or files and must respond in real-time. The syntax
#for commands is equal to those of COMMAND above, any file or project specific
#variables are not available though, so there is no $DATAFILE, $STATUSFILE, $INPUTDIRECTORY, $OUTPUTDIRECTORY or $PROJECT.

ACTIONS = [
]

# ======= FORWARDERS =============

#Global forwarders call a remote service, passing a backlink for the remote service to download an archive of ALL the output data. The remote service is expected to return a redirect (HTTP 302) . CLAM will insert the backlink where you put $BACKLINK in the url:

#FORWARDERS = [
    #Forwarder(id='otherservice', name="Other service", description="", url="https://my.service.com/grabfrom=$BACKLINK")
#]

# ======== DISPATCHING (ADVANCED! YOU CAN SAFELY SKIP THIS!) ========

#The dispatcher to use (defaults to clamdispatcher.py), you almost never want to change this
#DISPATCHER = 'clamdispatcher.py'

#DISPATCHER_POLLINTERVAL = 30   #interval at which the dispatcher polls for resource consumption (default: 30 secs)
#DISPATCHER_MAXRESMEM = 0    #maximum consumption of resident memory (in megabytes), processes that exceed this will be automatically aborted. (0 = unlimited, default)
#DISPATCHER_MAXTIME = 0      #maximum number of seconds a process may run, it will be aborted if this duration is exceeded.   (0=unlimited, default)
#DISPATCHER_PYTHONPATH = []        #list of extra directories to add to the python path prior to launch of dispatcher

#Run background process on a remote host? Then set the following (leave the lambda in):
#REMOTEHOST = lambda: return 'some.remote.host'
#REMOTEUSER = 'username'

#For this to work, the user under which CLAM runs must have (passwordless) ssh access (use ssh keys) to the remote host using the specified username (ssh REMOTEUSER@REMOTEHOST)
#Moreover, both systems must have access to the same filesystem (ROOT) under the same mountpoint.
