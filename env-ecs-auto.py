from troposphere import Base64, Select, FindInMap, GetAtt, GetAZs, Join, Output
from troposphere import Parameter, Ref, Tags, Template
from troposphere.cloudformation import Init
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.ec2 import PortRange
from troposphere.cloudwatch import Alarm, MetricDimension
from troposphere.elasticloadbalancingv2 import TargetGroup, Matcher
from troposphere.ecs import TaskDefinition, ContainerDefinition, VolumesFrom, MountPoint, PortMapping, Volume, Host, network_port, positive_integer, LoadBalancer, Environment
from troposphere.elasticloadbalancingv2 import Listener
from troposphere.applicationautoscaling import ScalableTarget, ScalingPolicy, StepScalingPolicyConfiguration, StepAdjustment
from troposphere.ecs import Service
from troposphere.autoscaling import ScalingPolicy as InstanceScalingPolicy
from troposphere.autoscaling import LaunchConfiguration
from troposphere.ecs import Cluster
from troposphere.iam import Role, Policy
from troposphere.autoscaling import AutoScalingGroup
from troposphere.elasticloadbalancingv2 import Action, LoadBalancerAttributes
from troposphere.elasticloadbalancingv2 import LoadBalancer as LoadBalancerv2
from troposphere.iam import InstanceProfile
from troposphere.ec2 import SecurityGroup
import inspect

t = Template()

t.add_version("2010-09-09")

MaxGeneralSize = t.add_parameter(Parameter(
    "MaxGeneralSize",
    Default="2",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Max number of General containers in service",
))

BodybeastContainerPort = t.add_parameter(Parameter(
    "BodybeastContainerPort",
    Default="8080",
    ConstraintDescription="must be a valid port.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Port of container",
))

MinGeneralSize = t.add_parameter(Parameter(
    "MinGeneralSize",
    Default="1",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Minimum number of General containers in service",
))

MinSolrSlaveSize = t.add_parameter(Parameter(
    "MinSolrSlaveSize",
    Default="1",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Minimum number of SolrSlave containers in service",
))

CPULowThresholdPrivate = t.add_parameter(Parameter(
    "CPULowThresholdPrivate",
    Default="60",
    ConstraintDescription="must be a numerical value.(0-99)",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="CPU in percentage at which instance will be reduced",
))

MinCertificationSize = t.add_parameter(Parameter(
    "MinCertificationSize",
    Default="1",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Minimum number of Certification containers in service",
))

PrivateSubnets = t.add_parameter(Parameter(
    "PrivateSubnets",
    ConstraintDescription="must be list of subnet ids",
    Type="List<AWS::EC2::Subnet::Id>",
    Description="subnets in which cluster will have instances",
))

ConfigEnv = t.add_parameter(Parameter(
    "ConfigEnv",
    Default="config_dr",
    ConstraintDescription="must be a valid volume docker.",
    Type="String",
    Description="Configuration Environment volume container",
))

MinAutoprocSize = t.add_parameter(Parameter(
    "MinAutoprocSize",
    Default="1",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Minimum number of Autoproc containers in service",
))

BodybeastImageVersion = t.add_parameter(Parameter(
    "BodybeastImageVersion",
    Default="latest",
    ConstraintDescription="must be a valid Tag.",
    Type="String",
    Description="Tag for Bodybeast  Image",
))

AutoprocCpu = t.add_parameter(Parameter(
    "AutoprocCpu",
    Default="1000",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Cpu for Autoproc",
))

CPULowThresholdPublic = t.add_parameter(Parameter(
    "CPULowThresholdPublic",
    Default="60",
    ConstraintDescription="must be a numerical value.(0-99)",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="CPU in percentage at which instance will be reduced",
))

LiferayImageVersion = t.add_parameter(Parameter(
    "LiferayImageVersion",
    Default="latest",
    ConstraintDescription="must be a valid Tag.",
    Type="String",
    Description="Tag for liferay  Image",
))

AutoprocContainerPort = t.add_parameter(Parameter(
    "AutoprocContainerPort",
    Default="8080",
    ConstraintDescription="must be a valid port.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Port of container",
))

LiferayMemory = t.add_parameter(Parameter(
    "LiferayMemory",
    Default="9000",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Memory for liferay",
))

SolrGlobalNutchImageVersion = t.add_parameter(Parameter(
    "SolrGlobalNutchImageVersion",
    Default="latest",
    ConstraintDescription="must be a valid Tag.",
    Type="String",
    Description="Tag for Solr Global Nutch  Image",
))

CertificationCpu = t.add_parameter(Parameter(
    "CertificationCpu",
    Default="300",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Cpu for Certification",
))

AutoprocImageVersion = t.add_parameter(Parameter(
    "AutoprocImageVersion",
    Default="latest",
    ConstraintDescription="must be a valid Tag.",
    Type="String",
    Description="Tag for Autoproc  Image",
))

CertificationImageVersion = t.add_parameter(Parameter(
    "CertificationImageVersion",
    Default="latest",
    ConstraintDescription="must be a valid Tag.",
    Type="String",
    Description="Tag for Certification  Image",
))

SolrNutchPort = t.add_parameter(Parameter(
    "SolrNutchPort",
    Default="8983",
    ConstraintDescription="must be a valid port.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Port of container",
))

PublicSubnets = t.add_parameter(Parameter(
    "PublicSubnets",
    ConstraintDescription="must be list of subnet ids",
    Type="List<AWS::EC2::Subnet::Id>",
    Description="subnets in which cluster will have instances",
))

SolrImageVersion = t.add_parameter(Parameter(
    "SolrImageVersion",
    Default="latest",
    ConstraintDescription="must be a valid Tag.",
    Type="String",
    Description="Tag for SolrSlave  Image",
))

MinPrivateClusterSize = t.add_parameter(Parameter(
    "MinPrivateClusterSize",
    Default="5",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Minimum number of ec2 instances in cluster",
))

SolrBURNutchImageVersion = t.add_parameter(Parameter(
    "SolrBURNutchImageVersion",
    Default="latest",
    ConstraintDescription="must be a valid Tag.",
    Type="String",
    Description="Tag for Solr BUR Nutch  Image",
))

KeyName = t.add_parameter(Parameter(
    "KeyName",
    ConstraintDescription="must be the name of an existing EC2 KeyPair.",
    Type="AWS::EC2::KeyPair::KeyName",
    Description="Name of an existing EC2 KeyPair to enable SSH access to the instance",
))

CPUHighThresholdPublic = t.add_parameter(Parameter(
    "CPUHighThresholdPublic",
    Default="80",
    ConstraintDescription="must be a numerical value.(0-99)",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="CPU in percentage at which new instance will be spinned up",
))

VPC = t.add_parameter(Parameter(
    "VPC",
    Type="AWS::EC2::VPC::Id",
    Description="VpcId of your existing Virtual Private Cloud (VPC)",
))

MaxCertificationSize = t.add_parameter(Parameter(
    "MaxCertificationSize",
    Default="2",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Max number of Certification containers in service",
))

SolrContainerPort = t.add_parameter(Parameter(
    "SolrContainerPort",
    Default="8983",
    ConstraintDescription="must be a valid port.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Port of container",
))

MaxLiferaySize = t.add_parameter(Parameter(
    "MaxLiferaySize",
    Default="2",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Max number of Liferay containers in service",
))

ApplicationCPUHighThreshold = t.add_parameter(Parameter(
    "ApplicationCPUHighThreshold",
    Default="100",
    ConstraintDescription="must be a numerical value.(0-99)",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="CPU in percentage at which new Application container will be spinned up",
))

MinPublicClusterSize = t.add_parameter(Parameter(
    "MinPublicClusterSize",
    Default="2",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Minimum number of ec2 instances in cluster",
))

MaxPrivateClusterSize = t.add_parameter(Parameter(
    "MaxPrivateClusterSize",
    Default="12",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Max number of ec2 instances in cluster",
))

SolrMemory = t.add_parameter(Parameter(
    "SolrMemory",
    Default="2000",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Memory for SolrSlave",
))

GeneralContainerPort = t.add_parameter(Parameter(
    "GeneralContainerPort",
    Default="8080",
    ConstraintDescription="must be a valid port.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Port of container",
))

MaxAutoprocSize = t.add_parameter(Parameter(
    "MaxAutoprocSize",
    Default="2",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Max number of Autoproc containers in service",
))

MaxSolrSlaveSize = t.add_parameter(Parameter(
    "MaxSolrSlaveSize",
    Default="2",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Max number of SolrSlave containers in service",
))

PublicInstanceType = t.add_parameter(Parameter(
    "PublicInstanceType",
    Default="m3.large",
    ConstraintDescription="must be a valid EC2 instance type.",
    Type="String",
    Description="Public EC2 instance type",
    AllowedValues=["t1.micro", "t2.nano", "t2.micro", "t2.small", "t2.medium", "t2.large", "m1.small", "m1.medium", "m1.large", "m1.xlarge", "m2.xlarge", "m2.2xlarge", "m2.4xlarge", "m3.medium", "m3.large", "m3.xlarge", "m3.2xlarge", "m4.large", "m4.xlarge", "m4.2xlarge", "m4.4xlarge", "m4.10xlarge", "c1.medium", "c1.xlarge", "c3.large", "c3.xlarge", "c3.2xlarge", "c3.4xlarge", "c3.8xlarge", "c4.large", "c4.xlarge", "c4.2xlarge", "c4.4xlarge", "c4.8xlarge", "g2.2xlarge", "g2.8xlarge", "r3.large", "r3.xlarge", "r3.2xlarge", "r3.4xlarge", "r3.8xlarge", "i2.xlarge", "i2.2xlarge", "i2.4xlarge", "i2.8xlarge", "d2.xlarge", "d2.2xlarge", "d2.4xlarge", "d2.8xlarge", "hi1.4xlarge", "hs1.8xlarge", "cr1.8xlarge", "cc2.8xlarge", "cg1.4xlarge"],
))

CPUHighThresholdPrivate = t.add_parameter(Parameter(
    "CPUHighThresholdPrivate",
    Default="80",
    ConstraintDescription="must be a numerical value.(0-99)",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="CPU in percentage at which new instance will be spinned up",
))

GeneralImageVersion = t.add_parameter(Parameter(
    "GeneralImageVersion",
    Default="latest",
    ConstraintDescription="must be a valid Tag.",
    Type="String",
    Description="Tag for General  Image",
))

CertificationContainerPort = t.add_parameter(Parameter(
    "CertificationContainerPort",
    Default="8080",
    ConstraintDescription="must be a valid port.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Port of container",
))

SolrCpu = t.add_parameter(Parameter(
    "SolrCpu",
    Default="200",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Cpu for SolrSlave",
))

PrivateInstanceType = t.add_parameter(Parameter(
    "PrivateInstanceType",
    Default="m4.xlarge",
    ConstraintDescription="must be a valid EC2 instance type.",
    Type="String",
    Description="Private EC2 instance type",
    AllowedValues=["t1.micro", "t2.nano", "t2.micro", "t2.small", "t2.medium", "t2.large", "m1.small", "m1.medium", "m1.large", "m1.xlarge", "m2.xlarge", "m2.2xlarge", "m2.4xlarge", "m3.medium", "m3.large", "m3.xlarge", "m3.2xlarge", "m4.large", "m4.xlarge", "m4.2xlarge", "m4.4xlarge", "m4.10xlarge", "c1.medium", "c1.xlarge", "c3.large", "c3.xlarge", "c3.2xlarge", "c3.4xlarge", "c3.8xlarge", "c4.large", "c4.xlarge", "c4.2xlarge", "c4.4xlarge", "c4.8xlarge", "g2.2xlarge", "g2.8xlarge", "r3.large", "r3.xlarge", "r3.2xlarge", "r3.4xlarge", "r3.8xlarge", "i2.xlarge", "i2.2xlarge", "i2.4xlarge", "i2.8xlarge", "d2.xlarge", "d2.2xlarge", "d2.4xlarge", "d2.8xlarge", "hi1.4xlarge", "hs1.8xlarge", "cr1.8xlarge", "cc2.8xlarge", "cg1.4xlarge"],
))

ApplicationCPULowThreshold = t.add_parameter(Parameter(
    "ApplicationCPULowThreshold",
    Default="50",
    ConstraintDescription="must be a numerical value.(0-99)",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="CPU in percentage at which  Application container will be removed",
))

SolrSlaveMasterNode = t.add_parameter(Parameter(
    "SolrSlaveMasterNode",
    Default="itbb-app1.productpartners.com:8983",
    ConstraintDescription="must be a master solr node.",
    Type="String",
    Description="Master Node  for solr slave",
))

GeneralCpu = t.add_parameter(Parameter(
    "GeneralCpu",
    Default="500",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Cpu for General",
))

MinBodybeastSize = t.add_parameter(Parameter(
    "MinBodybeastSize",
    Default="1",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Minimum number of Bodybeast containers in service",
))

AutoprocMemory = t.add_parameter(Parameter(
    "AutoprocMemory",
    Default="5000",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Memory for Autoproc",
))

MinLiferaySize = t.add_parameter(Parameter(
    "MinLiferaySize",
    Default="1",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Minimum number of Liferay containers in service",
))

CertificationMemory = t.add_parameter(Parameter(
    "CertificationMemory",
    Default="3000",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Memory for Certification",
))

GeneralMemory = t.add_parameter(Parameter(
    "GeneralMemory",
    Default="3000",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Memory for General",
))

LiferayContainerPort = t.add_parameter(Parameter(
    "LiferayContainerPort",
    Default="8080",
    ConstraintDescription="must be a valid port.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Port of container",
))

