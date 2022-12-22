#!/usr/bin/python

# policies.py
#
# Author:  M. Shankar, Jan 31, 2012
# Modification History
#        Jan 31, 2012, Shankar: Initial version of policies.py with comments.
#        May 14, 2012, Li, Shankar: Added support for archiving extra fields into policy file.
#
# This is the policies.py used to enforce policies for archiving PVs
# At a very high level, when users request PVs to be archived, the mgmt web app samples the PV to determine event rate and other parameters.
# In addition, various fields of the PV like .NAME, .ADEL, .MDEL, .RTYP etc are also obtained
# These are passed to this python script as a dictionary argument to a method called determinePolicy
# The variable name in the python environment for this information is 'pvInfo' (so use other variable names etc.).
# The method is expected to use this information to make decisions on various archiving parameters.
# The result is expected to be another dictionary that is placed into the variable called "pvPolicy".
# Optionally, fields in addition to the VAL field that are to be archived with the PV are passed in as a property of pvPolicy called 'archiveFields'
# If the user overrides the policy, this is communicated in the pvinfo as a property called 'policyName'
#
# In addition, this script must communicate the list of available policies to the JVM as another method called getPolicyList which takes no arguments.
# The results of this method is placed into a variable called called 'pvPolicies'.
# The dictionary is a name to description mapping - the description is used in the UI; the name is what is communicated to determinePolicy as a user override
#
# In addition, this script must communicate the list of fields that are to be archived as part of the stream in a method called getFieldsArchivedAsPartOfStream.
# The results of this method is placed into a list variable called called
# 'pvStandardFields'.


import sys
import os

# Generate a list of policy names. This is used to feed the dropdown in the UI.


def getPolicyList():
    pvPoliciesDict = {}
    pvPoliciesDict['Default'] = '1 Hz monitor'
    pvPoliciesDict['VeryFast'] = '10 hz monitor, LTS reduce to 10 sec, always archived'
    pvPoliciesDict['Fast'] = '1 hz monitor, LTS reduce to 30 sec, always archived'
    pvPoliciesDict['Medium'] = '10 sec monitor, LTS reduce to 60 sec, always archived'
    pvPoliciesDict['Slow'] = '60 sec scan, LTS reduce to 180 sec, always archived'
    pvPoliciesDict['VerySlow'] = '15 min scan, No LTS reduce, always archived'
    pvPoliciesDict['VeryFastControlled'] = '10 hz monitor, LTS reduce to 10 sec, archived based on PV status'
    pvPoliciesDict['FastControlled'] = '1 hz monitor, LTS reduce to 30 sec, archived based on PV status'
    pvPoliciesDict['MediumControlled'] = '10 sec monitor, LTS reduce to 60 sec, archived based on PV status'
    pvPoliciesDict['SlowControlled'] = '60 sec scan, LTS reduce to 180 sec, archived based on PV status'
    pvPoliciesDict['VerySlowControlled'] = '15 min scan, No LTS reduce, archived based on PV status'
    return pvPoliciesDict


# Define a list of fields that will be archived as part of every PV.
# The data for these fields will included in the stream for the PV.
# We also make an assumption that the data type for these fields is the
# same as that of the .VAL field
def getFieldsArchivedAsPartOfStream():
    return ['HIHI', 'HIGH', 'LOW', 'LOLO', 'LOPR', 'HOPR', 'DRVH', 'DRVL']


# We use the environment variables ARCHAPPL_SHORT_TERM_FOLDER and
# ARCHAPPL_MEDIUM_TERM_FOLDER to determine the location of the STS and the
# MTS in the appliance
STS_BASE_URL = 'pb://${HOSTNAME}?name=STS&rootFolder=${ARCHAPPL_SHORT_TERM_FOLDER}&partitionGranularity=PARTITION_HOUR&consolidateOnShutdown=true'
MTS_BASE_URL = 'pb://${HOSTNAME}?name=MTS&rootFolder=${ARCHAPPL_MEDIUM_TERM_FOLDER}&partitionGranularity=PARTITION_DAY&hold=2&gather=1'
LTS_BASE_URL = 'pb://${HOSTNAME}?name=LTS&rootFolder=${ARCHAPPL_LONG_TERM_FOLDER}&partitionGranularity=PARTITION_YEAR'


default_sts_plugin_url = '%s' % (STS_BASE_URL)
default_mts_plugin_url = '%s' % (MTS_BASE_URL)
default_lts_plugin_url = '%s' % (LTS_BASE_URL)

veryfast_sts_plugin_url = '%s' % (STS_BASE_URL)
veryfast_mts_plugin_url = '%s' % (MTS_BASE_URL)
veryfast_lts_plugin_url = '%s&reducedata=lastSample_10' % (LTS_BASE_URL)

fast_sts_plugin_url = '%s' % (STS_BASE_URL)
fast_mts_plugin_url = '%s' % (MTS_BASE_URL)
fast_lts_plugin_url = '%s&reducedata=lastSample_30' % (LTS_BASE_URL)

medium_sts_plugin_url = '%s' % (STS_BASE_URL)
medium_mts_plugin_url = '%s' % (MTS_BASE_URL)
medium_lts_plugin_url = '%s&reducedata=lastSample_60' % (LTS_BASE_URL)

