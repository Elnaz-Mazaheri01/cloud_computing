from __future__ import print_function


import getpass
import os

import libcloud.security
from libcloud.storage.providers import get_driver
from libcloud.storage.types import Provider
import string
import argparse

# reqs:
#   services: nova, glance, neutron
#   resources: 2 instances (m1.small), 2 floating ips (1 keypair, 2 security groups)

# HS-Fulda Private Cloud
auth_url = 'https://private-cloud2.informatik.hs-fulda.de:5000'
region_name = 'RegionOne'
domain_name = "default"
project_name = 'CloudCompGrp14'
auth_username = 'CloudComp14'
auth_password = "elnino"

def main():
    ###########################################################################
    #
    # get credentials
    #
    ###########################################################################

#     if "OS_PROJECT_NAME" in os.environ:
#         project_name = os.environ["OS_PROJECT_NAME"]
#     else:
#         project_name = input("Enter your OpenStack project:")
# 
#     if "OS_USERNAME" in os.environ:
#         auth_username = os.environ["OS_USERNAME"]
#     else:
#         auth_username = input("Enter your OpenStack username:")
# 
#     if "OS_PASSWORD" in os.environ:
#         auth_password = os.environ["OS_PASSWORD"]
#     else:
#         auth_password = getpass.getpass("Enter your OpenStack password:")

    # argument parser
    parser = argparse.ArgumentParser(description='Create a container to store object in OpenStack.')
    parser.add_argument('container_name', help='a name for the container to store object')
    parser.add_argument('object_name', help='a name for the object')
    parser.add_argument('file_path', help='the file path for the object')
    args = parser.parse_args()
    container_name = args.container_name
    object_name = args.object_name
    file_path = args.file_path

    ###########################################################################
    #
    # create connection
    #
    ###########################################################################

    libcloud.security.VERIFY_SSL_CERT = False

    provider = get_driver(Provider.OPENSTACK_SWIFT)
    swift = provider(auth_username,
                     auth_password,
                     ex_force_auth_url=auth_url,
                     ex_force_auth_version='3.x_password',
                     ex_tenant_name=project_name,
                     ex_force_service_region=region_name,
                     ex_domain_name=domain_name)

    ###########################################################################
    #
    # create container
    #
    ###########################################################################

#     container_name = 'fractals'
    containers = swift.list_containers()
    container = False
    for con in containers:
        if con.name == container_name:
            container = con

    if not container:
        container = swift.create_container(container_name=container_name)

    print(container)
    
    print(swift.list_containers())

    ###########################################################################
    #
    # upload a goat
    #
    ###########################################################################

#     object_name = 'an amazing goat'
#     file_path = 'C:\\Users\\Sebastian\\goat.jpg'
    objects = container.list_objects()
    object_data = False
    for obj in objects:
        if obj.name == object_name:
            object_data = obj

    if not object_data:
        # print(os.getcwd())
        container = swift.get_container(container_name=container_name)
        object_data = container.upload_object(file_path=file_path, object_name=object_name)

    objects = container.list_objects()
    print(objects)
    
    return

    ###########################################################################
    #
    # check goat integrity
    #
    ###########################################################################

    import hashlib
    print(hashlib.md5(open(file_path, 'rb').read()).hexdigest())

    ###########################################################################
    #
    # delete goat
    #
    ###########################################################################

    swift.delete_object(object_data)

    objects = container.list_objects()
    print(objects)


if __name__ == '__main__':
    main()