SolrNutchMemory = t.add_parameter(Parameter(
    "SolrNutchMemory",
    Default="2000",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Memory for Solr Nutch",
))

BodybeastCpu = t.add_parameter(Parameter(
    "BodybeastCpu",
    Default="400",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Cpu for Bodybeast",
))

LiferayCpu = t.add_parameter(Parameter(
    "LiferayCpu",
    Default="2048",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Cpu for liferay",
))

BodybeastMemory = t.add_parameter(Parameter(
    "BodybeastMemory",
    Default="4000",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Memory for Bodybeast",
))

MaxBodybeastSize = t.add_parameter(Parameter(
    "MaxBodybeastSize",
    Default="2",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Max number of Bodybeast containers in service",
))

MaxPublicClusterSize = t.add_parameter(Parameter(
    "MaxPublicClusterSize",
    Default="6",
    ConstraintDescription="must be a numerical value.",
    AllowedPattern="[0-9]*",
    Type="String",
    Description="Max number of ec2 instances in cluster",
))

t.add_mapping("AWSRegion2AMI",
{u'ap-northeast-1': {u'64': u'ami-1a15c77b'},
 u'ap-northeast-2': {u'64': u'ami-a04297ce'},
 u'ap-south-1': {u'64': u'ami-cacbbea5'},
 u'ap-southeast-1': {u'64': u'ami-7243e611'},
 u'ap-southeast-2': {u'64': u'ami-55d4e436'},
 u'cn-north-1': {u'64': u'ami-fa875397}'},
 u'eu-central-1': {u'64': u'ami-0044b96f'},
 u'eu-west-1': {u'64': u'ami-d41d58a7'},
 u'sa-east-1': {u'64': u'ami-b777e4db'},
 u'us-east-1': {u'64': u'ami-c481fad3'},
 u'us-west-1': {u'64': u'ami-de347abe'},
 u'us-west-2': {u'64': u'ami-b04e92d0'}}
)

CPUAlarmLowPrivateSolrMaster = t.add_resource(Alarm(
    "CPUAlarmLowPrivateSolrMaster",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateClusterSolrMaster")
            )
        ],
    AlarmActions=[Ref("ScaleDownPolicySolrMaster")],
    AlarmDescription="Scale-down if CPU Reserved < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(CPULowThresholdPrivate),
    MetricName="CPUReservation",
))

CertificationELBTarget = t.add_resource(TargetGroup(
    "CertificationELBTarget",
    HealthyThresholdCount=5,
    HealthCheckIntervalSeconds=300,
    VpcId=Ref(VPC),
    Protocol="HTTP",
    HealthCheckProtocol="HTTP",
    UnhealthyThresholdCount=4,
    HealthCheckPath="/certification-web/restapi/",
    HealthCheckTimeoutSeconds=60,
    Matcher=Matcher(HttpCode="200"),
    Port=5000,
))

MongoReplica1Task = t.add_resource(TaskDefinition(
    "MongoReplica1Task",
    ContainerDefinitions=[
    ContainerDefinition(
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/", Ref(ConfigEnv)]),
        Name="data",
        Essential="false",
        Memory=128,
    ),
    ContainerDefinition(
        MountPoints=[MountPoint(SourceVolume="mongodb", ContainerPath="/opt/mongodb")] ,
        Name="MongoReplica1",
        Image="904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/mongo_replica:latest",
        Cpu="400",
        PortMappings=[PortMapping(ContainerPort="27017")],
        Memory="2000",
        Essential="true",
        VolumesFrom=[VolumesFrom(SourceContainer="data" )],
    ),
    ],
    Volumes=[Volume(Host=Host(SourcePath="/opt/mongodb/") , Name="mongodb" )],
))

MongoReplica2Listener = t.add_resource(Listener(
    "MongoReplica2Listener",
    Protocol="HTTP",
    DefaultActions=[Action(TargetGroupArn= Ref("MongoReplica2ELBTarget"), Type="forward" )],
    LoadBalancerArn=Ref("MongoReplica2ELB"),
    Port=network_port("27017"),
))

LiferayscalableTarget = t.add_resource(ScalableTarget(
    "LiferayscalableTarget",
    ScalableDimension="ecs:service:DesiredCount",
    ResourceId=Join("", ["service/", Ref("ECSPrivateCluster"), "/", GetAtt("LiferayService", "Name")]),
    RoleARN=GetAtt("ECSAutoscaleRole", "Arn"),
    MinCapacity=Ref(MinLiferaySize),
    ServiceNamespace="ecs",
    MaxCapacity=Ref(MaxLiferaySize),
))

MongoReplica2CPUAlarmLow = t.add_resource(Alarm(
    "MongoReplica2CPUAlarmLow",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateClusterMongoReplica2")
            ),
            MetricDimension(
                Name="ServiceName",
                Value=  GetAtt("MongoReplica2Service", "Name")
            )
        ],
    AlarmActions=[Ref("MongoReplica2ScaleDownPolicy")],
    AlarmDescription="Scale-down if CPU < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPULowThreshold),
    MetricName="CPUUtilization",
))

OhsELBTarget = t.add_resource(TargetGroup(
    "OhsELBTarget",
    HealthyThresholdCount=5,
    HealthCheckIntervalSeconds=300,
    VpcId=Ref(VPC),
    Protocol="HTTP",
    HealthCheckProtocol="HTTP",
    UnhealthyThresholdCount=4,
    HealthCheckPath="/",
    HealthCheckTimeoutSeconds=60,
    Matcher=Matcher(HttpCode="301"),
    Port=5000,
))

BodybeastCPUAlarmHigh = t.add_resource(Alarm(
    "BodybeastCPUAlarmHigh",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value=  Ref("ECSPrivateCluster")
            ),
        
            MetricDimension(
                Name="ServiceName",
                Value=GetAtt("BodybeastService", "Name")
            )
        ],
    AlarmActions=[Ref("BodybeastScaleUpPolicy")],
    AlarmDescription="Scale-up if CPU > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPUHighThreshold),
    MetricName="CPUUtilization",
))

MongoReplica1ELBTarget = t.add_resource(TargetGroup(
    "MongoReplica1ELBTarget",
    HealthyThresholdCount=5,
    HealthCheckIntervalSeconds=300,
    VpcId=Ref(VPC),
    Protocol="HTTP",
    HealthCheckProtocol="HTTP",
    UnhealthyThresholdCount=4,
    HealthCheckPath="/",
    HealthCheckTimeoutSeconds=60,
    Matcher=Matcher(HttpCode="200"),
    Port=5000,
))
AutoprocService = t.add_resource(Service(
    "AutoprocService",
    LoadBalancers=[LoadBalancer(
        ContainerName="Autoproc",
        ContainerPort=network_port(Ref("AutoprocContainerPort")),
        TargetGroupArn=Ref("AutoprocELBTarget")
    )],
    Cluster=Ref("ECSPrivateCluster"),
    Role=Ref("ECSServiceRole"),
    TaskDefinition=Ref("AutoprocTask"),
    DesiredCount=Ref("MinAutoprocSize"),
    DependsOn=["AutoprocELB", "AutoprocListener"],
))

ScaleUpPolicySolrGlobalNutch = t.add_resource(InstanceScalingPolicy(
    "ScaleUpPolicySolrGlobalNutch",
    ScalingAdjustment="1",
    Cooldown="300",
    AutoScalingGroupName=Ref("AutoscalingSolrGlobalNutchGroup"),
    AdjustmentType="ChangeInCapacity",
))

ScaleUpPolicySolrSlave = t.add_resource(InstanceScalingPolicy(
    "ScaleUpPolicySolrSlave",
    ScalingAdjustment="1",
    Cooldown="300",
    AutoScalingGroupName=Ref("AutoscalingSolrSlaveGroup"),
    AdjustmentType="ChangeInCapacity",
))

SolrBURNutchCPUAlarmHigh = t.add_resource(Alarm(
    "SolrBURNutchCPUAlarmHigh",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateClusterSolrBURNutch")
            ),
            MetricDimension(
                Name="ServiceName",
                Value= GetAtt("SolrBURNutchService", "Name")
            )
        ],
    AlarmActions=[Ref("SolrBURNutchScaleUpPolicy")],
    AlarmDescription="Scale-up if CPU > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPUHighThreshold),
    MetricName="CPUUtilization",
))

OhsCPUAlarmHigh = t.add_resource(Alarm(
    "OhsCPUAlarmHigh",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPublicCluster")
            ),
            MetricDimension(
                Name="ServiceName",
                Value= GetAtt("OhsService", "Name")
            )
        ],
    AlarmActions=[Ref("OhsScaleUpPolicy")],
    AlarmDescription="Scale-up if CPU > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPUHighThreshold),
    MetricName="CPUUtilization",
))

ScaleUpPolicyMongoReplica2 = t.add_resource(InstanceScalingPolicy(
    "ScaleUpPolicyMongoReplica2",
    ScalingAdjustment="1",
    Cooldown="300",
    AutoScalingGroupName=Ref("AutoscalingMongoReplica2Group"),
    AdjustmentType="ChangeInCapacity",
))

CPUAlarmHighPrivate = t.add_resource(Alarm(
    "CPUAlarmHighPrivate",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateCluster")
            )
        ],
    AlarmActions=[Ref("ScaleUpPolicyPrivate")],
    AlarmDescription="Scale-up if CPU Reserved > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(CPUHighThresholdPrivate),
    MetricName="CPUReservation",
))

SolrGlobalNutchScaleUpPolicy = t.add_resource(ScalingPolicy(
    "SolrGlobalNutchScaleUpPolicy",
    ScalingTargetId=Ref("SolrGlobalNutchscalableTarget"),
    PolicyName="SolrGlobalNutchScaleUp",
    PolicyType="StepScaling",
    StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=1, MetricIntervalLowerBound=0) ], AdjustmentType="ChangeInCapacity" ),
))

CertificationService = t.add_resource(Service(
    "CertificationService",
     LoadBalancers=[LoadBalancer(
        ContainerName="Certification",
        ContainerPort=network_port(Ref("CertificationContainerPort")),
        TargetGroupArn=Ref("CertificationELBTarget")
    )],
    Cluster=Ref("ECSPrivateCluster"),
    Role=Ref("ECSServiceRole"),
    TaskDefinition=Ref("CertificationTask"),
    DesiredCount=Ref(MinCertificationSize),
    DependsOn=["CertificationELB", "CertificationListener"],
))

CertificationScaleDownPolicy = t.add_resource(ScalingPolicy(
    "CertificationScaleDownPolicy",
    ScalingTargetId=Ref("CertificationscalableTarget"),
    PolicyName="CertificationScaleDown",
    PolicyType="StepScaling",
    StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=-1, MetricIntervalUpperBound=0) ], AdjustmentType="ChangeInCapacity" )
))

LaunchConfigPrivate = t.add_resource(LaunchConfiguration(
    "LaunchConfigPrivate",
    UserData=Base64(Join("", ["#!/bin/bash\n", "yum update -y\n", "yum install -y ecs-init\n", "yum install -y docker\n", "sed -i  '1s/^/nameserver 10.1.64.15\\nnameserver 10.253.34.15\\n/' /etc/resolv.conf\n", "echo ECS_CLUSTER=", Ref("ECSPrivateCluster"), " > /etc/ecs/ecs.config\n", "service docker restart\n", "start ecs\n"])),
    InstanceMonitoring="false",
    ImageId=FindInMap("AWSRegion2AMI", Ref("AWS::Region"), "64"),
    BlockDeviceMappings=[{ "DeviceName": "/dev/xvda", "Ebs": { "Iops": 500, "VolumeSize": "100", "VolumeType": "io1" } }],
    KeyName=Ref(KeyName),
    SecurityGroups=[Ref("SGPrivate")],
    IamInstanceProfile=Ref("EC2InstanceProfile"),
    InstanceType=Ref(PrivateInstanceType),
))

OhsListener = t.add_resource(Listener(
    "OhsListener",
    Protocol="HTTP",
    DefaultActions=[Action(TargetGroupArn=Ref("OhsELBTarget"), Type="forward" )],
    LoadBalancerArn=Ref("OhsELB"),
    Port=network_port("80"),
))

GeneralELBTarget = t.add_resource(TargetGroup(
    "GeneralELBTarget",
    HealthyThresholdCount=5,
    HealthCheckIntervalSeconds=300,
    VpcId=Ref(VPC),
    Protocol="HTTP",
    HealthCheckProtocol="HTTP",
    UnhealthyThresholdCount=4,
    HealthCheckPath="/general-web/restapi/",
    HealthCheckTimeoutSeconds=60,
    Matcher=Matcher(HttpCode="200" ),
    Port=5000,
))

GeneralScaleUpPolicy = t.add_resource(ScalingPolicy(
    "GeneralScaleUpPolicy",
    ScalingTargetId=Ref("GeneralscalableTarget"),
    PolicyName="GeneralScaleUp",
    PolicyType="StepScaling",
     StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=1, MetricIntervalLowerBound=0) ], AdjustmentType="ChangeInCapacity" ),
))

BodybeastELBTarget = t.add_resource(TargetGroup(
    "BodybeastELBTarget",
    HealthyThresholdCount=5,
    HealthCheckIntervalSeconds=300,
    VpcId=Ref(VPC),
    Protocol="HTTP",
    HealthCheckProtocol="HTTP",
    UnhealthyThresholdCount=4,
    HealthCheckPath="/bodybeast-services/",
    HealthCheckTimeoutSeconds=60,
    Matcher=Matcher(HttpCode="200"),
    Port=network_port(5000),
))