slow_sts_plugin_url = '%s' % (STS_BASE_URL)
slow_mts_plugin_url = '%s' % (MTS_BASE_URL)
slow_lts_plugin_url = '%s&reducedata=lastSample_180' % (LTS_BASE_URL)

veryslow_sts_plugin_url = '%s' % (STS_BASE_URL)
veryslow_mts_plugin_url = '%s' % (MTS_BASE_URL)
veryslow_lts_plugin_url = '%s' % (LTS_BASE_URL)


def determinePolicy(pvInfoDict):
    pvPolicyDict = {}

    userPolicyOverride = ''
    if 'policyName' in pvInfoDict:
        userPolicyOverride = pvInfoDict['policyName']

    if 'Controlled' in userPolicyOverride:
        pvPolicyDict['controlPV'] = 'PLS:Archiver:Enable'

    if 'VeryFast' in userPolicyOverride:
        pvPolicyDict['samplingPeriod'] = 0.1
        pvPolicyDict['samplingMethod'] = 'MONITOR'
        pvPolicyDict['dataStores'] = [
            veryfast_sts_plugin_url,
            veryfast_mts_plugin_url,
            veryfast_lts_plugin_url
        ]
    elif 'Fast' in userPolicyOverride:
        pvPolicyDict['samplingPeriod'] = 1.0
        pvPolicyDict['samplingMethod'] = 'MONITOR'
        pvPolicyDict['dataStores'] = [
            fast_sts_plugin_url,
            fast_mts_plugin_url,
            fast_lts_plugin_url
        ]
    elif 'Medium' in userPolicyOverride:
        pvPolicyDict['samplingPeriod'] = 10.0
        pvPolicyDict['samplingMethod'] = 'MONITOR'
        pvPolicyDict['dataStores'] = [
            medium_sts_plugin_url,
            medium_mts_plugin_url,
            medium_lts_plugin_url
        ]
    elif 'VerySlow' in userPolicyOverride:
        pvPolicyDict['samplingPeriod'] = 900.0
        pvPolicyDict['samplingMethod'] = 'SCAN'
        pvPolicyDict['dataStores'] = [
            veryslow_sts_plugin_url,
            veryslow_mts_plugin_url,
            veryslow_lts_plugin_url
        ]
    elif 'Slow' in userPolicyOverride:
        pvPolicyDict['samplingPeriod'] = 60.0
        pvPolicyDict['samplingMethod'] = 'SCAN'
        pvPolicyDict['dataStores'] = [
            slow_sts_plugin_url,
            slow_mts_plugin_url,
            slow_lts_plugin_url
        ]
    elif 'Default' in userPolicyOverride:
        pvPolicyDict['samplingPeriod'] = 1.0
        pvPolicyDict['samplingMethod'] = 'MONITOR'
        pvPolicyDict['dataStores'] = [
            default_sts_plugin_url,
            default_mts_plugin_url,
            default_lts_plugin_url
        ]
    else:
        pvPolicyDict['samplingPeriod'] = 1.0
        pvPolicyDict['samplingMethod'] = 'MONITOR'
        pvPolicyDict['dataStores'] = [
            default_sts_plugin_url,
            default_mts_plugin_url,
            default_lts_plugin_url
        ]

    archiveFields = []

    if "RTYP" not in pvInfoDict:
        pvPolicyDict["archiveFields"] = archiveFields
    else:
        pvRTYP = pvInfoDict["RTYP"]
        if pvRTYP == "ai":
            archiveFields = [
                'HIHI',
                'HIGH',
                'LOW',
                'LOLO',
                'LOPR',
                'HOPR']
        elif pvRTYP == "ao":
            archiveFields = [
                'HIHI',
                'HIGH',
                'LOW',
                'LOLO',
                'LOPR',
                'HOPR',
                'DRVH',
                'DRVL']
        elif pvRTYP == "calc":
            archiveFields = [
                'HIHI',
                'HIGH',
                'LOW',
                'LOLO',
                'LOPR',
                'HOPR']
        elif pvRTYP == "calcout":
            archiveFields = [
                'HIHI',
                'HIGH',
                'LOW',
                'LOLO',
                'LOPR',
                'HOPR']
        elif pvRTYP == "longin":
            archiveFields = [
                'HIHI',
                'HIGH',
                'LOW',
                'LOLO',
                'LOPR',
                'HOPR']
        elif pvRTYP == "longout":
            archiveFields = [
                'HIHI',
                'HIGH',
                'LOW',
                'LOLO',
                'LOPR',
                'HOPR',
                'DRVH',
                'DRVL']
        elif pvRTYP == "dfanout":
            archiveFields = [
                'HIHI',
                'HIGH',
                'LOW',
                'LOLO',
                'LOPR',
                'HOPR']
        elif pvRTYP == "sub":
            archiveFields = [
                'HIHI',
                'HIGH',
                'LOW',
                'LOLO',
                'LOPR',
                'HOPR']
        elif pvRTYP == "motor":
            archiveFields = [
                'HIHI',
                'HIGH',
                'LOW',
                'LOLO',
                'LOPR',
                'HOPR',
                'VELO',
                'RBV']
        pvPolicyDict["archiveFields"] = archiveFields

    return pvPolicyDict
