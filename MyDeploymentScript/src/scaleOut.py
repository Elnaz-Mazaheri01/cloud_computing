# import getpass
# import os
# import libcloud.security

import time
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider

# reqs:
#   services: nova, glance, neutron
#   resources: 2 instances (m1.small), 2 floating ips (1 keypair, 2 security groups)

# Please use 1-25 for X in username, project etc., as coordinated in the lab sessions

# web service endpoint of the private cloud infrastructure
auth_url = 'https://private-cloud2.informatik.hs-fulda.de:5000'
# your username in OpenStack
auth_username = 'CloudComp14'
# your project in OpenStack
project_name = 'CloudCompGrp14'

# default region
region_name = 'RegionOne'
# domain to use, "default" for local accounts, "hsfulda" for LDAP of DVZ, e.g., using fdaiXXXX as auth_username
domain_name = "default"

ubuntu_image_name = "Ubuntu 18.04 - Bionic Beaver - 64-bit - Cloud Based Image"
#ubuntu_image_name = "Ubuntu 18.04 - Bionic Beaver - 64-bit - Cloud Based Image"

flavor_name = 'm1.small'

network_name = "CloudCompGrp14-net"

keypair_name = 'elnaz-pub'
pub_key_file = '~/.ssh/id_rsa.pub'