ECSPrivateClusterSolrMaster = t.add_resource(Cluster(
    "ECSPrivateClusterSolrMaster",
))

SolrMasterELBTarget = t.add_resource(TargetGroup(
    "SolrMasterELBTarget",
    HealthyThresholdCount=5,
    HealthCheckIntervalSeconds=300,
    VpcId=Ref(VPC),
    Protocol="HTTP",
    HealthCheckProtocol="HTTP",
    UnhealthyThresholdCount=4,
    HealthCheckPath="/solr/",
    HealthCheckTimeoutSeconds=60,
    Matcher=Matcher(HttpCode="200"),
    Port=network_port(5000),
))

GeneralCPUAlarmHigh = t.add_resource(Alarm(
    "GeneralCPUAlarmHigh",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateCluster")
            ),
        
            MetricDimension(
                Name="ServiceName",
                Value= GetAtt("GeneralService", "Name")
            )
        ],

    AlarmActions=[Ref(GeneralScaleUpPolicy)],
    AlarmDescription="Scale-up if CPU > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPUHighThreshold),
    MetricName="CPUUtilization",
))

GeneralTask = t.add_resource(TaskDefinition(
    "GeneralTask",
    ContainerDefinitions=[
    ContainerDefinition(
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/", Ref(ConfigEnv)]),
        Name="data",
        Essential="false",
        Memory=128,
    ),
    ContainerDefinition(
        PortMappings=[PortMapping(ContainerPort=Ref(GeneralContainerPort) )],
        Name="General",
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/general", ":", Ref(GeneralImageVersion)]),
        Essential="true",
        Environment=[Environment(Name="SERVICE_NAME",Value="general") ],
        Memory=Ref(GeneralMemory),
        Cpu=Ref(GeneralCpu),
        VolumesFrom=[VolumesFrom(SourceContainer="data") ],
    ),
    ],
))

LaunchConfigSolrMaster = t.add_resource(LaunchConfiguration(
    "LaunchConfigSolrMaster",
    UserData=Base64(Join("", ["#!/bin/bash\n", "yum update -y\n", "yum install -y ecs-init\n", "yum install -y docker\n", "sed -i  '1s/^/nameserver 10.1.64.15\\nnameserver 10.253.34.15\\n/' /etc/resolv.conf\n", "mkfs -t ext4 /dev/`lsblk  | grep 200G | grep xvd | awk '{print$1}'`\n", "mkdir -p /opt/data\n", "chmod -R 777 /opt/data\n", "cp /etc/fstab /etc/fstab.orig\n", "echo /dev/`lsblk  | grep 200G | grep xvd | awk '{print$1}'` /opt/data/ ext4 defaults, nofail 0 2  >> /etc/fstab\n", "mount -a\n", "echo ECS_CLUSTER=", Ref(ECSPrivateClusterSolrMaster), " > /etc/ecs/ecs.config\n", "service docker restart\n", "start ecs\n"])),
    InstanceMonitoring="false",
    ImageId=FindInMap("AWSRegion2AMI", Ref("AWS::Region"), "64"),
    BlockDeviceMappings=[{ "DeviceName": "/dev/xvda", "Ebs": { "Iops": 500, "VolumeSize": "100", "VolumeType": "io1" } }, { "DeviceName": "/dev/xvdb", "Ebs": { "Iops": 500, "DeleteOnTermination": "false", "VolumeType": "io1", "VolumeSize": "200" } }],
    KeyName=Ref(KeyName),
    SecurityGroups=[Ref("SGPrivate")],
    IamInstanceProfile=Ref("EC2InstanceProfile"),
    InstanceType=Ref(PrivateInstanceType),
))

SolrMasterService = t.add_resource(Service(
    "SolrMasterService",
    LoadBalancers=[LoadBalancer(
        ContainerName="SolrMaster",
        ContainerPort=network_port(Ref("SolrContainerPort")),
        TargetGroupArn=Ref("SolrMasterELBTarget")
    )],
    Cluster=Ref(ECSPrivateClusterSolrMaster),
    Role=Ref("ECSServiceRole"),
    TaskDefinition=Ref("SolrMasterTask"),
    DesiredCount=1,
    DependsOn=["SolrMasterELB", "SolrMasterListener"],
))

LiferayScaleDownPolicy = t.add_resource(ScalingPolicy(
    "LiferayScaleDownPolicy",
    ScalingTargetId=Ref(LiferayscalableTarget),
    PolicyName="LiferayScaleDown",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=-1, MetricIntervalUpperBound=0) ], AdjustmentType="ChangeInCapacity" )
))

LiferayCPUAlarmLow = t.add_resource(Alarm(
    "LiferayCPUAlarmLow",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateCluster")
            ),
        
            MetricDimension(
                Name="ServiceName",
                Value=GetAtt("LiferayService", "Name")
            ),
        ],
    AlarmActions=[Ref(LiferayScaleDownPolicy)],
    AlarmDescription="Scale-down if CPU < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPULowThreshold),
    MetricName="CPUUtilization",
))

SolrGlobalNutchTask = t.add_resource(TaskDefinition(
    "SolrGlobalNutchTask",
    ContainerDefinitions=[
    ContainerDefinition(
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/", Ref(ConfigEnv)]),
        Name="data",
        Essential="false",
        Memory=128,
    ),
    ContainerDefinition(
        MountPoints=[MountPoint(SourceVolume="data", ContainerPath= "/opt/data")],
        Name="SolrGlobalNutch",
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/tbb_gs", ":", Ref(SolrGlobalNutchImageVersion)]),
        Cpu=Ref(SolrCpu),
        PortMappings=[PortMapping(ContainerPort=Ref(SolrNutchPort) )],
        Memory=Ref(SolrNutchMemory),
        Essential="true",
        VolumesFrom=[VolumesFrom(SourceContainer="data")],
    ),
    ],
 Volumes=[Volume(Host=Host(SourcePath="/opt/data/") , Name="data" )],
))


CPUAlarmLowPrivateSolrBURNutch = t.add_resource(Alarm(
    "CPUAlarmLowPrivateSolrBURNutch",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateClusterSolrBURNutch")
            ),
        ],
    AlarmActions=[Ref("ScaleDownPolicySolrBURNutch")],
    AlarmDescription="Scale-down if CPU Reserved < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(CPULowThresholdPrivate),
    MetricName="CPUReservation",
))

ECSServiceRole = t.add_resource(Role(
    "ECSServiceRole",
    RoleName="ECSServiceRole",
    Path="/",
    Policies=[Policy( PolicyName="ecs-service", PolicyDocument={ "Statement": [{ "Action": ["elasticloadbalancing:Describe*", "elasticloadbalancing:DeregisterInstancesFromLoadBalancer", "elasticloadbalancing:RegisterInstancesWithLoadBalancer", "elasticloadbalancing:DeregisterTargets", "elasticloadbalancing:DescribeTargetGroups", "elasticloadbalancing:DescribeTargetHealth", "elasticloadbalancing:RegisterTargets", "ec2:Describe*", "ec2:AuthorizeSecurityGroupIngress"], "Resource": "*", "Effect": "Allow" }] } )],
    AssumeRolePolicyDocument={ "Statement": [{ "Action": ["sts:AssumeRole"], "Effect": "Allow", "Principal": { "Service": ["ecs.amazonaws.com"] } }] },
))

LiferayTask = t.add_resource(TaskDefinition(
    "LiferayTask",
    ContainerDefinitions=[
    ContainerDefinition(
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/", Ref(ConfigEnv)]),
        Name="data",
        Essential="false",
        Memory=128,
    ),
    ContainerDefinition(
        Name="Liferay",
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/liferay", ":", Ref(LiferayImageVersion)]),
        Cpu=Ref(LiferayCpu),
        PortMappings=[PortMapping(ContainerPort= Ref(LiferayContainerPort) )],
        Memory=Ref(LiferayMemory),
        Essential="true",
        VolumesFrom=[VolumesFrom(SourceContainer="data" )],
    ),
    ],
))

SolrGlobalNutchScaleDownPolicy = t.add_resource(ScalingPolicy(
    "SolrGlobalNutchScaleDownPolicy",
    ScalingTargetId=Ref("SolrGlobalNutchscalableTarget"),
    PolicyName="SolrGlobalNutchScaleDown",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=-1, MetricIntervalUpperBound=0) ], AdjustmentType="ChangeInCapacity" )
))

AutoscalingSolrSlaveGroup = t.add_resource(AutoScalingGroup(
    "AutoscalingSolrSlaveGroup",
    MinSize="2",
    MaxSize="3",
    VPCZoneIdentifier=Ref(PrivateSubnets),
    DesiredCapacity="2",
    LaunchConfigurationName=Ref("LaunchConfigSolrSlave"),
))

CPUAlarmHighPublic = t.add_resource(Alarm(
    "CPUAlarmHighPublic",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPublicCluster")
            ),
        ],
    AlarmActions=[Ref("ScaleUpPolicyPublic")],
    AlarmDescription="Scale-up if CPU reserved > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(CPUHighThresholdPublic),
    MetricName="CPUReservation",
))

SolrSlaveScaleDownPolicy = t.add_resource(ScalingPolicy(
    "SolrSlaveScaleDownPolicy",
    ScalingTargetId=Ref("SolrSlavescalableTarget"),
    PolicyName="SolrSlaveScaleDown",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=-1, MetricIntervalUpperBound=0) ], AdjustmentType="ChangeInCapacity" )
))

CPUAlarmLowPrivateSolrGlobalNutch = t.add_resource(Alarm(
    "CPUAlarmLowPrivateSolrGlobalNutch",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateClusterSolrGlobalNutch")
            ),
        ],
    AlarmActions=[Ref("ScaleDownPolicySolrGlobalNutch")],
    AlarmDescription="Scale-down if CPU Reserved < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(CPULowThresholdPrivate),
    MetricName="CPUReservation",
))

MongoReplica1scalableTarget = t.add_resource(ScalableTarget(
    "MongoReplica1scalableTarget",
    ScalableDimension="ecs:service:DesiredCount",
    ResourceId=Join("", ["service/", Ref("ECSPrivateClusterMongoReplica1"), "/", GetAtt("MongoReplica1Service", "Name")]),
    RoleARN=GetAtt("ECSAutoscaleRole", "Arn"),
    MinCapacity=1,
    ServiceNamespace="ecs",
    MaxCapacity=2,
))

MongoReplica2ScaleDownPolicy = t.add_resource(ScalingPolicy(
    "MongoReplica2ScaleDownPolicy",
    ScalingTargetId=Ref("MongoReplica2scalableTarget"),
    PolicyName="MongoReplica2ScaleDown",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=-1, MetricIntervalUpperBound=0) ], AdjustmentType="ChangeInCapacity" )
))

CertificationTask = t.add_resource(TaskDefinition(
    "CertificationTask",
    ContainerDefinitions=[
    ContainerDefinition(
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/", Ref(ConfigEnv)]),
        Name="data",
        Essential="false",
        Memory=128,
    ),
    ContainerDefinition(
        PortMappings=[PortMapping(ContainerPort= Ref(CertificationContainerPort) )],
        Name="Certification",
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/certification", ":", Ref(CertificationImageVersion)]),
        Essential="true",
        Environment=[Environment(Name="SERVICE_NAME",Value="certification") ],
        Memory=Ref(CertificationMemory),
        Cpu=Ref(CertificationCpu),
        VolumesFrom=[VolumesFrom(SourceContainer="data")],
    )
    ],
))

SolrSlaveTask = t.add_resource(TaskDefinition(
    "SolrSlaveTask",
    ContainerDefinitions=[
    ContainerDefinition(
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/", Ref(ConfigEnv)]),
        Name="data",
        Essential="false",
        Memory=128,
    ),
    ContainerDefinition(
        PortMappings=[PortMapping(ContainerPort= Ref(SolrContainerPort) )],
        Name="SolrSlave",
        MountPoints=[MountPoint(SourceVolume="data", ContainerPath= "/opt/data" )],
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/solr", ":", Ref(SolrImageVersion)]),
        Essential="true",
        Environment=[Environment(Name="NODE_TYPE",Value="SLAVE"),Environment(Name="MASTER", Value= Ref(SolrSlaveMasterNode)) ],
        Memory=Ref(SolrMemory),
        Cpu=Ref(SolrCpu),
        VolumesFrom=[VolumesFrom(SourceContainer="data" )],
    ),
    ],
    Volumes=[Volume(Host=Host(SourcePath="/opt/data/") , Name="data" )],
))

ECSAutoscaleRole = t.add_resource(Role(
    "ECSAutoscaleRole",
    RoleName="ecsAutoscaleRole",
    Path="/",
    Policies=[Policy(PolicyName="AmazonEC2ContainerServiceAutoscale", PolicyDocument={ "Statement": [{ "Action": ["application-autoscaling:*", "cloudwatch:DescribeAlarms", "cloudwatch:PutMetricAlarm", "ecs:DescribeServices", "ecs:UpdateService"], "Resource": "*", "Effect": "Allow" }] } )],
    AssumeRolePolicyDocument={ "Statement": [{ "Action": ["sts:AssumeRole"], "Effect": "Allow", "Principal": { "Service": ["application-autoscaling.amazonaws.com"] } }] },
))

