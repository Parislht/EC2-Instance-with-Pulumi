import pulumi
import pulumi_aws as aws

# 1. VPC por defecto
default_vpc = aws.ec2.get_vpc(default=True)

# 2. Subred pública por defecto
default_subnet = aws.ec2.get_subnets(filters=[
    {
        "name": "vpc-id",
        "values": [default_vpc.id],
    }
])

# 3. Grupo de seguridad con puertos 22 (SSH) y 80 (HTTP)
security_group = aws.ec2.SecurityGroup("ec2-security-group",
    description="Permitir SSH y HTTP",
    vpc_id=default_vpc.id,
    ingress=[
        {"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 80, "to_port": 80, "cidr_blocks": ["0.0.0.0/0"]},
    ],
    egress=[{
        "protocol": "-1",
        "from_port": 0,
        "to_port": 0,
        "cidr_blocks": ["0.0.0.0/0"],
    }]
)

# 4. AMI: Ubuntu 22.04 en us-east-1 (Cloud9ubuntu22)
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["099720109477"],  # Canonical (Ubuntu)
    filters=[
        {"name": "name", "values": ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]},
        {"name": "virtualization-type", "values": ["hvm"]}
    ]
)

# 5. Crear la instancia EC2
ec2_instance = aws.ec2.Instance("mi-instancia-pulumi",
    instance_type="t2.micro",
    vpc_security_group_ids=[security_group.id],
    ami=ami.id,
    subnet_id=default_subnet.ids[0],
    key_name="vockey",
    iam_instance_profile="LabInstanceProfile",
    root_block_device={
        "volume_size": 20,
        "volume_type": "gp2"
    },
    tags={"Name": "PulumiEC2"}
)

# 6. Exportar la IP pública
pulumi.export("public_ip", ec2_instance.public_ip)
pulumi.export("instance_id", ec2_instance.id)
