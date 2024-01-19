from flask import Flask

app = Flask("spdk-swordfish")


@app.route('/redfish/v1/')
def hello():
    return 'Start at Storage'


@app.route('/redfish/v1/Storage')
def systems():
    return "json of available subsystems"


@app.route('/redfish/v1/Storage/<storage_id>')
def system(storage_id):
    # Check if system_id is valid and fetch the following.
    # 1. NQN
    # 2. List of controllers
    # 3. List of volumes
    # 4. Discovery subsystems?
    return {
        "@odata.id": "/redfish/v1/Storage/NVMeoF-SS1",
        "@odata.type": "#Storage.v1_15_0.Storage",
        "Id": "1",
        "Name": "NVMe-oF Logical NVM Fabric System",
        "Description": "An NVM Express Subsystem is an NVMe device that contains one or more NVM Express controllers and may contain one or more namespaces.",
        "Status": {
            "State": "Enabled",
            "Health": "OK",
            "HealthRollup": "OK"
        },
        "Identifiers": [
            {
                "DurableNameFormat": "NQN",
                "DurableName": "nqn.2014-08.org.nvmexpress:uuid:6c5fe566-10e6-4fb6-aad4-8b4159f50245"
            }
        ],
        "Controllers": {
            "@odata.id": "/redfish/v1/Storage/NVMeoF-SS1/Controllers"
        },
        "Volumes": {
            "@odata.id": "/redfish/v1/Storage/NVMeoF-SS1/Volumes"
        },
        "Links": {
            "NVMeoFDiscoverySubysystems": [
                {
                    "@odata.id": "/redfish/v1/Storage/NVMeoF-Discovery"
                }
            ]
        },
        "@Redfish.Copyright": "Copyright 2015-2023 SNIA. All rights reserved."
    }


# Controllers
@app.route('/redfish/v1/Storage/<storage_id>/Controllers')
def controllers(storage_id):
    return "json of available controllers in this NVM subsystem"


@app.route('/redfish/v1/Storage/<storage_id>/Controllers/<controller_id>')
def controller(storage_id, controller_id):
    """
    Find the controller that matches system_id and controller_id
    Read the following fields from spdk
    1. Name
    2. Status.State
    3. Model
    4. Serial number
    5. Part number?
    6. Firmware version
    7. Supported protocols []
    8. Controller properties
    """
    return {
        "@odata.type": "#StorageController.v1_3_0.StorageController",
        "Name": "NVMe Admin Controller",
        "Description": "Single NVMe Admin Controller for in-band admin command access.",
        "Status": {
            "State": "Enabled",
            "Health": "OK"
        },
        "Id": "NVMeAdminController",
        "Model": "NVMe Connect Array",
        "SerialNumber": "NVME123456",
        "PartNumber": "NVM44",
        "FirmwareVersion": "1.0.0",
        "SupportedControllerProtocols": [
            "PCIe"
        ],
        "NVMeControllerProperties": {
            "ControllerType": "Admin",
            "NVMeVersion": "1.3",
            "NVMeControllerAttributes": {
                "SupportsSQAssociations": False,
                "SupportsTrafficBasedKeepAlive": False,
                "SupportsExceedingPowerOfNonOperationalState": False,
                "Supports128BitHostId": False,
                "SupportsReservations": False
            },
            "NVMeSMARTCriticalWarnings": {
                "MediaInReadOnly": False,
                "OverallSubsystemDegraded": False,
                "SpareCapacityWornOut": False
            },
            "MaxQueueSize": 1
        },
        "Links": {
            "NetworkDeviceFunctions": [
                {
                    "@odata.id": "/redfish/v1/Chassis/NVMeOpaqueArray/NetworkAdapters/OpaqueArrayNetworkAdapter/NetworkDeviceFunctions/11100"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/NVMeOpaqueArray/NetworkAdapters/OpaqueArrayNetworkAdapter/NetworkDeviceFunctions/11101"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/NVMeOpaqueArray/NetworkAdapters/OpaqueArrayNetworkAdapter/NetworkDeviceFunctions/11102"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/NVMeOpaqueArray/NetworkAdapters/OpaqueArrayNetworkAdapter/NetworkDeviceFunctions/11103"
                }
            ]
        },
        "@odata.id": "/redfish/v1/Storage/OpaqueArray/Controllers/NVMeAdminController",
        "@Redfish.Copyright": "Copyright 2015-2023 SNIA. All rights reserved."
    }


# Namespaces
@app.route('/redfish/v1/Storage/<storage_id>/Volumes')
def volumes(storage_id):
    return "json of available namespaces/volumes in this NVM subsystem"


@app.route('/redfish/v1/Storage/<storage_id>/Volumes/<volume_id>')
def volume(storage_id, volume_id):
    """
       Find the namespace/volume that matches system_id and volume_id
       Read the following fields
       1. Name
       2. Id
       3. Status.State
       4. NQN

    """
    return {
        "@odata.type": "#Volume.v1_9_0.Volume",
        "Id": "1",
        "Name": "Namespace 1",
        "Description": "A Namespace is a quantity of non-volatile memory that may be formatted into logical blocks. When formatted, a namespace of size n is acollection of logical blocks with logical block addresses from 0 to (n-1). NVMe systems can support multiple namespaces.",
        "DisplayName": "Not set",
        "Status": {
            "State": "Enabled",
            "Health": "OK"
        },
        "Identifiers": [{
            "DurableNameFormat": "NQN",
            "DurableName": "nqn.2014-08.org.nvmexpress:uuid:6c5fe566-10e6-4fb6-aad4-8b4159029384"
        }],
        "RemainingCapacityPercent": 100,
        "BlockSizeBytes": 4096,
        "Capacity": {
            "Data": {
                "ConsumedBytes": 0,
                "AllocatedBytes": 10737418240,
                "ProvisionedBytes": 10737418240
            }
        },
        "RAIDType": "None",
        "NVMeNamespaceProperties": {
            "IsShareable": False,
            "NamespaceId": "0x22F",
            "NamespaceFeatures": {
                "SupportsThinProvisioning": False,
                "SupportsAtomicTransactionSize": False,
                "SupportsDeallocatedOrUnwrittenLBError": False,
                "SupportsNGUIDReuse": False,
                "SupportsIOPerformanceHints": False
            },
            "LBAFormat": {
                "LBAFormatType": "LBAFormat0",
                "RelativePerformance": "Best",
                "LBADataSizeBytes": 4096,
                "LBAMetadataSizeBytes": 0
            },
            "MetadataTransferredAtEndOfDataLBA": False,
            "NVMeVersion": "1.4"
        },
        "Links": {
            "Drives": [{
                "@odata.id": "/redfish/v1/Chassis/SimplestNVMeSSD/Drives/SimplestNVMeSSD"
            }],
            "Controllers": [{
                "@odata.id": "/redfish/v1/Systems/Sys-1/Storage/SimplestNVMeSSD/Controllers/NVMeIOController"
            }]
        },
        "@odata.id": "/redfish/v1/Systems/Sys-1/Storage/SimplestNVMeSSD/Volumes/SimpleNamespace",
        "@Redfish.Copyright": "Copyright 2015-2023 SNIA. All rights reserved."
    }


if __name__ == "__main__":
    app.run(debug=True)