CertificationscalableTarget = t.add_resource(ScalableTarget(
    "CertificationscalableTarget",
    ScalableDimension="ecs:service:DesiredCount",
    ResourceId=Join("", ["service/", Ref("ECSPrivateCluster"), "/", GetAtt(CertificationService, "Name")]),
    RoleARN=GetAtt(ECSAutoscaleRole, "Arn"),
    MinCapacity=Ref(MinCertificationSize),
    ServiceNamespace="ecs",
    MaxCapacity=Ref(MaxCertificationSize),
))

SolrMasterScaleDownPolicy = t.add_resource(ScalingPolicy(
    "SolrMasterScaleDownPolicy",
    ScalingTargetId=Ref("SolrMasterscalableTarget"),
    PolicyName="SolrMasterScaleDown",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=-1, MetricIntervalUpperBound=0) ], AdjustmentType="ChangeInCapacity" )
))

SolrMasterTask = t.add_resource(TaskDefinition(
    "SolrMasterTask",
    ContainerDefinitions=[
    ContainerDefinition(
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/", Ref(ConfigEnv)]),
        Name="data",
        Essential="false",
        Memory=128,
    ),
    ContainerDefinition(
        PortMappings=[PortMapping(ContainerPort= Ref(SolrContainerPort) )],
        MountPoints=[MountPoint(SourceVolume="data", ContainerPath= "/opt/data" )],
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/solr", ":", Ref(SolrImageVersion)]),
        Essential="true",
        Environment=[Environment(Name="NODE_TYPE",Value="MASTER") ],
        Name="SolrMaster",
        Memory=Ref(SolrMemory),
        Cpu=Ref(SolrCpu),
        VolumesFrom=[VolumesFrom(SourceContainer="data" )],
    ),
    ],
    Volumes=[Volume(Host=Host(SourcePath="/opt/data/") , Name="data" )],

))

AutoscalingSolrBURNutchGroup = t.add_resource(AutoScalingGroup(
    "AutoscalingSolrBURNutchGroup",
    MinSize="1",
    MaxSize="2",
    VPCZoneIdentifier=Ref(PrivateSubnets),
    DesiredCapacity="1",
    LaunchConfigurationName=Ref("LaunchConfigSolrBURNutch"),
))

SolrGlobalNutchELB = t.add_resource(LoadBalancerv2(
    "SolrGlobalNutchELB",
    Subnets=Ref(PublicSubnets),
    Scheme="internal",
    SecurityGroups=[Ref("SGPrivate")],
    LoadBalancerAttributes=[LoadBalancerAttributes(Value="50", Key= "idle_timeout.timeout_seconds" )],
))

OhsscalableTarget = t.add_resource(ScalableTarget(
    "OhsscalableTarget",
    ScalableDimension="ecs:service:DesiredCount",
    ResourceId=Join("", ["service/", Ref("ECSPublicCluster"), "/", GetAtt("OhsService", "Name")]),
    RoleARN=GetAtt(ECSAutoscaleRole, "Arn"),
    MinCapacity=2,
    ServiceNamespace="ecs",
    MaxCapacity=4,
))

SolrMasterListener = t.add_resource(Listener(
    "SolrMasterListener",
    Protocol="HTTP",
    DefaultActions=[Action(TargetGroupArn=Ref("SolrMasterELBTarget"), Type="forward" )],
    LoadBalancerArn=Ref("SolrMasterELB"),
    Port=network_port("8983"),
))

SolrGlobalNutchService = t.add_resource(Service(
    "SolrGlobalNutchService",
    LoadBalancers=[LoadBalancer(
        ContainerName="SolrGlobalNutch",
        ContainerPort=network_port(Ref("SolrNutchPort")),
        TargetGroupArn=Ref("SolrGlobalNutchELBTarget")
    )],
    Cluster=Ref("ECSPrivateClusterSolrGlobalNutch"),
    Role=Ref(ECSServiceRole),
    TaskDefinition=Ref(SolrGlobalNutchTask),
    DesiredCount=1,
    DependsOn=["SolrGlobalNutchELB", "SolrGlobalNutchListener"],
))

ECSPublicCluster = t.add_resource(Cluster(
    "ECSPublicCluster",
))

ECSPrivateClusterSolrBURNutch = t.add_resource(Cluster(
    "ECSPrivateClusterSolrBURNutch",
))

SolrBURNutchListener = t.add_resource(Listener(
    "SolrBURNutchListener",
    Protocol="HTTP",
    DefaultActions=[Action(TargetGroupArn=Ref("SolrBURNutchELBTarget"), Type="forward" )], 
    LoadBalancerArn=Ref("SolrBURNutchELB"),
    Port=network_port("8983"),
))

AutoprocCPUAlarmLow = t.add_resource(Alarm(
    "AutoprocCPUAlarmLow",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateCluster")
            ),
        
            MetricDimension(
                Name="ServiceName",
                Value=  GetAtt(AutoprocService, "Name")
            ),
        ],
    AlarmActions=[Ref("AutoprocScaleDownPolicy")],
    AlarmDescription="Scale-down if CPU < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPULowThreshold),
    MetricName="CPUUtilization",
))

LiferayELBTarget = t.add_resource(TargetGroup(
    "LiferayELBTarget",
    HealthyThresholdCount=5,
    HealthCheckIntervalSeconds=300,
    VpcId=Ref(VPC),
    Protocol="HTTP",
    HealthCheckProtocol="HTTP",
    UnhealthyThresholdCount=4,
    HealthCheckPath="/",
    HealthCheckTimeoutSeconds=60,
    Matcher=Matcher(HttpCode="301"),
    Port=network_port(5000),
))

GeneralCPUAlarmLow = t.add_resource(Alarm(
    "GeneralCPUAlarmLow",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateCluster")
            ),

            MetricDimension(
                Name="ServiceName",
                Value=  GetAtt("GeneralService", "Name")
            ),
        ],
    AlarmActions=[Ref("GeneralScaleDownPolicy")],
    AlarmDescription="Scale-down if CPU < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPULowThreshold),
    MetricName="CPUUtilization",
))

MongoReplica1Service = t.add_resource(Service(
    "MongoReplica1Service",
    LoadBalancers=[LoadBalancer(
        ContainerName="MongoReplica1",
        ContainerPort=network_port("27017"),
        TargetGroupArn=Ref("MongoReplica1ELBTarget")
    )],
    Cluster=Ref("ECSPrivateClusterMongoReplica1"),
    Role=Ref(ECSServiceRole),
    TaskDefinition=Ref(MongoReplica1Task),
    DesiredCount=1,
    DependsOn=["MongoReplica1ELB", "MongoReplica1Listener"],
))

CPUAlarmLowPrivateMongoReplica1 = t.add_resource(Alarm(
    "CPUAlarmLowPrivateMongoReplica1",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateClusterMongoReplica1")
            ),
        ],
    AlarmActions=[Ref("ScaleDownPolicyMongoReplica1")],
    AlarmDescription="Scale-down if CPU Reserved < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(CPULowThresholdPrivate),
    MetricName="CPUReservation",
))

CPUAlarmLowPrivateMongoReplica2 = t.add_resource(Alarm(
    "CPUAlarmLowPrivateMongoReplica2",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateClusterMongoReplica2")
            ),
        ],
    AlarmActions=[Ref("ScaleDownPolicyMongoReplica2")],
    AlarmDescription="Scale-down if CPU Reserved < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(CPULowThresholdPrivate),
    MetricName="CPUReservation",
))

BodybeastELB = t.add_resource(LoadBalancerv2(
    "BodybeastELB",
    Subnets=Ref(PublicSubnets),
    Scheme="internal",
    SecurityGroups=[Ref("SGPrivate")],
    LoadBalancerAttributes=[LoadBalancerAttributes(Value="50", Key="idle_timeout.timeout_seconds" )],
))

LaunchConfigPublic = t.add_resource(LaunchConfiguration(
    "LaunchConfigPublic",
    UserData=Base64(Join("", ["#!/bin/bash\n", "yum update -y\n", "yum install -y ecs-init\n", "yum install -y docker\n", "sed -i  '1s/^/nameserver 10.1.64.15\\nnameserver 10.253.34.15\\n/' /etc/resolv.conf\n", "echo ECS_CLUSTER=", Ref(ECSPublicCluster), " > /etc/ecs/ecs.config\n", "service docker restart\n", "start ecs\n"])),
    InstanceMonitoring="false",
    ImageId=FindInMap("AWSRegion2AMI", Ref("AWS::Region"), "64"),
    BlockDeviceMappings=[{ "DeviceName": "/dev/xvda", "Ebs": { "Iops": 500, "VolumeSize": "100", "VolumeType": "io1" } }],
    KeyName=Ref(KeyName),
    SecurityGroups=[Ref("SGPublic"), Ref("SGPrivate")],
    IamInstanceProfile=Ref("EC2InstanceProfile"),
    InstanceType=Ref(PublicInstanceType),
    AssociatePublicIpAddress="true",
))

AutoprocELB = t.add_resource(LoadBalancerv2(
    "AutoprocELB",
    Subnets=Ref(PublicSubnets),
    Scheme="internal",
    SecurityGroups=[Ref("SGPrivate")],
    LoadBalancerAttributes=[LoadBalancerAttributes(Value="50", Key="idle_timeout.timeout_seconds" )],
))

MongoReplica1Listener = t.add_resource(Listener(
    "MongoReplica1Listener",
    Protocol="HTTP",
    DefaultActions=[Action(TargetGroupArn= Ref("MongoReplica1ELBTarget"), Type="forward" )],
    LoadBalancerArn=Ref("MongoReplica1ELB"),
    Port=network_port("27017"),
))

AutoprocScaleUpPolicy = t.add_resource(ScalingPolicy(
    "AutoprocScaleUpPolicy",
    ScalingTargetId=Ref("AutoprocscalableTarget"),
    PolicyName="AutoprocScaleUp",
    PolicyType="StepScaling",
     StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=1, MetricIntervalLowerBound=0) ], AdjustmentType="ChangeInCapacity" ),
))


ScaleDownPolicyPrivate = t.add_resource(InstanceScalingPolicy(
    "ScaleDownPolicyPrivate",
    ScalingAdjustment="-1",
    Cooldown="300",
    AutoScalingGroupName=Ref("AutoscalingPrivateGroup"),
    AdjustmentType="ChangeInCapacity",
))

MongoReplica1CPUAlarmHigh = t.add_resource(Alarm(
    "MongoReplica1CPUAlarmHigh",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateClusterMongoReplica1")
            ),
       
            MetricDimension(
                Name="ServiceName",
                Value= GetAtt(MongoReplica1Service, "Name")
            ),
        ],
    AlarmActions=[Ref("MongoReplica1ScaleUpPolicy")],
    AlarmDescription="Scale-up if CPU > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPUHighThreshold),
    MetricName="CPUUtilization",
))

AutoprocCPUAlarmHigh = t.add_resource(Alarm(
    "AutoprocCPUAlarmHigh",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateCluster")
            ),

            MetricDimension(
                Name="ServiceName",
                Value= GetAtt(AutoprocService, "Name")
            ),
        ],
    AlarmActions=[Ref(AutoprocScaleUpPolicy)],
    AlarmDescription="Scale-up if CPU > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPUHighThreshold),
    MetricName="CPUUtilization",
))

MongoReplica2scalableTarget = t.add_resource(ScalableTarget(
    "MongoReplica2scalableTarget",
    ScalableDimension="ecs:service:DesiredCount",
    ResourceId=Join("", ["service/", Ref("ECSPrivateClusterMongoReplica2"), "/", GetAtt("MongoReplica2Service", "Name")]),
    RoleARN=GetAtt(ECSAutoscaleRole, "Arn"),
    MinCapacity=1,
    ServiceNamespace="ecs",
    MaxCapacity=2,
))

ECSPrivateClusterMongoReplica1 = t.add_resource(Cluster(
    "ECSPrivateClusterMongoReplica1",
))

ECSPrivateClusterMongoReplica2 = t.add_resource(Cluster(
    "ECSPrivateClusterMongoReplica2",
))

AutoscalingMongoReplica1Group = t.add_resource(AutoScalingGroup(
    "AutoscalingMongoReplica1Group",
    MinSize="1",
    MaxSize="2",
    VPCZoneIdentifier=Ref(PrivateSubnets),
    DesiredCapacity="1",
    LaunchConfigurationName=Ref("LaunchConfigMongoReplica1"),
))

AutoprocListener = t.add_resource(Listener(
    "AutoprocListener",
    Protocol="HTTP",
DefaultActions=[Action(TargetGroupArn= Ref("AutoprocELBTarget"), Type="forward" )],
    LoadBalancerArn=Ref(AutoprocELB),
    Port=network_port("80"),
))

AutoprocELBTarget = t.add_resource(TargetGroup(
    "AutoprocELBTarget",
    HealthyThresholdCount=5,
    HealthCheckIntervalSeconds=300,
    VpcId=Ref(VPC),
    Protocol="HTTP",
    HealthCheckProtocol="HTTP",
    UnhealthyThresholdCount=4,
    HealthCheckPath="/",
    HealthCheckTimeoutSeconds=60,
    Matcher=Matcher(HttpCode="200"),
    Port=5000,
))

ScaleDownPolicySolrMaster = t.add_resource(InstanceScalingPolicy(
    "ScaleDownPolicySolrMaster",
    ScalingAdjustment="-1",
    Cooldown="300",
    AutoScalingGroupName=Ref("AutoscalingSolrMasterGroup"),
    AdjustmentType="ChangeInCapacity",
))

EC2InstanceProfile = t.add_resource(InstanceProfile(
    "EC2InstanceProfile",
    Path="/",
    Roles=[Ref("EC2Role")],
))