def main():
    ###########################################################################
    #
    # get credentials
    #
    ###########################################################################

    # if "OS_PASSWORD" in os.environ:
    #     auth_password = os.environ["OS_PASSWORD"]
    # else:
    #     auth_password = getpass.getpass("Enter your OpenStack password:")
    auth_password = "elnino"

    ###########################################################################
    #
    # create connection
    #
    ###########################################################################

    # libcloud.security.VERIFY_SSL_CERT = False

    provider = get_driver(Provider.OPENSTACK)
    conn = provider(auth_username,
                    auth_password,
                    ex_force_auth_url=auth_url,
                    ex_force_auth_version='3.x_password',
                    ex_tenant_name=project_name,
                    ex_force_service_region=region_name,
                    ex_domain_name=domain_name)

    ###########################################################################
    #
    # get image, flavor, network for instance creation
    #
    ###########################################################################

    images = conn.list_images()
    image = ''
    for img in images:
        if img.name == ubuntu_image_name:
            image = img

    flavors = conn.list_sizes()
    flavor = ''
    for flav in flavors:
        if flav.name == flavor_name:
            flavor = conn.ex_get_size(flav.id)

    networks = conn.ex_list_networks()
    network = ''
    for net in networks:
        if net.name == network_name:
            network = net

    ###########################################################################
    #
    # create keypair dependency
    #
    ###########################################################################

    print('Checking for existing SSH key pair...')
    keypair_exists = False
    for keypair in conn.list_key_pairs():
        if keypair.name == keypair_name:
            keypair_exists = True

    if keypair_exists:
        print('Keypair ' + keypair_name + ' already exists. Skipping import.')
    else:
        print('adding keypair...')
        conn.import_key_pair_from_file(keypair_name, pub_key_file)

    for keypair in conn.list_key_pairs():
        print(keypair)

    ###########################################################################
    #
    # clean up resources from previous demos
    #
    ###########################################################################

    # destroy running demo instances
    for instance in conn.list_nodes():
        if instance.name in ['all-in-one', 'app-worker-1', 'app-worker-2', 'app-worker-3', 'app-controller',
                             'app-services', 'app-api-1', 'app-api-2']:
            print('Destroying Instance: %s' % instance.name)
            conn.destroy_node(instance)

    # wait until all nodes are destroyed to be able to remove depended security groups
    nodes_still_running = True
    while nodes_still_running:
        nodes_still_running = False
        time.sleep(3)
        instances = conn.list_nodes()
        for instance in instances:
            # if we see any demo instances still running continue to wait for them to stop
            if instance.name in ['all-in-one', 'app-worker-1', 'app-worker-2', 'app-controller']:
                nodes_still_running = True
        print('There are still instances running, waiting for them to be destroyed...')

    # delete security groups
    for group in conn.ex_list_security_groups():
        if group.name in ['control', 'worker', 'api', 'services']:
            print('Deleting security group: %s' % group.name)
            conn.ex_delete_security_group(group)

    ###########################################################################
    #
    # create security group dependency
    #
    ###########################################################################

    def get_security_group(connection, security_group_name):
        """A helper function to check if security group already exists"""
        print('Checking for existing ' + security_group_name + ' security group...')
        for security_grp in connection.ex_list_security_groups():
            if security_grp.name == security_group_name:
                print('Security Group ' + security_group_name + ' already exists. Skipping creation.')
                return worker_security_group
        return False

    if not get_security_group(conn, "api"):
        api_security_group = conn.ex_create_security_group('api', 'for API services only')
        conn.ex_create_security_group_rule(api_security_group, 'TCP', 80, 80)
        conn.ex_create_security_group_rule(api_security_group, 'TCP', 22, 22)
    else:
        api_security_group = get_security_group(conn, "api")

    if not get_security_group(conn, "worker"):
        worker_security_group = conn.ex_create_security_group('worker', 'for services that run on a worker node')
        conn.ex_create_security_group_rule(worker_security_group, 'TCP', 22, 22)
    else:
        worker_security_group = get_security_group(conn, "worker")

    if not get_security_group(conn, "control"):
        controller_security_group = conn.ex_create_security_group('control', 'for services that run on a control node')
        conn.ex_create_security_group_rule(controller_security_group, 'TCP', 22, 22)
        conn.ex_create_security_group_rule(controller_security_group, 'TCP', 80, 80)
        conn.ex_create_security_group_rule(controller_security_group, 'TCP', 5672, 5672,
                                           source_security_group=worker_security_group)

    if not get_security_group(conn, "services"):
        services_security_group = conn.ex_create_security_group('services', 'for DB and AMQP services only')
        conn.ex_create_security_group_rule(services_security_group, 'TCP', 22, 22)
        conn.ex_create_security_group_rule(services_security_group, 'TCP', 3306, 3306,
                                           source_security_group=api_security_group)
        conn.ex_create_security_group_rule(services_security_group, 'TCP', 5672, 5672,
                                           source_security_group=worker_security_group)
        conn.ex_create_security_group_rule(services_security_group, 'TCP', 5672, 5672,
                                           source_security_group=api_security_group)
    else:
        services_security_group = get_security_group(conn, "services")

    for security_group in conn.ex_list_security_groups():
        print(security_group)

    ###########################################################################
    #
    # get floating ip helper function
    #
    ###########################################################################

    def get_floating_ip(connection):
        """A helper function to re-use available Floating IPs"""
        unused_floating_ip = None
        for float_ip in connection.ex_list_floating_ips():
            if not float_ip.node_id:
                unused_floating_ip = float_ip
                break
        if not unused_floating_ip:
            pool = connection.ex_list_floating_ip_pools()[0]
            unused_floating_ip = pool.create_floating_ip()
        return unused_floating_ip

    ###########################################################################
    #
    # create app-api instances
    #
    ###########################################################################

    userdata_api = '''#!/usr/bin/env bash
    sudo apt update && \
    sudo apt -y install default-jdk && \
    sudo apt -y install python && \
    sudo DEBIAN_FRONTEND=noninteractive apt -y install python-libcloud && \
    sudo useradd -r -m -U -d /opt/tomcat -s /bin/false tomcat && \
    wget http://www-eu.apache.org/dist/tomcat/tomcat-9/v9.0.20/bin/apache-tomcat-9.0.20.tar.gz -P /tmp && \
    sudo tar xf /tmp/apache-tomcat-9*.tar.gz -C /opt/tomcat && \
    sudo ln -s /opt/tomcat/apache-tomcat-9.0.20 /opt/tomcat/latest && \
    sudo chown -RH tomcat: /opt/tomcat/latest && \
    sudo sh -c 'chmod +x /opt/tomcat/latest/bin/*.sh' && \
    sudo echo '[Unit]
            Description=Tomcat 9 servlet container
            After=network.target

            [Service]
            Type=forking

            User=tomcat
            Group=tomcat

            Environment="JAVA_HOME=/usr/lib/jvm/default-java"
            Environment="JAVA_OPTS=-Djava.security.egd=file:///dev/urandom -Djava.awt.headless=true"

            Environment="CATALINA_BASE=/opt/tomcat/latest"
            Environment="CATALINA_HOME=/opt/tomcat/latest"
            Environment="CATALINA_PID=/opt/tomcat/latest/temp/tomcat.pid"
            Environment="CATALINA_OPTS=-Xms512M -Xmx1024M -server -XX:+UseParallelGC"

            ExecStart=/opt/tomcat/latest/bin/startup.sh
            ExecStop=/opt/tomcat/latest/bin/shutdown.sh

            [Install]
            WantedBy=multi-user.target' > /etc/systemd/system/tomcat.service && \
    sudo systemctl daemon-reload && \
    sudo systemctl start tomcat && \
    cd /tmp && \
    git clone https://github.com/Elnaz-Mazaheri01/cloud_computing && \
    sudo cp /tmp/cloud_computing/cloud.war /opt/tomcat/latest/webapps/
    '''

    print('Starting new app-api-1 instance and wait until it is running...')
    instance_api_1 = conn.create_node(name='app-api-1',
                                      image=image,
                                      size=flavor,
                                      networks=[network],
                                      ex_keyname=keypair_name,
                                      ex_userdata=userdata_api,
                                      ex_security_groups=[api_security_group])

    print('Starting new app-api-2 instance and wait until it is running...')
    instance_api_2 = conn.create_node(name='app-api-2',
                                      image=image,
                                      size=flavor,
                                      networks=[network],
                                      ex_keyname=keypair_name,
                                      ex_userdata=userdata_api,
                                      ex_security_groups=[api_security_group])

    instance_api_1 = conn.wait_until_running(nodes=[instance_api_1], timeout=120,
                                             ssh_interface='private_ips')[0][0]
    api_1_ip = instance_api_1.private_ips[0]
    instance_api_2 = conn.wait_until_running(nodes=[instance_api_2], timeout=120,
                                             ssh_interface='private_ips')[0][0]
    # api_2_ip = instance_api_2.private_ips[0]

    for instance in [instance_api_1, instance_api_2]:
        floating_ip = get_floating_ip(conn)
        conn.ex_attach_floating_ip_to_node(instance, floating_ip)
        print('allocated %(ip)s to %(host)s' % {'ip': floating_ip.ip_address, 'host': instance.name})

    ###########################################################################
 


if __name__ == '__main__':
    main()