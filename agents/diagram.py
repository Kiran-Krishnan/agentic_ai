import importlib

import hcl2
from diagrams import Diagram, Cluster, Edge
from diagrams.generic.compute import Rack


def normalize_type(value) -> str:
    return str(value).strip().lower().replace('"', '').replace("'", "")


def load_terraform(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return hcl2.load(f)


def extract_resources(tf_data: dict) -> list[dict]:
    resources = []
    for resource_block in tf_data.get("resource", []):
        for res_type, res_objs in resource_block.items():
            res_type = normalize_type(res_type)
            for name, config in res_objs.items():
                resources.append(
                    {
                        "type": res_type,
                        "name": name,
                        "config": config or {},
                        "address": f"{res_type}.{name}",
                    }
                )
    return resources


def first_resource(resources: list[dict], resource_type: str, predicate=None):
    for resource in resources:
        if resource["type"] != resource_type:
            continue
        if predicate is not None and not predicate(resource):
            continue
        return resource
    return None


def config_value(resource: dict | None, key: str, default=None):
    if not resource:
        return default
    value = resource.get("config", {}).get(key)
    return default if value in (None, "") else value


def resource_label(resource: dict | None, default: str) -> str:
    if not resource:
        return default

    cfg = resource.get("config", {})
    tags = cfg.get("tags", {})

    if isinstance(tags, dict):
        for key in ("Name", "name", "Title"):
            value = tags.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    for key in (
        "bucket",
        "function_name",
        "cluster_name",
        "cluster_identifier",
        "db_name",
        "table_name",
        "topic_name",
        "queue_name",
        "log_group_name",
        "repository_name",
        "domain_name",
        "identifier",
        "policy_name",
        "role_name",
        "group_name",
        "user_name",
        "name",
    ):
        value = cfg.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return default


def subnet_role(resource: dict) -> str:
    cfg = resource.get("config", {})
    if cfg.get("map_public_ip_on_launch") is True:
        return "public"

    label = resource_label(resource, resource["name"]).lower()
    if "public" in label and "private" not in label:
        return "public"
    return "private"


def build_node(label: str, candidates: list[tuple[str, str]]):
    for module_name, class_name in candidates:
        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            return cls(label)
        except Exception:
            continue

    # Visible fallback node
    return Rack(label)


SERVICE_CANDIDATES = {
    "aws_user": [("diagrams.aws.general", "User")],
    "aws_cloudfront_distribution": [("diagrams.aws.network", "CloudFront")],
    "aws_wafv2_web_acl": [("diagrams.aws.security", "WAF")],
    "aws_vpc": [("diagrams.aws.network", "VPC")],
    "aws_subnet_public": [("diagrams.aws.network", "PublicSubnet")],
    "aws_subnet_private": [("diagrams.aws.network", "PrivateSubnet")],
    "aws_internet_gateway": [("diagrams.aws.network", "InternetGateway")],
    "aws_nat_gateway": [("diagrams.aws.network", "NATGateway")],
    "aws_lb": [
        ("diagrams.aws.network", "ELB"),
        ("diagrams.aws.network", "ELBv2"),
    ],
    "aws_instance": [("diagrams.aws.compute", "EC2")],
    "aws_autoscaling_group": [("diagrams.aws.compute", "AutoScaling")],
    "aws_lambda_function": [("diagrams.aws.compute", "Lambda")],
    "aws_ecs_cluster": [
        ("diagrams.aws.compute", "ECS"),
        ("diagrams.aws.container", "ECS"),
    ],
    "aws_db_instance": [("diagrams.aws.database", "RDS")],
    "aws_dynamodb_table": [("diagrams.aws.database", "DynamoDB")],
    "aws_elasticache_cluster": [("diagrams.aws.database", "ElastiCache")],
    "aws_s3_bucket": [("diagrams.aws.storage", "S3")],
    "aws_efs_file_system": [("diagrams.aws.storage", "EFS")],
    "aws_sqs_queue": [("diagrams.aws.integration", "SQS")],
    "aws_sns_topic": [("diagrams.aws.integration", "SNS")],
    "aws_iam_role": [("diagrams.aws.security", "IAM")],
    "aws_kms_key": [("diagrams.aws.security", "KMS")],
    "aws_secretsmanager_secret": [("diagrams.aws.security", "SecretsManager")],
    "aws_cloudwatch_log_group": [("diagrams.aws.management", "Cloudwatch")],
    "aws_cloudtrail": [("diagrams.aws.management", "Cloudtrail")],
    "aws_codepipeline": [("diagrams.aws.devtools", "CodePipeline")],
    "aws_codebuild_project": [("diagrams.aws.devtools", "CodeBuild")],
    "aws_ecr_repository": [
        ("diagrams.aws.container", "ECR"),
        ("diagrams.aws.devtools", "ECR"),
    ],
}


def node_for(resource: dict | None, default_label: str):
    if not resource:
        return None

    rtype = normalize_type(resource["type"])

    if rtype == "aws_subnet":
        role = subnet_role(resource)
        key = f"aws_subnet_{role}"
        label = resource_label(resource, default_label)
        return build_node(label, SERVICE_CANDIDATES.get(key, []))

    label = resource_label(resource, default_label)
    return build_node(label, SERVICE_CANDIDATES.get(rtype, []))


def connect(src, dst, dashed: bool = False):
    if src is None or dst is None:
        return
    if dashed:
        src >> Edge(style="dashed", color="gray") >> dst
    else:
        src >> dst


def render(terraform_file: str = "infra.tf", out_name: str = "aws_architecture_from_iac"):
    tf_data = load_terraform(terraform_file)
    resources = extract_resources(tf_data)

    if not resources:
        raise ValueError("No Terraform resources found in the file.")

    vpc_res = first_resource(resources, "aws_vpc")
    cloudfront_res = first_resource(resources, "aws_cloudfront_distribution")
    waf_res = first_resource(resources, "aws_wafv2_web_acl")
    alb_res = first_resource(resources, "aws_lb")

    igw_res = first_resource(resources, "aws_internet_gateway")
    nat_res = first_resource(resources, "aws_nat_gateway")
    eip_res = first_resource(resources, "aws_eip")
    sg_res = first_resource(resources, "aws_security_group")

    public_subnet_res = first_resource(
        resources,
        "aws_subnet",
        lambda r: subnet_role(r) == "public",
    )
    private_subnet_res = first_resource(
        resources,
        "aws_subnet",
        lambda r: subnet_role(r) == "private",
    )

    asg_res = first_resource(resources, "aws_autoscaling_group")
    ec2_res = first_resource(resources, "aws_instance")
    lambda_res = first_resource(resources, "aws_lambda_function")
    ecs_res = first_resource(resources, "aws_ecs_cluster")

    rds_res = first_resource(resources, "aws_db_instance")
    dynamo_res = first_resource(resources, "aws_dynamodb_table")
    cache_res = first_resource(resources, "aws_elasticache_cluster")

    s3_res = first_resource(resources, "aws_s3_bucket")
    efs_res = first_resource(resources, "aws_efs_file_system")

    sqs_res = first_resource(resources, "aws_sqs_queue")
    sns_res = first_resource(resources, "aws_sns_topic")

    iam_res = first_resource(resources, "aws_iam_role")
    kms_res = first_resource(resources, "aws_kms_key")
    secret_res = first_resource(resources, "aws_secretsmanager_secret")

    logs_res = first_resource(resources, "aws_cloudwatch_log_group")
    trail_res = first_resource(resources, "aws_cloudtrail")

    pipeline_res = first_resource(resources, "aws_codepipeline")
    build_res = first_resource(resources, "aws_codebuild_project")
    repo_res = first_resource(resources, "aws_ecr_repository")

    rendered_addresses = set()

    def pick(resource: dict | None, default_label: str):
        node = node_for(resource, default_label)
        if resource is not None:
            rendered_addresses.add(resource["address"])
        return node

    vpc_cidr = config_value(vpc_res, "cidr_block", "")
    vpc_title = "VPC" if not vpc_cidr else f"VPC ({vpc_cidr})"

    with Diagram(
        "AWS Architecture from IaC",
        filename=out_name,
        outformat="png",
        show=True,
        direction="LR",
        graph_attr={
            "splines": "ortho",
            "nodesep": "0.7",
            "ranksep": "1.0",
            "pad": "0.4",
            "compound": "true",
        },
    ):
        user = pick(
            {"type": "aws_user", "name": "user", "config": {"name": "User"}, "address": "aws_user.user"},
            "User",
        )

        with Cluster("Edge / Public Entry"):
            cloudfront = pick(cloudfront_res, "CloudFront")
            waf = pick(waf_res, "WAF")

        with Cluster(vpc_title):
            vpc = pick(vpc_res, "main")

            with Cluster("Public Subnet"):
                public_subnet = pick(public_subnet_res, "public-subnet")
                igw = pick(igw_res, "Internet Gateway")
                alb = pick(alb_res, "ALB")
                nat = pick(nat_res, "NAT Gateway")
                eip = pick(eip_res, "EIP")

            with Cluster("Private Subnet"):
                private_subnet = pick(private_subnet_res, "private-subnet")
                sg = pick(sg_res, "Security Group")
                asg = pick(asg_res, "ASG")
                ec2 = pick(ec2_res, "app-server")
                lambda_fn = pick(lambda_res, "Lambda")
                ecs = pick(ecs_res, "ECS Cluster")

            with Cluster("Data Tier"):
                rds = pick(rds_res, "RDS")
                dynamo = pick(dynamo_res, "DynamoDB")
                cache = pick(cache_res, "ElastiCache")

        with Cluster("Storage"):
            s3 = pick(s3_res, "S3")
            efs = pick(efs_res, "EFS")

        with Cluster("Integration"):
            sqs = pick(sqs_res, "SQS")
            sns = pick(sns_res, "SNS")

        with Cluster("Security / Identity"):
            iam_role = pick(iam_res, "IAM Role")
            kms = pick(kms_res, "KMS")
            secret = pick(secret_res, "Secrets Manager")

        with Cluster("Observability"):
            logs = pick(logs_res, "CloudWatch Logs")
            trail = pick(trail_res, "CloudTrail")

        with Cluster("DevOps"):
            pipeline = pick(pipeline_res, "CodePipeline")
            build = pick(build_res, "CodeBuild")
            repo = pick(repo_res, "ECR")

        # Optional: any extra resources you later add will still appear.
        other_resources = [r for r in resources if r["address"] not in rendered_addresses]
        if other_resources:
            with Cluster("Other Resources"):
                for r in other_resources:
                    pick(r, r["name"].replace("_", " ").title())

        # Clean AWS-style flow
        connect(user, cloudfront)
        connect(cloudfront, waf)
        connect(waf, alb)

        connect(vpc, public_subnet)
        connect(vpc, private_subnet)

        connect(public_subnet, igw)
        connect(igw, alb)
        connect(eip, nat)
        connect(public_subnet, nat)
        connect(nat, private_subnet)

        connect(private_subnet, sg)
        connect(private_subnet, asg)
        connect(asg, ec2)
        connect(alb, asg)

        connect(private_subnet, lambda_fn)
        connect(private_subnet, ecs)

        connect(private_subnet, rds)
        connect(private_subnet, dynamo)
        connect(private_subnet, cache)

        connect(ec2, rds)
        connect(ec2, dynamo)
        connect(ec2, cache)
        connect(ec2, s3)
        connect(ec2, efs)
        connect(ec2, logs)
        connect(lambda_fn, logs)

        connect(sns, sqs)
        connect(sqs, lambda_fn)

        connect(iam_role, ec2, dashed=True)
        connect(iam_role, lambda_fn, dashed=True)
        connect(kms, secret)
        connect(secret, ec2, dashed=True)

        connect(pipeline, build)
        connect(build, repo)
        connect(repo, ecs)

        connect(sg, ec2, dashed=True)
        connect(sg, alb, dashed=True)

    print(f"Saved diagram to {out_name}.png")


if __name__ == "__main__":
    render("infra.tf")