ScaleDownPolicySolrBURNutch = t.add_resource(InstanceScalingPolicy(
    "ScaleDownPolicySolrBURNutch",
    ScalingAdjustment="-1",
    Cooldown="300",
    AutoScalingGroupName=Ref(AutoscalingSolrBURNutchGroup),
    AdjustmentType="ChangeInCapacity",
))

OhsScaleUpPolicy = t.add_resource(ScalingPolicy(
    "OhsScaleUpPolicy",
    ScalingTargetId=Ref(OhsscalableTarget),
    PolicyName="OhsScaleUp",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=1, MetricIntervalLowerBound=0) ], AdjustmentType="ChangeInCapacity" ),
))


CPUAlarmHighPrivateSolrMaster = t.add_resource(Alarm(
    "CPUAlarmHighPrivateSolrMaster",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateClusterSolrMaster")
            ),
        ],
    AlarmActions=[Ref("ScaleUpPolicySolrMaster")],
    AlarmDescription="Scale-up if CPU Reserved > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(CPUHighThresholdPrivate),
    MetricName="CPUReservation",
))

MongoReplica1CPUAlarmLow = t.add_resource(Alarm(
    "MongoReplica1CPUAlarmLow",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref(ECSPrivateClusterMongoReplica1)
            ),

            MetricDimension(
                Name="ServiceName",
                Value=  GetAtt(MongoReplica1Service, "Name")
            ),
        ],
    AlarmActions=[Ref("MongoReplica1ScaleDownPolicy")],
    AlarmDescription="Scale-down if CPU < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPULowThreshold),
    MetricName="CPUUtilization",
))

SolrMasterCPUAlarmLow = t.add_resource(Alarm(
    "SolrMasterCPUAlarmLow",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref(ECSPrivateClusterSolrMaster)
            ),

            MetricDimension(
                Name="ServiceName",
                Value= GetAtt(SolrMasterService, "Name")
            ),
        ],
    AlarmActions=[Ref(SolrMasterScaleDownPolicy)],
    AlarmDescription="Scale-down if CPU < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPULowThreshold),
    MetricName="CPUUtilization",
))

SolrGlobalNutchELBTarget = t.add_resource(TargetGroup(
    "SolrGlobalNutchELBTarget",
    HealthyThresholdCount=5,
    HealthCheckIntervalSeconds=300,
    VpcId=Ref(VPC),
    Protocol="HTTP",
    HealthCheckProtocol="HTTP",
    UnhealthyThresholdCount=4,
    HealthCheckPath="/solr/",
    HealthCheckTimeoutSeconds=60,
    Matcher=Matcher(HttpCode="200"),
    Port=5000,
))

ScaleUpPolicySolrMaster = t.add_resource(InstanceScalingPolicy(
    "ScaleUpPolicySolrMaster",
    ScalingAdjustment="1",
    Cooldown="300",
    AutoScalingGroupName=Ref("AutoscalingSolrMasterGroup"),
    AdjustmentType="ChangeInCapacity",
))

ECSPrivateClusterSolrGlobalNutch = t.add_resource(Cluster(
    "ECSPrivateClusterSolrGlobalNutch",
))

GeneralscalableTarget = t.add_resource(ScalableTarget(
    "GeneralscalableTarget",
    ScalableDimension="ecs:service:DesiredCount",
    ResourceId=Join("", ["service/", Ref("ECSPrivateCluster"), "/", GetAtt("GeneralService", "Name")]),
    RoleARN=GetAtt(ECSAutoscaleRole, "Arn"),
    MinCapacity=Ref(MinGeneralSize),
    ServiceNamespace="ecs",
    MaxCapacity=Ref(MaxGeneralSize),
))

SolrBURNutchscalableTarget = t.add_resource(ScalableTarget(
    "SolrBURNutchscalableTarget",
    ScalableDimension="ecs:service:DesiredCount",
    ResourceId=Join("", ["service/", Ref(ECSPrivateClusterSolrBURNutch), "/", GetAtt("SolrBURNutchService", "Name")]),
    RoleARN=GetAtt(ECSAutoscaleRole, "Arn"),
    MinCapacity=1,
    ServiceNamespace="ecs",
    MaxCapacity=2,
))

LiferayService = t.add_resource(Service(
    "LiferayService",
    LoadBalancers=[LoadBalancer(
        ContainerName="Liferay",
        ContainerPort=network_port(Ref("LiferayContainerPort")),
        TargetGroupArn=Ref("LiferayELBTarget")
    )],
    Cluster=Ref("ECSPrivateCluster"),
    Role=Ref(ECSServiceRole),
    TaskDefinition=Ref(LiferayTask),
    DesiredCount=Ref(MinLiferaySize),
    DependsOn=["LiferayELB", "LiferayListener"],
))

SGPrivate = t.add_resource(SecurityGroup(
    "SGPrivate",
    SecurityGroupIngress=[{ "ToPort": "65535", "IpProtocol": "tcp", "CidrIp": "10.0.0.0/8", "FromPort": "0" }, { "ToPort": "65535", "IpProtocol": "tcp", "CidrIp": "172.0.0.0/8", "FromPort": "0" }],
    VpcId=Ref(VPC),
    GroupDescription="PrivateSG",
))

CertificationCPUAlarmLow = t.add_resource(Alarm(
    "CertificationCPUAlarmLow",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateCluster")
            ),

            MetricDimension(
                Name="ServiceName",
                Value=  GetAtt("CertificationService", "Name")
            ),
        ],
    AlarmActions=[Ref(CertificationScaleDownPolicy)],
    AlarmDescription="Scale-down if CPU < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPULowThreshold),
    MetricName="CPUUtilization",
))

EC2Role = t.add_resource(Role(
    "EC2Role",
    RoleName="EC2Role",
    Path="/",
    Policies=[Policy(PolicyName="ecs-service", PolicyDocument={ "Statement": [{ "Action": ["ecs:CreateCluster", "ecs:DeregisterContainerInstance", "ecs:DiscoverPollEndpoint", "ecs:Poll", "ecs:RegisterContainerInstance", "ecs:StartTelemetrySession", "ecs:Submit*", "ecr:BatchCheckLayerAvailability", "ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer", "ecr:GetAuthorizationToken", "logs:CreateLogStream", "logs:PutLogEvents"], "Resource": "*", "Effect": "Allow" }] } )],
    AssumeRolePolicyDocument={ "Statement": [{ "Action": ["sts:AssumeRole"], "Effect": "Allow", "Principal": { "Service": ["ec2.amazonaws.com"] } }] },
))

LiferayCPUAlarmHigh = t.add_resource(Alarm(
    "LiferayCPUAlarmHigh",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateCluster")
            ),

            MetricDimension(
                Name="ServiceName",
                Value=  GetAtt(LiferayService, "Name")
            ),
        ],
    AlarmActions=[Ref("LiferayScaleUpPolicy")],
    AlarmDescription="Scale-up if CPU > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPUHighThreshold),
    MetricName="CPUUtilization",
))

OhsService = t.add_resource(Service(
    "OhsService",
    LoadBalancers=[LoadBalancer(
        ContainerName="Ohs",
        ContainerPort=network_port("7777"),
        TargetGroupArn=Ref("OhsELBTarget")
    )],
    Cluster=Ref(ECSPublicCluster),
    Role=Ref(ECSServiceRole),
    TaskDefinition=Ref("OhsTask"),
    DesiredCount=2,
    DependsOn=["OhsELB", "OhsListener"],
))

SolrGlobalNutchCPUAlarmLow = t.add_resource(Alarm(
    "SolrGlobalNutchCPUAlarmLow",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateClusterSolrGlobalNutch")
            ),

            MetricDimension(
                Name="ServiceName",
                Value=  GetAtt(SolrGlobalNutchService, "Name")
            ),
        ],
    AlarmActions=[Ref(SolrGlobalNutchScaleDownPolicy)],
    AlarmDescription="Scale-down if CPU < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPULowThreshold),
    MetricName="CPUUtilization",
))

OhsTask = t.add_resource(TaskDefinition(
    "OhsTask",
    ContainerDefinitions=[
    ContainerDefinition(
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/", Ref(ConfigEnv)]),
        Name="data",
        Essential="false",
        Memory=128,
    ),
    ContainerDefinition(
        Name="Ohs",
        Image="904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/ohs:latest",
        Cpu="2000",
        PortMappings=[PortMapping(ContainerPort= "7777" )],
        Memory="2000",
        Essential="true",
        VolumesFrom=[VolumesFrom( SourceContainer="data" )],
    ),
    ],
))

LaunchConfigSolrBURNutch = t.add_resource(LaunchConfiguration(
    "LaunchConfigSolrBURNutch",
    UserData=Base64(Join("", ["#!/bin/bash\n", "yum update -y\n", "yum install -y ecs-init\n", "yum install -y docker\n", "sed -i  '1s/^/nameserver 10.1.64.15\\nnameserver 10.253.34.15\\n/' /etc/resolv.conf\n", "mkfs -t ext4 /dev/`lsblk  | grep 200G | grep xvd | awk '{print$1}'`\n", "mkdir -p /opt/data\n", "chmod -R 777 /opt/data\n", "cp /etc/fstab /etc/fstab.orig\n", "echo /dev/`lsblk  | grep 200G | grep xvd | awk '{print$1}'` /opt/data/ ext4 defaults, nofail 0 2  >> /etc/fstab\n", "mount -a\n", "echo ECS_CLUSTER=", Ref(ECSPrivateClusterSolrBURNutch), " > /etc/ecs/ecs.config\n", "service docker restart\n", "start ecs\n"])),
    InstanceMonitoring="false",
    ImageId=FindInMap("AWSRegion2AMI", Ref("AWS::Region"), "64"),
    BlockDeviceMappings=[{ "DeviceName": "/dev/xvda", "Ebs": { "Iops": 500, "VolumeSize": "100", "VolumeType": "io1" } }, { "DeviceName": "/dev/xvdb", "Ebs": { "Iops": 500, "DeleteOnTermination": "false", "VolumeType": "io1", "VolumeSize": "200" } }],
    KeyName=Ref(KeyName),
    SecurityGroups=[Ref(SGPrivate)],
    IamInstanceProfile=Ref(EC2InstanceProfile),
    InstanceType=Ref(PrivateInstanceType),
))

CPUAlarmHighPrivateSolrSlave = t.add_resource(Alarm(
    "CPUAlarmHighPrivateSolrSlave",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateClusterSolriSlave")
            )
        ],
    AlarmActions=[Ref(ScaleUpPolicySolrSlave)],
    AlarmDescription="Scale-up if CPU Reserved > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(CPUHighThresholdPrivate),
    MetricName="CPUReservation",
))

AutoprocScaleDownPolicy = t.add_resource(ScalingPolicy(
    "AutoprocScaleDownPolicy",
    ScalingTargetId=Ref("AutoprocscalableTarget"),
    PolicyName="AutoprocScaleDown",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=-1, MetricIntervalUpperBound=0) ], AdjustmentType="ChangeInCapacity" )
))

BodybeastService = t.add_resource(Service(
    "BodybeastService",
    LoadBalancers=[LoadBalancer(
        ContainerName="Bodybeast",
        ContainerPort=network_port(Ref("BodybeastContainerPort")),
        TargetGroupArn=Ref("BodybeastELBTarget")
    )],
    Cluster=Ref("ECSPrivateCluster"),
    Role=Ref(ECSServiceRole),
    TaskDefinition=Ref("BodybeastTask"),
    DesiredCount=Ref(MinBodybeastSize),
    DependsOn=["BodybeastELB", "BodybeastListener"],
))

SolrBURNutchScaleDownPolicy = t.add_resource(ScalingPolicy(
    "SolrBURNutchScaleDownPolicy",
    ScalingTargetId=Ref(SolrBURNutchscalableTarget),
    PolicyName="SolrBURNutchScaleDown",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=-1, MetricIntervalUpperBound=0) ], AdjustmentType="ChangeInCapacity" )
))

LaunchConfigSolrGlobalNutch = t.add_resource(LaunchConfiguration(
    "LaunchConfigSolrGlobalNutch",
    UserData=Base64(Join("", ["#!/bin/bash\n", "yum update -y\n", "yum install -y ecs-init\n", "yum install -y docker\n", "sed -i  '1s/^/nameserver 10.1.64.15\\nnameserver 10.253.34.15\\n/' /etc/resolv.conf\n", "mkfs -t ext4 /dev/`lsblk  | grep 200G | grep xvd | awk '{print$1}'`\n", "mkdir -p /opt/data\n", "chmod -R 777 /opt/data\n", "cp /etc/fstab /etc/fstab.orig\n", "echo /dev/`lsblk  | grep 200G | grep xvd | awk '{print$1}'` /opt/data/ ext4 defaults, nofail 0 2  >> /etc/fstab\n", "mount -a\n", "echo ECS_CLUSTER=", Ref(ECSPrivateClusterSolrGlobalNutch), " > /etc/ecs/ecs.config\n", "service docker restart\n", "start ecs\n"])),
    InstanceMonitoring="false",
    ImageId=FindInMap("AWSRegion2AMI", Ref("AWS::Region"), "64"),
    BlockDeviceMappings=[{ "DeviceName": "/dev/xvda", "Ebs": { "Iops": 500, "VolumeSize": "100", "VolumeType": "io1" } }, { "DeviceName": "/dev/xvdb", "Ebs": { "Iops": 500, "DeleteOnTermination": "false", "VolumeType": "io1", "VolumeSize": "200" } }],
    KeyName=Ref(KeyName),
    SecurityGroups=[Ref(SGPrivate)],
    IamInstanceProfile=Ref(EC2InstanceProfile),
    InstanceType=Ref(PrivateInstanceType),
))

ScaleDownPolicySolrGlobalNutch = t.add_resource(InstanceScalingPolicy(
    "ScaleDownPolicySolrGlobalNutch",
    ScalingAdjustment="-1",
    Cooldown="300",
    AutoScalingGroupName=Ref("AutoscalingSolrGlobalNutchGroup"),
    AdjustmentType="ChangeInCapacity",
))

SolrSlavescalableTarget = t.add_resource(ScalableTarget(
    "SolrSlavescalableTarget",
    ScalableDimension="ecs:service:DesiredCount",
    ResourceId=Join("", ["service/", Ref("ECSPrivateClusterSolrSlave"), "/", GetAtt("SolrSlaveService", "Name")]),
    RoleARN=GetAtt(ECSAutoscaleRole, "Arn"),
    MinCapacity=Ref(MinSolrSlaveSize),
    ServiceNamespace="ecs",
    MaxCapacity=Ref(MaxSolrSlaveSize),
))

ScaleUpPolicyPublic = t.add_resource(InstanceScalingPolicy(
    "ScaleUpPolicyPublic",
    ScalingAdjustment="1",
    Cooldown="300",
    AutoScalingGroupName=Ref("AutoscalingPublicGroup"),
    AdjustmentType="ChangeInCapacity",
))

GeneralListener = t.add_resource(Listener(
    "GeneralListener",
    Protocol="HTTP",
    DefaultActions=[Action(TargetGroupArn=Ref("GeneralELBTarget"), Type= "forward")],
    LoadBalancerArn=Ref("GeneralELB"),
    Port=network_port("80"),
))

AutoscalingPublicGroup = t.add_resource(AutoScalingGroup(
    "AutoscalingPublicGroup",
    MinSize=Ref(MinPublicClusterSize),
    MaxSize=Ref(MaxPublicClusterSize),
    VPCZoneIdentifier=Ref(PublicSubnets),
    DesiredCapacity=Ref(MinPublicClusterSize),
    LaunchConfigurationName=Ref(LaunchConfigPublic),
))

AutoscalingMongoReplica2Group = t.add_resource(AutoScalingGroup(
    "AutoscalingMongoReplica2Group",
    MinSize="1",
    MaxSize="2",
    VPCZoneIdentifier=Ref(PrivateSubnets),
    DesiredCapacity="1",
    LaunchConfigurationName=Ref("LaunchConfigMongoReplica2"),
))

CPUAlarmLowPrivate = t.add_resource(Alarm(
    "CPUAlarmLowPrivate",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateCluster")
            )
        ],
    AlarmActions=[Ref(ScaleDownPolicyPrivate)],
    AlarmDescription="Scale-down if CPU Reserved < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(CPULowThresholdPrivate),
    MetricName="CPUReservation",
))

CPUAlarmLowPublic = t.add_resource(Alarm(
    "CPUAlarmLowPublic",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPublicCluster")
            )
        ],
    AlarmActions=[Ref("ScaleDownPolicyPublic")],
    AlarmDescription="Scale-down if CPU reserved < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(CPULowThresholdPublic),
    MetricName="CPUReservation",
))

ECSPrivateClusterSolrSlave = t.add_resource(Cluster(
    "ECSPrivateClusterSolrSlave",
))

MongoReplica1ScaleUpPolicy = t.add_resource(ScalingPolicy(
    "MongoReplica1ScaleUpPolicy",
    ScalingTargetId=Ref(MongoReplica1scalableTarget),
    PolicyName="MongoReplica1ScaleUp",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=1, MetricIntervalLowerBound=0) ], AdjustmentType="ChangeInCapacity" ),
))


LiferayListener = t.add_resource(Listener(
    "LiferayListener",
    Protocol="HTTP",
    DefaultActions=[Action(TargetGroupArn=Ref(LiferayELBTarget), Type="forward" )],
    LoadBalancerArn=Ref("LiferayELB"),
    Port="80",
))

CPUAlarmHighPrivateSolrBURNutch = t.add_resource(Alarm(
    "CPUAlarmHighPrivateSolrBURNutch",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateClusterSolrBURNutch")
            )
        ],
    AlarmActions=[Ref("ScaleUpPolicySolrBURNutch")],
    AlarmDescription="Scale-up if CPU Reserved > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(CPUHighThresholdPrivate),
    MetricName="CPUReservation",
))

MongoReplica2CPUAlarmHigh = t.add_resource(Alarm(
    "MongoReplica2CPUAlarmHigh",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref(ECSPrivateClusterMongoReplica2)
            ),

            MetricDimension(
                Name="ServiceName",
                Value=  GetAtt("MongoReplica2Service", "Name")
            ),
        ],
    AlarmActions=[Ref("MongoReplica2ScaleUpPolicy")],
    AlarmDescription="Scale-up if CPU > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPUHighThreshold),
    MetricName="CPUUtilization",
))

LaunchConfigSolrSlave = t.add_resource(LaunchConfiguration(
    "LaunchConfigSolrSlave",
    UserData=Base64(Join("", ["#!/bin/bash\n", "yum update -y\n", "yum install -y ecs-init\n", "yum install -y docker\n", "sed -i  '1s/^/nameserver 10.1.64.15\\nnameserver 10.253.34.15\\n/' /etc/resolv.conf\n", "mkfs -t ext4 /dev/`lsblk  | grep 200G | grep xvd | awk '{print$1}'`\n", "mkdir -p /opt/data\n", "chmod -R 777 /opt/data\n", "cp /etc/fstab /etc/fstab.orig\n", "echo /dev/`lsblk  | grep 200G | grep xvd | awk '{print$1}'` /opt/data/ ext4 defaults, nofail 0 2  >> /etc/fstab\n", "mount -a\n", "echo ECS_CLUSTER=", Ref(ECSPrivateClusterSolrSlave), " > /etc/ecs/ecs.config\n", "service docker restart\n", "start ecs\n"])),
    InstanceMonitoring="false",
    ImageId=FindInMap("AWSRegion2AMI", Ref("AWS::Region"), "64"),
    BlockDeviceMappings=[{ "DeviceName": "/dev/xvda", "Ebs": { "Iops": 500, "VolumeSize": "100", "VolumeType": "io1" } }, { "DeviceName": "/dev/xvdb", "Ebs": { "Iops": 500, "DeleteOnTermination": "false", "VolumeType": "io1", "VolumeSize": "200" } }],
    KeyName=Ref(KeyName),
    SecurityGroups=[Ref(SGPrivate)],
    IamInstanceProfile=Ref(EC2InstanceProfile),
    InstanceType=Ref(PrivateInstanceType),
))

SolrSlaveService = t.add_resource(Service(
    "SolrSlaveService",
    LoadBalancers=[LoadBalancer(
        ContainerName="SolrSlave",
        ContainerPort=network_port(Ref("SolrContainerPort")),
        TargetGroupArn=Ref("SolrSlaveELBTarget")
    )],
    Cluster=Ref(ECSPrivateClusterSolrSlave),
    Role=Ref(ECSServiceRole),
    TaskDefinition=Ref(SolrSlaveTask),
    DesiredCount=1,
    DependsOn=["SolrSlaveELB", "SolrSlaveListener"],
))

LiferayScaleUpPolicy = t.add_resource(ScalingPolicy(
    "LiferayScaleUpPolicy",
    ScalingTargetId=Ref(LiferayscalableTarget),
    PolicyName="LiferayScaleUp",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=1, MetricIntervalLowerBound=0) ], AdjustmentType="ChangeInCapacity" ),
))


SolrSlaveCPUAlarmLow = t.add_resource(Alarm(
    "SolrSlaveCPUAlarmLow",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref(ECSPrivateClusterSolrSlave)
            ),

            MetricDimension(
                Name="ServiceName",
                Value=  GetAtt("SolrSlaveService", "Name")
            ),
        ],
    AlarmActions=[Ref(SolrSlaveScaleDownPolicy)],
    AlarmDescription="Scale-down if CPU < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPULowThreshold),
    MetricName="CPUUtilization",
))

SolrGlobalNutchListener = t.add_resource(Listener(
    "SolrGlobalNutchListener",
    Protocol="HTTP",
    DefaultActions=[Action(TargetGroupArn=Ref("SolrGlobalNutchELBTarget"),Type="forward" )],
    LoadBalancerArn=Ref("SolrGlobalNutchELB"),
    Port="8983",
))

LaunchConfigMongoReplica1 = t.add_resource(LaunchConfiguration(
    "LaunchConfigMongoReplica1",
    UserData=Base64(Join("", ["#!/bin/bash\n", "yum update -y\n", "yum install -y ecs-init\n", "yum install -y docker\n", "sed -i  '1s/^/nameserver 10.1.64.15\\nnameserver 10.253.34.15\\n/' /etc/resolv.conf\n", "mkfs -t ext4 /dev/`lsblk  | grep 200G | grep xvd | awk '{print$1}'`\n", "mkdir -p /opt/mongodb\n", "chmod -R 777 /opt/mongodb\n", "cp /etc/fstab /etc/fstab.orig\n", "echo /dev/`lsblk  | grep 200G | grep xvd | awk '{print$1}'` /opt/mongodb/ ext4 defaults, nofail 0 2  >> /etc/fstab\n", "mount -a\n", "echo ECS_CLUSTER=", Ref(ECSPrivateClusterMongoReplica1), " > /etc/ecs/ecs.config\n", "service docker restart\n", "start ecs\n"])),
    InstanceMonitoring="false",
    ImageId=FindInMap("AWSRegion2AMI", Ref("AWS::Region"), "64"),
    BlockDeviceMappings=[{ "DeviceName": "/dev/xvda", "Ebs": { "Iops": 500, "VolumeSize": "100", "VolumeType": "io1" } }, { "DeviceName": "/dev/xvdb", "Ebs": { "Iops": 500, "DeleteOnTermination": "false", "VolumeType": "io1", "VolumeSize": "200" } }],
    KeyName=Ref(KeyName),
    SecurityGroups=[Ref(SGPrivate)],
    IamInstanceProfile=Ref(EC2InstanceProfile),
    InstanceType=Ref(PrivateInstanceType),
))

LaunchConfigMongoReplica2 = t.add_resource(LaunchConfiguration(
    "LaunchConfigMongoReplica2",
    UserData=Base64(Join("", ["#!/bin/bash\n", "yum update -y\n", "yum install -y ecs-init\n", "yum install -y docker\n", "sed -i  '1s/^/nameserver 10.1.64.15\\nnameserver 10.253.34.15\\n/' /etc/resolv.conf\n", "mkfs -t ext4 /dev/`lsblk  | grep 200G | grep xvd | awk '{print$1}'`\n", "mkdir -p /opt/mongodb\n", "chmod -R 777 /opt/mongodb\n", "cp /etc/fstab /etc/fstab.orig\n", "echo /dev/`lsblk  | grep 200G | grep xvd | awk '{print$1}'` /opt/mongodb/ ext4 defaults, nofail 0 2  >> /etc/fstab\n", "mount -a\n", "echo ECS_CLUSTER=", Ref(ECSPrivateClusterMongoReplica2), " > /etc/ecs/ecs.config\n", "service docker restart\n", "start ecs\n"])),
    InstanceMonitoring="false",
    ImageId=FindInMap("AWSRegion2AMI", Ref("AWS::Region"), "64"),
    BlockDeviceMappings=[{ "DeviceName": "/dev/xvda", "Ebs": { "Iops": 500, "VolumeSize": "100", "VolumeType": "io1" } }, { "DeviceName": "/dev/xvdb", "Ebs": { "Iops": 500, "DeleteOnTermination": "false", "VolumeType": "io1", "VolumeSize": "200" } }],
    KeyName=Ref(KeyName),
    SecurityGroups=[Ref(SGPrivate)],
    IamInstanceProfile=Ref(EC2InstanceProfile),
    InstanceType=Ref(PrivateInstanceType),
))

MongoReplica2ELBTarget = t.add_resource(TargetGroup(
    "MongoReplica2ELBTarget",
    HealthyThresholdCount=5,
    HealthCheckIntervalSeconds=300,
    VpcId=Ref(VPC),
    Protocol="HTTP",
    HealthCheckProtocol="HTTP",
    UnhealthyThresholdCount=4,
    HealthCheckPath="/",
    HealthCheckTimeoutSeconds=60,
    Matcher=Matcher(HttpCode="200"),
    Port=5000,
))

SolrSlaveScaleUpPolicy = t.add_resource(ScalingPolicy(
    "SolrSlaveScaleUpPolicy",
    ScalingTargetId=Ref(SolrSlavescalableTarget),
    PolicyName="SolrSlaveScaleUp",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=1, MetricIntervalLowerBound=0) ], AdjustmentType="ChangeInCapacity" ),
))


AutoscalingSolrGlobalNutchGroup = t.add_resource(AutoScalingGroup(
    "AutoscalingSolrGlobalNutchGroup",
    MinSize="1",
    MaxSize="2",
    VPCZoneIdentifier=Ref(PrivateSubnets),
    DesiredCapacity="1",
    LaunchConfigurationName=Ref(LaunchConfigSolrGlobalNutch),
))

CPUAlarmHighPrivateMongoReplica2 = t.add_resource(Alarm(
    "CPUAlarmHighPrivateMongoReplica2",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateClusterMongoReplica2")
            )
        ],
    AlarmActions=[Ref(ScaleUpPolicyMongoReplica2)],
    AlarmDescription="Scale-up if CPU Reserved > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(CPUHighThresholdPrivate),
    MetricName="CPUReservation",
))

CPUAlarmHighPrivateMongoReplica1 = t.add_resource(Alarm(
    "CPUAlarmHighPrivateMongoReplica1",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateClusterMongoReplica1")
            )
        ],
    AlarmActions=[Ref("ScaleUpPolicyMongoReplica1")],
    AlarmDescription="Scale-up if CPU Reserved > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(CPUHighThresholdPrivate),
    MetricName="CPUReservation",
))

MongoReplica2Task = t.add_resource(TaskDefinition(
    "MongoReplica2Task",
    ContainerDefinitions=[
    ContainerDefinition(
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/", Ref(ConfigEnv)]),
        Name="data",
        Essential="false",
        Memory=128,
    ),
    ContainerDefinition(

        Name="MongoReplica2",
        Image="904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/mongo_replica:latest",
        Cpu="400",
        Memory="2000",
        Essential="true",

        PortMappings=[PortMapping(ContainerPort="27017" )],
        MountPoints=[MountPoint(SourceVolume="mongodb", ContainerPath= "/opt/mongodb" )],
        VolumesFrom=[VolumesFrom(SourceContainer="data" )],
    )],
    Volumes=[Volume(Host=Host(SourcePath="/opt/mongodb/") , Name="mongodb" )],

))

MongoReplica1ScaleDownPolicy = t.add_resource(ScalingPolicy(
    "MongoReplica1ScaleDownPolicy",
    ScalingTargetId=Ref(MongoReplica1scalableTarget),
    PolicyName="MongoReplica1ScaleDown",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=-1, MetricIntervalUpperBound=0) ], AdjustmentType="ChangeInCapacity" )
))


SolrMasterscalableTarget = t.add_resource(ScalableTarget(
    "SolrMasterscalableTarget",
    ScalableDimension="ecs:service:DesiredCount",
    ResourceId=Join("", ["service/", Ref(ECSPrivateClusterSolrMaster), "/", GetAtt(SolrMasterService, "Name")]),
    RoleARN=GetAtt(ECSAutoscaleRole, "Arn"),
    MinCapacity=1,
    ServiceNamespace="ecs",
    MaxCapacity=2,
))

SolrMasterELB = t.add_resource(LoadBalancerv2(
    "SolrMasterELB",
    Subnets=Ref(PublicSubnets),
    Scheme="internal",
    SecurityGroups=[Ref(SGPrivate)],
    LoadBalancerAttributes=[LoadBalancerAttributes(Value="50", Key="idle_timeout.timeout_seconds" )],
))

SolrSlaveELB = t.add_resource(LoadBalancerv2(
    "SolrSlaveELB",
    Subnets=Ref(PublicSubnets),
    Scheme="internal",
    SecurityGroups=[Ref(SGPrivate)],
    LoadBalancerAttributes=[LoadBalancerAttributes(Value="50", Key="idle_timeout.timeout_seconds" )],
))

BodybeastScaleDownPolicy = t.add_resource(ScalingPolicy(
    "BodybeastScaleDownPolicy",
    ScalingTargetId=Ref("BodybeastscalableTarget"),
    PolicyName="BodybeastScaleDown",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=-1, MetricIntervalUpperBound=0) ], AdjustmentType="ChangeInCapacity" )
))

SolrGlobalNutchCPUAlarmHigh = t.add_resource(Alarm(
    "SolrGlobalNutchCPUAlarmHigh",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref(ECSPrivateClusterSolrGlobalNutch)
            ),

            MetricDimension(
                Name="ServiceName",
                Value=  GetAtt("SolrGlobalNutchService", "Name")
            ),
        ],
    AlarmActions=[Ref(SolrGlobalNutchScaleUpPolicy)],
    AlarmDescription="Scale-up if CPU > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPUHighThreshold),
    MetricName="CPUUtilization",
))

ScaleUpPolicySolrBURNutch = t.add_resource(InstanceScalingPolicy(
    "ScaleUpPolicySolrBURNutch",
    ScalingAdjustment="1",
    Cooldown="300",
    AutoScalingGroupName=Ref(AutoscalingSolrBURNutchGroup),
    AdjustmentType="ChangeInCapacity",
))

AutoscalingSolrMasterGroup = t.add_resource(AutoScalingGroup(
    "AutoscalingSolrMasterGroup",
    MinSize="1",
    MaxSize="2",
    VPCZoneIdentifier=Ref(PrivateSubnets),
    DesiredCapacity="1",
    LaunchConfigurationName=Ref(LaunchConfigSolrMaster),
))

CertificationListener = t.add_resource(Listener(
    "CertificationListener",
    Protocol="HTTP",
    DefaultActions=[Action(TargetGroupArn=Ref("CertificationELBTarget"), Type="forward" )],
    LoadBalancerArn=Ref("CertificationELB"),
    Port="80",
))

SolrBURNutchCPUAlarmLow = t.add_resource(Alarm(
    "SolrBURNutchCPUAlarmLow",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref(ECSPrivateClusterSolrBURNutch)
            ),

            MetricDimension(
                Name="ServiceName",
                Value=  GetAtt("SolrBURNutchService", "Name")
            ),
        ],
    AlarmActions=[Ref(SolrBURNutchScaleDownPolicy)],
    AlarmDescription="Scale-down if CPU < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPULowThreshold),
    MetricName="CPUUtilization",
))

GeneralScaleDownPolicy = t.add_resource(ScalingPolicy(
    "GeneralScaleDownPolicy",
    ScalingTargetId=Ref(GeneralscalableTarget),
    PolicyName="GeneralScaleDown",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=-1, MetricIntervalUpperBound=0) ], AdjustmentType="ChangeInCapacity" )
))

GeneralService = t.add_resource(Service(
    "GeneralService",
     LoadBalancers=[LoadBalancer(
        ContainerName="General",
        ContainerPort=network_port(Ref("GeneralContainerPort")),
        TargetGroupArn=Ref("GeneralELBTarget")
    )],
    Cluster=Ref("ECSPrivateCluster"),
    Role=Ref(ECSServiceRole),
    TaskDefinition=Ref(GeneralTask),
    DesiredCount=Ref(MinGeneralSize),
    DependsOn=["GeneralELB", "GeneralListener"],
))

ScaleDownPolicyMongoReplica1 = t.add_resource(InstanceScalingPolicy(
    "ScaleDownPolicyMongoReplica1",
    ScalingAdjustment="-1",
    Cooldown="300",
    AutoScalingGroupName=Ref(AutoscalingMongoReplica1Group),
    AdjustmentType="ChangeInCapacity",
))

ScaleDownPolicyMongoReplica2 = t.add_resource(InstanceScalingPolicy(
    "ScaleDownPolicyMongoReplica2",
    ScalingAdjustment="-1",
    Cooldown="300",
    AutoScalingGroupName=Ref(AutoscalingMongoReplica2Group),
    AdjustmentType="ChangeInCapacity",
))

AutoscalingPrivateGroup = t.add_resource(AutoScalingGroup(
    "AutoscalingPrivateGroup",
    MinSize=Ref(MinPrivateClusterSize),
    MaxSize=Ref(MaxPrivateClusterSize),
    VPCZoneIdentifier=Ref(PrivateSubnets),
    DesiredCapacity=Ref(MinPrivateClusterSize),
    LaunchConfigurationName=Ref(LaunchConfigPrivate),
))

ScaleUpPolicyMongoReplica1 = t.add_resource(InstanceScalingPolicy(
    "ScaleUpPolicyMongoReplica1",
    ScalingAdjustment="1",
    Cooldown="300",
    AutoScalingGroupName=Ref(AutoscalingMongoReplica1Group),
    AdjustmentType="ChangeInCapacity",
))

ScaleDownPolicySolrSlave = t.add_resource(InstanceScalingPolicy(
    "ScaleDownPolicySolrSlave",
    ScalingAdjustment="-1",
    Cooldown="300",
    AutoScalingGroupName=Ref(AutoscalingSolrSlaveGroup),
    AdjustmentType="ChangeInCapacity",
))

AutoprocTask = t.add_resource(TaskDefinition(
    "AutoprocTask",
    ContainerDefinitions=[
    ContainerDefinition(
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/", Ref(ConfigEnv)]),
        Name="data",
        Essential="false",
        Memory=128,
    ),
    ContainerDefinition(
        Name="Autoproc",
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/autoproc", ":", Ref(AutoprocImageVersion)]),
        Cpu=Ref(AutoprocCpu),
        PortMappings=[PortMapping(ContainerPort=Ref("AutoprocContainerPort") )],
        Memory=Ref(AutoprocMemory),
        Essential="true",
        VolumesFrom=[VolumesFrom(SourceContainer="data" )],
    ),
    ],
))

OhsScaleDownPolicy = t.add_resource(ScalingPolicy(
    "OhsScaleDownPolicy",
    ScalingTargetId=Ref(OhsscalableTarget),
    PolicyName="OhsScaleDown",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=-1, MetricIntervalUpperBound=0) ], AdjustmentType="ChangeInCapacity" )
))

CertificationCPUAlarmHigh = t.add_resource(Alarm(
    "CertificationCPUAlarmHigh",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateCluster")
            ),

            MetricDimension(
                Name="ServiceName",
                Value=  GetAtt("CertificationService", "Name")
            ),
        ],

    AlarmActions=[Ref("CertificationScaleUpPolicy")],
    AlarmDescription="Scale-up if CPU > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPUHighThreshold),
    MetricName="CPUUtilization",
))

LiferayELB = t.add_resource(LoadBalancerv2(
    "LiferayELB",
    Subnets=Ref(PublicSubnets),
    Scheme="internal",
    SecurityGroups=[Ref(SGPrivate)],
    LoadBalancerAttributes=[LoadBalancerAttributes(Value="50", Key= "idle_timeout.timeout_seconds" )],

))

BodybeastCPUAlarmLow = t.add_resource(Alarm(
    "BodybeastCPUAlarmLow",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateCluster")
            ),

            MetricDimension(
                Name="ServiceName",
                Value=  GetAtt("BodybeastServicee", "Name")
            ),
        ],

    AlarmActions=[Ref(BodybeastScaleDownPolicy)],
    AlarmDescription="Scale-down if CPU < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPULowThreshold),
    MetricName="CPUUtilization",
))

BodybeastListener = t.add_resource(Listener(
    "BodybeastListener",
    Protocol="HTTP",
    DefaultActions=[Action(TargetGroupArn=Ref("BodybeastELBTarget"), Type="forward" )],
    LoadBalancerArn=Ref(BodybeastELB),
    Port="80",
))

SolrBURNutchELBTarget = t.add_resource(TargetGroup(
    "SolrBURNutchELBTarget",
    HealthyThresholdCount=5,
    HealthCheckIntervalSeconds=300,
    VpcId=Ref(VPC),
    Protocol="HTTP",
    HealthCheckProtocol="HTTP",
    UnhealthyThresholdCount=4,
    HealthCheckPath="/solr/",
    HealthCheckTimeoutSeconds=60,
    Matcher=Matcher(HttpCode="200"),
    Port=5000,
))

BodybeastTask = t.add_resource(TaskDefinition(
    "BodybeastTask",
    ContainerDefinitions=[
    ContainerDefinition(
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/", Ref(ConfigEnv)]),
        Name="data",
        Essential="false",
        Memory=128,
    ),
    ContainerDefinition(
        PortMappings=[PortMapping(ContainerPort=Ref("BodybeastContainerPort") )],
        Name="Bodybeast",
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/bodybeast", ":", Ref(BodybeastImageVersion)]),
        Essential="true",
        Environment=[Environment(Name="SERVICE_NAME", Value="bodybeast" )],
        Memory=Ref(BodybeastMemory),
        Cpu=Ref(BodybeastCpu),
        VolumesFrom=[VolumesFrom(SourceContainer="data" )],
    ),
    ],
))

MongoReplica1ELB = t.add_resource(LoadBalancerv2(
    "MongoReplica1ELB",
    Subnets=Ref(PublicSubnets),
    Scheme="internal",
    SecurityGroups=[Ref(SGPrivate)],
    LoadBalancerAttributes=[LoadBalancerAttributes(Value="50", Key="idle_timeout.timeout_seconds" )],
))

SolrMasterScaleUpPolicy = t.add_resource(ScalingPolicy(
    "SolrMasterScaleUpPolicy",
    ScalingTargetId=Ref(SolrMasterscalableTarget),
    PolicyName="SolrMasterScaleUp",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=1, MetricIntervalLowerBound=0) ], AdjustmentType="ChangeInCapacity" ),
))

CertificationScaleUpPolicy = t.add_resource(ScalingPolicy(
    "CertificationScaleUpPolicy",
    ScalingTargetId=Ref(CertificationscalableTarget),
    PolicyName="CertificationScaleUp",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=1, MetricIntervalLowerBound=0) ], AdjustmentType="ChangeInCapacity" ),
))

SolrBURNutchService = t.add_resource(Service(
    "SolrBURNutchService",
    LoadBalancers=[LoadBalancer(
        ContainerName="SolrBURNutch",
        ContainerPort=network_port(Ref("SolrNutchPort")),
        TargetGroupArn=Ref("SolrBURNutchELBTarget")
    )],
    Cluster=Ref(ECSPrivateClusterSolrBURNutch),
    Role=Ref(ECSServiceRole),
    TaskDefinition=Ref("SolrBURNutchTask"),
    DesiredCount=1,
    DependsOn=["SolrBURNutchELB", "SolrBURNutchListener"],
))

MongoReplica2ScaleUpPolicy = t.add_resource(ScalingPolicy(
    "MongoReplica2ScaleUpPolicy",
    ScalingTargetId=Ref(MongoReplica2scalableTarget),
    PolicyName="MongoReplica2ScaleUp",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=1, MetricIntervalLowerBound=0) ], AdjustmentType="ChangeInCapacity" ),
))

SGPublic = t.add_resource(SecurityGroup(
    "SGPublic",
    SecurityGroupIngress=[{ "ToPort": "80", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "80" }],
    VpcId=Ref(VPC),
    GroupDescription="PublicSG",
))

ScaleUpPolicyPrivate = t.add_resource(InstanceScalingPolicy(
    "ScaleUpPolicyPrivate",
    ScalingAdjustment="1",
    Cooldown="300",
    AutoScalingGroupName=Ref(AutoscalingPrivateGroup),
    AdjustmentType="ChangeInCapacity",
))

SolrBURNutchScaleUpPolicy = t.add_resource(ScalingPolicy(
    "SolrBURNutchScaleUpPolicy",
    ScalingTargetId=Ref(SolrBURNutchscalableTarget),
    PolicyName="SolrBURNutchScaleUp",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=1, MetricIntervalLowerBound=0) ], AdjustmentType="ChangeInCapacity" ),
))


OhsCPUAlarmLow = t.add_resource(Alarm(
    "OhsCPUAlarmLow",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPublicCluster")
            ),

            MetricDimension(
                Name="ServiceName",
                Value=  GetAtt("OhsService", "Name")
            ),
        ],
    AlarmActions=[Ref(OhsScaleDownPolicy)],
    AlarmDescription="Scale-down if CPU < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPULowThreshold),
    MetricName="CPUUtilization",
))

SolrSlaveELBTarget = t.add_resource(TargetGroup(
    "SolrSlaveELBTarget",
    HealthyThresholdCount=5,
    HealthCheckIntervalSeconds=300,
    VpcId=Ref(VPC),
    Protocol="HTTP",
    HealthCheckProtocol="HTTP",
    UnhealthyThresholdCount=4,
    HealthCheckPath="/solr/",
    HealthCheckTimeoutSeconds=60,
    Matcher=Matcher(HttpCode="200"),
    Port=5000,
))

SolrSlaveCPUAlarmHigh = t.add_resource(Alarm(
    "SolrSlaveCPUAlarmHigh",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateClusterSolrSlave")
            ),

            MetricDimension(
                Name="ServiceName",
                Value=  GetAtt("SolrSlaveService", "Name")
            ),
        ],

    AlarmActions=[Ref(SolrSlaveScaleUpPolicy)],
    AlarmDescription="Scale-up if CPU > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPUHighThreshold),
    MetricName="CPUUtilization",
))

BodybeastScaleUpPolicy = t.add_resource(ScalingPolicy(
    "BodybeastScaleUpPolicy",
    ScalingTargetId=Ref("BodybeastscalableTarget"),
    PolicyName="BodybeastScaleUp",
    PolicyType="StepScaling",
 StepScalingPolicyConfiguration=StepScalingPolicyConfiguration(MetricAggregationType="Average", Cooldown=60, StepAdjustments=[StepAdjustment(ScalingAdjustment=1, MetricIntervalLowerBound=0) ], AdjustmentType="ChangeInCapacity" ),
))


BodybeastscalableTarget = t.add_resource(ScalableTarget(
    "BodybeastscalableTarget",
    ScalableDimension="ecs:service:DesiredCount",
    ResourceId=Join("", ["service/", Ref("ECSPrivateCluster"), "/", GetAtt(BodybeastService, "Name")]),
    RoleARN=GetAtt(ECSAutoscaleRole, "Arn"),
    MinCapacity=Ref(MinBodybeastSize),
    ServiceNamespace="ecs",
    MaxCapacity=Ref(MaxBodybeastSize),
))

CPUAlarmLowPrivateSolrSlave = t.add_resource(Alarm(
    "CPUAlarmLowPrivateSolrSlave",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateClusterSolrSlave")
            )
        ],
    AlarmActions=[Ref(ScaleDownPolicySolrSlave)],
    AlarmDescription="Scale-down if CPU Reserved < 60% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="LessThanThreshold",
    Statistic="Average",
    Threshold=Ref(CPULowThresholdPrivate),
    MetricName="CPUReservation",
))

SolrSlaveListener = t.add_resource(Listener(
    "SolrSlaveListener",
    Protocol="HTTP",
    DefaultActions=[Action(TargetGroupArn=Ref("SolrSlaveELBTarget"), Type="forward" )],
    LoadBalancerArn=Ref(SolrSlaveELB),
    Port="8983",
))

SolrMasterCPUAlarmHigh = t.add_resource(Alarm(
    "SolrMasterCPUAlarmHigh",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateClusterSolrMaster")
            ),

            MetricDimension(
                Name="ServiceName",
                Value=  GetAtt("SolrMasterService", "Name")
            ),
        ],
    AlarmActions=[Ref(SolrMasterScaleUpPolicy)],
    AlarmDescription="Scale-up if CPU > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(ApplicationCPUHighThreshold),
    MetricName="CPUUtilization",
))

CPUAlarmHighPrivateSolrGlobalNutch = t.add_resource(Alarm(
    "CPUAlarmHighPrivateSolrGlobalNutch",
    EvaluationPeriods="2",
    Dimensions=[
            MetricDimension(
                Name="ClusterName",
                Value= Ref("ECSPrivateClusterSolrGlobalNutch")
            )
        ],
    AlarmActions=[Ref(ScaleUpPolicySolrGlobalNutch)],
    AlarmDescription="Scale-up if CPU Reserved > 80% for 5 minutes",
    Namespace="AWS/ECS",
    Period="300",
    ComparisonOperator="GreaterThanThreshold",
    Statistic="Average",
    Threshold=Ref(CPUHighThresholdPrivate),
    MetricName="CPUReservation",
))

AutoprocscalableTarget = t.add_resource(ScalableTarget(
    "AutoprocscalableTarget",
    ScalableDimension="ecs:service:DesiredCount",
    ResourceId=Join("", ["service/", Ref("ECSPrivateCluster"), "/", GetAtt(AutoprocService, "Name")]),
    RoleARN=GetAtt(ECSAutoscaleRole, "Arn"),
    MinCapacity=Ref(MinAutoprocSize),
    ServiceNamespace="ecs",
    MaxCapacity=Ref(MaxAutoprocSize),
))

OhsELB = t.add_resource(LoadBalancerv2(
    "OhsELB",
    Subnets=Ref(PublicSubnets),
    Scheme="internet-facing",
    SecurityGroups=[Ref(SGPublic)],
    LoadBalancerAttributes=[LoadBalancerAttributes(Value="50", Key="idle_timeout.timeout_seconds" )],
))

ScaleDownPolicyPublic = t.add_resource(InstanceScalingPolicy(
    "ScaleDownPolicyPublic",
    ScalingAdjustment="-1",
    Cooldown="300",
    AutoScalingGroupName=Ref(AutoscalingPublicGroup),
    AdjustmentType="ChangeInCapacity",
))

SolrBURNutchELB = t.add_resource(LoadBalancerv2(
    "SolrBURNutchELB",
    Subnets=Ref(PublicSubnets),
    Scheme="internal",
    SecurityGroups=[Ref(SGPrivate)],
    LoadBalancerAttributes=[LoadBalancerAttributes(Value="50", Key="idle_timeout.timeout_seconds" )],
))

SolrGlobalNutchscalableTarget = t.add_resource(ScalableTarget(
    "SolrGlobalNutchscalableTarget",
    ScalableDimension="ecs:service:DesiredCount",
    ResourceId=Join("", ["service/", Ref(ECSPrivateClusterSolrGlobalNutch), "/", GetAtt(SolrGlobalNutchService, "Name")]),
    RoleARN=GetAtt(ECSAutoscaleRole, "Arn"),
    MinCapacity=1,
    ServiceNamespace="ecs",
    MaxCapacity=2,
))

CertificationELB = t.add_resource(LoadBalancerv2(
    "CertificationELB",
    Subnets=Ref(PublicSubnets),
    Scheme="internal",
    SecurityGroups=[Ref(SGPrivate)],
    LoadBalancerAttributes=[LoadBalancerAttributes(Value="50", Key="idle_timeout.timeout_seconds" )],
))

MongoReplica2ELB = t.add_resource(LoadBalancerv2(
    "MongoReplica2ELB",
    Subnets=Ref(PublicSubnets),
    Scheme="internal",
    SecurityGroups=[Ref(SGPrivate)],
    LoadBalancerAttributes=[LoadBalancerAttributes(Value="50", Key="idle_timeout.timeout_seconds" )],
))

SolrBURNutchTask = t.add_resource(TaskDefinition(
    "SolrBURNutchTask",
    ContainerDefinitions=[
    ContainerDefinition(
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/", Ref(ConfigEnv)]),
        Name="data",
        Essential="false",
        Memory=128,
    ),
    ContainerDefinition(
        MountPoints=[MountPoint(SourceVolume="data", ContainerPath="/opt/data")],
        Name="SolrBURNutch",
        Image=Join("", ["904597257252.dkr.ecr.us-west-2.amazonaws.com/tbb/tbb_bur", ":", Ref(SolrBURNutchImageVersion)]),
        Cpu=Ref(SolrCpu),
        PortMappings=[PortMapping(ContainerPort=Ref("SolrNutchPort") )],
        Memory=Ref(SolrNutchMemory),
        Essential="true",
        VolumesFrom=[VolumesFrom(SourceContainer="data" )],
    ),
    ],
 Volumes=[Volume(Host=Host(SourcePath="/opt/data/") , Name="data" )],
))


ECSPrivateCluster = t.add_resource(Cluster(
    "ECSPrivateCluster",
))

GeneralELB = t.add_resource(LoadBalancerv2(
    "GeneralELB",
    Subnets=Ref(PublicSubnets),
    Scheme="internal",
    SecurityGroups=[Ref(SGPrivate)],
    LoadBalancerAttributes=[LoadBalancerAttributes(Value="50", Key="idle_timeout.timeout_seconds" )],

))

MongoReplica2Service = t.add_resource(Service(
    "MongoReplica2Service",
    LoadBalancers=[LoadBalancer(
        ContainerName="MongoReplica2",
        ContainerPort=network_port("27017"),
        TargetGroupArn=Ref("MongoReplica2ELBTarget")
    )],
    Cluster=Ref(ECSPrivateClusterMongoReplica2),
    Role=Ref(ECSServiceRole),
    TaskDefinition=Ref(MongoReplica2Task),
    DesiredCount=1,
    DependsOn=["MongoReplica2ELB", "MongoReplica2Listener"],
))

SolrGlobalNutchELB = t.add_output(Output(
    "SolrGlobalNutchELB",
    Description="The DNSName of the SolrGlobalNutch load balancer",
    Value=GetAtt(SolrGlobalNutchELB, "DNSName"),
))

SolrBURlNutchELB = t.add_output(Output(
    "SolrBURlNutchELB",
    Description="The DNSName of the SolrBURNutch load balancer",
    Value=GetAtt(SolrBURNutchELB, "DNSName"),
))

BodybeastLoadBalancerDNSName = t.add_output(Output(
    "BodybeastLoadBalancerDNSName",
    Description="The DNSName of the Bodybeast load balancer",
    Value=GetAtt(BodybeastELB, "DNSName"),
))

SolrMasterELB = t.add_output(Output(
    "SolrMasterELB",
    Description="The DNSName of the SolrMaster load balancer",
    Value=GetAtt(SolrMasterELB, "DNSName"),
))

MongoReplica1ELB = t.add_output(Output(
    "MongoReplica1ELB",
    Description="The DNSName of the MongoReplica1 load balancer",
    Value=GetAtt(MongoReplica1ELB, "DNSName"),
))

OhsLoadBalancerDNSName = t.add_output(Output(
    "OhsLoadBalancerDNSName",
    Description="The DNSName of the Ohs load balancer",
    Value=GetAtt(OhsELB, "DNSName"),
))

MongoReplica2ELB = t.add_output(Output(
    "MongoReplica2ELB",
    Description="The DNSName of the MongoReplica2 load balancer",
    Value=GetAtt(MongoReplica2ELB, "DNSName"),
))

CertificationLoadBalancerDNSName = t.add_output(Output(
    "CertificationLoadBalancerDNSName",
    Description="The DNSName of the Certification load balancer",
    Value=GetAtt(CertificationELB, "DNSName"),
))

LiferayLoadBalancerDNSName = t.add_output(Output(
    "LiferayLoadBalancerDNSName",
    Description="The DNSName of the Liferay load balancer",
    Value=GetAtt(LiferayELB, "DNSName"),
))

GeneralELB = t.add_output(Output(
    "GeneralELB",
    Description="The DNSName of the General load balancer",
    Value=GetAtt(GeneralELB, "DNSName"),
))

SolrSlaveELB = t.add_output(Output(
    "SolrSlaveELB",
    Description="The DNSName of the SolrSlave load balancer",
    Value=GetAtt(SolrSlaveELB, "DNSName"),
))

AutoprocLoadBalancerDNSName = t.add_output(Output(
    "AutoprocLoadBalancerDNSName",
    Description="The DNSName of the Autoproc load balancer",
    Value=GetAtt(AutoprocELB, "DNSName"),
))

print(t.to_json())
